import json
d = json.load(open("/home/claude/work/questions.json"))
fmt = lambda v: (f"{v:,.0f}" if float(v).is_integer() else f"{v:,.2f}" if abs(v) >= 1 else f"{v:.4g}") if isinstance(v, float) else (f"{v:,}" if isinstance(v, int) else str(v))
L = ["# Answer key with common mistakes",
     "",
     f"{len(d['questions'])} questions · {sum(len(q['traps']) for q in d['questions'])} diagnosed mistakes · every answer computed from the course data.",
     "",
     "Each wrong answer listed under a question is the exact number that the described mistake produces, so the website can tell students which trap they fell into.",
     "",
     "## Findings worth knowing",
     "",
     "- **Dates are US-formatted** (month/day/year) in the film-permit .txt and the 2015 payroll file. Imported on Danish settings, the average shoot is 163 hours instead of 17, lead time is 105 days instead of 5, the busiest start day becomes Friday instead of Thursday, and about 60% of dates silently stay as text.",
     "- **The PwC Chinook key's '49 albums'** counts album purchases. The number of *distinct* albums is 41, and every qualifying album has only one track.",
     "- **The PwC film-permit key** reproduces exactly (20/20).",
     "- **IntegrateCo:** the 2016 − 2015 gross-wage increase is $266,055.56 (Noah's 'about $266,000'). Job codes carry undocumented suffixes (R, SH) and one corrupt code (14S1440). 68 phantom 2016 rows total $32,951.29.",
     "- **P-cards:** the database is already filtered to OSU with no blank dates, so those case instructions don't change any answer. The real traps are text dates, negative returns, > vs ≥, and SQLite's case-sensitive '=' ('Amazon.com' ≠ 'AMAZON.COM'), whereas Access ignores case.",
     "- **Journal entries:** PreparerID is not unique (101 is five different people). The key is PreparerID + BusinessUnitID, and 148 lines have no valid preparer. Names are padded with CHAR(160), which TRIM does not remove.",
     "- **Restaurant regression:** sales, weather and game sheets merged by date; days when the restaurant was closed (sales 7 or 364 days earlier = 0) excluded, leaving 305 days. Temperature is significant alone (p = 0.011) but not once past sales are included (p = 0.18). The case's own forecast for 7 January 2019 is $2,910.33. Interpretation answers are computed from the coefficients as displayed.",
     "- **Tie:** Helena Bonham Carter's top-rated film is a tie (The King's Speech / Night Will Fall, both 8.0). Both are accepted.",
     ""]
cur = None
for q in d["questions"]:
    if q["case"] != cur:
        cur = q["case"]; L += [f"## {cur}", ""]
    a = q["answer"]
    ans = a.get("label") or fmt(a["value"])
    unit = f" {a['unit']}" if a.get("unit") and not a.get("label") else ""
    L += [f"### {q['id']} — {q['prompt']}", "", f"**Answer:** {ans}{unit}"]
    if q.get("alternatives"):
        L.append(f"*Also accepted:* {', '.join(q['alternatives'])}")
    if q.get("model"):
        m = q["model"]
        L += ["", f"*{m['title']}* (n = {m['n']}, R² = {m['r2']}): " + "; ".join(f"{c['label']} {c['estimate']} (p = {c['p']})" for c in m["coefficients"])]
    if q.get("explanation"):
        L.append(f"*Interpretation:* {q['explanation']}")
    if q.get("note"):
        L.append(f"*Note:* {q['note']}")
    sol = q["solution"]
    if "sql" in sol:
        L += ["", "```sql", sol["sql"], "```"]
    else:
        L += ["", f"*How:* {sol['excel']}"]
    if q["traps"]:
        L += ["", "| If the student gets… | Diagnosis |", "|---|---|"]
        for t in q["traps"]:
            L.append(f"| {fmt(t['value'])} | {t['message'].replace('|', '/')} |")
    L.append("")
open("/home/claude/work/ANSWER_KEY.md", "w").write("\n".join(L))
print(len(L), "lines")
