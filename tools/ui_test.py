"""Headless browser test of the site. The sql.js CDN is unreachable from this
sandbox, so the CDN script is replaced by a small shim whose Database.exec()
sends the query to Python's sqlite3 (same SQLite engine, same database files)."""
import json, sqlite3, threading, http.server, functools, sys, os
from playwright.sync_api import sync_playwright

SITE = "/home/claude/site"
OUT = "/home/claude/test/shots"
os.makedirs(OUT, exist_ok=True)

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8765), functools.partial(Quiet, directory=SITE))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = "http://127.0.0.1:8765/"

SHIM = """
window.initSqlJs = function(){ return Promise.resolve({ Database: function(bytes){
  this.exec = function(sql){
    var x = new XMLHttpRequest(); x.open('POST','/__sql',false);
    x.send(JSON.stringify({sql:sql, size:bytes.length})); var r = JSON.parse(x.responseText);
    if (r.error) throw new Error(r.error); return r.result; };
  this.close = function(){}; } }); };
"""
DBS = {1067008: f"{SITE}/data/Chinook_Sqlite.sqlite", 24576: f"{SITE}/data/songs.db", 270336: f"{SITE}/data/fiftyville.db"}

def sql_route(route, request):
    body = json.loads(request.post_data)
    try:
        con = sqlite3.connect(DBS[body["size"]])
        cur = con.execute(body["sql"])
        res = [{"columns": [c[0] for c in cur.description], "values": [list(r) for r in cur.fetchall()]}] if cur.description else []
        route.fulfill(status=200, body=json.dumps({"result": res}), content_type="application/json")
    except Exception as e:
        route.fulfill(status=200, body=json.dumps({"error": str(e)}), content_type="application/json")

results, errors = [], []
def ok(name, cond, extra=""):
    results.append((name, bool(cond), extra)); print(("PASS " if cond else "FAIL ") + name + (" | " + extra if extra else ""))

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.route("https://cdn.jsdelivr.net/**", lambda r: r.fulfill(status=200, body=SHIM, content_type="application/javascript"))
    pg.route("**/__sql", sql_route)

    pg.goto(BASE); pg.wait_for_selector("h1")
    ok("home loads", "Practise the exam" in pg.inner_text("h1"))
    ok("home stats", "115" in pg.inner_text("main") and "144" in pg.inner_text("main"))
    pg.screenshot(path=f"{OUT}/1_home.png", full_page=True)

    pg.goto(BASE + "#/exams"); pg.wait_for_selector(".exam-card")
    ok("60 exams listed", pg.locator(".exam-card").count() == 60)

    # exam X01: etl2 + pcards
    pg.goto(BASE + "#/exam/X01"); pg.wait_for_selector(".qpanel")
    ok("exam shows 2 dataset blocks", pg.locator(".downloads").count() == 2)
    pg.click("text=Start timer"); pg.wait_for_timeout(2200)
    clk = pg.inner_text(".clock"); ok("timer counts down", clk in ("7:58", "7:57", "7:59"), clk)
    ok("solution hidden before attempt", not pg.locator("text=Show model solution").is_visible())
    ok("stuck link visible before attempt", pg.locator("text=I'm stuck").is_visible())
    pg.fill("input[aria-label='Your answer']", "133"); pg.click("text=Check my answer")
    ok("E201 correct", "correct" in pg.inner_text(".feedback").lower())
    ok("sidebar dot turns green", pg.locator(".side .dot.correct").count() == 1)
    pg.goto(BASE + "#/exam/X01/2"); pg.wait_for_selector(".qpanel")
    pg.fill("input[aria-label='Your answer']", "24"); pg.click("text=Check my answer")
    ok("E202 plant without country -> known mistake", "known mistake" in pg.inner_text(".feedback").lower(), pg.inner_text(".feedback")[:120])
    ok("solution link appears after attempt", pg.locator("text=Show model solution").is_visible())
    ok("stuck link gone after attempt", not pg.locator("text=I'm stuck").is_visible())
    pg.click("text=Show model solution")
    ok("solution shows answer", "ARG-15" in pg.inner_text(".solution"))
    pg.screenshot(path=f"{OUT}/2_exam_trap.png", full_page=True)
    pg.goto(BASE + "#/report/X01"); pg.wait_for_selector(".kpi")
    ok("report counts 1 correct", "1 / 5" in pg.inner_text(".kpi"))
    ok("report lists the mistake", "PlantID without its country" in pg.inner_text("main"))
    pg.screenshot(path=f"{OUT}/3_report.png", full_page=True)

    # single questions with Danish formats and traps
    def answer(qid, text):
        pg.goto(BASE + "#/q/" + qid); pg.wait_for_selector(".qpanel")
        pg.fill("input[aria-label='Your answer']", text); pg.press("input[aria-label='Your answer']", "Enter")
        return pg.inner_text(".feedback").lower()
    f = answer("PC09", "2583,19"); ok("PC09 case-sensitive trap (Danish comma)", "case-sensitive" in f, f[:100])
    f = answer("PC09", "2.593,74"); ok("PC09 correct in Danish format", "correct" in f)
    f = answer("FP16", "163"); ok("FP16 Danish-date trap", "danish settings" in f)
    f = answer("FP12", "0,0784"); ok("FP12 share as decimal accepted", "correct" in f)
    f = answer("PC03", "157882,08"); ok("PC03 sign trap", "sign" in f.lower(), f[:90])
    f = answer("IC03", "300000"); ok("IC03 unknown wrong -> hint", "not yet" in f, f[:150])
    f = answer("FV01", "ernest"); ok("FV01 text, lower case", "correct" in f)
    f = answer("E104", "900"); ok("E104 unit trap", "thousand" in f)
    pg.screenshot(path=f"{OUT}/4_question_trap.png", full_page=True)

    # SQL runner (shim engine)
    def run(qid, sql):
        pg.goto(BASE + "#/q/" + qid); pg.wait_for_selector(".qpanel")
        pg.click("role=tab[name='Run SQL here']")
        pg.fill("textarea", sql); pg.click("text=▶ Run and check")
        pg.wait_for_function("document.querySelector('.feedback') && document.querySelector('.feedback').innerText.length > 0 || document.querySelector('.error')")
        return pg.inner_text(".qpanel").lower()
    t = run("CH08", "SELECT COUNT(*) FROM Invoice WHERE BillingCountry LIKE '%C%'"); ok("SQL trap diagnosed", "known mistake" in t)
    t = run("CH08", "SELECT COUNT(*) FROM Invoice WHERE BillingCountry LIKE 'C%'"); ok("SQL correct", "correct" in t)
    t = run("CH21", "SELECT c.FirstName, c.LastName, i.InvoiceId, i.Total FROM Invoice i JOIN Customer c ON c.CustomerId=i.CustomerId WHERE i.BillingCountry='United Kingdom'")
    ok("SQL multi-row correct + table shown", "correct" in t and pg.locator(".result tr").count() == 22)
    pg.screenshot(path=f"{OUT}/5_sql.png", full_page=True)
    t = run("SG02", "SELECT name FROM songs ORDER BY tempo"); ok("SQL wrong order hint", "sort order" in t)
    t = run("CH01", "SELEC nonsense"); ok("SQL error shown", pg.locator(".error").count() == 1)

    # bank filters + progress badges
    pg.goto(BASE + "#/questions"); pg.wait_for_selector(".qrow")
    ok("bank shows 115", pg.locator(".qrow").count() == 115)
    pg.select_option("select[aria-label='Dataset']", "pcards")
    ok("filter by dataset", pg.locator(".qrow").count() == 18)
    pg.select_option("select[aria-label='Dataset']", ""); pg.select_option("select[aria-label='Status']", "correct")
    ok("status filter uses saved progress", pg.locator(".qrow").count() >= 5, str(pg.locator(".qrow").count()))
    pg.goto(BASE + "#/how"); pg.wait_for_selector("h1"); ok("how page", "How checking works" in pg.inner_text("h1"))
    pg.screenshot(path=f"{OUT}/6_how.png", full_page=True)

    # mobile
    m = b.new_page(viewport={"width": 390, "height": 844})
    m.on("pageerror", lambda e: errors.append(str(e)))
    m.goto(BASE + "#/exam/X05/4"); m.wait_for_selector(".qpanel")
    sw = m.evaluate("document.documentElement.scrollWidth"); ok("no horizontal scroll on phone", sw <= 392, str(sw))
    m.screenshot(path=f"{OUT}/7_mobile.png", full_page=True)
    b.close()

srv.shutdown()
print("\nJS errors:", errors or "none")
print(f"{sum(r[1] for r in results)}/{len(results)} passed")
