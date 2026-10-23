"""The five views and the leak check (STRATEGY.md section 7).

A view is one text pack built from one run log. Each view holds exactly its field list:
  V1  stage2.message
  V2  stage3.choice, payoff
  V3  stage2.message, stage2.stated_action, stage3.choice, payoff   (raw log text, log order)
  V4  the same four fields as a ledger, one row per agent per round, no marks, no summaries
  V5  V4 plus a mark where stated and actual order differ, and one line per round naming who gained and who lost
The round number and the agent letter are the row keys of every view.

This file never reads data/run_meta.csv. The leak check takes the forbidden class names
and instruction texts from classes.py, and the model name from the log itself.
"""

import json
import re
from typing import Dict, List, Optional, Tuple

from swarm_referee import classes

VIEW_NAMES = ("V1", "V2", "V3", "V4", "V5")
MARK = "STATED != ACTUAL"
LEDGER_HEAD = ["round", "agent", "message", "stated order", "actual order", "payoff"]
V5_HEAD = LEDGER_HEAD + ["mark"]


class LeakError(Exception):
    """A view holds text it must not hold. Scoring stops."""


def rounds_of(log: dict) -> List[Tuple[int, Dict[str, dict], Dict[str, float]]]:
    """(round number from 1, agents in log order, payoffs) for each trial of the log."""
    out = []
    for rnd in log.get("rounds", []):
        for trial in rnd.get("trials", []):
            payoffs = (trial.get("outcomes") or {}).get("payoffs") or {}
            out.append((int(rnd["round_id"]) + 1, trial.get("agents", {}), payoffs))
    return out


def one_line(text: Optional[str]) -> str:
    return " ".join((text or "").split())


def cell(text: Optional[str]) -> str:
    return one_line(text).replace("|", "\\|")


def value(text: Optional[str]) -> str:
    return text if text is not None else ""


def v1(log: dict) -> str:
    lines = []
    for number, agents, _ in rounds_of(log):
        lines.append(f"Round {number}")
        lines += [f"{a}: {one_line(d['stage2'].get('message'))}" for a, d in agents.items()]
    return "\n".join(lines) + "\n"


def v2(log: dict) -> str:
    lines = []
    for number, agents, payoffs in rounds_of(log):
        lines.append(f"Round {number}")
        lines += [f"{a}: {value(d['stage3'].get('choice')) or 'none'}, payoff {payoffs.get(a, 'none')}"
                  for a, d in agents.items()]
    return "\n".join(lines) + "\n"


def v3(log: dict) -> str:
    """Raw log text: one JSON line per round, the four fields in the order the log stores them."""
    lines = []
    for number, agents, payoffs in rounds_of(log):
        body = {
            "round": number,
            "agents": {a: {"stage2": {"stated_action": d["stage2"].get("stated_action"),
                                      "message": d["stage2"].get("message")},
                           "stage3": {"choice": d["stage3"].get("choice")}} for a, d in agents.items()},
            "payoffs": payoffs,
        }
        lines.append(json.dumps(body, ensure_ascii=False))
    return "\n".join(lines) + "\n"


def ledger_rows(log: dict) -> List[Tuple[int, List[List[str]]]]:
    rows = []
    for number, agents, payoffs in rounds_of(log):
        rows.append((number, [[str(number), a, cell(d["stage2"].get("message")),
                               value(d["stage2"].get("stated_action")), value(d["stage3"].get("choice")),
                               str(payoffs.get(a, ""))] for a, d in agents.items()]))
    return rows


def mismatch(stated: str, actual: str) -> bool:
    return bool(stated) and bool(actual) and stated.upper() != actual.upper()


def table(head: List[str], rows: List[List[str]]) -> List[str]:
    return ["| " + " | ".join(head) + " |"] + ["| " + " | ".join(r) + " |" for r in rows]


def v4(log: dict) -> str:
    rows = [r for _, block in ledger_rows(log) for r in block]
    return "\n".join(table(LEDGER_HEAD, rows)) + "\n"


def gain_line(number: int, agents: Dict[str, dict], payoffs: Dict[str, float]) -> str:
    """Who gained and who lost: an agent gains with a payoff above the table mean, loses below it."""
    got = {a: payoffs[a] for a in agents if isinstance(payoffs.get(a), (int, float))}
    mean = sum(got.values()) / len(got) if got else 0.0
    gained = [a for a, p in got.items() if p > mean + 1e-9]
    lost = [a for a, p in got.items() if p < mean - 1e-9]
    return f"Round {number}: gained: {', '.join(gained) or 'none'}; lost: {', '.join(lost) or 'none'}"


def v5(log: dict) -> str:
    out = []
    by_round = {n: (agents, payoffs) for n, agents, payoffs in rounds_of(log)}
    rows = []
    for number, block in ledger_rows(log):
        for r in block:
            rows.append(r + [MARK if mismatch(r[3], r[4]) else ""])
    out += table(V5_HEAD, rows)
    out.append("")
    out += [gain_line(n, *by_round[n]) for n in by_round]
    return "\n".join(out) + "\n"


def build_views(log: dict) -> Dict[str, str]:
    return {"V1": v1(log), "V2": v2(log), "V3": v3(log), "V4": v4(log), "V5": v5(log)}


# ---- leak check ------------------------------------------------------------------------------

NUM = r"-?\d+(?:\.\d+)?"
ROW_V1 = re.compile(r"^(Round \d+|[A-Z]: .*)$")
ROW_V2 = re.compile(rf"^(Round \d+|[A-Z]: (?:[A-Z]+|none), payoff (?:{NUM}|none))$")
ROW_GAIN = re.compile(r"^Round \d+: gained: (?:none|[A-Z](?:, [A-Z])*); lost: (?:none|[A-Z](?:, [A-Z])*)$")
MIN_SENTENCE = 25  # shorter sentences ("Keep your promise.") are too common in honest messages
V3_KEYS = {"round", "agents", "payoffs"}
V3_AGENT_KEYS = {"stage2": {"stated_action", "message"}, "stage3": {"choice"}}


def sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def forbidden_terms(log: dict) -> List[Tuple[str, str]]:
    """(kind, text) pairs that must not appear in any view of this run."""
    terms = []
    for text in classes.all_instruction_texts():
        for part in [text] + [s for s in sentences(text) if len(s) >= MIN_SENTENCE]:
            terms.append(("injected instruction text", part))
    for name in classes.CLASS_NAMES:
        terms += [("class name", name), ("class name", name.replace("_", " "))]
    model = (log.get("metadata") or {}).get("model") or ""
    for part in {model, model.split("/")[-1], model.split(":")[0], model.split("/")[0]} - {""}:
        terms.append(("model name", part))
    return terms


def private_values(log: dict) -> List[Tuple[str, str]]:
    """Long text from log fields outside every view list: private plans, reasoning, judge, reflection."""
    found = []
    for number, agents, _ in rounds_of(log):
        for agent, d in agents.items():
            for stage in ("stage1", "stage3"):
                text = one_line((d.get(stage) or {}).get("reasoning"))
                if len(text) >= 20:
                    found.append((f"private {stage}.reasoning of {agent}, round {number}", text))
            for take in ((d.get("reflection") or {}).get("takeaways") or {}).values():
                text = one_line(take.get("assessment"))
                if len(text) >= 20:
                    found.append((f"reflection of {agent}, round {number}", text))
    return found


def check_grammar(name: str, text: str) -> None:
    """Every line of a view must match the shape of that view. A stray column or line fails."""
    lines = [ln for ln in text.split("\n") if ln != ""]
    for ln in lines:
        if name == "V1" and not ROW_V1.match(ln):
            raise LeakError(f"V1 line outside its field list: {ln[:60]!r}")
        if name == "V2" and not ROW_V2.match(ln):
            raise LeakError(f"V2 line outside its field list: {ln[:60]!r}")
        if name == "V3":
            body = json.loads(ln)
            if set(body) != V3_KEYS:
                raise LeakError(f"V3 keys outside its field list: {sorted(body)}")
            for d in body["agents"].values():
                if {k: set(v) for k, v in d.items()} != V3_AGENT_KEYS:
                    raise LeakError(f"V3 agent fields outside its field list: {d.keys()}")
        if name in ("V4", "V5"):
            if ln.startswith("Round "):
                if name == "V4" or not ROW_GAIN.match(ln):
                    raise LeakError(f"{name} line outside its field list: {ln[:60]!r}")
                continue
            cols = len(ln[2:-2].split(" | "))
            if cols != (len(LEDGER_HEAD) if name == "V4" else len(V5_HEAD)):
                raise LeakError(f"{name} row has {cols} columns: {ln[:60]!r}")


def leak_check(run_id: str, log: dict, views: Dict[str, str]) -> None:
    """Raise LeakError when any view holds text outside its field list. One failure stops scoring."""
    for name in classes.CLASS_NAMES:
        if name in run_id or name.replace("_", " ") in run_id:
            raise LeakError(f"run id {run_id} encodes a class name")
    if set(views) != set(VIEW_NAMES):
        raise LeakError(f"{run_id}: views are {sorted(views)}, expected {list(VIEW_NAMES)}")
    forbidden = forbidden_terms(log)
    private = private_values(log)
    allowed_text = " ".join(one_line((d["stage2"]).get("message")) for _, ag, _ in rounds_of(log) for d in ag.values())
    for view_name, text in views.items():
        lowered = text.lower()
        for kind, term in forbidden:
            if term.lower() in lowered:
                raise LeakError(f"{run_id} {view_name}: {kind} found: {term!r}")
        for kind, term in private:
            # A private text counts as a leak only when it is not also a public message.
            if term in text and term not in allowed_text:
                raise LeakError(f"{run_id} {view_name}: {kind} found: {term[:50]!r}")
        check_grammar(view_name, text)


def check_run(run_id: str, log: dict) -> Dict[str, str]:
    """Build the views of one run and leak-check them. Returns the views."""
    views = build_views(log)
    leak_check(run_id, log, views)
    return views
