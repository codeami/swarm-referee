# Judge reply cache

File: `data/judge_cache.jsonl`. One JSON object per line. Every call that reaches a judge writes one line.
A request that is already in the file is answered from the file, and the judge is not called.

| Field | Meaning |
|---|---|
| `judge` | Adapter name: `deepseek`, `ollama` or `vertex`. |
| `model` | Model id the server reported (falls back to the id asked for). |
| `date` | Day of the call, `YYYY-MM-DD`. |
| `request_hash` | sha256 of the judge identity (judge, model, temperature, seed, format, thinking, token limit) and the messages, as sorted JSON. Any change to the prompt, the view or a setting gives a new hash. |
| `reply` | The raw reply text, as the model sent it. Not parsed. |
| `thinking` | `on` or `off`. |
| `finish_reason` | The server's stop reason (`stop`, `length`). |
| `prompt_tokens`, `completion_tokens` | Token counts the server reported. |
| `json_mode` | Ollama only. `true` when the server enforced JSON output, `false` when the model refused JSON mode and the prompt alone asked for JSON. |

Replay with the network off:

```
.venv/bin/python -m swarm_referee.referee_run run_015 --set scored --judge ollama --offline --out /tmp/replayed.csv
```

A request that is not in the file stops the run with "cache miss". Replay applies the same parse and flag rule
as a live run, so a new rule can be tried on old replies without a model call.

Limits: a retry of an unparseable reply has the same request, so it gets the same cached reply. Delete the line
to ask again. The file holds only the first reply for a request.
