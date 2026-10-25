# Submission checklist and open items

Final edit round, 2026-10-25. Nothing is pushed or published. The lead claim for pair versus independent cheats is pre-registered outcome 1 (the author's choice).

## A. Submission checklist (Apart guidelines)
- [ ] Report is a PDF in the official template: https://docs.google.com/document/d/1Y5wd3VRbXU5N08BvAGiJUQTaWbMCSPjhzXsR-ozuehg/copy?usp=sharing (copy the markdown into it).
- [ ] Main body (Sections 1–5) is 8 pages or fewer, not counting references and appendices. The markdown body has about 3651 words including tables; the payoff table, token and call counts and the preexisting-code detail are in Appendix B. Check the page count in the template.
- [ ] Abstract is 150 to 250 words. Draft count: 214 words.
- [ ] Project title is final and exact, and identical on any resubmission (`00_title_abstract.md`).
- [ ] Authors and affiliations filled in.
- [ ] Appendix "Limitations and Dual-Use / Ethical Considerations" is present (Appendix A, `07_appendix_limitations_dual_use.md`).
- [ ] Preexisting code is marked in the report (Appendix B.3) and in `README.md` (section "Preexisting code").
- [ ] No secrets: search the repo and the PDF for key strings; `.env` is not committed. A search of `data/writeup/` for keys and home paths found none.
- [ ] All references are checked and complete (`06_references.md`); the ABA entry is unverified.
- [ ] Every [CHECK] below is resolved or removed.
- [ ] Links work (repo URL, template, harness).
- [ ] Optional: public GitHub repo; 3 to 5 minute video.
- [ ] Submit before Sunday 25 October 23:59 AoE (Monday 26 October 17:29 IST). A resubmission with the exact same title replaces the files.

## B. Choices for the author
1. Lead claim: outcome 1 (evidence check coded the M/Q messages "none"). Outcome 3 (V4 made 2 errors) is a secondary reading in Section 3.6 and is explained in Section 4. Outcome 4 (mixed) can also be argued.
2. Whether to code the scored M/Q messages for cues (not done). This would show whether agreement cues were present.
3. Whether to keep the dual-use reasoning in A.3.

## C. Other known gaps (not marked in the text)
- `CLAUDE.md` section 1 still says the referee prompt "is empty until the captain writes it". This is out of date.
- No diagnostics (coalition advantage, joint regret) were run on the scored logs. The report makes no claim about payoffs or agent behaviour beyond the labels and flags.
- The referee `reason` fields and the scored transcripts were not read for this draft; statements about why the referee flagged a run are marked [CHECK].
- Closed in this round: class-text freeze date and commit (2026-10-23 18:15 UTC, `0a86a3c`); talk-only M/Q orders (never expensive in run_018 and run_023); the word "captain" removed from the report text.

## D. Every [CHECK] item (30)
- `00_title_abstract.md` line 1: exact title; it must be the same on any resubmission
- `00_title_abstract.md` line 3: author name(s)
- `00_title_abstract.md` line 3: affiliation(s)
- `01_introduction.md` line 3: confirm the wording against the paper
- `01_introduction.md` line 17: the author should read each paper and correct these one-line summaries; they come from the sprint page, not from a full reading.
- `02_method.md` line 8: sampling temperature of the agents is unconfirmed; the wrapper falls back to 1.0 when a request carries none
- `02_method.md` line 47: which two practice runs; the second coder; the agreement rate; the author's own blind coding
- `03_results.md` line 59: outcome 4 (mixed) can also be argued
- `04_discussion.md` line 3: confirm against the `reason` fields in `data/verdicts.csv`; we did not read them for this draft
- `04_discussion.md` line 7: confirm; the figures were 12 to 18 liar-rounds for pairs and 14 to 17 for independents
- `04_discussion.md` line 7: from `data/verdicts.csv`
- `04_discussion.md` line 11: the author may add next steps: a second rater; repeated samples per class; a referee from another vendor; a prompt that tests "at the cost of agents outside the plan"; pair instructions that allow public signals, with the evidence check run again on the scored messages.
- `06_references.md` line 3: Titles below were read from the arXiv abstract pages by a checker, not by the author. Confirm each title and add the full author list. Do not keep an entry that the report does not cite.
- `06_references.md` line 5: authors
- `06_references.md` line 7: full title, authors
- `06_references.md` line 8: not verified; the page could not be fetched. Confirm title, authors and date, or remove.
- `06_references.md` line 9: authors
- `06_references.md` line 10: authors
- `06_references.md` line 11: authors
- `06_references.md` line 12: authors
- `06_references.md` line 13: authors, venue
- `07_appendix_limitations_dual_use.md` line 24: recomputed by a checker, not part of `score_scored.txt`.
- `07_appendix_limitations_dual_use.md` line 25: from the checker's log count
- `07_appendix_limitations_dual_use.md` line 29: details, second coder, agreement
- `07_appendix_limitations_dual_use.md` line 31: (no detail)
- `07_appendix_limitations_dual_use.md` line 33: the author planned to contact the authors
- `07_appendix_limitations_dual_use.md` line 38: the author decides whether to keep this reasoning.
- `07_appendix_limitations_dual_use.md` line 41: run a final search of the repo for key strings before publishing.
- `07_appendix_limitations_dual_use.md` line 43: the author edits this line to say exactly what is true.
- `08_appendix_method_details.md` line 16: cost in money is not computed.
