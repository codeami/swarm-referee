"""Judge adapter and cache tests with fake transports. No model call, no network call."""

import io
import json
import urllib.error

import pytest

from swarm_referee import judges, referee

GOOD = '{"collusion": true, "confidence": 0.8, "reason": "They lied together."}'
MESSAGES = [{"role": "system", "content": "prompt"}, {"role": "user", "content": "view"}]


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def ollama_reply(content=GOOD, **extra):
    data = {"model": "gemma4:12b", "message": {"role": "assistant", "content": content}, "done": True,
            "done_reason": "stop", "prompt_eval_count": 120, "eval_count": 30, **extra}
    return FakeResponse(json.dumps(data).encode())


def ollama_with(reply):
    sent = []

    def opener(req, timeout):
        sent.append(json.loads(req.data))
        if isinstance(reply, Exception):
            raise reply
        return reply()

    return judges.OllamaJudge(opener=opener), sent


def test_ollama_sends_temperature_zero_seed_and_json_format():
    judge, sent = ollama_with(ollama_reply)
    assert judge(MESSAGES) == GOOD
    body = sent[0]
    assert body["format"] == "json" and body["stream"] is False
    assert body["options"]["temperature"] == 0 and body["options"]["seed"] == judges.OLLAMA_SEED
    assert body["messages"] == MESSAGES


def test_ollama_records_metadata_for_run_view():
    judge, _ = ollama_with(ollama_reply)
    verdict = referee.run_view(judge, "prompt", "view")
    assert verdict.status == referee.FLAG
    assert (verdict.model, verdict.finish_reason, verdict.prompt_tokens, verdict.completion_tokens) == \
        ("gemma4:12b", "stop", 120, 30)


def test_ollama_drops_json_mode_when_the_model_refuses_it():
    sent = []

    def opener(req, timeout):
        body = json.loads(req.data)
        sent.append(body)
        if "format" in body:
            raise urllib.error.HTTPError(req.full_url, 501, "structured output is unavailable", {}, None)
        return ollama_reply()

    judge = judges.OllamaJudge(opener=opener)
    assert judge(MESSAGES) == GOOD
    assert ["format" in b for b in sent] == [True, False]
    assert judge.last["json_mode"] is False


def test_ollama_down_is_a_clear_fatal_error():
    judge, _ = ollama_with(urllib.error.URLError("refused"))
    with pytest.raises(referee.FatalApiError, match="not reachable"):
        judge(MESSAGES)


def test_vertex_needs_login_and_makes_no_call():
    with pytest.raises(referee.FatalApiError, match="needs login"):
        judges.make_judge("vertex")


def test_unknown_judge_is_refused():
    with pytest.raises(ValueError):
        judges.make_judge("nope")


def test_cache_writes_one_line_then_replays_without_the_judge(tmp_path):
    path = str(tmp_path / "cache.jsonl")
    judge, sent = ollama_with(ollama_reply)
    cached = judges.CachedJudge(judge, path, today="2026-11-06")
    assert cached(MESSAGES) == GOOD
    rows = [json.loads(line) for line in open(path)]
    assert len(rows) == 1
    assert rows[0]["judge"] == "ollama" and rows[0]["model"] == "gemma4:12b" and rows[0]["date"] == "2026-11-06"
    assert rows[0]["reply"] == GOOD and rows[0]["finish_reason"] == "stop"
    assert rows[0]["prompt_tokens"] == 120 and rows[0]["completion_tokens"] == 30
    assert rows[0]["request_hash"] == judges.request_hash(judge.identity, MESSAGES)

    again, sent_again = ollama_with(urllib.error.URLError("network off"))
    replay = judges.CachedJudge(again, path, offline=True)
    assert replay(MESSAGES) == GOOD
    assert replay.last["model"] == "gemma4:12b" and replay.hits == 1
    assert sent_again == [] and len(sent) == 1
    assert len(open(path).read().splitlines()) == 1  # a hit writes nothing


def test_offline_cache_miss_is_an_error(tmp_path):
    judge, _ = ollama_with(ollama_reply)
    cached = judges.CachedJudge(judge, str(tmp_path / "cache.jsonl"), offline=True)
    with pytest.raises(referee.FatalApiError, match="cache miss"):
        cached(MESSAGES)


def test_different_settings_do_not_share_a_cache_entry():
    a = judges.OllamaJudge(seed=1).identity
    b = judges.OllamaJudge(seed=2).identity
    assert judges.request_hash(a, MESSAGES) != judges.request_hash(b, MESSAGES)
