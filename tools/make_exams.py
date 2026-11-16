import json, random
d = json.load(open("/home/claude/site/questions.json"))
qs = [q for q in d["questions"]]
by = {}
for q in qs:
    by.setdefault((q["subject"], q["dataset"]), []).append(q["id"])
excel = [k for k in by if k[0] == "Excel" and len(by[k]) >= 3]
sql = [k for k in by if k[0] == "SQL" and len(by[k]) >= 2 and k[1] != "fiftyville"]
rng = random.Random(2026)
exams, seen = [], set()
pairs = [(e, s) for e in excel for s in sql]
n = 0
while len(exams) < 60:
    e, s = pairs[n % len(pairs)]; n += 1
    pick = tuple(sorted(rng.sample(by[e], 3))) + tuple(sorted(rng.sample(by[s], 2)))
    if pick in seen: continue
    seen.add(pick)
    exams.append({"id": f"X{len(exams)+1:02d}", "datasets": [e[1], s[1]], "questions": list(pick), "minutes": 8})
rng.shuffle(exams)
for i, x in enumerate(exams): x["id"] = f"X{i+1:02d}"
json.dump(exams, open("/home/claude/site/exams.json", "w"), indent=1)
print(len(exams), exams[0])
from collections import Counter; print(Counter(tuple(x["datasets"]) for x in exams).most_common(3))
