"""Run one Diners game with the Shi harness and a free judge model.

The harness sends the judge step to the paid model openai/gpt-5-mini.
This wrapper swaps that model name, then runs the harness entry point.
It does not change vendor/. It also counts calls and estimates tokens.

Usage: .venv/bin/python swarm_referee/run_diners.py <free-model> [output-dir]
"""

import asyncio
import json
import os
import runpy
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENDOR = os.path.join(ROOT, "vendor", "LLM-Trust-Breaking")
PAID_JUDGE = "openai/gpt-5-mini"
CHARS_PER_TOKEN = 4  # rough estimate; the harness does not log token usage

# Free OpenRouter models allow 20 requests per minute. Start one request every 3.5 s.
MIN_GAP_SECONDS = 3.5
MAX_RETRIES = 8
next_slot = 0.0

stats = {"calls": 0, "prompt_chars": 0, "reply_chars": 0}


def main() -> None:
    model = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "data", "runs", "run_001")
    sys.path.insert(0, VENDOR)
    os.chdir(VENDOR)  # the harness loads .env from its own folder tree
    from dotenv import load_dotenv

    load_dotenv(os.path.join(ROOT, ".env"))

    from src.endogenous.core import trial_runner

    build_request = trial_runner._build_request

    def build_free(*args, **kwargs):
        if kwargs.get("model") == PAID_JUDGE:
            kwargs["model"] = model
        return build_request(*args, **kwargs)

    execute = trial_runner._execute_requests_split_by_provider

    def counted(requests, *args, **kwargs):
        result = execute(requests, *args, **kwargs)
        stats["calls"] += len(requests)
        stats["prompt_chars"] += sum(len(json.dumps(r.get("messages", ""))) for r in requests)
        stats["reply_chars"] += len(json.dumps(result, default=str))
        return result

    from src.llm.providers import queued_openrouter

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
    trial_runner._build_request = build_free
    trial_runner._execute_requests_split_by_provider = counted

    sys.argv = [
        "run_endogenous.py", "--game", "diners", "--agents", "5", "--trials", "1",
        "--rounds", "5", "--model", model, "--use-queue", "--round-robin",
        "--output-dir", out_dir,
    ]
    try:
        runpy.run_path(os.path.join(VENDOR, "experiments", "run_endogenous.py"), run_name="__main__")
    finally:
        est = (stats["prompt_chars"] + stats["reply_chars"]) // CHARS_PER_TOKEN
        print(f"CALLS={stats['calls']} EST_TOKENS={est} "
              f"(prompt~{stats['prompt_chars']//CHARS_PER_TOKEN}, reply~{stats['reply_chars']//CHARS_PER_TOKEN})")


if __name__ == "__main__":
    main()
