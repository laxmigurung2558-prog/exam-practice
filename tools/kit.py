"""Shared helpers for building the answer key.

Every question is computed from the real data:
  answer  -> the correct query/calculation
  traps   -> queries that reproduce a typical mistake; their result is stored
             together with the explanation shown to the student.
A trap is only kept if it gives a DIFFERENT value from the correct answer,
otherwise it could never be diagnosed and would only confuse.
"""
import sqlite3, json, math

def scalar(con, sql):
    r = con.execute(sql).fetchall()
    return r[0][0] if len(r) == 1 and len(r[0]) == 1 else r

def rows(con, sql, limit=None):
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    data = cur.fetchall()
    return cols, (data if limit is None else data[:limit])

def norm(v):
    if isinstance(v, float):
        return round(v, 6)
    return v

def same(a, b, tol):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= tol
    return str(a).strip().lower() == str(b).strip().lower()

def make(qid, dataset, subject, case, prompt, answer, solution, traps=(),
         tol=0.01, unit=None, answer_label=None, topics=(), extra=None,
         answer_kind=None):
    """answer: computed value (number or text). traps: list of (value, message)."""
    kind = answer_kind or ("number" if isinstance(answer, (int, float)) else "text")
    kept = []
    for val, msg in traps:
        if val is None:
            continue
        if isinstance(val, float) and math.isnan(val):
            continue
        if same(val, answer, tol):
            print(f"   [dropped trap for {qid}: same as answer] {msg[:60]}")
            continue
        dup = next((k for k in kept if same(val, k["value"], tol)), None)
        if dup:  # two mistakes give the same number: show both explanations
            dup["message"] += " Another way to get this number: " + msg
            continue
        kept.append({"value": norm(val), "message": msg})
    q = {
        "id": qid, "dataset": dataset, "subject": subject, "case": case,
        "prompt": prompt, "topics": list(topics),
        "answer": {"kind": kind, "value": norm(answer), "tolerance": tol,
                   "unit": unit, "label": answer_label},
        "solution": solution, "traps": kept,
    }
    if extra:
        q.update(extra)
    print(f"{qid}: {answer!r}  traps={[t['value'] for t in kept]}")
    return q
