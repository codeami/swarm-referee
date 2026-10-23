# Swarm-Referee

## What
Swarm-Referee is a tool. One LLM reads one evidence pack from a multi-agent game.
It uses one fixed prompt. It returns one JSON object: collusion true or false, a confidence, and a reason.

## Why
This repo is for the Apart Research AI Collusion Research Sprint (23-25 Oct 2026).
The test question: can a single fixed-prompt referee find collusion in game logs?

## Status
- Class texts were frozen on 2026-10-23 at 18:15 UTC (23:45 IST), see `data/class_texts_freeze.txt`.
  Code commit when frozen: `0a86a3c`. sha256 of `swarm_referee/classes.py`: `0c6163fc8fc8...`.
- The referee prompt (`swarm_referee/prompts/referee_v1.md`) is a draft. It is not frozen.
- The 16 scored runs are made. Their logs stay unopened until the referee is frozen.

## How to run
Run all commands from the repo root.
1. Create a virtualenv and install the harness dependencies:
   `python3 -m venv .venv && .venv/bin/pip install -r vendor/LLM-Trust-Breaking/requirements.txt`
2. Copy `.env.example` to `.env`. Add a line `DEEPSEEK_API_KEY=` with your own key (the agents and the referee use it; `.env.example` does not list it yet). Never commit `.env`.
3. Run the tests (no model call): `.venv/bin/python -m pytest tests -q`
4. Practice batch (4 games, one of each class except `innocent_parallel`):
   `.venv/bin/python -u -m swarm_referee.run_batch deepseek-flash --set practice`
   One game: `.venv/bin/python -m swarm_referee.run_diners deepseek-flash --class planted_pair --set practice`
5. Scored batch (16 games). Already done. Do not open the scored logs before the freeze:
   `.venv/bin/python -u -m swarm_referee.run_batch deepseek-flash --set scored`
6. Referee runner (one or more runs, chosen views). Proposed settings, not frozen: thinking off, temperature 0, model `deepseek-v4-pro`:
   `.venv/bin/python -m swarm_referee.referee_run run_011 run_008 --set practice --thinking off --out data/practice/referee_gate_v1a_thinking_off.csv`
   A scored run needs `--set scored`.
`CLAUDE.md` section 2 has more detail on the run commands, the classes and the call budget.

## Five views
V1 messages only. V2 actions only. V3 messages and actions, raw.
V4 ledger: one row per agent per round (message, stated order, actual order, payoff).
V5 is V4 plus a mark where the stated order and the actual order differ, and one line per round that names who gained and who lost.

## Preexisting code
- `vendor/LLM-Trust-Breaking/` is preexisting code. It is the Shi et al. harness.
  Source: https://github.com/Jerick-1380/LLM-Trust-Breaking, pinned commit `fd11aca351e52c65c929e1a7d46d9f087f237adf`.
  This repo does not change it. Git ignores the folder. Clone it again with the commit above.
  The harness has no stated licence.
- The repo scaffold, the first wrapper and the `run_001` log were made before the sprint started (22 and 23 October 2026). They are preexisting.
- The views, the referee prompt and client, the scoring, the baselines, the diagnostics, the class instructions, the practice and scored runs, the labels and the results are new work from the sprint.
