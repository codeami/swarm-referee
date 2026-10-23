"""Run folders, the parse rule and data/run_meta.csv.

The intended class is written ONLY to run_meta.csv. The views and the referee
must never read that file. The landed class lives in data/labels.csv (hand labels).
"""

import csv
import json
import os
import re
from datetime import date
from typing import Dict, List, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
META_PATH = os.path.join(DATA, "run_meta.csv")
LABELS_PATH = os.path.join(DATA, "labels.csv")
LABEL_FIELDS = ["run_id", "round", "label", "secondary_label", "landed_class", "notes"]
RUN_ROW = "run"  # value of the round column on the row that labels the whole run
META_FIELDS = [
    "run_id", "set", "intended_class", "model", "expensive_joy", "cheap_joy",
    "expensive_cost", "cheap_cost", "mode", "date", "calls", "stage1_missing", "stage2_missing",
    "stage3_missing", "scoreable", "regen_of", "note",
]


def used_run_numbers(data_dir: str = DATA) -> List[int]:
    """Run numbers in use in both folders, failed runs included, so ids stay unique."""
    found = []
    for sub in ("runs", "practice"):
        folder = os.path.join(data_dir, sub)
        for name in os.listdir(folder) if os.path.isdir(folder) else []:
            m = re.fullmatch(r"(?:failed_)?run_(\d+)", name)
            if m:
                found.append(int(m.group(1)))
    return found


def run_dir_for(set_name: str, number: int, data_dir: str = DATA) -> str:
    return os.path.join(data_dir, "runs" if set_name == "scored" else "practice", f"run_{number:03d}")


def next_run_dir(set_name: str, data_dir: str = DATA) -> str:
    """Return the next free run folder path (not created)."""
    return run_dir_for(set_name, max(used_run_numbers(data_dir), default=0) + 1, data_dir)


def update_meta(run_id: str, changes: dict, path: str = META_PATH) -> None:
    """Change fields of the last row with this run_id."""
    rows = read_meta(path)
    for row in reversed(rows):
        if row["run_id"] == run_id:
            row.update(changes)
            break
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=META_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def find_log(run_dir: str) -> Optional[str]:
    """Return the harness log file inside a run folder, or None."""
    for base, _, files in os.walk(run_dir):
        for name in files:
            if name.endswith("_endogenous.json"):
                return os.path.join(base, name)
    return None


def count_missing(log: dict) -> Dict[str, int]:
    """Count agent-stages whose action field is missing (None) per stage."""
    missing = {"stage1": 0, "stage2": 0, "stage3": 0}
    key = {"stage1": "intended_action", "stage2": "stated_action", "stage3": "choice"}
    for rnd in log.get("rounds", []):
        for trial in rnd.get("trials", []):
            for agent in trial.get("agents", {}).values():
                for stage, field in key.items():
                    if (agent.get(stage) or {}).get(field) is None:
                        missing[stage] += 1
    return missing


def parse_rule(missing: Dict[str, int]) -> bool:
    """A game is scoreable only if no stage-3 action is missing.

    The harness counts a missing action as CHEAP in the payoff, so such a
    game is wrong. A missing stage-1 or stage-2 field only leaves a blank.
    """
    return missing["stage3"] == 0


def meta_row(run_dir: str, set_name: str, intended_class: str, model: str, dish: dict,
             mode: str, calls: int, missing: Optional[Dict[str, int]], note: str = "",
             regen_of: str = "") -> dict:
    ok = missing is not None and parse_rule(missing)
    miss = missing or {"stage1": "", "stage2": "", "stage3": ""}
    return {
        "run_id": os.path.basename(run_dir), "set": set_name, "intended_class": intended_class,
        "model": model, **dish, "mode": mode, "date": date.today().isoformat(),
        "calls": calls, "stage1_missing": miss["stage1"], "stage2_missing": miss["stage2"],
        "stage3_missing": miss["stage3"], "scoreable": "yes" if ok else "no", "regen_of": regen_of, "note": note,
    }


def append_meta(row: dict, path: str = META_PATH) -> None:
    new = not os.path.exists(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=META_FIELDS)
        if new:
            writer.writeheader()
        writer.writerow(row)


def read_meta(path: str = META_PATH) -> List[dict]:
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def check_run(run_dir: str) -> Optional[Dict[str, int]]:
    """Missing-stage counts for a finished run folder, or None when no log exists."""
    path = find_log(run_dir)
    if path is None:
        return None
    with open(path) as f:
        return count_missing(json.load(f))


def read_labels(path: str = LABELS_PATH) -> List[dict]:
    """Hand labels: one row per run (round = "run") and one per round (round = 1..5)."""
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def run_labels(path: str = LABELS_PATH) -> Dict[str, dict]:
    """The run-level label row for each run id."""
    return {r["run_id"]: r for r in read_labels(path) if r["round"] == RUN_ROW}
