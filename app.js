/* Exam Practice · Data Analytics in Accounting
   Static single-page app: questions.json + exams.json, answer checking via checker.js,
   in-browser SQL for the small databases via sql.js (loaded on demand). */
(function () {
  "use strict";
  var app = document.getElementById("app");
  var D = null, EXAMS = [], QUEST = {}, DS = {};
  var SQLJS_BASE = "https://cdn.jsdelivr.net/npm/sql.js@1.10.3/dist/";

  // ---------------- progress (this browser only) ----------------
  var KEY = "exam-practice-progress-v1";
  var progress = {};
  try { progress = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { progress = {}; }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(progress)); } catch (e) { /* storage unavailable */ } }
  function record(id, status, trapMsg) {
    var p = progress[id] || { tries: 0 };
    p.tries += 1;
    if (p.status !== "correct") p.status = status;      // once correct, stays correct
    if (status === "trap") { p.traps = p.traps || []; if (p.traps.indexOf(trapMsg) < 0) p.traps.push(trapMsg); }
    progress[id] = p; save();
  }
  function statusOf(id) { return (progress[id] && progress[id].status) || "none"; }
  var KIND = {
    manipulation: { title: "Data Manipulation", subjects: ["Excel", "SQL"],
      examIntro: "Each exam has 3 Excel and 2 SQL questions on two data files, with an 8-minute timer like the real exam. Download and open the files before you start the timer.",
      bankIntro: "Every Excel and SQL question from the exams, organised by dataset. Practise them one at a time." },
    interpretation: { title: "Data Interpretation", subjects: ["Interpretation"],
      examIntro: "Each exam has 4 regression questions on the restaurant case (Excel Part 4): read the model output, make a prediction and interpret the results. The models were estimated on the real case data.",
      bankIntro: "Regression questions on the restaurant case: predictions, coefficients, units, dummies, interactions and significance." }
  };
  // short topic labels so interpretation exam cards can be told apart
  var SHORT = { RI01: "Forecast for 7 Jan 2019", RI02: "Prediction (game day)", RI03: "Prediction (no game)", RI04: "Prediction (game day)",
    RI05: "Temperature slope", RI06: "Units: °C vs °F", RI07: "Prediction in °C", RI08: "Significance (simple model)", RI09: "Significance (with controls)",
    RI10: "Game-day difference", RI11: "Game-day level", RI12: "Game day, controlling for past sales",
    RI13: "Interaction slope", RI14: "Interaction: game-day effect", RI15: "Interaction prediction", RI16: "R²" };
  function kindOf(q) { return q.subject === "Interpretation" ? "interpretation" : "manipulation"; }
  function subTabs(kind, active) {
    return h("div", { class: "tabs", style: "margin:0 0 20px" }, [
      h("a", { class: "btn" + (active === "exams" ? " current-tab" : ""), href: "#/" + kind + "/exams", "aria-current": active === "exams" ? "page" : null, text: KIND[kind].title + " exams" }),
      h("a", { class: "btn" + (active === "questions" ? " current-tab" : ""), href: "#/" + kind + "/questions", "aria-current": active === "questions" ? "page" : null, text: KIND[kind].title + " questions" })]);
  }
  var STATUS_LABEL = { correct: "Correct", trap: "Known mistake", wrong: "Not yet", none: "Not tried" };

  // ---------------- helpers ----------------
  function h(tag, attrs, kids) {
    var el = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      var v = attrs[k];
      if (v == null || v === false) return;
      if (k === "class") el.className = v;
      else if (k === "text") el.textContent = v;
      else if (k.slice(0, 2) === "on") el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v === true ? "" : v);
    });
    (kids || []).forEach(function (c) { if (c != null) el.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return el;
  }
  function fmt(v) {
    if (typeof v !== "number") return String(v);
    if (Number.isInteger(v)) return v.toLocaleString("en-US");
    return v.toLocaleString("en-US", { maximumFractionDigits: 3 });
  }
  function answerText(q) { return q.answer.label || (fmt(q.answer.value) + (q.answer.unit ? " " + q.answer.unit : "")); }
  function subjectPill(s) { return h("span", { class: "pill " + s.toLowerCase(), text: s }); }
  function setNav(name) {
    document.querySelectorAll("[data-nav]").forEach(function (a) { a.classList.toggle("active", a.getAttribute("data-nav") === name); });
  }
  function render(nodes, title) {
    app.innerHTML = "";
    nodes.forEach(function (n) { if (n) app.appendChild(n); });
    document.title = (title ? title + " · " : "") + "Exam Practice · Data Analytics in Accounting";
    app.focus({ preventScroll: true });
    window.scrollTo(0, 0);
  }
  function downloads(dsKey) {
    var ds = DS[dsKey];
    var box = h("div", { class: "downloads" });
    ds.files.forEach(function (f) { box.appendChild(h("a", { class: "btn", href: "data/" + encodeURIComponent(f), download: f, text: "⬇ " + f })); });
    // files too big for the repository are attached to a GitHub Release (tag "data") of this same repository
    (ds.release_files || []).forEach(function (f) {
      var m = location.hostname.match(/^([^.]+)\.github\.io$/), repo = location.pathname.split("/")[1];
      if (m && repo) box.appendChild(h("a", { class: "btn", href: "https://github.com/" + m[1] + "/" + repo + "/releases/download/data/" + encodeURIComponent(f), text: "⬇ " + f }));
    });
    var wrap = h("div", null, [h("div", null, [h("strong", { text: ds.title }), " ", subjectPill(ds.subject)]), box]);
    if (ds.size_note) wrap.appendChild(h("p", { class: "note", text: ds.size_note }));
    return wrap;
  }

  // ---------------- sql.js (in-browser SQLite) ----------------
  var sqlReady = null, dbBuffers = {};
  function loadSql() {
    if (sqlReady) return sqlReady;
    sqlReady = new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = SQLJS_BASE + "sql-wasm.js";
      s.onload = function () { window.initSqlJs({ locateFile: function (f) { return SQLJS_BASE + f; } }).then(resolve, reject); };
      s.onerror = function () { sqlReady = null; reject(new Error("Could not load the SQL engine (check your internet connection).")); };
      document.head.appendChild(s);
    });
    return sqlReady;
  }
  function loadDb(dsKey) {
    if (dbBuffers[dsKey]) return Promise.resolve(dbBuffers[dsKey]);
    var file = DS[dsKey].files[0];
    return fetch("data/" + encodeURIComponent(file)).then(function (r) {
      if (!r.ok) throw new Error("Could not load " + file);
      return r.arrayBuffer();
    }).then(function (b) { dbBuffers[dsKey] = new Uint8Array(b); return dbBuffers[dsKey]; });
  }
  // every run uses a fresh copy of the database, so a DELETE or UPDATE can't break later questions
  function runSql(dsKey, sql) {
    return Promise.all([loadSql(), loadDb(dsKey)]).then(function (x) {
      var SQL = x[0], db = new SQL.Database(x[1]);
      try {
        var res = db.exec(sql);
        if (!res.length) return { columns: [], rows: [] };
        var last = res[res.length - 1];
        return { columns: last.columns, rows: last.values };
      } finally { db.close(); }
    });
  }
  function table(columns, rows) {
    var max = 200;
    var t = h("table", null, [
      h("thead", null, [h("tr", null, columns.map(function (c) { return h("th", { scope: "col", text: c }); }))]),
      h("tbody", null, rows.slice(0, max).map(function (r) {
        return h("tr", null, r.map(function (v) { return h("td", { text: v == null ? "NULL" : String(v) }); }));
      }))
    ]);
    var wrap = h("div", null, [h("div", { class: "result" }, [t])]);
    wrap.appendChild(h("p", { class: "note", text: rows.length + " row(s)" + (rows.length > max ? " — showing the first " + max : "") }));
    return wrap;
  }

  // ---------------- question panel (used in exams and single questions) ----------------
  function questionPanel(q, onStatus) {
    var ds = DS[q.dataset];
    var fb = h("div", { class: "feedback", role: "status", "aria-live": "polite" });
    var solBox = h("div", { class: "solution", hidden: true });
    var revealBtn = h("button", { class: "link", type: "button", text: "Show model solution" });
    var attempted = progress[q.id] && progress[q.id].tries > 0;

    function showFeedback(res, viaSql) {
      fb.className = "feedback " + res.status;
      fb.innerHTML = "";
      if (res.status === "empty") { fb.appendChild(h("p", { text: res.message })); return; }
      var heads = { correct: ["Correct", "Well done" + (viaSql ? " — your query returns the right result." : ".")],
                    trap: ["Known mistake", "Your answer matches a common mistake:"],
                    wrong: ["Not yet", res.message] };
      fb.appendChild(h("span", { class: "tag", text: heads[res.status][0] }));
      fb.appendChild(h("p", { text: heads[res.status][1] }));
      if (res.status === "trap") fb.appendChild(h("p", null, [h("strong", { text: res.message })]));
      if (res.hints && res.hints.length) fb.appendChild(h("ul", null, res.hints.map(function (x) { return h("li", { text: x }); })));
      if (res.status === "correct" && q.note) fb.appendChild(h("p", { class: "note", text: "Note: " + q.note }));
      if (res.status !== "correct") fb.appendChild(h("p", { class: "note", text: "Try again, or open the model solution below." }));
      record(q.id, res.status, res.message);
      revealBtn.hidden = false;
      peek.hidden = true;
      if (onStatus) onStatus(statusOf(q.id));
    }

    // answer box
    var input = h("input", { type: "text", id: "ans-" + q.id, autocomplete: "off", spellcheck: "false",
      placeholder: q.answer.kind === "number" ? "e.g. 1,234.56 or 1.234,56" : (/^(yes|no)$/.test(q.answer.value) ? "yes or no" : "Type your answer"), "aria-label": "Your answer" });
    function doCheck() { showFeedback(Checker.checkAnswer(q, input.value)); }
    input.addEventListener("keydown", function (e) { if (e.key === "Enter") doCheck(); });
    var answerTab = h("div", null, [
      h("label", { for: "ans-" + q.id, class: "note", text: q.subject === "Interpretation" ? "Your answer, worked out from the model output:" : "Enter the result you got in " + (q.subject === "SQL" ? "your database tool" : "Excel") + ":" }),
      h("div", { class: "answer-row" }, [input, q.answer.unit ? h("span", { class: "unit", text: q.answer.unit }) : null,
        h("button", { class: "primary", type: "button", onclick: doCheck, text: "Check my answer" })])
    ]);

    // optional in-browser SQL
    var tabs = null, sqlTab = null;
    if (q.runnable_in_browser && ds.browser_sql) {
      var ta = h("textarea", { "aria-label": "SQL query", spellcheck: "false", placeholder: "SELECT …" });
      var out = h("div");
      var last = null;
      var runBtn = h("button", { class: "primary", type: "button", text: "▶ Run and check" });
      runBtn.addEventListener("click", function () {
        if (!ta.value.trim()) { showFeedback({ status: "empty", message: "Write a query first." }); return; }
        runBtn.disabled = true; out.innerHTML = ""; out.appendChild(h("p", { class: "note", text: "Running…" }));
        runSql(q.dataset, ta.value).then(function (r) {
          last = r; out.innerHTML = "";
          if (!r.columns.length) { out.appendChild(h("p", { class: "note", text: "The query ran but returned no table (only SELECT statements return rows)." })); return; }
          out.appendChild(table(r.columns, r.rows));
          showFeedback(Checker.checkResult(q, r.columns, r.rows), true);
        }).catch(function (e) {
          out.innerHTML = ""; out.appendChild(h("p", { class: "error", text: "SQL error: " + (e && e.message ? e.message : e) }));
        }).then(function () { runBtn.disabled = false; });
      });
      ta.addEventListener("keydown", function (e) { if ((e.ctrlKey || e.metaKey) && e.key === "Enter") runBtn.click(); });
      sqlTab = h("div", { class: "sql-area", hidden: true }, [
        h("p", { class: "note", text: "Runs on a fresh copy of " + ds.files[0] + " in your browser. Ctrl/⌘ + Enter runs the query." }),
        ta, h("div", { class: "sql-actions" }, [runBtn]), out]);
      var b1 = h("button", { type: "button", role: "tab", "aria-selected": "true", text: "Enter my answer" });
      var b2 = h("button", { type: "button", role: "tab", "aria-selected": "false", text: "Run SQL here" });
      function sel(which) {
        b1.setAttribute("aria-selected", String(which === 1)); b2.setAttribute("aria-selected", String(which === 2));
        answerTab.hidden = which !== 1; sqlTab.hidden = which !== 2;
      }
      b1.onclick = function () { sel(1); }; b2.onclick = function () { sel(2); ta.focus(); };
      tabs = h("div", { class: "tabs", role: "tablist" }, [b1, b2]);
    }

    // model solution: offered after an attempt (or on request, with a nudge)
    revealBtn.hidden = !attempted;
    revealBtn.addEventListener("click", function () {
      solBox.hidden = !solBox.hidden;
      revealBtn.textContent = solBox.hidden ? "Show model solution" : "Hide model solution";
    });
    var peek = h("button", { class: "link", type: "button", text: "I'm stuck — show the solution without trying" });
    peek.hidden = attempted;
    peek.addEventListener("click", function () {
      if (window.confirm("Practising works best if you commit to an answer first. Show the solution anyway?")) {
        peek.hidden = true; revealBtn.hidden = false; revealBtn.click();
      }
    });
    solBox.appendChild(h("h3", { text: "Answer: " + answerText(q) }));
    if (q.alternatives && q.alternatives.length) solBox.appendChild(h("p", { class: "note", text: "Also accepted: " + q.alternatives.join("; ") }));
    if (q.solution.sql) solBox.appendChild(h("pre", null, [h("code", { text: q.solution.sql })]));
    if (q.solution.excel) solBox.appendChild(h("p", null, [h("strong", { text: "How: " }), q.solution.excel]));
    if (q.explanation) solBox.appendChild(h("p", null, [h("strong", { text: "Interpretation: " }), q.explanation]));
    if (q.note) solBox.appendChild(h("p", { class: "note", text: "Note: " + q.note }));
    if (q.traps.length) {
      solBox.appendChild(h("p", { class: "note", text: "Common mistakes on this question:" }));
      solBox.appendChild(h("ul", { class: "note" }, q.traps.map(function (t) { return h("li", { text: t.message }); })));
    }

    var modelBox = null;
    if (q.model) {
      var m = q.model;
      modelBox = h("figure", { class: "model" }, [
        h("figcaption", null, [h("strong", { text: m.title }), h("span", { class: "note", text: " · Outcome: " + m.outcome + " · n = " + m.n + " · R² = " + m.r2 })]),
        h("div", { class: "result" }, [h("table", null, [
          h("thead", null, [h("tr", null, ["Term", "Estimate", "Std. error", "p-value"].map(function (c) { return h("th", { scope: "col", text: c }); }))]),
          h("tbody", null, m.coefficients.map(function (c) {
            return h("tr", null, [h("td", { text: c.label }), h("td", { class: "num", text: String(c.estimate) }), h("td", { class: "num", text: String(c.se) }), h("td", { class: "num", text: c.p < 0.001 ? "< 0.001" : c.p.toFixed(3) })]);
          }))])])]);
    }
    return h("section", { class: "card qpanel", "aria-labelledby": "qt-" + q.id }, [
      h("div", { class: "qmeta" }, [subjectPill(q.subject), h("span", { text: q.id + " · " + q.case })]),
      modelBox,
      h("h2", { id: "qt-" + q.id, text: q.prompt }),
      tabs, answerTab, sqlTab, fb,
      h("div", { class: "sql-actions" }, [revealBtn, peek]), solBox
    ]);
  }

  // ---------------- views ----------------
  function viewHome() {
    setNav("");
    var nTraps = D.questions.reduce(function (s, q) { return s + q.traps.length; }, 0);
    var done = D.questions.filter(function (q) { return statusOf(q.id) === "correct"; }).length;
    function count(kind, what) {
      return what === "q" ? D.questions.filter(function (q) { return kindOf(q) === kind; }).length : EXAMS.filter(function (x) { return x.kind === kind; }).length;
    }
    function part(kind, text) {
      return h("section", { class: "card part" }, [
        h("h2", { text: KIND[kind].title }), h("p", { text: text }),
        h("div", { class: "hero-actions" }, [
          h("a", { class: "btn primary", href: "#/" + kind + "/exams", text: KIND[kind].title + " Exams (" + count(kind, "x") + ")" }),
          h("a", { class: "btn", href: "#/" + kind + "/questions", text: KIND[kind].title + " Questions (" + count(kind, "q") + ")" })])]);
    }
    render([
      h("h1", { text: "Oral exam practice — and find out if you're actually right" }),
      h("p", { class: "lead", text: "The oral exam has a full data manipulation exam and a full data interpretation exam. Practise both here. Type the result you get and the site tells you instantly whether it's correct — and if it isn't, which common mistake you probably made." }),
      h("div", { class: "parts" }, [
        part("manipulation", "Excel and SQL tasks on the course cases: film permits, ETL, IntegrateCo payroll, Chinook, CS50 and OSU purchasing cards. Practise complete exams (3 Excel + 2 SQL, 8 minutes) or single questions."),
        part("interpretation", "Regression on the restaurant case: read the model output, make predictions, and interpret coefficients, dummies, interactions and p-values.")]),
      h("div", { class: "grid", style: "margin-top:22px" }, [
        h("div", { class: "card" }, [h("div", { class: "stat", text: String(D.questions.length) }), h("div", { text: "questions with verified answers" })]),
        h("div", { class: "card" }, [h("div", { class: "stat", text: String(nTraps) }), h("div", { text: "common mistakes the checker recognises" })]),
        h("div", { class: "card" }, [h("div", { class: "stat", text: done + " / " + D.questions.length }), h("div", { text: "answered correctly in this browser" })])
      ]),
      h("h2", { text: "What makes this different" }),
      h("div", { class: "card feature" }, [
        h("p", null, ["Practising alone, you can't tell whether your number is right. Here every answer is checked against the result computed from the actual data files. Wrong answers are compared with ", h("strong", { text: "the wrong numbers that typical mistakes produce" }), " — dates imported with Danish settings, returns stored as negative numbers, a lookup on a key that isn't unique, Celsius plugged into a Fahrenheit model — so you learn ", h("em", { text: "why" }), " you were wrong."]),
        h("a", { href: "#/how", text: "How checking works →" })
      ])
    ], "Home");
  }

  function viewExams(kind) {
    setNav(kind);
    var list = EXAMS.filter(function (x) { return x.kind === kind; });
    render([
      h("h1", { text: KIND[kind].title }),
      subTabs(kind, "exams"),
      h("p", { class: "lead", text: KIND[kind].examIntro }),
      h("div", { class: "hero-actions" }, [h("a", { class: "btn primary", href: "#/exam/" + list[Math.floor(Math.random() * list.length)].id, text: "Choose one for me" })]),
      h("div", { class: "grid" }, list.map(function (x) {
        var done = x.questions.filter(function (id) { return statusOf(id) === "correct"; }).length;
        return h("a", { class: "card exam-card btn", href: "#/exam/" + x.id }, [
          h("span", { class: "id", text: x.id }),
          h("strong", { text: x.datasets.map(function (k) { return DS[k].title; }).join(" + ") }),
          kind === "interpretation" ? h("span", { class: "topics", text: x.questions.map(function (id) { return SHORT[id] || id; }).join(" · ") }) : null,
          h("span", { class: "meta", text: x.questions.length + " questions · " + x.minutes + " min · " + done + "/" + x.questions.length + " correct" })]);
      }))
    ], KIND[kind].title + " exams");
  }

  var timer = { id: null, left: 0, running: false, examId: null };
  function viewExam(id, idx) {
    var x = EXAMS.filter(function (e) { return e.id === id; })[0];
    if (!x) return viewNotFound();
    setNav(x.kind);
    var lastIdx = x.questions.length - 1;
    idx = Math.max(0, Math.min(lastIdx, idx || 0));
    if (timer.examId !== id) { clearInterval(timer.id); timer = { id: null, left: x.minutes * 60, running: false, examId: id }; }
    var clock = h("span", { class: "clock", "aria-live": "off" });
    var timeMsg = h("span", { class: "note", role: "status", "aria-live": "polite" });
    function draw() {
      var s = Math.abs(timer.left), t = Math.floor(s / 60) + ":" + ("0" + (s % 60)).slice(-2);
      clock.textContent = (timer.left < 0 ? "+" : "") + t;
      clock.classList.toggle("over", timer.left < 0);
    }
    var startBtn = h("button", { class: "primary", type: "button" });
    function label() { startBtn.textContent = timer.running ? "Pause" : (timer.left === x.minutes * 60 ? "Start timer" : "Resume"); }
    startBtn.onclick = function () {
      if (timer.running) { clearInterval(timer.id); timer.running = false; }
      else {
        timer.running = true;
        timer.id = setInterval(function () {
          timer.left -= 1; draw();
          if (timer.left === 0) timeMsg.textContent = "Time is up. You can keep going to finish, but in the exam you'd stop here.";
        }, 1000);
      }
      label();
    };
    var resetBtn = h("button", { type: "button", text: "Reset", onclick: function () {
      clearInterval(timer.id); timer.running = false; timer.left = x.minutes * 60; timeMsg.textContent = ""; draw(); label(); } });
    draw(); label();

    var side = h("nav", { class: "side", "aria-label": "Exam questions" });
    x.questions.forEach(function (qid, i) {
      var q = QUEST[qid];
      side.appendChild(h("button", { type: "button", class: i === idx ? "current" : "", "aria-current": i === idx ? "step" : null,
        onclick: function () { location.hash = "#/exam/" + id + "/" + (i + 1); } },
        [h("span", { text: (i + 1) + ". " + (q.subject === "Interpretation" ? "" : q.subject + " · ") + q.id }), h("span", { class: "dot " + statusOf(qid), title: STATUS_LABEL[statusOf(qid)] })]));
    });
    side.appendChild(h("a", { class: "btn", href: "#/report/" + id, text: "Finish → report" }));

    var q = QUEST[x.questions[idx]];
    var panel = questionPanel(q, function () {
      var dots = side.querySelectorAll(".dot");
      x.questions.forEach(function (qid, i) { dots[i].className = "dot " + statusOf(qid); });
    });
    var nav = h("div", { class: "qnav" }, [
      idx > 0 ? h("a", { class: "btn", href: "#/exam/" + id + "/" + idx, text: "← Previous" }) : h("span"),
      idx < lastIdx ? h("a", { class: "btn", href: "#/exam/" + id + "/" + (idx + 2), text: "Next →" }) : h("a", { class: "btn primary", href: "#/report/" + id, text: "Finish → report" })
    ]);
    render([
      h("p", null, [h("a", { href: "#/" + x.kind + "/exams", text: "← All " + KIND[x.kind].title.toLowerCase() + " exams" })]),
      h("div", { class: "exam-head" }, [
        h("div", null, [h("h1", { text: KIND[x.kind].title + " exam " + x.id })].concat(x.datasets.map(function (k, i) { return h("div", { style: i ? "margin-top:8px" : null }, [downloads(k)]); }))),
        h("div", { class: "card timer" }, [h("div", null, [h("div", { class: "note", text: "Time remaining" }), clock]), startBtn, resetBtn, timeMsg])
      ]),
      h("div", { class: "exam-body" }, [side, h("div", null, [panel, nav])])
    ], "Exam " + x.id);
  }

  function viewReport(id) {
    var x = EXAMS.filter(function (e) { return e.id === id; })[0];
    if (!x) return viewNotFound();
    setNav(x.kind);
    clearInterval(timer.id); timer.running = false;
    var qs = x.questions.map(function (qid) { return QUEST[qid]; });
    var correct = qs.filter(function (q) { return statusOf(q.id) === "correct"; }).length;
    var traps = [];
    qs.forEach(function (q) { ((progress[q.id] || {}).traps || []).forEach(function (t) { traps.push({ q: q, t: t }); }); });
    render([
      h("p", null, [h("a", { href: "#/exam/" + id, text: "← Back to exam " + id })]),
      h("h1", { text: "Exam " + id + " — report" }),
      h("div", { class: "kpi" }, [
        h("div", { class: "card" }, [h("div", { class: "stat", text: correct + " / " + qs.length }), h("div", { text: "correct" })]),
        h("div", { class: "card" }, [h("div", { class: "stat", text: String(traps.length) }), h("div", { text: "known mistakes made" })]),
        h("div", { class: "card" }, [h("div", { class: "stat", text: timer.examId === id ? (Math.floor((x.minutes * 60 - timer.left) / 60) + " min") : "—" }), h("div", { text: "time used" })])
      ]),
      h("div", { class: "qlist" }, qs.map(function (q, i) {
        return h("a", { class: "qrow btn", href: "#/exam/" + id + "/" + (i + 1) }, [
          h("span", { class: "id", text: q.id }), h("span", null, [q.prompt]), h("span", { class: "status " + statusOf(q.id), text: STATUS_LABEL[statusOf(q.id)] })]);
      })),
      traps.length ? h("h2", { text: "Mistakes to remember for the oral exam" }) : null,
      traps.length ? h("ul", { class: "report" }, traps.map(function (x) { return h("li", null, [h("strong", { text: x.q.id + ": " }), x.t]); })) : null
    ], "Report " + id);
  }

  var bankState = {};
  function viewQuestions(kind) {
    setNav(kind);
    var st = bankState[kind] || (bankState[kind] = { subject: "", dataset: "", status: "", text: "" });
    var list = h("div", { class: "qlist" });
    var count = h("p", { class: "note", role: "status", "aria-live": "polite" });
    function draw() {
      var t = st.text.toLowerCase();
      var qs = D.questions.filter(function (q) {
        return kindOf(q) === kind && (!st.subject || q.subject === st.subject) && (!st.dataset || q.dataset === st.dataset) &&
          (!st.status || statusOf(q.id) === st.status) && (!t || (q.id + " " + q.prompt + " " + q.topics.join(" ")).toLowerCase().indexOf(t) >= 0);
      });
      count.textContent = qs.length + " question(s)";
      list.innerHTML = "";
      qs.forEach(function (q) {
        list.appendChild(h("a", { class: "qrow btn", href: "#/q/" + q.id }, [
          h("span", { class: "id", text: q.id }),
          h("span", null, [q.prompt, h("span", { class: "sub", text: q.case + (q.runnable_in_browser ? " · runs in browser" : "") })]),
          h("span", { class: "status " + statusOf(q.id), text: STATUS_LABEL[statusOf(q.id)] })]));
      });
    }
    function selectBox(lbl, key, opts) {
      var s = h("select", { "aria-label": lbl }, [h("option", { value: "", text: "All" })].concat(opts.map(function (o) { return h("option", { value: o[0], text: o[1] }); })));
      s.value = st[key];
      s.onchange = function () { st[key] = s.value; draw(); };
      return h("label", null, [lbl, s]);
    }
    var search = h("input", { type: "search", placeholder: "e.g. returns, join, dates", value: st.text, "aria-label": "Search questions" });
    search.oninput = function () { st.text = search.value; draw(); };
    var dsKeys = Object.keys(DS).filter(function (k) { return KIND[kind].subjects.indexOf(DS[k].subject) >= 0; });
    render([
      h("h1", { text: KIND[kind].title }),
      subTabs(kind, "questions"),
      h("p", { class: "lead", text: KIND[kind].bankIntro }),
      h("div", { class: "filters" }, [
        kind === "manipulation" ? selectBox("Subject", "subject", [["Excel", "Excel"], ["SQL", "SQL"]]) : null,
        dsKeys.length > 1 ? selectBox("Dataset", "dataset", dsKeys.map(function (k) { return [k, DS[k].title]; })) : null,
        selectBox("Status", "status", [["none", "Not tried"], ["wrong", "Not yet"], ["trap", "Known mistake"], ["correct", "Correct"]]),
        h("label", null, ["Search", search])]),
      count, list
    ], KIND[kind].title + " questions");
    draw();
  }

  function viewQuestion(id) {
    var q = QUEST[id];
    if (!q) return viewNotFound();
    setNav(kindOf(q));
    var same = D.questions.filter(function (x) { return x.dataset === q.dataset; });
    var i = same.indexOf(q);
    render([
      h("p", null, [h("a", { href: "#/" + kindOf(q) + "/questions", text: "← " + KIND[kindOf(q)].title + " questions" })]),
      h("div", { class: "card", style: "margin-bottom:16px" }, [downloads(q.dataset)]),
      questionPanel(q),
      h("div", { class: "qnav" }, [
        i > 0 ? h("a", { class: "btn", href: "#/q/" + same[i - 1].id, text: "← " + same[i - 1].id }) : h("span"),
        i < same.length - 1 ? h("a", { class: "btn", href: "#/q/" + same[i + 1].id, text: same[i + 1].id + " →" }) : h("span")])
    ], q.id);
  }

  function viewHow() {
    setNav("how");
    var byDs = {};
    D.questions.forEach(function (q) { byDs[q.dataset] = (byDs[q.dataset] || 0) + q.traps.length; });
    var ex = QUEST["FP16"];
    render([
      h("h1", { text: "How checking works" }),
      h("p", { class: "lead", text: "The checker compares your answer with the correct result computed from the course data — and with the results that typical mistakes produce." }),
      h("div", { class: "grid" }, [
        h("div", { class: "card" }, [h("h3", { text: "1. Correct?" }), h("p", { text: "Every answer was calculated from the actual data files and re-checked. Numbers can be typed the Danish or the English way (1.234,56 or 1,234.56), with or without %, $ or a minus in parentheses." })]),
        h("div", { class: "card" }, [h("h3", { text: "2. Which mistake?" }), h("p", { text: "For most questions we computed the exact wrong number that each common mistake produces. If your answer matches one, you're told what went wrong." })]),
        h("div", { class: "card" }, [h("h3", { text: "3. Otherwise: a hint" }), h("p", { text: "Unknown wrong answers get a targeted hint: wrong sign, off by a factor of 100 or 1,000, days vs hours, too many rows from a join…" })])
      ]),
      ex ? h("h2", { text: "Example: " + ex.prompt }) : null,
      ex ? h("div", { class: "card" }, [
        h("p", null, ["Correct answer: ", h("strong", { text: answerText(ex) })]),
        h("ul", null, ex.traps.map(function (t) { return h("li", null, [h("strong", { text: fmt(t.value) + " → " }), t.message]); }))
      ]) : null,
      h("h2", { text: "Data interpretation" }),
      h("p", { text: "The regression models were estimated on the restaurant case data (sales, weather and game sheets merged by date; days when the restaurant was closed excluded). Answers are computed from the coefficients exactly as displayed, so working from the table gives the stored answer. Mistakes recognised include leaving out the intercept, reading a dummy as a level instead of a difference, ignoring an interaction term, and plugging Celsius into a Fahrenheit model." }),
      h("h2", { text: "SQL in the browser" }),
      h("p", { text: "For the smaller databases (Chinook, songs, Fiftyville) you can also paste your query and run it here. Your result is compared with the expected result — same rows, and the same order when the question asks for one. The P-card (94 MB) and movies (69 MB) databases are too large for a browser: run those in DB Browser for SQLite and enter your result." }),
      h("h2", { text: "Mistakes recognised, by dataset" }),
      h("ul", null, Object.keys(byDs).map(function (k) { return h("li", { text: DS[k].title + ": " + byDs[k] }); }))
    ], "How checking works");
  }

  function viewNotFound() { render([h("h1", { text: "Not found" }), h("p", null, [h("a", { href: "#/", text: "Go to the start page" })])], "Not found"); }

  // ---------------- router ----------------
  function route() {
    var parts = (location.hash || "#/").replace(/^#\/?/, "").split("/");
    switch (parts[0]) {
      case "": return viewHome();
      case "manipulation":
      case "interpretation":
        return parts[1] === "questions" ? viewQuestions(parts[0]) : viewExams(parts[0]);
      case "exams": return viewExams("manipulation");
      case "exam": return viewExam(parts[1], parseInt(parts[2] || "1", 10) - 1);
      case "report": return viewReport(parts[1]);
      case "questions": return viewQuestions("manipulation");
      case "q": return viewQuestion(parts[1]);
      case "how": return viewHow();
      default: return viewNotFound();
    }
  }

  Promise.all([fetch("questions.json").then(function (r) { return r.json(); }), fetch("exams.json").then(function (r) { return r.json(); })])
    .then(function (x) {
      D = x[0]; EXAMS = x[1]; DS = D.datasets;
      D.questions.forEach(function (q) { QUEST[q.id] = q; });
      window.addEventListener("hashchange", route);
      route();
    })
    .catch(function () {
      app.innerHTML = "";
      app.appendChild(h("p", { class: "error", text: "Could not load the question files. If you opened index.html directly from your disk, use the published GitHub Pages link instead (browsers block loading files from disk)." }));
    });
})();
