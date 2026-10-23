"""Run a batch of Diners games one at a time, alternating classes.

Usage: .venv/bin/python -m swarm_referee.run_batch <free-model> --set practice|scored [--dry-run]

A game is rerun under a new run id when it is unscoreable (any stage-3 action missing).
The batch also waits 10 minutes before the rerun when a "Max retries" line appears
or when more than one stage-3 action is missing. The bad log moves to data/practice/failed_run_NNN.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from typing import Callable, List, Optional

from swarm_referee import classes, records

PER_CLASS = {"practice": 1, "scored": 4}
ALTERNATION = ("collusion", "benign", "talk_only")
PAUSE_SECONDS = 600
MAX_RERUNS = 2  # per game slot; after that the batch stops


def batch_order(per_class: int) -> List[str]:
    """Classes in run order: one of each in turn, so an outage cannot empty one class."""
    return [name for _ in range(per_class) for name in ALTERNATION]


def needs_pause(max_retries_seen: bool, missing: Optional[dict]) -> bool:
    return max_retries_seen or (missing is not None and missing["stage3"] > 1)


def play(model: str, class_name: str, set_name: str, run_dir: str) -> tuple:
    """Run one game in a child process. Returns (exit code, saw 'Max retries')."""
    cmd = [sys.executable, "-m", "swarm_referee.run_diners", model, "--class", class_name,
           "--set", set_name, "--run-dir", run_dir]
    proc = subprocess.Popen(cmd, cwd=records.ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    saw = False
    for line in proc.stdout:
        print(line, end="")
        saw = saw or "Max retries" in line
    return proc.wait(), saw


def mark_failed(run_dir: str, data_dir: str = records.DATA) -> str:
    """Move a bad log to data/practice/failed_run_NNN and note it in run_meta.csv."""
    target = os.path.join(data_dir, "practice", "failed_" + os.path.basename(run_dir))
    if os.path.isdir(run_dir):
        shutil.move(run_dir, target)
    return target


def run_batch(model: str, set_name: str, per_class: int, play_fn: Callable = play,
              sleep_fn: Callable = time.sleep, data_dir: str = records.DATA) -> int:
    done = 0
    for slot, class_name in enumerate(batch_order(per_class), 1):
        for attempt in range(MAX_RERUNS + 1):
            run_dir = records.next_run_dir(set_name, data_dir)
            print(f"[{slot}] class run {os.path.basename(run_dir)} (attempt {attempt + 1})")
            code, saw_retries = play_fn(model, class_name, set_name, run_dir)
            missing = records.check_run(run_dir)
            if code == 0 and missing is not None and records.parse_rule(missing):
                done += 1
                break
            moved = mark_failed(run_dir, data_dir)
            records.update_meta(os.path.basename(run_dir), {"note": f"unscoreable; log moved to {moved}"},
                                os.path.join(data_dir, "run_meta.csv"))
            if needs_pause(saw_retries, missing):
                print(f"Pause {PAUSE_SECONDS // 60} min before rerun.")
                sleep_fn(PAUSE_SECONDS)
        else:
            print(f"Stop: slot {slot} failed {MAX_RERUNS + 1} times.")
            return 1
    print(f"Batch done: {done} games.")
    return 0


def dry_run(model: str, set_name: str, per_class: int) -> None:
    """Print the plan. Makes no model call, no network call and writes nothing."""
    order = batch_order(per_class)
    start = max(records.used_run_numbers(), default=0) + 1
    print(f"DRY RUN: model={model} set={set_name} games={len(order)}")
    for i, class_name in enumerate(order):
        run_id = os.path.basename(records.run_dir_for(set_name, start + i))
        print(f"  {i + 1:2d}. {run_id}  class={class_name}  expected_calls={classes.EXPECTED_CALLS}")
    total = len(order) * classes.EXPECTED_CALLS
    minutes = total * 3.5 / 60
    print(f"Total expected calls: {total} (about {minutes:.0f} min at 3.5 s per call, reruns not counted)")


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--set", dest="set_name", required=True, choices=["practice", "scored"])
    ap.add_argument("--per-class", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    per_class = args.per_class or PER_CLASS[args.set_name]
    if args.dry_run:
        dry_run(args.model, args.set_name, per_class)
        return 0
    return run_batch(args.model, args.set_name, per_class)


if __name__ == "__main__":
    sys.exit(main())
