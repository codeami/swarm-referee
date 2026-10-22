# CLAUDE.md - constants and current status

## 1. Constants
- Game: Diners. Agents: 5. Rounds: 5. Trials per run: 1.
- Harness: vendor/LLM-Trust-Breaking (commit fd11aca). Do not edit it.
- Models: free OpenRouter models only. Never use a paid model.
- Never create, read, print, log or copy an API key. Keys live in `.env` only.
- Prompt file `swarm_referee/prompts/referee_v1.md` is frozen after the practice runs.
- Write names and technical text in ASD-STE100.

## 2. Run command (Diners, one game)
Status: run_001 finished with this command (exit 0).
```
.venv/bin/python swarm_referee/run_diners.py minimax/minimax-m3.1-flash:free
```
The wrapper runs the harness with `--game diners --agents 5 --trials 1 --rounds 5 --use-queue --round-robin`
and writes to `data/runs/run_001`. It swaps the paid judge model `openai/gpt-5-mini` for the free model.
It also limits requests to one per 3.5 s, because free models allow 20 per minute.
Cost of run_001: 200 calls, about 188k tokens (estimate: characters / 4; the harness logs no usage).

## 3. Log fields (verified on data/runs/run_001/)
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
- Step 4 live game: done. Log: `data/runs/run_001/diners/5agents/minimax_minimax-m3.1-flash_free_endogenous.json`.
- Step 5 schema: verified against run_001.

## 5. Open issues
- The judge step is hard-coded to a paid model. The wrapper swaps it. Do not run the harness directly.
- Free-model limits: `google/gemma-4-31b-it:free` was rate-limited upstream (first attempt, 0 of 75 stages parsed).
  An unthrottled run also hits the 20 requests per minute limit.
- run_001 is a benign game: all agents chose EXPENSIVE every round. It has one parse failure (1 of 75 stages).
