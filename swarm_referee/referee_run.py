"""Run the referee on chosen runs and views. Appends one row per call to a verdicts CSV.

Usage: .venv/bin/python -m swarm_referee.referee_run run_011 run_008 --set practice
           [--views V1 V2 V3 V4 V5] [--thinking on|off] [--prompt FILE] [--out FILE]

Runs are looked up under data/practice (--set practice) or data/runs (--set scored). A scored run needs
--set scored, so a practice command can never touch a scored log. This file never reads data/run_meta.csv.
Each view passes the leak check before it is sent. Stops at once on a 401, 402, 403 or 404 reply.
"""

import argparse
import json
import os
import sys
from typing import List, Optional

from dotenv import load_dotenv

from swarm_referee import records, referee, referee_client, views


def load_log(run_id: str, set_name: str) -> dict:
    folder = os.path.join(records.DATA, "practice" if set_name == "practice" else "runs", run_id)
    path = records.find_log(folder)
    if path is None:
        raise SystemExit(f"no log for {run_id} in {folder}")
    with open(path) as f:
        return json.load(f)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--set", dest="set_name", default="practice", choices=["practice", "scored"])
    ap.add_argument("--views", nargs="+", default=list(views.VIEW_NAMES), choices=list(views.VIEW_NAMES))
    ap.add_argument("--thinking", default="off", choices=["on", "off"])
    ap.add_argument("--prompt", default=referee.PROMPT_PATH)
    ap.add_argument("--out", default=referee.VERDICTS_PATH)
    args = ap.parse_args(argv)

    load_dotenv(os.path.join(records.ROOT, ".env"))
    prompt = referee.load_prompt(args.prompt)
    if not prompt.strip():
        raise SystemExit(f"prompt file is empty: {args.prompt}")
    client = referee_client.DeepSeekClient(thinking=args.thinking == "on")
    for run_id in args.runs:
        built = views.check_run(run_id, load_log(run_id, args.set_name))  # leak check first; raises on a leak
        for name in args.views:
            try:
                verdict = referee.run_view(client, prompt, built[name])
            except referee.FatalApiError as exc:
                print(f"STOP: {exc}")
                return 2
            referee.record_verdict(run_id, name, verdict, args.out)
            print(f"{run_id} {name} {verdict.status} conf={verdict.confidence} "
                  f"finish={verdict.finish_reason} attempts={verdict.attempts} "
                  f"tokens={verdict.prompt_tokens}+{verdict.completion_tokens}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
