# Tech debt

Concrete debt found by reading the code and docs at commit `53d7a57`. Each item has a place (file:line), the impact and a fix. Line numbers can drift after later commits.
Severity is the planner's reading **(inference)**: High = can mislead a reader or break a reproduction, Medium = costs time, Low = tidiness.

Related: [PENDING.md](PENDING.md), [ROADMAP.md](ROADMAP.md).

| ID | Where | Debt | Impact | Fix | Severity |
|---|---|---|---|---|---|
| D1 | `CLAUDE.md:8` | Says the referee prompt "is empty until the captain writes it". The prompt is written and frozen. | A reader or agent may think the referee has no prompt. | Correct the sentence (project rule: edit only wrong text). | High |
| D2 | `CLAUDE.md:13`, `data/referee_freeze_DRAFT.md:13` | Name `STRATEGY.md` and `PROJECT.md`. Neither file is in the repo (`git ls-files` shows neither). | The "plan of record" cannot be read by anyone who clones the repo. | Add the plan as a file, or remove the two references and point to `docs/planning/HOW-IT-WAS-PLANNED.md`. | High |
| D3 | `.env.example:2-3`, `README.md:21` | The example file lists only `OPENROUTER_API_KEY`. The code needs `DEEPSEEK_API_KEY` (`run_diners.py:170`, `referee_client.py:35`). README admits the gap. | A new user starts with a wrong template. | Add `DEEPSEEK_API_KEY=` to `.env.example`. Update the README sentence. | Medium |
| D4 | `README.md:20`, `.gitignore:6`, `swarm_referee/run_diners.py:34` | The harness folder is git-ignored and pinned only by commit text. There is no requirements file for this repo and no lock. | A reproduction needs manual clone and install. Dependency versions are not recorded. | Add a `requirements.txt` with versions, and a short script that clones the pinned commit. | Medium |
| D5 | `swarm_referee/run_diners.py:168` (`patch_deepseek`), `:293-294` | The wrapper patches harness classes at run time, calls `sys.path.insert` and `os.chdir` into `vendor/`. | Fragile. A harness change at another commit can break the patch with no test warning. The `chdir` affects the whole process. | Keep the patch in one module with a version check of the harness commit. Restore the working directory after the run. | Medium |
| D6 | `swarm_referee/run_diners.py:38-39` | Comment and constant describe a 20-request-per-minute free OpenRouter limit. The agents now use DeepSeek. `run_batch.py:128` repeats `3.5` as a literal. | Stale reason. Two places hold the same number. | Reword the comment. Make `run_batch.py` import `MIN_GAP_SECONDS`. | Low |
| D7 | `swarm_referee/schema.py:4`, `tests/logbuilder.py:12`, `tests/test_views.py:80`, `tests/test_wrapper.py:208` | The old MiniMax free model name is still in a docstring and in test fixtures. | Misleading. Not wrong in tests (fixtures), but the schema note reads as current. | Update the schema docstring to say the run_001 log came from that model. | Low |
| D8 | `swarm_referee/referee_client.py:21`, `swarm_referee/referee.py:23` | Referee model id and the 0.5 threshold are constants in code. The freeze record is in a separate markdown file. | A code edit can change the frozen setup with no check. | Add a test that compares the prompt sha256 and the two constants to `data/referee_freeze_DRAFT.md`. | Medium |
| D9 | `swarm_referee/records.py:14-16`, `swarm_referee/referee_run.py:23`, `swarm_referee/label_pack.py:99` | The data folder is set at import time from the file location. Some entry points read `records.DATA` directly and have no option to change it. | Hard to run the pipeline on a copy of the data. | Pass the data folder from one command-line option. | Low |
| D10 | `data/referee_freeze_DRAFT.md` | The file is called DRAFT but its title says APPROVED. `README.md:14` links to it as the freeze record. | Confusing name for the main freeze record. | Rename to `referee_freeze.md` and fix the links in `README.md`. | Low |
| D11 | `data/label_pack_key_DO_NOT_OPEN.json` | The key that maps blind letters to run ids is committed. | The labelling cannot be repeated blind by an outside second rater who clones the repo. | Keep the key out of the main tree for a second-rater round, or build a new shuffled pack. | Medium |
| D12 | `data/writeup/` vs `data/second_referee/` | The second-referee check was done by hand in two Claude sessions. The Opus run is not blind. The script path (`referee_run.py`) cannot run it. | One result in the write-up cannot be reproduced by command. | Add a runner for a second vendor (see PENDING P9). | Medium |
| D13 | `.claude/context-transfers/2026-10-22_experiment-note.md` (tracked) | A tool-context note is tracked in a public repo. | Noise in the repo. Review it before publishing (see PENDING P10). | Read it, then remove it or move it out of the tree. | Low |
| D14 | `tests/` (69 test functions in 5 files) | No test covers `score.py` output end to end against `data/score_scored.txt`, and there is no CI workflow in the repo. | A scoring change can alter published numbers unseen. | Add one test that rebuilds the score text from the data files and compares it. Add a minimal CI run of `pytest`. | Medium |

## Not debt (decisions on record)

- `vendor/` is not edited. Decision in `CLAUDE.md` section 1.
- The wrapper skips the harness judge and reflection steps. Decision in `CLAUDE.md` call-budget section.
- The class texts are "untested guesses" by design and are frozen (`data/class_texts_freeze.txt`).
