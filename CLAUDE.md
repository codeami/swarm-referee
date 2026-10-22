# CLAUDE.md - constants and current status

## 1. Constants
- Game: Diners. Agents: 5. Rounds: 5. Trials per run: 1.
- Harness: vendor/LLM-Trust-Breaking (commit fd11aca). Do not edit it.
- Models: free OpenRouter models only. Never use a paid model.
- Never create, read, print, log or copy an API key. Keys live in `.env` only.
- Prompt file `swarm_referee/prompts/referee_v1.md` is frozen after the practice runs.
- Write names and technical text in ASD-STE100.

## 2. Run command (Diners, one game)
Status: command taken from the README. `--help` works. The game has not run.
```
.venv/bin/python vendor/LLM-Trust-Breaking/experiments/run_endogenous.py \
  --game diners --agents 5 --trials 1 --rounds 5 \
  --model google/gemma-4-31b-it:free --use-queue --round-robin \
  --output-dir data/runs/run_001
```
Warning: the harness always sends the judge step to the paid model `openai/gpt-5-mini`
(trial_runner.py, `_build_judge_request`). See Open issues.

## 3. Log fields (UNVERIFIED until a real log exists in data/runs/run_001/)
The log is one JSON file: `<output-dir>/diners/5agents/<model>_endogenous.json`.
Path to one agent in one round: `rounds[].trials[].agents.<agent>`.

| Event field | Exact name in the harness log |
|---|---|
| round | `rounds[].round_id` |
| agent | dictionary key under `agents` (single letters, for example `A`) |
| plan | `stage1.intended_action`, `stage1.reasoning` |
| message | `stage2.message`, `stage2.stated_action` |
| action | `stage3.choice`, `stage3.reasoning` |
| payoff | `rounds[].trials[].outcomes.payoffs.<agent>` (trial level, not agent level) |

The harness does not write a run id. This repo uses the folder name.

## 4. Status
- Step 1 repo layout: done.
- Step 2 clone: done.
- Step 3 install: done in `.venv` (Python 3.9.6). `run_endogenous.py --help` works. The harness refuses to start without a key in `.env`.
- Step 4 live game: waiting. No OpenRouter key in `.env`.
- Step 5 schema: written from source. Unverified.

## 5. Open issues
- The judge step uses the paid model `openai/gpt-5-mini` and cannot be turned off by a flag.
  The captain must decide: allow a small paid cost, or patch the model name from a wrapper outside `vendor/`.
