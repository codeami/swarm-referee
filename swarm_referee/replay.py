"""Replay the scoring from the stored files. No model call, no network call.

Usage: .venv/bin/python -m swarm_referee.replay [--expected data/score_scored.txt]

Runs the scoring over data/labels.csv, data/run_meta.csv, the logs and data/verdicts.csv, and compares the
text with the stored score text. Exit 0 when the two are equal, 1 when they differ (a diff is printed), 2 when
the scoring itself stops (for example a leak check failure).
"""

import argparse
import contextlib
import difflib
import io
import os
import sys
from typing import List, Optional

from swarm_referee import records, score

EXPECTED = os.path.join(records.DATA, "score_scored.txt")


def render(data_dir: str = records.DATA) -> tuple:
    """Return (exit code of the scoring, the text it printed)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = score.main(data_dir)
    return code, out.getvalue()


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--expected", default=EXPECTED)
    ap.add_argument("--data", default=records.DATA)
    args = ap.parse_args(argv)

    code, text = render(args.data)
    if code != 0:
        print(text, end="")
        return 2
    with open(args.expected) as f:
        expected = f.read()
    if text == expected:
        print(f"REPLAY OK: scoring from stored verdicts equals {os.path.relpath(args.expected, records.ROOT)}")
        return 0
    diff = difflib.unified_diff(expected.splitlines(), text.splitlines(), "stored", "replayed", lineterm="")
    print("REPLAY DIFFERS")
    print("\n".join(diff))
    return 1


if __name__ == "__main__":
    sys.exit(main())
