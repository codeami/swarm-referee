"""Post-hoc descriptive diagnostic: coalition advantage and joint regret.

It is not a view, not a score and not part of the referee. It reads payoffs from one run log
and prints numbers. The coalition is an input. This file never reads data/run_meta.csv,
a class name or an injected instruction.
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Sequence

from swarm_referee import classes, records, views

HEADER = "post-hoc descriptive diagnostic, not a view, not a score"
SCORED_DIR = os.path.join(records.DATA, "runs")
ALLOWED_SCORED = {"run_001"}  # the only scored-folder log that is open


def best_per_agent() -> float:
    """Payoff of one agent when all agents order CHEAP (joy minus the equal share of cost)."""
    return classes.DISH["cheap_joy"] - classes.DISH["cheap_cost"]


def coalition_advantage(log: dict, coalition: Sequence[str]) -> dict:
    """Mean payoff of the coalition minus mean payoff of the other agents.

    Returns {"rounds": [(round, advantage)], "mean": advantage over the run}.
    The coalition is an argument. The other agents are the rest of the agents in the round.
    """
    members = set(coalition)
    per_round = []
    for number, _, payoffs in views.rounds_of(log):
        inside = [p for a, p in payoffs.items() if a in members]
        outside = [p for a, p in payoffs.items() if a not in members]
        if not inside or not outside:
            raise ValueError(f"round {number}: coalition or the other agents have no payoff")
        per_round.append((number, sum(inside) / len(inside) - sum(outside) / len(outside)))
    mean = sum(v for _, v in per_round) / len(per_round) if per_round else 0.0
    return {"rounds": per_round, "mean": mean}


def joint_regret(log: dict) -> dict:
    """Best joint score minus achieved score (sum of payoffs), per round and for the run.

    This uses the all-CHEAP table as the optimum: 3.0 per agent, so 15.0 in total with 5 agents.
    Regret is negative when the agents together do better than that.
    Returns {"rounds": [(round, achieved, regret)], "total": run regret}.
    """
    per_round = []
    for number, _, payoffs in views.rounds_of(log):
        best = best_per_agent() * len(payoffs)
        achieved = sum(payoffs.values())
        per_round.append((number, achieved, best - achieved))
    return {"rounds": per_round, "total": sum(r for _, _, r in per_round)}


def choices_of(log: dict) -> List[Dict[str, str]]:
    return [{a: (v.get("stage3") or {}).get("choice") or "-" for a, v in agents.items()}
            for _, agents, _ in views.rounds_of(log)]


def format_report(log: dict, coalition: Sequence[str]) -> str:
    adv = coalition_advantage(log, coalition)
    reg = joint_regret(log)
    choices = choices_of(log)
    lines = [f"# {HEADER}", f"coalition: {','.join(coalition)}",
             "round | advantage | achieved | regret | choices"]
    for (n, a), (_, got, r), ch in zip(adv["rounds"], reg["rounds"], choices):
        lines.append(f"{n} | {a:+.2f} | {got:.1f} | {r:+.1f} | "
                     + " ".join(f"{k}={v[:1]}" for k, v in ch.items()))
    lines.append(f"run | mean advantage {adv['mean']:+.2f} | total regret {reg['total']:+.1f}")
    return "\n".join(lines)


def under_scored_dir(run_dir: str) -> bool:
    path = os.path.realpath(run_dir)
    root = os.path.realpath(SCORED_DIR)
    return path != root and path.startswith(root + os.sep)


def main(argv: List[str] = None) -> int:
    parser = argparse.ArgumentParser(description=HEADER)
    parser.add_argument("run_dir")
    parser.add_argument("--coalition", required=True, help="agent letters, for example M,Q")
    parser.add_argument("--allow-scored", action="store_true",
                        help="allow a run folder under data/runs/ (scored logs stay closed until the referee prompt is frozen)")
    args = parser.parse_args(argv)
    name = os.path.basename(os.path.normpath(args.run_dir))
    if under_scored_dir(args.run_dir) and name not in ALLOWED_SCORED:
        if not args.allow_scored:
            print(f"refused: {args.run_dir} is under data/runs/. Use --allow-scored only after the referee prompt is frozen.",
                  file=sys.stderr)
            return 2
        print("WARNING: reading a scored log.", file=sys.stderr)
    path = records.find_log(args.run_dir)
    if path is None:
        print(f"no log found in {args.run_dir}", file=sys.stderr)
        return 1
    with open(path) as handle:
        log = json.load(handle)
    coalition = [a.strip() for a in args.coalition.split(",") if a.strip()]
    print(format_report(log, coalition))
    return 0


if __name__ == "__main__":
    sys.exit(main())
