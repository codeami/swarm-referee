"""Stub check: build every request for each class with the wrapper hook; print what each agent gets added."""
import sys
sys.path.insert(0, "/Users/artsys/.treehouse/apart-research_Sprint1_Oct22_2026_Eval_Agents_Collusion-8f1c7e/1/apart-research_Sprint1_Oct22_2026_Eval_Agents_Collusion")
from swarm_referee import classes, run_diners

def stub(**kw):
    return kw

for cls in ["planted_pair", "independent_cheats", "cooperation_pact", "talk_only"]:
    build = run_diners.make_build_request(stub, "free/model", cls, {})
    print(f"== {cls}")
    for agent in classes.AGENT_NAMES:
        for rnd in range(classes.N_ROUNDS):
            for st in (1, 2, 3):
                out = build(custom_id=f"r{rnd}_t0_s{st}_{agent}", system_prompt="BASE", user_prompt="U")
                added = out["system_prompt"][len("BASE"):].strip()
                if rnd in (0, 4) or added and rnd == 0:
                    pass
                if rnd == 0 or rnd == 4:
                    print(f"{agent} r{rnd+1} s{st}: {added or '-'}")
