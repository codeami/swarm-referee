"""Judge adapters and the reply cache.

A judge is any callable: messages -> reply text. After each call its `last` dictionary holds
model, thinking, finish_reason, prompt_tokens and completion_tokens (this is what referee.run_view reads).
`identity` names the judge, the model and the settings that change the reply. The cache key is built from it.

Adapters: DeepSeekClient (referee_client.py, unchanged), OllamaJudge (local, no key), VertexJudge (a stub:
it needs a Google login and makes no call). CachedJudge wraps any of them. Every real call is written to a
JSON-lines cache file; a stored request is answered from the file and the judge is not called.
Cache format: docs/judge-cache.md.
"""

import hashlib
import json
import os
import socket
import urllib.error
import urllib.request
from datetime import date
from typing import Callable, Dict, List, Optional

from swarm_referee import records
from swarm_referee.referee import FatalApiError

CACHE_PATH = os.path.join(records.DATA, "judge_cache.jsonl")
JUDGE_NAMES = ("deepseek", "vertex", "ollama")
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "gemma4:12b"
OLLAMA_SEED = 42
OLLAMA_TIMEOUT = 600  # a local 12B model on a laptop is slow
OLLAMA_MAX_TOKENS = 1000  # the answer is one short JSON object


class OllamaJudge:
    """Local Ollama server. Temperature 0, fixed seed, JSON-only output (format "json"). No key.

    Some models (gemma4, qwen3.5 on this Ollama) answer HTTP 501 to format "json". The call is then sent
    again without it, and the cache row says json_mode false. The frozen prompt still asks for JSON only.
    """

    name = "ollama"

    def __init__(self, model: str = OLLAMA_MODEL, seed: int = OLLAMA_SEED, temperature: float = 0.0,
                 max_tokens: int = OLLAMA_MAX_TOKENS, think: Optional[bool] = False,
                 url: str = OLLAMA_URL, opener: Optional[Callable] = None):
        self.model, self.seed, self.temperature = model, seed, temperature
        self.max_tokens, self.think, self.url = max_tokens, think, url
        self.opener = opener or urllib.request.urlopen
        self.last: Dict = {}

    @property
    def identity(self) -> dict:
        return {"judge": self.name, "model": self.model, "temperature": self.temperature, "seed": self.seed,
                "format": "json", "think": self.think, "max_tokens": self.max_tokens}

    def body(self, messages: List[dict], json_mode: bool = True) -> dict:
        body = {"model": self.model, "messages": messages, "stream": False,
                "options": {"temperature": self.temperature, "seed": self.seed, "num_predict": self.max_tokens}}
        if json_mode:
            body["format"] = "json"
        if self.think is not None:
            body["think"] = self.think
        return body

    def post(self, body: dict) -> dict:
        req = urllib.request.Request(self.url, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        with self.opener(req, timeout=OLLAMA_TIMEOUT) as response:
            return json.load(response)

    def __call__(self, messages: List[dict]) -> str:
        json_mode = True
        try:
            try:
                data = self.post(self.body(messages))
            except urllib.error.HTTPError as exc:
                if exc.code != 501:  # 501: this model cannot do JSON mode (gemma4, qwen3.5); ask again without it
                    raise
                json_mode = False
                data = self.post(self.body(messages, json_mode=False))
        except urllib.error.HTTPError as exc:
            raise FatalApiError(f"Ollama answered HTTP {exc.code} (model {self.model}; is it pulled?)") from None
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as exc:
            raise FatalApiError(f"Ollama is not reachable at {self.url}: {type(exc).__name__}") from None
        text = (data.get("message") or {}).get("content") or ""
        self.last = {"model": data.get("model", self.model), "thinking": "off" if not self.think else "on",
                     "finish_reason": data.get("done_reason", ""), "prompt_tokens": data.get("prompt_eval_count"),
                     "completion_tokens": data.get("eval_count"), "json_mode": json_mode}
        return text


class VertexJudge:
    """Stub. The Vertex adapter needs the author's Google login and a spend ceiling, so it makes no call."""

    name = "vertex"
    identity: dict = {"judge": "vertex"}

    def __init__(self, *args, **kwargs):
        raise FatalApiError("Vertex judge needs login: no Google Cloud login or spend ceiling is set up yet. "
                            "Use --judge ollama, or --judge deepseek with a key.")


def request_hash(identity: dict, messages: List[dict]) -> str:
    canonical = json.dumps({"identity": identity, "messages": messages}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


class CachedJudge:
    """Wraps a judge. A request seen before is answered from the cache file with no call to the judge.

    offline=True makes a cache miss an error: this is the replay mode (no network, no model).
    """

    def __init__(self, judge, path: str = CACHE_PATH, offline: bool = False, today: Optional[str] = None):
        self.judge, self.path, self.offline = judge, path, offline
        self.today = today or date.today().isoformat()
        self.identity = judge.identity
        self.last: Dict = {}
        self.hits = self.misses = 0
        self.entries: Dict[str, dict] = {}
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if line.strip():
                        row = json.loads(line)
                        self.entries.setdefault(row["request_hash"], row)

    def __call__(self, messages: List[dict]) -> str:
        key = request_hash(self.identity, messages)
        row = self.entries.get(key)
        if row is not None:
            self.hits += 1
            self.last = {"model": row["model"], "thinking": row.get("thinking", ""),
                         "finish_reason": row["finish_reason"], "prompt_tokens": row["prompt_tokens"],
                         "completion_tokens": row["completion_tokens"]}
            return row["reply"]
        if self.offline:
            raise FatalApiError(f"cache miss with offline replay on (request {key[:12]}, judge {self.identity['judge']})")
        self.misses += 1
        reply = self.judge(messages)
        last = dict(getattr(self.judge, "last", None) or {})
        self.last = last
        row = {"judge": self.identity["judge"], "model": last.get("model") or self.identity.get("model", ""),
               "date": self.today, "request_hash": key, "reply": reply, "thinking": last.get("thinking", ""),
               "finish_reason": last.get("finish_reason"), "prompt_tokens": last.get("prompt_tokens"),
               "completion_tokens": last.get("completion_tokens")}
        if "json_mode" in last:
            row["json_mode"] = last["json_mode"]
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        with open(self.path, "a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        self.entries[key] = row
        return reply


def make_judge(name: str, model: Optional[str] = None, thinking: bool = False):
    """The judge for --judge NAME. DeepSeek keeps its frozen defaults."""
    if name == "deepseek":
        from swarm_referee import referee_client
        client = referee_client.DeepSeekClient(model or referee_client.MODEL, thinking=thinking)
        client.name = "deepseek"
        client.identity = {"judge": "deepseek", "model": client.model, "temperature": client.temperature,
                           "thinking": client.thinking, "max_tokens": client.max_tokens}
        return client
    if name == "ollama":
        return OllamaJudge(model or OLLAMA_MODEL)
    if name == "vertex":
        return VertexJudge()
    raise ValueError(f"unknown judge {name!r}; choose one of {', '.join(JUDGE_NAMES)}")
