# Pending work

Open work, with size and priority. Source of each item is named. Sizes are the planner's estimates **(inference)**: S = under half a day, M = about a day, L = several days.
Priority: P0 = blocks the report or breaks a claim, P1 = should be done next, P2 = useful, P3 = later.

Related: [ROADMAP.md](ROADMAP.md), [TECH-DEBT.md](TECH-DEBT.md).

| ID | Item | Size | Priority | Source |
|---|---|---|---|---|
| P1 | Close the 7 `[CHECK]` markers in the write-up | S | P0 | `data/writeup/checklist.md` section D |
| P2 | Close the submission checklist (PDF in template, page count, abstract word count, link check) | M | P0 | `data/writeup/checklist.md` section A |
| P3 | Update the write-up: the `run_027` label reason is now in `data/labels.csv` (commit `9482f4c`), but the write-up still says it has none | S | P0 | `05_limitations.md`; appendix A.2 item 9; `checklist.md` B.4 |
| P4 | Second rater for the 16 hand labels, with an agreement figure | M | P1 | `05_limitations.md`; appendix A.2 item 6 |
| P5 | Evidence check (message cue coding) on the scored M and Q messages | M | P1 | `checklist.md` B.2; appendix A.2 item 13 |
| P6 | Referee prompt v2: name who is harmed, check it against payoffs; new freeze | M | P1 | `04_discussion.md` (run_019 error, last paragraph) |
| P7 | Run `diagnostics.py` on the scored logs (needs `--allow-scored`) | S | P2 | `checklist.md` section C; `CLAUDE.md` diagnostics section |
| P8 | Repeat runs and more runs per class (one sample per run today) | L | P2 | `05_limitations.md` |
| P9 | Run a second-vendor referee through `referee_run.py` instead of by hand | M | P2 | `data/second_referee/README.md` |
| P10 | Final search of the repo for key strings before publishing | S | P0 | appendix A.3 "Secrets" `[CHECK]`; `checklist.md` section A |
| P11 | State the AI-tools line exactly (what was used for what) | S | P1 | appendix A.3 "AI tools" `[CHECK]` |
| P12 | Contact the harness authors about the missing licence | S | P2 | appendix A.2 item 17 `[CHECK]` |
| P13 | Read each cited paper and correct the one-line summaries | M | P1 | `01_introduction.md` line 17 `[CHECK]` |
| P14 | Fix stale text in `CLAUDE.md` and `README.md` (see TECH-DEBT D1, D2) | S | P1 | `checklist.md` section C |
| P15 | Decide on the dual-use reasoning in appendix A.3 | S | P2 | `checklist.md` B.3 |

## Notes per item

**P1.** The seven markers: `01_introduction.md` lines 3 and 17; `07_appendix_limitations_dual_use.md` lines 25, 33, 38, 41, 43. Items P3, P10, P11, P12, P13 and P15 each close one or more of them.

**P2.** Checklist boxes still open on 2026-10-25: PDF in the official template, body of 8 pages or fewer (markdown body is 3,780 words by `wc -w`), abstract 150 to 250 words (draft 214), appendix present, preexisting code marked, no secrets, links work. The repo does not record the submission outcome. Confirm and tick the boxes.

**P3.** `run_027` is the only V4 false flag among pair and independent-cheat runs. The label was kept after a re-read on 26 Oct and the reason is in `data/labels.csv`. The text in `05_limitations.md` and in appendix A.2 item 9 (also in `report.md`) still says "no recorded reason", and `checklist.md` lists it as open. Align the write-up with the CSV. Do not change the label.

**P4.** The author labelled all runs and also wrote the plan. Runs D, K and O (blind-pack letters) carried small hints in the question text. A second rater should see the same blind pack.

**P5.** The evidence check supports the lead claim (outcome 1). It rests on 20 messages from two practice runs. Run it on the scored messages with the rubric fixed before coding.

**P6.** A new prompt file with a new name (for example `referee_v2.md`) and a new freeze record. Keep `referee_v1.md` and its sha256 `a7df12646c31...` untouched.

**P7.** Descriptive only. The report makes no payoff claim today.

**P14.** Edit only the wrong text (project rule). Do not add sections.
