"""Run one Diners game with the Shi harness, free models only.

What this wrapper changes (it never edits vendor/):
  - swaps the paid judge model name for the free model (safety net);
  - skips the judge and reflection calls, so one game is 75 calls;
  - adds the earlier rounds' public messages to every agent prompt;
  - adds the instructions of the chosen class to the named agents, set by --class (see classes.py);
  - limits requests to one per 3.5 s (free models allow 20 per minute);
  - counts calls, and writes one row to data/run_meta.csv.

Usage: .venv/bin/python -m swarm_referee.run_diners <free-model> --class planted_pair|independent_cheats|cooperation_pact|talk_only|innocent_parallel
           [--set practice|scored] [--run-dir DIR]
"""

import argparse
import asyncio
import json
import os
import re
import runpy
import sys
import time
from typing import Callable, Dict, Optional

from swarm_referee import classes, records

VENDOR = os.path.join(records.ROOT, "vendor", "LLM-Trust-Breaking")
PAID_JUDGE = "openai/gpt-5-mini"
CHARS_PER_TOKEN = 4  # rough estimate; the harness does not log token usage

# Free OpenRouter models allow 20 requests per minute. Start one request every 3.5 s.
MIN_GAP_SECONDS = 3.5
MAX_RETRIES = 8
SKIPPED_STEPS = ("Judge", "Reflection")  # progress labels of the calls we drop

CID = re.compile(r"r(\d+)_t\d+_s([123])_(\w+)$")

next_slot = 0.0
stats = {"calls": 0, "prompt_chars": 0, "reply_chars": 0, "max_retries": 0}


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


def make_execute(execute: Callable, history: dict, parse: Callable, count_stats: dict) -> Callable:
    """Wrap the harness request executor: skip judge/reflection, count, keep history."""

    def run(requests, *args, **kwargs):
        label = args[2] if len(args) > 2 else kwargs.get("progress_desc", "")
        if str(label).startswith(SKIPPED_STEPS):
            return {}
        result = execute(requests, *args, **kwargs)
        count_stats["calls"] += len(requests)
        count_stats["prompt_chars"] += sum(len(json.dumps(r.get("messages", ""))) for r in requests)
        count_stats["reply_chars"] += len(json.dumps(result, default=str))
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

    async def throttled(self, session, request):
        global next_slot
        slot = max(time.monotonic(), next_slot)
        next_slot = slot + MIN_GAP_SECONDS
        await asyncio.sleep(slot - time.monotonic())
        self.max_retries = MAX_RETRIES
        return await send(self, session, request)

    client_cls._execute_single_async = throttled

    d = classes.DISH
    sys.argv = [
        "run_endogenous.py", "--game", "diners", "--agents", str(classes.N_AGENTS), "--trials", "1",
        "--rounds", str(classes.N_ROUNDS), "--model", args.model, "--use-queue", "--round-robin",
        "--expensive-joy", str(d["expensive_joy"]), "--cheap-joy", str(d["cheap_joy"]),
        "--expensive-cost", str(d["expensive_cost"]), "--cheap-cost", str(d["cheap_cost"]),
        "--output-dir", run_dir,
    ]
    note = ""
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
        records.append_meta(records.meta_row(
            run_dir, args.set_name, args.class_name, args.model, classes.DISH, classes.MODE,
            stats["calls"], missing, note, args.regen_of))
    return 0


if __name__ == "__main__":
    sys.exit(main())
