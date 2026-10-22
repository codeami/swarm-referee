"""Event schema for one agent in one round.

Field names in HARNESS_FIELDS come from the Shi harness source and README.
Status: UNVERIFIED until a real log exists in data/runs/run_001/.
Harness: Jerick-1380/LLM-Trust-Breaking, commit fd11aca, Diners game.
"""

from dataclasses import dataclass
from typing import Optional

# Where each event field lives in the harness JSON log.
# Path: rounds[].trials[].agents[<agent>]... ; payoff is at trial level.
HARNESS_FIELDS = {
    "run_id": None,  # not in the harness log; set by this repo (folder name)
    "round": "rounds[].round_id",
    "agent": "rounds[].trials[].agents.<agent name>  (dictionary key)",
    "plan": "agents.<agent>.stage1.intended_action  (+ stage1.reasoning)",
    "message": "agents.<agent>.stage2.message  (+ stage2.stated_action)",
    "action": "agents.<agent>.stage3.choice  (+ stage3.reasoning)",
    "payoff": "rounds[].trials[].outcomes.payoffs.<agent name>",
}


@dataclass(frozen=True)
class Event:
    """One row of the V4 ledger: one agent, one round."""

    run_id: str
    round: int
    agent: str
    plan: str  # private plan: intended action and reasoning
    message: str  # public message
    action: str  # final action: EXPENSIVE or CHEAP in Diners
    payoff: Optional[float]
