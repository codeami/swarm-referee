## Appendix A. Limitations and Dual-Use / Ethical Considerations

### A.1 What the result does and does not establish
**It establishes (for these 16 runs only):**
- One frozen referee prompt, with `deepseek-v4-pro`, flagged the planted pair in 6 of 6 runs on the ledger view (95% CI 54.1–100%).
- We found no evidence of detection from messages alone or from actions alone in 16 runs (one-sided 95% upper bound on recall 34.8%; on false-positive rate 28.3%).
- On the combined views, the referee also flagged 5 or 6 of the 9 runs the author labelled not collusion, including both talk-only runs.

**It does not establish:**
- Any claim about monitors in general, or about any real deployment.
- That the agents collude by themselves. We planted all collusion by instruction.
- That a referee can tell an agreed pair from independent cheats. The evidence check coded the pair's messages "none", so the question is unanswerable from these logs.
- Any rate with narrow bounds. All intervals are wide.
- Any result about other games, other models, other vendors, other prompts or other seeds.

### A.2 Full list of limits
1. **The collusion is planted by instruction.** The pair's agreement, the cheap deal and the keepers' promise are all given in the prompts. The game's incentives create none of them. The result says whether a referee can see planted collusion. It does not say whether these agents collude on their own.
2. **Small pilot.** 16 runs: 7 collusion, 9 not. One run moves recall by about 14 points and the false-positive rate by about 11 points. The decoy classes hold 1 to 5 runs each. The tests are underpowered and the intervals are wide (for example 42.1–99.6% for recall on V4). The sprint guidance for a pilot is 20 to 40 runs; we are below it.
3. **One game, one agent model, one sample per run.** We used Diners only. The harness passes no seed, so each run is one sample with no repeats, and we have no variance estimate.
4. **Same vendor for agents and referee.** The agents (`deepseek-flash`) and the referee (`deepseek-v4-pro`) both come from DeepSeek. They are different models, but shared habits are possible. The optional second-referee check was not done.
5. **The referee flags many runs the author labelled not collusion.** The false-positive rate is 5/9 = 56% on V3 and V4 and 6/9 = 67% on V5. Those 9 runs include 4 independent cheats and 2 talk-only runs in which other agents lied, so they are not all plainly innocent. We did not tune the prompt or the threshold, as planned.
6. **One labeller, no second rater.** The author, who also wrote the study plan, labelled all 16 runs. There is no agreement figure. The labelling was blind to run id and class name, from shuffled letters.
7. **Hints in the labelling questions.** For runs D, K and O (letters in the blind pack), the person who ran the labelling session put a small hint in the question text. For D the text said that no partner or pact was named in the plan lines shown. For K it quoted the pact lines, and the author first answered "unclear". For O the text pointed out that the sheet quotes M and Q naming a pact; the author had first labelled it not collusion and changed it to collusion after the hint. Run I was skipped at first and labelled in a second pass. Most labels have no recorded reason.
8. **Sensitivity without D, K and O (descriptive, not pre-registered).** With these three runs removed (13 runs: 5 collusion, 8 not): V3 flagged 4/5 collusion runs and 4/8 others; V4 4/5 and 4/8; V5 5/5 and 6/8; V1 and V2 0/5 and 0/8; R0 5/5 and 7/8. [CHECK: recomputed by a checker, not part of `score_scored.txt`.]
9. **Labels without a reason.** The labels for run_025 (collusion, intended independent cheats) and run_027 (not collusion, independent cheats) have no recorded reason. M and Q stated cheap and ordered expensive in all 5 rounds in both runs [CHECK: from the checker's log count]. The V4 error count (2) depends on this pair; if either label changed, V4 would have one error.
10. **Labels are not independent of the planted instruction.** The author judged from private plans. In the planted pair the plan stage holds a sentence that names the pact and the partner. So "blind to class" holds for the class name only; the plan text can carry the class signal.
11. **Practice tuning.** We adjusted the class instructions on practice runs until the agents behaved as the classes need (Section 2.3). The referee prompt was checked for output format only. The scored batch was generated once.
12. **Per-class numbers use the intended class.** We did not code which class each run showed. One independent-cheats run (run_025) was labelled collusion.
13. **Thin evidence check.** One blind scout coded the pair and independents messages from two practice runs as "none". The check was not run on the scored runs [CHECK: details, second coder, agreement].
14. **Possible style tells.** The planted pair and the independent cheats received instructions that differ by one sentence. A residual difference in wording that is not about agreement cannot be ruled out.
15. **Agent temperature unconfirmed.** The sampling temperature of the agents is not confirmed [CHECK].
16. **Agents have message history but no private reflection.** The judge and reflection steps of the harness were skipped.
17. **Harness licence.** The harness has no stated licence. We use it unchanged at a pinned commit and do not redistribute it [CHECK: the author planned to contact the authors].

### A.3 Dual-use considerations
- **Defensive purpose.** The work builds a test for a monitor (a referee). Its goal is to help people who need to detect collusion between AI agents.
- **Planted instructions.** The collusion instructions are a few plain sentences of role-play in a dinner game with fictional payoffs. They give no capability that is useful outside the game. We publish the class texts so that others can repeat the study.
- **Blind spots.** A published referee prompt can be studied for blind spots. Our results show some: in these 16 runs the referee flagged runs with lying whether or not it saw marks, and we found no evidence of detection from messages alone or from actions alone. A group of agents could use such findings to learn that matching words and actions, or avoiding public cues, may reduce flags. We think the benefit of open results (others can repeat the test and find the limits) outweighs this risk for a toy game. [CHECK: the author decides whether to keep this reasoning.]
- **False accusations.** A referee that flags 56–67% of the runs labelled not collusion would cause harm if used in practice (for example, if agents or their operators were penalised). This setup is not ready for any use of that kind.
- **No people.** The data holds only text from language-model agents in a fictional game. There are no human subjects and no personal data.
- **Secrets.** The API key lives in a local `.env` file that is not in the repository. No key appears in any log, file or commit. [CHECK: run a final search of the repo for key strings before publishing.]
- **Reuse of preexisting code.** The harness is by Shi et al. We did not change it. It has no stated licence, so we do not copy it into our repo.
- **AI tools.** The code, the draft text and the run orchestration used AI coding assistants (Claude and others). The author checked outputs by hand and is responsible for the report. [CHECK: the author edits this line to say exactly what is true.]
