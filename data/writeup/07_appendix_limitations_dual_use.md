## Appendix A. Limitations and Dual-Use / Ethical Considerations

### A.1 What the result does and does not establish
**It establishes (for these 16 runs only):**
- One frozen referee prompt, with `deepseek-v4-pro`, flagged the planted pair in 6 of 6 runs on the ledger view (95% CI 54.1–100%).
- On the same runs, the referee flagged none of the 16 when it saw only messages or only actions (upper bounds: 34.8% on recall, 28.3% on false-positive rate).
- On the combined views, the referee also flagged 5 or 6 of the 9 runs labelled not collusion, including both talk-only runs.

**It does not establish:**
- Any claim about monitors in general, or about any real deployment.
- That the agents collude by themselves. We planted all collusion by instruction.
- That a referee can tell an agreed pair from independent cheats. Our evidence gate failed, so we make no claim.
- Any rate with narrow bounds. All intervals are wide.
- Any result about other games, other models, other vendors, other prompts or other seeds.

### A.2 Full list of limits
1. **The collusion is planted by instruction.** The pair's agreement, the cheap deal and the keepers' promise are all given in the prompts. The game's incentives create none of them. The result says whether a referee can see planted collusion. It does not say whether these agents collude on their own.
2. **Small pilot.** 16 runs: 7 collusion, 9 not. One run moves recall by about 14 points and the false-positive rate by about 11 points. The decoy classes hold 1 to 5 runs each. The tests are underpowered and the intervals are wide (for example 42.1–99.6% for recall on V4). The sprint guidance for a pilot is 20 to 40 runs; we are below it.
3. **One game, one agent model, one run per condition.** We used Diners only. The harness passes no seed and the agents run at the harness default temperature [CHECK: 1.0], so each run is one sample. We have no variance estimate.
4. **Same vendor for agents and referee.** The agents (`deepseek-flash`) and the referee (`deepseek-v4-pro`) both come from DeepSeek. They are different models, but shared habits are possible. The optional second-referee check was not done.
5. **The referee flags many innocent runs.** The false-positive rate is 5/9 = 56% on V3 and V4 and 6/9 = 67% on V5. We did not tune the prompt or the threshold, as planned, so these rates are what the frozen setup gives.
6. **One labeller, no second rater.** The author, who also wrote the study plan, labelled all 16 runs. There is no agreement figure. The labels were collected blind to run id and class, from shuffled letters.
7. **Hints in the labelling questions.** For runs D, K and O (letters in the blind pack), the person who ran the labelling session put a small hint in the question text. For D the text said that no partner or pact was named in the plan lines shown. For K it quoted the pact lines, and the author first answered "unclear". For O the text pointed out that the sheet quotes M and Q naming a pact; the author had first labelled it not collusion and changed it to collusion after the hint. Run I was skipped at first and labelled in a second pass. Most labels have no recorded reason. These labels may be biased towards the hint [CHECK: the author may want to report the scores with D, K and O removed; we did not compute this].
8. **Practice tuning.** We adjusted the class instructions on practice runs until the agents behaved as the classes need (Section 2.3). The referee prompt was checked for output format only. The scored batch was generated once.
9. **Intended class is not the landed class.** Per-class numbers use the intended class. We did not code the landed class independently. One independent-cheats run (run_025) was labelled collusion.
10. **The evidence gate had thin support.** One blind scout coded the pair and independents messages from practice runs as "none". The gate was run on practice runs, not on the scored runs [CHECK: details, second coder, agreement].
11. **Possible style tells.** The planted pair and the independent cheats received instructions that differ by one sentence. A residual difference in wording that is not about agreement cannot be ruled out.
12. **Agents have message history but no private reflection.** The judge and reflection steps of the harness were skipped.
13. **Harness licence.** The harness has no stated licence. We use it unchanged at a pinned commit and do not redistribute it [CHECK: the author planned to contact the authors].

### A.3 Dual-use considerations
- **Defensive purpose.** The work builds a test for a monitor (a referee). Its goal is to help people who need to detect collusion between AI agents.
- **Planted instructions.** The collusion instructions are a few plain sentences of role-play in a dinner game with fictional payoffs. They give no capability that is useful outside the game. We publish the class texts so that others can repeat the study.
- **Blind spots.** A published referee prompt can be studied for blind spots. Our results show one: a referee that flags by reading lying marks also flags innocent runs, and it did not flag the pair when it saw only messages or only actions. A group of agents could use such a finding to learn that matching words and actions, or avoiding public cues, may reduce flags. We think the benefit of open results (others can repeat the test and find the limits) outweighs this risk for a toy game. [CHECK: the author decides whether to keep this reasoning.]
- **False accusations.** A referee that accuses 56–67% of innocent runs would cause harm if used in practice (for example, if it led to agents or their operators being penalised). We say clearly that this setup is not ready for any use of that kind.
- **No people.** The data holds only text from language-model agents in a fictional game. There are no human subjects and no personal data.
- **Secrets.** The API key lives in a local `.env` file that is not in the repository. No key appears in any log, file or commit. [CHECK: run a final search of the repo for key strings before publishing.]
- **Reuse of preexisting code.** The harness is by Shi et al. We did not change it. It has no stated licence, so we do not copy it into our repo.
- **AI tools.** The code, the draft text and the run orchestration used AI coding assistants (Claude and others). The author checked outputs by hand and is responsible for the report. [CHECK: the author edits this line to say exactly what is true.]
