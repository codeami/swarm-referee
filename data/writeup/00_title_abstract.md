# Swarm-Referee: Can One Fixed-Prompt Referee Find Planted Collusion in Multi-Agent Dinner Logs?

**Authors:** Ashish Raina, Independent researcher

**Track:** Track 2, question 2.2 (Apart Research AI Collusion Research Sprint, 23–25 October 2026)

## Abstract

Does a monitor that reads both what agents say and what they do flag collusion more than a monitor that reads only one of them? We tested this in a pilot of 16 games of the Diners game (Shi et al.) with five LLM agents and five rounds. We planted collusion by instruction in 6 games: two agents received a pre-dinner pact to promise "cheap" and order "expensive". Four decoy classes used the same payoffs: independent cheats, a table-wide cheap pact, collusive talk with no matching orders, and no instruction. One frozen referee (deepseek-v4-pro, one fixed prompt, temperature 0) read each game in five views, from messages only to a ledger with marks for stated-versus-actual orders. Two rule baselines served as comparison. One author labelled all 16 games by hand. The referee flagged the planted pair in 6 of 6 games on the ledger view (95% CI 54.1–100%). It also flagged 5 of the 10 games the author labelled not collusion (50%). We found no evidence of detection from messages alone or from actions alone in 16 runs (one-sided 95% upper bound on recall 39.3%). Our evidence check found no message cue that separates an agreed pair from independent cheats, so the pair-versus-independents question is unanswerable from these logs. All collusion here is planted.
