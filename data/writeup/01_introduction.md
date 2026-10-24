## 1. Introduction

Teams now run groups of AI agents that talk to each other and act together. If two agents agree to gain at the cost of the others, we want a monitor to see it. The monitor can read what the agents say, what they do, or both. Words and actions often disagree. In repeated games, more than 90% of deviations from public announcements were already stated in the agents' private plans (Shi et al., 2026) [CHECK: confirm the figure and the paper details against the paper; this figure is taken from the sprint page]. This suggests that the gap between words and actions is where collusion shows.

The sprint asks this as question 2.2 of Track 2: does combining what agents say with what they do beat either alone? The organisers also ask (question 2.3) for evidence that separates a deliberate coalition from parallel conduct, from talk that never changes behaviour, and from harm without agreement. In antitrust law, parallel conduct alone is not enough. Courts look for extra evidence, called plus factors (Berger et al., 2025) [CHECK: citation form].

**What we did.** We built a small, fully pre-registered pilot. We ran 16 games of one dinner game, in five run classes: one that plants collusion by instruction and four decoys. We gave one frozen referee model one fixed prompt and showed it each game in five views. We compared it with two baselines that use no language model. One author labelled every game by hand. We froze the class texts, the referee prompt, the model and the verdict rule before we opened any scored log.

**Claims.** All claims are about these 16 runs only. They show direction, not rates. We make no claim about monitors in general. Where a result is zero, we write that we found no evidence of detection in N runs, and we give the one-sided 95% upper bound.

**Contributions.**
1. A small design with one positive class and four decoy classes. Each decoy targets one weakness of one view (Section 2.3).
2. A fixed protocol: five views with a leak check, a frozen referee, two rule baselines, and a pre-registered rule for the novelty claim (Section 2).
3. Results with exact confidence intervals for every rate and exact McNemar tests (Section 3). The first results are for pair versus cooperation pact, and for talk only.
4. An honest account of what the evidence did not allow: our check for a message cue that separates agreed from independent cheating failed, so that question stays open (Section 3.6).

**Scope of the novelty claim.** The sprint literature measures lying (plan, announcement and action) and coalition advantage. We ask whether a monitor can tell agreement apart from independent lying when both harm the same victims. Our evidence gate (Section 2.6) found no cue in the public messages of the pair that the independent cheats lacked. So the pair-versus-independents question is unanswerable from these logs.

**Related work in brief.** Colosseum measures coalition advantage when agents can talk in private (Nakamura et al., 2026). The Diners harness we use records private plans, public announcements, actions and outcomes (Shi et al., 2026). Work on monitors finds that extra detail can lower a monitor's accuracy (Arike et al., 2026), and that analysing actions on several dimensions can lift a single-dimension monitor (Nguyen et al., 2026). Earlier collusion studies use market games with prices (Fish et al., 2024; Lin et al., 2024; Agrawal et al., 2025). We borrow from these and do not repeat them [CHECK: the author should read each paper and correct these one-line summaries; they come from the sprint page, not from a full reading].
