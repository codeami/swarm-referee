"""Diagnostic tests. No model call. Synthetic logs and practice runs 011 and 014 only."""

import os

import pytest

from logbuilder import make_log, planted_pair_log, table_round
from swarm_referee import diagnostics, records


def test_advantage_known_payoffs():
    # M,Q expensive, rest cheap: share = (2*8 + 3*2)/5 = 4.4 -> M,Q 5.6, others 0.6
    adv = diagnostics.coalition_advantage(make_log([table_round()]), ["M", "Q"])
    assert adv["rounds"] == [(1, pytest.approx(5.0))]
    assert adv["mean"] == pytest.approx(5.0)


def test_advantage_all_cheap_is_zero():
    log = make_log([{a: ("hi", "CHEAP", "CHEAP") for a in "JMQTZ"}])
    assert diagnostics.coalition_advantage(log, ["M", "Q"])["mean"] == pytest.approx(0.0)


def test_coalition_must_leave_others():
    with pytest.raises(ValueError):
        diagnostics.coalition_advantage(make_log([table_round()]), list("JMQTZ"))


def test_regret_all_cheap_is_zero():
    log = make_log([{a: ("hi", "CHEAP", "CHEAP") for a in "JMQTZ"}] * 2)
    reg = diagnostics.joint_regret(log)
    assert reg["total"] == pytest.approx(0.0)
    assert diagnostics.best_per_agent() == 3.0


def test_regret_planted_pair():
    # payoffs 5.6*2 + 0.6*3 = 13.0 -> regret 2.0 per round
    reg = diagnostics.joint_regret(planted_pair_log())
    assert reg["rounds"][0][2] == pytest.approx(2.0)
    assert reg["total"] == pytest.approx(10.0)


def test_report_header_and_totals():
    text = diagnostics.format_report(planted_pair_log(), ["M", "Q"])
    assert "post-hoc descriptive diagnostic, not a view, not a score" in text
    assert "total regret +10.0" in text


def test_cli_refuses_scored_dir(capsys):
    assert diagnostics.main([os.path.join(records.DATA, "runs", "run_002"), "--coalition", "M,Q"]) == 2
    assert "refused" in capsys.readouterr().err


def test_guard_helper():
    assert diagnostics.under_scored_dir(os.path.join(records.DATA, "runs", "run_020"))
    assert not diagnostics.under_scored_dir(os.path.join(records.DATA, "practice", "run_011"))


@pytest.mark.parametrize("run,coalition", [("run_011", "M,Q"), ("run_014", "M,Q")])
def test_practice_runs(run, coalition, capsys):
    path = os.path.join(records.DATA, "practice", run)
    if not os.path.isdir(path):
        pytest.skip("practice log absent")
    assert diagnostics.main([path, "--coalition", coalition]) == 0
    assert "mean advantage" in capsys.readouterr().out
