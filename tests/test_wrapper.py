"""Wrapper tests. No model call, no network call, no harness import."""

import json
import os

from swarm_referee import classes, records, run_batch, run_diners

KEY = {"stage1": "intended_action", "stage2": "stated_action", "stage3": "choice"}


def fake_build(**kwargs):
    return kwargs


def test_one_payoff_matrix_and_class_table():
    assert classes.DISH == {"expensive_joy": 10.0, "cheap_joy": 5.0, "expensive_cost": 8.0, "cheap_cost": 2.0}
    assert set(classes.CLASS_NAMES) == {"benign", "collusion", "talk_only"}
    assert classes.CLASSES["benign"]["agent"] is None
    for name in ("collusion", "talk_only"):
        assert classes.CLASSES[name]["agent"] in classes.AGENT_NAMES


def test_instruction_text_does_not_leak_class_or_label_rule():
    text = " ".join(v for spec in classes.CLASSES.values() for k, v in spec.items() if k != "agent" and v)
    for word in ("collusion", "talk_only", "benign", "4 of 5", "scored"):
        assert word not in text.lower()


def test_call_count_math():
    assert classes.EXPECTED_CALLS == 75
    calls = {"calls": 0, "prompt_chars": 0, "reply_chars": 0, "max_retries": 0}
    ran = []

    def execute(requests, oa, orr, label):
        ran.append(label)
        return {r["custom_id"]: {"content": "{}"} for r in requests}

    run = run_diners.make_execute(execute, {}, lambda r, f: {}, calls)
    for rnd in range(classes.N_ROUNDS):
        for label, n in (("Stage 1", 5), ("Stage 2 pos 0", 1), ("Stage 2 pos 1", 1), ("Stage 2 pos 2", 1),
                         ("Stage 2 pos 3", 1), ("Stage 2 pos 4", 1), ("Stage 3", 5), ("Judge", 5), ("Reflection", 20)):
            reqs = [{"custom_id": f"r{rnd}_t0_s1_{i}", "messages": []} for i in range(n)]
            run(reqs, None, None, label)
    assert calls["calls"] == classes.EXPECTED_CALLS
    assert "Judge" not in ran and "Reflection" not in ran


def test_hook_adds_instruction_to_seeded_agent_only_and_history_from_round_two():
    history = {0: {"J": ("CHEAP", "Let us all order CHEAP")}}
    build = run_diners.make_build_request(fake_build, "free/model", "collusion", history)
    seeded = build(custom_id="r0_t0_s2_J", system_prompt="sys", user_prompt="usr", model="m")
    other = build(custom_id="r0_t0_s2_M", system_prompt="sys", user_prompt="usr", model="m")
    later = build(custom_id="r1_t0_s3_M", system_prompt="sys", user_prompt="usr", model="m")
    assert classes.CLASSES["collusion"]["s2"] in seeded["system_prompt"]
    assert other["system_prompt"] == "sys" and other["user_prompt"] == "usr"
    assert "Let us all order CHEAP" in later["user_prompt"]
    benign = run_diners.make_build_request(fake_build, "free/model", "benign", {})
    assert benign(custom_id="r0_t0_s1_J", system_prompt="sys", user_prompt="usr", model="m")["system_prompt"] == "sys"


def test_hook_swaps_paid_judge_model():
    build = run_diners.make_build_request(fake_build, "free/model", "benign", {})
    assert build(custom_id="r0_t0_judge_J", model=run_diners.PAID_JUDGE)["model"] == "free/model"


def make_log(missing: dict) -> dict:
    agents = {a: {s: {f: "EXPENSIVE"} for s, f in KEY.items()} for a in "JM"}
    for stage, agent in missing.items():
        agents[agent][stage][KEY[stage]] = None
    return {"rounds": [{"trials": [{"agents": agents}]}]}


def test_parse_rule():
    assert records.parse_rule(records.count_missing(make_log({})))
    assert records.parse_rule(records.count_missing(make_log({"stage1": "J", "stage2": "M"})))
    assert not records.parse_rule(records.count_missing(make_log({"stage3": "J"})))


def test_batch_order_alternates_classes():
    order = run_batch.batch_order(4)
    assert len(order) == 12 and all(order.count(c) == 4 for c in classes.CLASS_NAMES)
    assert order[:3] == ["collusion", "benign", "talk_only"]
    assert run_batch.batch_order(1) == ["collusion", "benign", "talk_only"]


def test_batch_reruns_bad_game_under_new_id_and_moves_log(tmp_path):
    data = str(tmp_path)
    os.makedirs(os.path.join(data, "practice"))
    meta = os.path.join(data, "run_meta.csv")
    attempts = []
    sleeps = []

    def play(model, class_name, set_name, run_dir):
        bad = len(attempts) == 0  # first game has two stage-3 gaps
        attempts.append(run_dir)
        os.makedirs(run_dir + "/diners/5agents")
        log = make_log({"stage3": "J"} if bad else {})
        if bad:
            log["rounds"][0]["trials"][0]["agents"]["M"]["stage3"]["choice"] = None
        with open(run_dir + "/diners/5agents/x_endogenous.json", "w") as f:
            json.dump(log, f)
        records.append_meta(records.meta_row(run_dir, set_name, class_name, model, classes.DISH, classes.MODE,
                                             75, records.check_run(run_dir)), meta)
        return 0, False

    assert run_batch.run_batch("m", "practice", 1, play, sleeps.append, data) == 0
    assert [os.path.basename(a) for a in attempts] == ["run_001", "run_002", "run_003", "run_004"]
    assert os.path.isdir(os.path.join(data, "practice", "failed_run_001"))
    assert sleeps == [run_batch.PAUSE_SECONDS]  # two stage-3 gaps -> 10 minute pause
    rows = records.read_meta(meta)
    assert rows[0]["scoreable"] == "no" and "failed_run_001" in rows[0]["note"]
    assert all(r["landed_class"] == "" for r in rows)


def test_dry_run_prints_plan_and_writes_nothing(capsys, tmp_path, monkeypatch):
    monkeypatch.setattr(records, "DATA", str(tmp_path))
    before = set(os.listdir(records.ROOT))
    assert run_batch.main(["m", "--set", "scored", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "games=12" in out and "Total expected calls: 900" in out
    assert set(os.listdir(records.ROOT)) == before
