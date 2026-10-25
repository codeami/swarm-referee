## 1. Introduction

Teams now run groups of AI agents that talk to each other and act together. If two agents agree to gain at the cost of the others, we want a monitor to see it. The monitor can read what the agents say, what they do, or both. Words and actions often disagree. In repeated games, deviations from public announcements were predominantly already stated in the agents' private plans, and above 90% in the highest-deception conditions (Shi et al., 2026) [CHECK: confirm the wording against the paper].

The sprint asks this as question 2.2 of Track 2 (Apart Research, 2026): does combining what agents say with what they do beat either alone? Question 2.3 asks for evidence that separates a deliberate coalition from parallel conduct, from talk that never changes behaviour, and from harm without agreement. In antitrust law, parallel conduct alone is not enough; courts look for extra evidence, called plus factors (Berger et al., 2025).

**What we did.** We ran a small pilot that was pre-specified in a plan and in freeze records (`STRATEGY.md`, `data/class_texts_freeze.txt`, `data/referee_freeze_DRAFT.md`). It has 16 games of one dinner game in five run classes: one that plants collusion by instruction, and four decoys. One frozen referee model read each game in five views with one fixed prompt. Two baselines use no language model. One author labelled every game by hand. We froze the class texts, the referee prompt, the model and the verdict rule before we opened any scored log.

**Claims.** All claims are about these 16 runs only. They show direction, not rates. We make no claim about monitors in general. Where a result is zero, we write that we found no evidence of detection in N runs, with the one-sided 95% upper bound.

**Contributions.**
1. A design with one positive class and four decoy classes. Each decoy targets one weakness of one view (Section 2.3).
2. A fixed protocol: five views with a leak check, a frozen referee, two rule baselines, and a pre-registered rule for the novelty claim (Section 2).
3. Results with exact intervals for every rate and exact McNemar tests (Section 3), led by pair versus cooperation pact, and talk only.
4. An account of what the evidence did not allow: our check for a message cue that separates agreed from independent cheating found none, so that question stays open (Section 3.6).

**Related work.** Colosseum measures coalition advantage when agents can talk in private (Nakamura et al., 2026). The Diners harness records private plans, public announcements, actions and outcomes (Shi et al., 2026). Work on monitors reports that extra detail can lower accuracy (Arike et al., 2026) and that monitoring several dimensions of an agent's actions can help (Nguyen et al., 2026). Earlier collusion studies use market games (Fish et al., 2024; Lin et al., 2024; Agrawal et al., 2025). [CHECK: the author should read each paper and correct these one-line summaries; they come from the sprint page, not from a full reading.]
