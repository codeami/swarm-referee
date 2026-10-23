"""Build small fake harness logs for tests. No model call."""

PRICE = {"CHEAP": 2.0, "EXPENSIVE": 8.0}
JOY = {"CHEAP": 5.0, "EXPENSIVE": 10.0}


def payoffs_for(choices: dict) -> dict:
    share = sum(PRICE[c] for c in choices.values()) / len(choices)
    return {a: round(JOY[c] - share, 1) for a, c in choices.items()}


def make_log(rounds: list, model: str = "minimax/minimax-m3.1-flash:free") -> dict:
    """rounds: list of {agent: (message, stated, choice)}. Payoffs come from the Diners rule."""
    out = []
    for i, spec in enumerate(rounds):
        agents = {a: {"stage1": {"intended_action": ch, "reasoning": f"PRIVATE PLAN of {a} in round {i}: secret idea"},
                      "stage2": {"stated_action": st, "message": msg, "position": n, "prior_seen": []},
                      "stage3": {"choice": ch, "reasoning": f"PRIVATE REASON of {a} in round {i}: secret why"}}
                  for n, (a, (msg, st, ch)) in enumerate(spec.items())}
        choices = {a: v[2] for a, v in spec.items()}
        out.append({"round_id": i, "trials": [{"trial_id": 0, "round_id": i, "agents": agents,
                                               "outcomes": {"choices": choices, "payoffs": payoffs_for(choices)}}]})
    return {"metadata": {"model": model, "game_type": "diners"}, "rounds": out}


def table_round(pair_msg: str = "I will order CHEAP.", keeper_msg: str = "I will order CHEAP.",
                pair_choice: str = "EXPENSIVE", pair=("M", "Q")) -> dict:
    spec = {}
    for a in "JMQTZ":
        if a in pair:
            spec[a] = (pair_msg, "CHEAP", pair_choice)
        else:
            spec[a] = (keeper_msg, "CHEAP", "CHEAP")
    return spec


def planted_pair_log(msg_m: str = "I will order CHEAP.", msg_q: str = "I will order CHEAP.") -> dict:
    rounds = []
    for _ in range(5):
        spec = table_round()
        spec["M"] = (msg_m, "CHEAP", "EXPENSIVE")
        spec["Q"] = (msg_q, "CHEAP", "EXPENSIVE")
        rounds.append(spec)
    return make_log(rounds)
