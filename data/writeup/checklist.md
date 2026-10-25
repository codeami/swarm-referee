# Submission checklist and open items

Draft revised 2026-10-25 (author chose outcome 3) from commit d36d3a9 (scoring) on branch `fm/sprint1-practice-runs`. Nothing is pushed or published.

## A. Submission checklist (Apart guidelines)
- [ ] Report is a PDF in the official template: https://docs.google.com/document/d/1Y5wd3VRbXU5N08BvAGiJUQTaWbMCSPjhzXsR-ozuehg/copy?usp=sharing (copy the markdown into it).
- [ ] Main body is 8 pages or fewer, not counting references and appendices. The markdown body (Sections 1–5) has about 4379 words with tables. Check the page count in the template; cut Section 2.1 text or the Section 3.4 table if it is over.
- [ ] Abstract is 150 to 250 words. Draft count: 247 words.
- [ ] Project title is final and exact. It must be identical on any resubmission. Draft title is in `00_title_abstract.md`.
- [ ] Authors and affiliations filled in.
- [ ] Appendix "Limitations and Dual-Use / Ethical Considerations" is present (`07_appendix_limitations_dual_use.md`).
- [ ] Preexisting code is marked in the report (Section 2.8) and in `README.md` (section "Preexisting code").
- [ ] README status lines match the final state of the repo (updated in this commit; re-check).
- [ ] No secrets: search the repo and the PDF for key strings; `.env` is not committed.
- [ ] All references are checked and complete; no reference is made up (see `06_references.md`).
- [ ] Every [CHECK] below is resolved or removed.
- [ ] Links work (repo URL, template, harness).
- [ ] Optional: public GitHub repo; 3 to 5 minute video.
- [ ] Submit before Sunday 25 October 23:59 AoE (Monday 26 October 17:29 IST). A resubmission with the exact same title replaces the files.

## B. Choices for the author
1. Primary claim for pair versus independent cheats: the author chose pre-registered outcome 3 (V4 made 2 errors). The draft leads with it. The earlier blind evidence check coded the M/Q messages "none"; this is stated as a caveat in Section 3.6, Section 4 (discussion), Section 5 and Appendix A.2 item 10. The outcome 1 sentence is quoted in Section 3.6 so a reader can see the other reading. Outcome 4 (mixed) can also be argued.
2. Whether to code the scored M/Q messages for cues (not done). This would settle whether "agreement cues were present".
3. Whether to report scores without D, K and O (not computed).
4. Whether to keep the dual-use reasoning in A.3.

## C. Other known gaps (not marked in the text)
- `CLAUDE.md` section 1 still says the referee prompt "is empty until the captain writes it". This is out of date.
- No diagnostics (coalition advantage, joint regret) were run on the scored logs. The report makes no claim about payoffs or agent behaviour beyond the labels and flags.
- I did not read the `reason` fields of the referee verdicts or the scored transcripts. Statements about why the referee flagged a run are marked [CHECK].

## D. Every [CHECK] item (35)
- `00_title_abstract.md` line 1: exact title; it must be the same on any resubmission
- `00_title_abstract.md` line 3: author name(s)
- `00_title_abstract.md` line 3: affiliation(s)
- `00_title_abstract.md` line 11: word count must stay between 150 and 250 — counted in checklist.md
- `01_introduction.md` line 3: confirm the figure and the paper details against the paper; this figure is taken from the sprint page
- `01_introduction.md` line 5: citation form
- `01_introduction.md` line 19: the author should read each paper and correct these one-line summaries; they come from the sprint page, not from a full reading
- `02_method.md` line 17: sampling temperature of the agents — the harness default is 1.0; confirm
- `02_method.md` line 37: freeze date 2026-10-23 18:15 UTC, code commit `0a86a3c`
- `02_method.md` line 53: the file still says "captain"
- `02_method.md` line 58: which two practice runs; the second coder; the agreement rate between coders; the author's own blind coding
- `02_method.md` line 64: licence status; the author planned to contact the harness authors
- `03_results.md` line 3: we did not check the landed class independently; the labels agree with the intended class in 15 of 16 runs, see Section 3.1
- `03_results.md` line 6: ask the author whether the plans showed a shared plan
- `03_results.md` line 40: the author has read these two runs; confirm that M and Q did so
- `03_results.md` line 63: the author may want to code them
- `03_results.md` line 65: outcome 4 (mixed) can also be argued
- `04_discussion.md` line 3: confirm this reading against the `reason` fields in `data/verdicts.csv`; we did not read them for this draft
- `04_discussion.md` line 11: the author may add or remove next steps.
- `06_references.md` line 3: These entries hold only what the sprint page and the talk notes state: first author, year, arXiv number or link. I did not add titles from memory, because a made-up reference can disqualify the project. Look up each paper, add the full title and author list, and delete any entry the report does not cite.
- `06_references.md` line 5: title, authors
- `06_references.md` line 6: title, authors
- `06_references.md` line 7: authors
- `06_references.md` line 8: title, authors
- `06_references.md` line 9: title, authors
- `06_references.md` line 10: title, authors
- `06_references.md` line 11: title, authors
- `06_references.md` line 12: title, authors, venue
- `07_appendix_limitations_dual_use.md` line 19: 1.0
- `07_appendix_limitations_dual_use.md` line 23: the author may want to report the scores with D, K and O removed; we did not compute this
- `07_appendix_limitations_dual_use.md` line 26: details, second coder, agreement
- `07_appendix_limitations_dual_use.md` line 29: the author planned to contact the authors
- `07_appendix_limitations_dual_use.md` line 34: the author decides whether to keep this reasoning.
- `07_appendix_limitations_dual_use.md` line 37: run a final search of the repo for key strings before publishing.
- `07_appendix_limitations_dual_use.md` line 39: the author edits this line to say exactly what is true.
