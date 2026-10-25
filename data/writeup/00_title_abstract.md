# Swarm-Referee: Can One Fixed-Prompt Referee Find Planted Collusion in Multi-Agent Dinner Logs? [CHECK: exact title; it must be the same on any resubmission]

**Authors:** [CHECK: author name(s)] — [CHECK: affiliation(s)]

**Track:** Track 2, question 2.2 (Apart Research AI Collusion Research Sprint, 23–25 October 2026)

## Abstract

Does a monitor that reads both what agents say and what they do flag collusion more than a monitor that reads only one of them? We tested this on a pilot of 16 games of the Diners game (Shi et al.) with five LLM agents and five rounds. We planted collusion by instruction in 6 games: two agents received a pre-dinner pact to promise "cheap" and order "expensive". We built four decoy classes with the same payoffs: independent cheats, a table-wide cheap pact, collusive talk with no matching orders, and no instruction. One frozen referee (deepseek-v4-pro, one fixed prompt, temperature 0) read each game in five views, from messages only to a ledger with marks for stated-versus-actual orders. We compared it with two rule baselines. One author labelled all 16 games by hand, blind to run and class. The referee flagged the planted pair in 6 of 6 games on the ledger view (95% CI 54.1–100%). It also flagged 5 of 9 not-collusion games (56%), including collusive talk that was never acted on. Messages alone and actions alone flagged no game in 16. On the question of agreed pair versus independent cheats, the referee made 2 errors on the ledger view, and the view with lying marks flagged all 5 independent cheats. We read this as detecting lying, not agreement (pre-registered outcome 3). An earlier blind check coded the pair's messages as holding no agreement cue, which we state as a caveat. All collusion here is planted.

[CHECK: word count must stay between 150 and 250 — counted in checklist.md]
