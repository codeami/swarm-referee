"""The referee's model client: DeepSeek's OpenAI-style API, one blocking call per request.

Same rules as the agent calls in run_diners.py: 90 s limit per request, at most two retries
for 408, 429 and 5xx replies, and a stop at once for 401, 402, 403 and 404 (FatalApiError).
A reply cut by length with no text is asked again once with twice the tokens.
The key DEEPSEEK_API_KEY is read from the environment (load_dotenv has put .env there).
It is never printed, logged or written.
"""

import json
import os
import socket
import time
import urllib.error
import urllib.request
from typing import Callable, Dict, List, Optional

from swarm_referee import run_diners
from swarm_referee.referee import FatalApiError

MODEL = "deepseek-v4-pro"
MAX_TOKENS = 8000
FATAL_STATUSES = (401, 402, 403, 404)


class DeepSeekClient:
    """Callable: messages -> reply text. After each call, `last` holds model, thinking, finish reason, tokens."""

    def __init__(self, model: str = MODEL, thinking: bool = False, temperature: float = 0.0,
                 max_tokens: int = MAX_TOKENS, opener: Optional[Callable] = None,
                 sleep: Callable = time.sleep, api_key: Optional[str] = None):
        self.model, self.thinking, self.temperature, self.max_tokens = model, thinking, temperature, max_tokens
        self.opener = opener or urllib.request.urlopen
        self.sleep = sleep
        self._key = api_key if api_key is not None else os.environ.get("DEEPSEEK_API_KEY", "")
        if not self._key:
            raise FatalApiError("DEEPSEEK_API_KEY is missing or empty")
        self.last: Dict = {}

    def body(self, messages: List[dict], max_tokens: int) -> dict:
        body = {"model": self.model, "messages": messages, "max_tokens": max_tokens,
                "thinking": {"type": "enabled" if self.thinking else "disabled"}}
        if not self.thinking:
            body["temperature"] = self.temperature  # DeepSeek ignores temperature while thinking is on
        return body

    def post(self, body: dict) -> dict:
        """One HTTP call with the retry rules. Returns the parsed JSON reply."""
        req = urllib.request.Request(
            run_diners.DEEPSEEK_URL, data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {self._key}", "Content-Type": "application/json"})
        error = "no reply"
        for attempt in range(run_diners.DEEPSEEK_TRIES):
            try:
                with self.opener(req, timeout=run_diners.REQUEST_TIMEOUT) as response:
                    return json.load(response)
            except urllib.error.HTTPError as exc:
                error = f"HTTP {exc.code}"
                if exc.code in FATAL_STATUSES:
                    raise FatalApiError(f"{error} (model {self.model})") from None
                if exc.code not in run_diners.RETRY_STATUSES:
                    raise RuntimeError(error) from None
            except (urllib.error.URLError, socket.timeout, TimeoutError, ValueError) as exc:
                error = type(exc).__name__
            if attempt < run_diners.DEEPSEEK_TRIES - 1:
                self.sleep(run_diners.RETRY_SLEEP[attempt])
        raise RuntimeError(f"Max retries exceeded: {error}")

    def __call__(self, messages: List[dict]) -> str:
        tokens = self.max_tokens
        prompt_used = completion_used = 0
        for _ in range(2):
            data = self.post(self.body(messages, tokens))
            choice = data["choices"][0]
            usage = data.get("usage") or {}
            prompt_used += usage.get("prompt_tokens") or 0
            completion_used += usage.get("completion_tokens") or 0
            text = choice["message"].get("content") or ""
            if text or choice.get("finish_reason") != "length":
                break
            tokens *= 2  # the model used all its tokens: ask once more with twice as many
        self.last = {"model": data.get("model", self.model), "thinking": "on" if self.thinking else "off",
                     "finish_reason": choice.get("finish_reason"), "prompt_tokens": prompt_used,
                     "completion_tokens": completion_used}
        return text
