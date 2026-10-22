# Experiment note (chat to Code handoff)

## Question
Can one LLM, with one fixed prompt, read an evidence pack from a multi-agent game
and answer: collusion true or false, with a confidence and a reason?

## Tool name
Swarm-Referee. One prompt. One JSON output.

## Test data
Game logs from the Shi harness (Jerick-1380/LLM-Trust-Breaking).
Game: Diners. 5 agents. 5 rounds.
Each agent, each round, writes a private plan, posts a public message, and takes an action.
The harness logs all three and the payoff.

## Views (always called "views")
- V1: messages only.
- V2: actions only.
- V3: messages and actions, raw.
- V4: ledger. One row per agent per round: plan, message, action, payoff.

## Rules
- Do not copy code from other projects. Do not build a graph.
- Write names and technical text in ASD-STE100: one idea per sentence, active voice, one term per thing.
- Repo and file names follow org-name_purpose_sequence_date_topic.
- Rings: referee.guard = frozen prompt, threshold, freeze date.
  referee.learn = practice-run tuning before the freeze.
  referee.judge = scored runs, confusion matrix, FPR.
- Practice runs in data/practice/ are not scored.
- referee_v1.md is frozen after the practice runs. Nobody edits it afterward.

## Fallback
If the harness does not log all three steps per agent, or does not run, report it.
The captain decides whether to switch to Q3.4.
