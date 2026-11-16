import json, random
from itertools import product
d = json.load(open("/home/claude/site/questions.json"))
qs = d["questions"]
by = {}
for q in qs:
    by.setdefault((q["subject"], q["dataset"]), []).append(q["id"])
rng = random.Random(2026)

# ---- Data Manipulation: 3 Excel questions (one dataset) + 2 SQL questions (one database)
excel = [k for k in by if k[0] == "Excel" and len(by[k]) >= 3]
sql = [k for k in by if k[0] == "SQL" and len(by[k]) >= 2 and k[1] != "fiftyville"]
pools = {s: [] for s in sql}
seen = set()
pairs = list(product(excel, sql))
n = 0
while sum(len(v) for v in pools.values()) < 60:
    e, s = pairs[n % len(pairs)]; n += 1
    pick = tuple(sorted(rng.sample(by[e], 3))) + tuple(sorted(rng.sample(by[s], 2)))
    if pick in seen: continue
    seen.add(pick)
    pools[s].append({"datasets": [e[1], s[1]], "questions": list(pick)})
for v in pools.values(): rng.shuffle(v)
manip, last_excel = [], None
order = [s for s in sql]
while any(pools.values()):                       # round-robin: never the same database twice in a row
    for s in order:
        if pools[s]:
            i = next((j for j, x in enumerate(pools[s]) if x["datasets"][0] != last_excel), 0)
            x = pools[s].pop(i); last_excel = x["datasets"][0]; manip.append(x)
for i, x in enumerate(manip):
    x.update({"id": f"X{i+1:02d}", "kind": "manipulation", "minutes": 8})

# ---- Data Interpretation: 4 regression questions, each a different skill
groups = [["RI01", "RI02", "RI03", "RI04"],            # prediction
          ["RI05", "RI06", "RI07", "RI08", "RI09"],    # temperature: slope, units, significance
          ["RI10", "RI11", "RI12"],                    # game-day dummy
          ["RI13", "RI14", "RI15", "RI16"]]            # interaction / fit
interp, seen = [], set()
while len(interp) < 12:
    pick = tuple(rng.choice(g) for g in groups)
    if pick in seen: continue
    seen.add(pick)
    interp.append({"id": f"R{len(interp)+1:02d}", "kind": "interpretation", "datasets": ["restaurant"], "questions": list(pick), "minutes": 8})

json.dump(manip + interp, open("/home/claude/site/exams.json", "w"), indent=1)
print(len(manip), "manipulation,", len(interp), "interpretation")
print([x["datasets"][1] for x in manip][:16])
from collections import Counter
print(Counter(q for x in interp for q in x["questions"]))
