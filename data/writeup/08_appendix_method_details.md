## Appendix B. Method details

### B.1 Payoffs
Expensive dish: joy 10, price 8. Cheap dish: joy 5, price 2. Payoff is joy minus one fifth of the table's total price.

| Agents ordering expensive | Expensive diner | Cheap diner |
|---|---|---|
| 0 | – | 3.0 |
| 1 | 6.8 | 1.8 |
| 2 | 5.6 | 0.6 |
| 3 | 4.4 | -0.6 |
| 4 | 3.2 | -1.8 |
| 5 | 2.0 | – |

### B.2 Calls and tokens
One game makes 75 calls (5 agents, 3 stages, 5 rounds). The wrapper skips the harness judge and reflection calls and asks again once when a reply has no action field. The 16 scored games made 1,201 calls in total, with 1,751,291 prompt tokens and 800,118 completion tokens. The one call above 1,200 was a length retry in run_028: the reasoning model's reply was empty and cut by length, so the wrapper asked again with twice the token limit. We ask for at least 8000 tokens per agent reply. The referee made 80 calls with 191,531 prompt tokens and 4,704 completion tokens; all 80 finished with reason "stop". [CHECK: cost in money is not computed.]

### B.3 Preexisting code and what is new
`vendor/LLM-Trust-Breaking/` is preexisting code by Shi et al. Source: https://github.com/Jerick-1380/LLM-Trust-Breaking, commit `fd11aca351e52c65c929e1a7d46d9f087f237adf`. It has no stated licence. We did not change it, and it is not committed to our repo. The repo scaffold, the first wrapper and one early example log (`run_001`) were made on 22 and 23 October, before the sprint start, and are also preexisting. New work from the sprint: the class instructions, the wrapper changes (DeepSeek routing, retries, time limits), the views and leak check, the referee prompt, client and runner, the baselines, the scoring, the label pack, the practice and scored runs, the labels and the results (`swarm_referee/`, `tests/`, `data/`).
