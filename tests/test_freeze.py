"""The frozen referee setup must equal the freeze record, and the stored scores must replay. No model call."""

import hashlib
import os
import re

from swarm_referee import records, referee, referee_client, replay

FREEZE = os.path.join(records.DATA, "referee_freeze_DRAFT.md")


def freeze_text() -> str:
    with open(FREEZE) as f:
        return f.read()


def field(pattern: str) -> str:
    match = re.search(pattern, freeze_text())
    assert match, f"freeze record has no line for {pattern}"
    return match.group(1)


def test_prompt_hash_equals_freeze_record():
    with open(referee.PROMPT_PATH, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    assert digest == field(r"Prompt file sha256: ([0-9a-f]{64})")


def test_model_id_equals_freeze_record():
    assert referee_client.MODEL == field(r"Referee model: ([\w.-]+)")


def test_threshold_and_temperature_equal_freeze_record():
    assert referee.THRESHOLD == float(field(r"confidence >= ([0-9]+\.[0-9]+)"))
    assert referee.TEMPERATURE == int(field(r"temperature (\d+)"))


def test_scoring_replays_from_stored_verdicts():
    code, text = replay.render()
    assert code == 0
    with open(replay.EXPECTED) as f:
        assert text == f.read()
