# Swarm-Referee

## What
Swarm-Referee is a tool. One LLM reads one evidence pack from a multi-agent game.
It uses one fixed prompt. It returns one JSON object: collusion true or false, a confidence, and a reason.

## Why
This repo is for the Apart Research AI Collusion Research Sprint (23-25 Oct 2026).
The test question: can a single fixed-prompt referee find collusion in game logs?

## How to run
1. Create a virtualenv and install the harness dependencies:
   `python3 -m venv .venv && .venv/bin/pip install -r vendor/LLM-Trust-Breaking/requirements.txt`
2. Copy `.env.example` to `.env`. Put your own OpenRouter key in it. Never commit `.env`.
3. Run one Diners game. See `CLAUDE.md` section 2 for the exact command.
4. Referee code (`views.py`, `referee.py`, `score.py`) is not built yet.

## Four views
V1 messages only. V2 actions only. V3 messages and actions, raw.
V4 ledger: one row per agent per round (plan, message, action, payoff).

## Preexisting code
- `vendor/LLM-Trust-Breaking/` is preexisting code. It is the Shi harness.
  Source: https://github.com/Jerick-1380/LLM-Trust-Breaking, commit `fd11aca351e52c65c929e1a7d46d9f087f237adf`.
  This repo does not change it. Git ignores the folder. Clone it again with the commit above.
- The harness has no stated licence.
- Everything in `swarm_referee/` is new.
