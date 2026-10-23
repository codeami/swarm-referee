"""Run a batch of Diners games one at a time, alternating classes (PROJECT.md section 4).

Usage:
  .venv/bin/python -m swarm_referee.run_batch <free-model> --set practice|scored [--floor] [--dry-run]
  .venv/bin/python -m swarm_referee.run_batch <free-model> --regen run_NNN [--dry-run]

The mix of classes comes from the MIX table below. --floor uses the floor mix (12 scored runs).
--regen replays one drifted planted_pair run under a new id. The drifted run stays in the set.
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
from typing import Callable, Dict, List, Optional

from swarm_referee import classes, records

# Runs per class. The key order is the alternation order. Edit the numbers here.
MIX: Dict[str, Dict[str, int]] = {
    "practice": {"planted_pair": 1, "independent_cheats": 1, "cooperation_pact": 1, "talk_only": 1},
    "scored": {"planted_pair": 6, "independent_cheats": 5, "cooperation_pact": 2, "talk_only": 2,
               "innocent_parallel": 1},
    "floor": {"planted_pair": 4, "independent_cheats": 3, "cooperation_pact": 2, "talk_only": 2,
              "innocent_parallel": 1},
}
REGEN_CLASS = "planted_pair"  # the drift policy allows a regeneration only for a drifted positive
PAUSE_SECONDS = 600
MAX_RERUNS = 2  # per game slot; after that the batch stops


def batch_order(mix: Dict[str, int]) -> List[str]:
    """Classes in run order: one of each in turn while runs remain, so an outage cannot empty one class."""
    left = dict(mix)
    order: List[str] = []
    while any(left.values()):
        for name in mix:
            if left[name]:
                order.append(name)
                left[name] -= 1
    return order


def needs_pause(max_retries_seen: bool, missing: Optional[dict]) -> bool:
    return max_retries_seen or (missing is not None and missing["stage3"] > 1)


def play(model: str, class_name: str, set_name: str, run_dir: str, regen_of: str = "") -> tuple:
    """Run one game in a child process. Returns (exit code, saw 'Max retries')."""
    cmd = [sys.executable, "-m", "swarm_referee.run_diners", model, "--class", class_name,
           "--set", set_name, "--run-dir", run_dir]
    if regen_of:
        cmd += ["--regen-of", regen_of]
    proc = subprocess.Popen(cmd, cwd=records.ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    saw = False
    for line in proc.stdout:
        print(line, end="")
        saw = saw or "Max retries" in line
    return proc.wait(), saw


def mark_failed(run_dir: str, data_dir: str = records.DATA) -> str:
    """Move a bad log to data/practice/failed_run_NNN."""
    target = os.path.join(data_dir, "practice", "failed_" + os.path.basename(run_dir))
    if os.path.isdir(run_dir):
        shutil.move(run_dir, target)
    return target


def check_regen(run_id: str, meta: List[dict], labels: Dict[str, dict]) -> str:
    """Return the class to replay for a drifted run, or raise ValueError with the reason."""
    rows = [r for r in meta if r["run_id"] == run_id]
    if not rows:
        raise ValueError(f"{run_id} has no row in run_meta.csv")
    row = rows[-1]
    if row["set"] != "scored" or row["intended_class"] != REGEN_CLASS:
        raise ValueError(f"{run_id} is not a scored {REGEN_CLASS} run: only a drifted positive may be regenerated")
    landed = (labels.get(run_id) or {}).get("landed_class", "")
    if not landed:
        raise ValueError(f"{run_id} has no landed_class in labels.csv: label the run first")
    if landed == row["intended_class"]:
        raise ValueError(f"{run_id} landed in its intended class: no regeneration allowed")
    done = [r["run_id"] for r in meta if r["regen_of"] == run_id]
    if done:
        raise ValueError(f"{run_id} was already regenerated as {done[0]}: one regeneration per drifted positive")
    return row["intended_class"]


def run_slots(model: str, set_name: str, order: List[str], play_fn: Callable = play,
              sleep_fn: Callable = time.sleep, data_dir: str = records.DATA, regen_of: str = "") -> int:
    done = 0
    for slot, class_name in enumerate(order, 1):
        for attempt in range(MAX_RERUNS + 1):
            run_dir = records.next_run_dir(set_name, data_dir)
            print(f"[{slot}] run {os.path.basename(run_dir)} (attempt {attempt + 1})")
            code, saw_retries = play_fn(model, class_name, set_name, run_dir, regen_of)
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


def dry_run(model: str, set_name: str, order: List[str], regen_of: str = "") -> None:
    """Print the plan. Makes no model call, no network call and writes nothing."""
    start = max(records.used_run_numbers(), default=0) + 1
    note = f" regen_of={regen_of}" if regen_of else ""
    print(f"DRY RUN: model={model} set={set_name} games={len(order)}{note}")
    for i, class_name in enumerate(order):
        run_id = os.path.basename(records.run_dir_for(set_name, start + i))
        print(f"  {i + 1:2d}. {run_id}  class={class_name}  expected_calls={classes.EXPECTED_CALLS}")
    total = len(order) * classes.EXPECTED_CALLS
    minutes = total * 3.5 / 60
    print(f"Total expected calls: {total} (about {minutes:.0f} min at 3.5 s per call, reruns not counted)")


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--set", dest="set_name", choices=["practice", "scored"])
    ap.add_argument("--floor", action="store_true", help="use the floor mix (12 scored runs)")
    ap.add_argument("--regen", metavar="RUN_ID", help="replay one drifted planted_pair run under a new id")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    if args.regen:
        try:
            class_name = check_regen(args.regen, records.read_meta(), records.run_labels())
        except ValueError as exc:
            print(f"Refused: {exc}")
            return 2
        set_name, order, regen_of = "scored", [class_name], args.regen
    elif args.set_name:
        set_name, regen_of = args.set_name, ""
        order = batch_order(MIX["floor" if args.floor and set_name == "scored" else set_name])
    else:
        ap.error("give --set or --regen")
    if args.dry_run:
        dry_run(args.model, set_name, order, regen_of)
        return 0
    return run_slots(args.model, set_name, order, regen_of=regen_of)


if __name__ == "__main__":
    sys.exit(main())
