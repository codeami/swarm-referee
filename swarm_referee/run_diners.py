"""Run one Diners game with the Shi harness (OpenRouter models, or deepseek* models through DeepSeek's own API).

What this wrapper changes (it never edits vendor/):
  - swaps the paid judge model name for the free model (safety net);
  - skips the judge and reflection calls, so one game is 75 calls (plus one extra call for each stage reply
    that has no action field: the same request is sent once more; failed replies go to raw_failures.json);
  - adds the earlier rounds' public messages to every agent prompt;
  - adds the instructions of the chosen class to the named agents, set by --class (see classes.py);
  - limits requests to one per 3.5 s, with a 90 s request timeout and a 120 s idle watchdog;
  - for a model name that starts with deepseek, sends the agent calls to https://api.deepseek.com with the key
    DEEPSEEK_API_KEY from .env; a 401, 402, 403 or 404 reply stops the game at once;
  - counts calls, and writes one row to data/run_meta.csv.

Usage: .venv/bin/python -m swarm_referee.run_diners <free-model> --class planted_pair|independent_cheats|cooperation_pact|talk_only|innocent_parallel
           [--set practice|scored] [--run-dir DIR]
"""

import argparse
import asyncio
import faulthandler
import json
import os
import re
import runpy
import sys
import threading
import time
from typing import Callable, Dict, Optional

import aiohttp

from swarm_referee import classes, records

VENDOR = os.path.join(records.ROOT, "vendor", "LLM-Trust-Breaking")
PAID_JUDGE = "openai/gpt-5-mini"
CHARS_PER_TOKEN = 4  # rough estimate; the harness does not log token usage

# Free OpenRouter models allow 20 requests per minute. Start one request every 3.5 s.
MIN_GAP_SECONDS = 3.5
MAX_RETRIES = 8
REQUEST_TIMEOUT = 90  # seconds for one request; the harness default is 120 per attempt
IDLE_ABORT_SECONDS = 120  # abort the game when no request starts or ends for this long
SKIPPED_STEPS = ("Judge", "Reflection")  # progress labels of the calls we drop

CID = re.compile(r"r(\d+)_t\d+_s([123])_(\w+)$")

next_slot = 0.0
stats = {"calls": 0, "prompt_chars": 0, "reply_chars": 0, "max_retries": 0}
activity = {"last": time.monotonic(), "loop": None}  # watchdog clock: set when a request starts or ends


def touch() -> None:
    activity["last"] = time.monotonic()


def dump_stacks(path: str) -> None:
    """Write every Python thread stack and every asyncio task stack to path."""
    with open(path, "w") as fh:
        fh.write("Thread stacks:\n")
        fh.flush()
        faulthandler.dump_traceback(file=fh, all_threads=True)
        loop = activity.get("loop")
        fh.write("\nAsyncio tasks:\n")
        if loop is not None:
            for task in asyncio.all_tasks(loop):
                task.print_stack(file=fh)


def start_watchdog(idle_seconds: float, on_hang: Callable, poll: float = 1.0) -> threading.Thread:
    """Call on_hang once when touch() was not called for idle_seconds. Runs as a daemon thread."""

    def watch():
        while True:
            time.sleep(poll)
            if time.monotonic() - activity["last"] > idle_seconds:
                on_hang()
                return

    thread = threading.Thread(target=watch, daemon=True)
    thread.start()
    return thread


DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_TRIES = 3  # one call and two retries; only 408, 429 and 5xx are retried
RETRY_STATUSES = (408, 429, 500, 502, 503, 504)
RETRY_SLEEP = (1.0, 2.0)
DEEPSEEK_MIN_TOKENS = 8000  # the model thinks before it answers; with 2000 the answer was empty (finish_reason length)
api_log: list = []  # one row per DeepSeek reply: finish reason and token counts; saved as api_calls.jsonl


def is_deepseek(model: str) -> bool:
    return model.lower().startswith("deepseek")


def make_throttled(send: Callable) -> Callable:
    """Wrap a client request sender: one request per MIN_GAP_SECONDS, a hard time limit, watchdog marks."""

    async def throttled(self, session, request):
        global next_slot
        activity["loop"] = asyncio.get_running_loop()
        slot = max(time.monotonic(), next_slot)
        next_slot = slot + MIN_GAP_SECONDS
        await asyncio.sleep(slot - time.monotonic())
        self.max_retries = MAX_RETRIES
        touch()
        try:
            return await asyncio.wait_for(send(self, session, request), REQUEST_TIMEOUT * 2)
        finally:
            touch()

    return throttled


def make_deepseek_send(fatal: Callable, sleep: Callable = asyncio.sleep) -> Callable:
    """Sender for the OpenAI-style queue client pointed at DeepSeek.

    Fails fast: 401, 402, 403 and 404 (bad key, no balance, unknown model) call fatal() at once.
    408, 429 and 5xx get at most two retries. Other statuses return an error reply.
    """

    async def send(self, session, request):
        cid = request["custom_id"]
        payload = {"model": request["model"], "messages": request["messages"],
                   "max_tokens": max(request.get("max_tokens", 100), DEEPSEEK_MIN_TOKENS),
                   "temperature": request.get("temperature", 1.0)}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        error = "no reply"
        doubled = False
        attempt = 0
        while attempt < DEEPSEEK_TRIES:
            try:
                async with session.post(self.chat_url, json=payload, headers=headers) as response:
                    if response.status < 300:
                        data = await response.json()
                        choice = data["choices"][0]
                        content = choice["message"].get("content") or ""
                        usage = data.get("usage") or {}
                        api_log.append({
                            "custom_id": cid, "finish_reason": choice.get("finish_reason"),
                            "max_tokens": payload["max_tokens"], "content_chars": len(content),
                            "prompt_tokens": usage.get("prompt_tokens"),
                            "completion_tokens": usage.get("completion_tokens"),
                            "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                        })
                        if not content and choice.get("finish_reason") == "length" and not doubled:
                            doubled = True  # the model used all its tokens thinking: ask once more with twice as many
                            payload = {**payload, "max_tokens": payload["max_tokens"] * 2}
                            stats["calls"] += 1
                            stats["length_retries"] = stats.get("length_retries", 0) + 1
                            continue
                        return cid, {"content": content, "finish_reason": choice.get("finish_reason")}
                    error = f"HTTP {response.status}: {(await response.text())[:200]}"
                    if response.status not in RETRY_STATUSES:
                        if response.status in (401, 402, 403, 404):
                            fatal(f"{error} (model {request['model']})")
                        return cid, {"status": "error", "error": error}
            except (asyncio.TimeoutError, aiohttp.ClientError, KeyError, IndexError, ValueError) as exc:
                error = f"{type(exc).__name__}: {exc}"
            if attempt < DEEPSEEK_TRIES - 1:
                await sleep(RETRY_SLEEP[attempt])
            attempt += 1
        return cid, {"status": "error", "error": f"Max retries exceeded: {error}"}

    return send


def patch_deepseek(client_factory, trial_runner, openai_cls, environ: dict, fatal: Callable) -> None:
    """Route deepseek* agent models through the OpenAI-style queue client, pointed at DeepSeek's API."""
    key = environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        raise SystemExit("DEEPSEEK_API_KEY is missing or empty in .env")
    environ["OPENAI_API_KEY"] = key  # the harness reads this variable for its OpenAI-style client
    original = client_factory.is_openai_model

    def routes_to_openai_client(model: str) -> bool:
        return is_deepseek(model) or original(model)

    client_factory.is_openai_model = routes_to_openai_client
    trial_runner.is_openai_model = routes_to_openai_client
    init = openai_cls.__init__

    def init_with_url(self, *a, **kw):
        init(self, *a, **kw)
        self.chat_url = DEEPSEEK_URL
        self.timeout = REQUEST_TIMEOUT

    openai_cls.__init__ = init_with_url
    openai_cls._execute_single_async = make_throttled(make_deepseek_send(fatal))


def history_block(history: Dict[int, Dict[str, tuple]], round_idx: int) -> str:
    """Public messages of rounds before round_idx. Empty in round 0."""
    lines = []
    for rnd in sorted(r for r in history if r < round_idx):
        lines.append(f"Round {rnd + 1}:")
        for agent, (stated, message) in history[rnd].items():
            lines.append(f'  {agent} said they would order {stated}: "{message}"')
    return f"\n\n{classes.HISTORY_HEADER}\n" + "\n".join(lines) if lines else ""


def make_build_request(build_request: Callable, model: str, class_name: str, history: dict) -> Callable:
    """Wrap the harness _build_request: judge swap, class instruction, message history."""

    def build(*args, **kwargs):
        if kwargs.get("model") == PAID_JUDGE:
            kwargs["model"] = model
        m = CID.search(kwargs.get("custom_id", ""))
        if m:
            round_idx, stage, agent = int(m.group(1)), m.group(2), m.group(3)
            text = classes.instruction_for(class_name, agent, f"s{stage}", round_idx)
            if text:
                kwargs["system_prompt"] += "\n\n" + text
            kwargs["user_prompt"] += history_block(history, round_idx)
        return build_request(*args, **kwargs)

    return build


def record_messages(history: dict, results: dict, parse: Callable) -> None:
    """Store each stage-2 reply of a finished request batch in history."""
    for cid, response in results.items():
        m = CID.search(cid)
        if m and m.group(2) == "2":
            parsed = parse(response, ["stated_action"])
            history.setdefault(int(m.group(1)), {})[m.group(3)] = (
                parsed.get("stated_action") or "unknown", parsed.get("message", ""))


STAGE_FIELD = {"1": "intended_action", "2": "stated_action", "3": "choice"}  # field a stage must return


def unparsed(requests: list, result: dict, parse: Callable) -> list:
    """Requests of a finished batch whose reply lacks the stage's action field."""
    bad = []
    for req in requests:
        m = CID.search(req.get("custom_id", ""))
        if m and not parse(result.get(req["custom_id"]), [STAGE_FIELD[m.group(2)]]).get(STAGE_FIELD[m.group(2)]):
            bad.append(req)
    return bad


def make_execute(execute: Callable, history: dict, parse: Callable, count_stats: dict) -> Callable:
    """Wrap the harness request executor: skip judge/reflection, retry once, count, keep history."""

    def count(requests, result):
        count_stats["calls"] += len(requests)
        count_stats["prompt_chars"] += sum(len(json.dumps(r.get("messages", ""))) for r in requests)
        count_stats["reply_chars"] += len(json.dumps(result, default=str))

    def run(requests, *args, **kwargs):
        label = args[2] if len(args) > 2 else kwargs.get("progress_desc", "")
        if str(label).startswith(SKIPPED_STEPS):
            return {}
        touch()
        result = execute(requests, *args, **kwargs)
        touch()
        count(requests, result)
        retry = unparsed(requests, result, parse)  # same prompt, one extra call each
        if retry:
            for req in retry:
                count_stats.setdefault("raw_failures", []).append(
                    {"custom_id": req["custom_id"], "reply": str(result.get(req["custom_id"]))[:2000]})
            touch()
            again = execute(retry, *args, **kwargs)
            touch()
            count(retry, again)
            count_stats["retries"] = count_stats.get("retries", 0) + len(retry)
            result = {**result, **{cid: r for cid, r in again.items() if not unparsed(
                [q for q in retry if q["custom_id"] == cid], {cid: r}, parse)}}
        for cid, resp in result.items():
            if isinstance(resp, dict) and "Max retries" in str(resp.get("error", "")):
                count_stats["max_retries"] += 1
                print(f"Max retries exceeded for {cid}")
        record_messages(history, result, parse)
        return result

    return run


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--class", dest="class_name", required=True, choices=classes.CLASS_NAMES)
    ap.add_argument("--set", dest="set_name", default="practice", choices=["practice", "scored"])
    ap.add_argument("--run-dir", default=None)
    ap.add_argument("--rounds", type=int, default=classes.N_ROUNDS,
                    help="fewer rounds only to test the setup; such a game writes no run_meta row")
    ap.add_argument("--regen-of", default="", help="run id of the drifted planted_pair run this game replaces")
    args = ap.parse_args(argv)
    run_dir = os.path.abspath(args.run_dir or records.next_run_dir(args.set_name))

    sys.path.insert(0, VENDOR)
    os.chdir(VENDOR)  # the harness loads .env from its own folder tree
    from dotenv import load_dotenv

    load_dotenv(os.path.join(records.ROOT, ".env"))

    from src.endogenous.core import trial_runner
    from src.llm.providers import queued_openrouter

    history: dict = {}
    trial_runner._build_request = make_build_request(
        trial_runner._build_request, args.model, args.class_name, history)
    trial_runner._execute_requests_split_by_provider = make_execute(
        trial_runner._execute_requests_split_by_provider, history, trial_runner._parse_response, stats)

    client_cls = queued_openrouter.QueuedOpenRouterClient
    send = client_cls._execute_single_async

    init = client_cls.__init__

    def init_with_timeout(self, *a, **kw):
        init(self, *a, **kw)
        self.timeout = REQUEST_TIMEOUT  # used for the whole HTTP session of one request batch

    client_cls.__init__ = init_with_timeout

    client_cls._execute_single_async = make_throttled(send)

    d = classes.DISH
    sys.argv = [
        "run_endogenous.py", "--game", "diners", "--agents", str(classes.N_AGENTS), "--trials", "1",
        "--rounds", str(args.rounds), "--model", args.model, "--use-queue", "--round-robin",
        "--expensive-joy", str(d["expensive_joy"]), "--cheap-joy", str(d["cheap_joy"]),
        "--expensive-cost", str(d["expensive_cost"]), "--cheap-cost", str(d["cheap_cost"]),
        "--output-dir", run_dir,
    ]
    note = ""
    full_game = args.rounds == classes.N_ROUNDS

    def abort_game(reason: str = "hang") -> None:
        """Stop the game: a hang (save the stacks) or a fatal API error. Record the run, then exit."""
        if reason == "hang":
            dump_stacks(os.path.join(records.DATA, "practice", "hang_dump.txt"))
            print(f"HANG: no request activity for {IDLE_ABORT_SECONDS} s; stacks in data/practice/hang_dump.txt",
                  flush=True)
        else:
            print(f"FATAL API ERROR: {reason}", flush=True)
        if full_game:
            records.append_meta(records.meta_row(
                run_dir, args.set_name, args.class_name, args.model, classes.DISH, classes.MODE,
                stats["calls"], records.check_run(run_dir), f"aborted: {reason[:80]}", args.regen_of))
        os._exit(3)

    if is_deepseek(args.model):
        from src.llm import client_factory
        from src.llm.providers.queued_openai import QueuedOpenAIClient

        patch_deepseek(client_factory, trial_runner, QueuedOpenAIClient, os.environ, abort_game)

    touch()
    start_watchdog(IDLE_ABORT_SECONDS, abort_game)
    try:
        runpy.run_path(os.path.join(VENDOR, "experiments", "run_endogenous.py"), run_name="__main__")
    except BaseException as exc:  # keep a record of a crashed game
        note = f"crashed: {type(exc).__name__}"
        raise
    finally:
        est = (stats["prompt_chars"] + stats["reply_chars"]) // CHARS_PER_TOKEN
        print(f"CALLS={stats['calls']} EXPECTED={classes.EXPECTED_CALLS} EST_TOKENS={est}")
        missing = records.check_run(run_dir)
        if missing is not None:
            print(f"MISSING stage1={missing['stage1']} stage2={missing['stage2']} stage3={missing['stage3']}")
        if stats["max_retries"]:
            note = (note + f" max_retries={stats['max_retries']}").strip()
        if stats.get("length_retries"):
            note = (note + f" length_retries={stats['length_retries']}").strip()
        if api_log:
            os.makedirs(run_dir, exist_ok=True)
            with open(os.path.join(run_dir, "api_calls.jsonl"), "w") as fh:
                fh.writelines(json.dumps(row) + "\n" for row in api_log)
        if stats.get("retries"):
            note = (note + f" reply_retries={stats['retries']}").strip()
            with open(os.path.join(run_dir, "raw_failures.json"), "w") as fh:
                json.dump(stats["raw_failures"], fh, indent=1)
        if full_game:
            records.append_meta(records.meta_row(
                run_dir, args.set_name, args.class_name, args.model, classes.DISH, classes.MODE,
                stats["calls"], missing, note, args.regen_of))
    return 0


if __name__ == "__main__":
    sys.exit(main())
