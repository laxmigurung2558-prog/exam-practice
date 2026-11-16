"""Combine all builders' output into questions.json and verify it independently."""
import json, sqlite3, math, collections, sys

W = "/home/claude/work/"
BASE = "/home/claude/mat/"
parts = ["out_film.json", "out_etl.json", "out_ic.json", "out_sql1.json", "out_pcards.json"]
qs = [q for p in parts for q in json.load(open(W + p))]

datasets = {
    "film":       {"title": "NYC film permits", "files": ["NYC_Film_Permits.txt"], "subject": "Excel"},
    "etl1":       {"title": "Messy balance sheet (ETL case 1)", "files": ["Analytics_mindset_case_studies_ETL_Case1.csv"], "subject": "Excel"},
    "etl2":       {"title": "Employee codes (ETL case 2)", "files": ["Analytics_mindset_case_studies_ETL_Case2_Excel.xlsx"], "subject": "Excel"},
    "etl3":       {"title": "Messy employee codes (ETL case 3)", "files": ["Analytics_mindset_case_studies_ETL_Case3_Excel.xlsx"], "subject": "Excel"},
    "etl4":       {"title": "Journal entries (ETL case 4)", "files": ["Analytics_mindset_case_studies_ETL_Case4_Excel.xlsx"], "subject": "Excel"},
    "payroll":    {"title": "IntegrateCo payroll", "files": ["Analytics_mindset_case_studies_IntegrateCo_2015payroll.csv", "Analytics_mindset_case_studies_IntegrateCo_2016payroll.csv", "Analytics_mindset_case_studies_IntegrateCo_jobcodes.csv", "Analytics_mindset_case_studies_IntegrateCo_locations.csv"], "subject": "Excel"},
    "chinook":    {"title": "Chinook music store", "files": ["Chinook_Sqlite.sqlite"], "subject": "SQL", "browser_sql": True},
    "songs":      {"title": "CS50 songs", "files": ["songs.db"], "subject": "SQL", "browser_sql": True},
    "fiftyville": {"title": "Fiftyville mystery", "files": ["fiftyville.db"], "subject": "SQL", "browser_sql": True},
    "movies":     {"title": "CS50 movies", "files": [], "release_files": ["movies.db.zip"], "subject": "SQL", "browser_sql": False, "size_note": "69 MB unzipped — too large to run in the browser. Unzip, open in DB Browser for SQLite and enter your result. (It is also in your SQL Part 1 course folder.)"},
    "pcards":     {"title": "OSU purchasing cards", "files": ["pcards.db.zip"], "subject": "SQL", "browser_sql": False, "size_note": "94 MB unzipped — too large to run in the browser. Unzip, open in DB Browser for SQLite and enter your result."},
}
DB = {"chinook": "2__SQL_part_1/2. SQL part 1/Assignments/pwc assignment/Chinook_Sqlite.sqlite",
      "songs": "2__SQL_part_1/2. SQL part 1/Assignments/cs50 assignment/songs/songs.db",
      "movies": "2__SQL_part_1/2. SQL part 1/Assignments/cs50 assignment/movies/movies.db",
      "fiftyville": "2__SQL_part_1/2. SQL part 1/Assignments/cs50 assignment/mystery (OPTIONAL)/fiftyville.db",
      "pcards": "ace7146b-2._SQL_part_2/2. SQL part 2/Pcards Assignment/pcards.db"}

problems = []
ids = [q["id"] for q in qs]
dupe = [k for k, v in collections.Counter(ids).items() if v > 1]
if dupe: problems.append(f"duplicate ids {dupe}")

def close(a, b, tol):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= max(tol, 1e-9)
    return str(a).strip().lower() == str(b).strip().lower()

checked = 0
for q in qs:
    a = q["answer"]
    if q["dataset"] not in datasets: problems.append(f"{q['id']}: unknown dataset")
    if a["value"] is None or (isinstance(a["value"], float) and math.isnan(a["value"])):
        problems.append(f"{q['id']}: empty answer")
    for t in q["traps"]:
        if close(t["value"], a["value"], a["tolerance"]): problems.append(f"{q['id']}: trap equals answer")
        if not t["message"].strip(): problems.append(f"{q['id']}: empty trap message")
    # independent re-run of every stored SQL solution
    sql = q["solution"].get("sql")
    if sql and q["dataset"] in DB:
        con = sqlite3.connect(BASE + DB[q["dataset"]])
        res = con.execute(sql).fetchall()
        if str(a.get("label") or "").endswith("rows"):
            cands = [len(res)]                       # answer is a row count
        elif len(res) == 1 and len(res[0]) == 1:
            cands = [res[0][0]]                      # single value
        else:
            cands = list(res[0])                     # answer is a cell of the first row (e.g. name + count)
        if not any(close(c, a["value"], a["tolerance"]) for c in cands):
            problems.append(f"{q['id']}: stored SQL gives {cands!r}, answer is {a['value']!r}")
        exp = q.get("expected_result")
        if exp and [list(r) for r in res] != exp["rows"]:
            problems.append(f"{q['id']}: expected_result differs from SQL output")
        checked += 1

out = {"version": 1, "generated": "2026-11-16", "datasets": datasets, "questions": qs}
json.dump(out, open(W + "questions.json", "w"), indent=1, ensure_ascii=False)
by = collections.Counter((q["subject"], q["dataset"]) for q in qs)
print("questions:", len(qs), dict(by))
print("with traps:", sum(1 for q in qs if q["traps"]), " traps total:", sum(len(q["traps"]) for q in qs))
print("SQL solutions re-run:", checked)
print("PROBLEMS:", problems or "none")
