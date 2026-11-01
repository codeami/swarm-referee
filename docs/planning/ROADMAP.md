# Roadmap

Status of Swarm-Referee after the Apart Research AI Collusion Research Sprint (23-25 Oct 2026).
Facts come from the repo (`README.md`, `CLAUDE.md`, `data/`, `data/writeup/`, git history).
Lines marked **(inference)** are the planner's reading, not a recorded decision.

Related: [PENDING.md](PENDING.md) (open work), [TECH-DEBT.md](TECH-DEBT.md) (code debt), [HOW-IT-WAS-PLANNED.md](HOW-IT-WAS-PLANNED.md) (how the sprint ran).

## 1. Delivered in the sprint (done)

| Item | Where | Evidence |
|---|---|---|
| Diners wrapper around the pinned harness (agents: `deepseek-flash`) | `swarm_referee/run_diners.py`, `run_batch.py` | commits `3749ae3`, `f5ba178`, `e19de08` |
| Five run classes, instruction texts frozen 2026-10-23 | `swarm_referee/classes.py`, `data/class_texts_freeze.txt` | commit `3ed437f` |
| 16 scored runs (`run_015` to `run_030`), generated once | `data/runs/`, `data/run_meta.csv` | commit `62181a9` |
| Five views and a leak check (80 of 80 views passed) | `swarm_referee/views.py` | commit `2ad5246`; `data/writeup/02_method.md` 2.4 |
| Frozen referee: `deepseek-v4-pro`, thinking off, temperature 0, prompt `referee_v1.md` | `swarm_referee/referee*.py`, `data/referee_freeze_DRAFT.md` | commits `72e9571`, `7dc3777` |
| Two no-model baselines R0 and R1 | `swarm_referee/baselines.py` | `data/baselines_scored.csv` |
| Verdicts on 16 runs x 5 views (80 calls, 0 retries, 0 no-verdict) | `data/verdicts.csv` | commit `d87af74` |
| Blind label pack and hand labels for 16 runs | `swarm_referee/label_pack.py`, `data/labels.csv` | commits `047c14e`, `d36d3a9` |
| Exact scoring (Clopper-Pearson, McNemar) | `swarm_referee/score.py`, `data/score_scored.txt` | commit `acc6220` |
| Post-hoc diagnostic (coalition advantage, joint regret) | `swarm_referee/diagnostics.py` | commit `9b37ae4` (not run on scored logs) |
| Write-up draft, four edit rounds | `data/writeup/` | commits `0a34bd6` to `68cc89e` |
| Second-referee check (Claude Opus 5.5 not blind, Claude Sonnet 5.5 clean) | `data/second_referee/` | commit `53d7a57` |

Headline results (from `data/score_scored.txt` and the write-up, not changed here):
- Positive control: V4 flagged the planted pair in 6 of 6 runs.
- V1 (messages only) and V2 (actions only) flagged 0 of 6 collusion runs. One-sided 95% upper bound on recall: 39.3%.
- False flags on the 10 not-collusion runs: V3 5, V4 5, V5 7.
- The pair-versus-independents question is unanswerable from these logs (pre-registered outcome 1).
- A second referee from another vendor flagged far fewer runs (Sonnet 5.5, clean run: 1 of 6 pairs on V3 to V5, 0 of 10 others). Result depends on the referee model.

## 2. Next: submit the sprint report (days)

The sprint deadline was Sunday 25 Oct 2026, 23:59 AoE. The repo does not record whether the report was submitted. `data/writeup/checklist.md` still shows open boxes.
- Close the open checklist items and the 7 `[CHECK]` markers (see PENDING P1, P2).
- Decide whether to publish the repo and the optional video. **(inference)** The repo is public, so the first part is done.

## 3. Next research steps (weeks)

These come from the write-up's "next steps" sentence (`data/writeup/04_discussion.md`, last paragraph) and its limitations.
1. **Referee prompt v2** that names who is harmed and checks it against the payoffs. This is a new frozen prompt, not an edit of `referee_v1.md`.
2. **Second rater** for the 16 hand labels, with a reported agreement figure.
3. **Evidence check on the scored messages.** The check ran only on `run_007` and `run_008`.
4. **More runs per class and repeats.** The pilot has 6 collusion runs and 10 others, one sample each. One run moves recall by about 17 points.
5. **Referee from another vendor, run in the same automated pipeline.** The second-referee check was done by hand.
6. **Run the diagnostic** (`diagnostics.py`) on the scored logs now that the prompt is frozen.

## 4. Later (months, **inference**)

- More games than Diners, more agent models, more than five agents.
- Collusion that arises without a planted instruction. The current design only tests whether a referee can see planted collusion.
- A monitor that reports a false-positive rate next to recall as a standard result.
- Contact the harness authors about the missing licence (write-up item A.2-17).

## 5. Not planned

- Edits to `vendor/LLM-Trust-Breaking/`. The repo rule is to use it unchanged at the pinned commit.
- Retuning the frozen v1 prompt or the 0.5 threshold. Any change needs a new version and a new freeze record.
