/* Answer checker: decides whether a student's answer is correct and, if not,
   whether it matches a known mistake ("trap") recorded in questions.json.
   Pure functions, no DOM, so it can be tested in Node as well as used in the browser. */
(function (root) {
  "use strict";

  // ---------- numbers ----------
  // Students type numbers in many ways: 1,507,686.68 / 1.507.686,68 / 35,11 / $2,593.74 / (15600000000) / 7.84%.
  // Ambiguous inputs (e.g. "1.187" or "1,187") yield several candidate values; any match counts.
  function parseNumberCandidates(raw) {
    if (raw == null) return [];
    var s = String(raw).trim();
    if (!s) return [];
    var percent = /%/.test(s);
    s = s.replace(/[−–]/g, "-");
    var m = s.match(/\d[\d.,\s']*\d|\d/);
    if (!m) return [];
    var before = s.slice(0, m.index), after = s.slice(m.index + m[0].length);
    var neg = /-/.test(before)                                   // -5, $-5, kr -5
      || (/\(/.test(before) && /\)/.test(after))                  // (5) accounting notation
      || /^\s*-\s*$/.test(after.replace(/[a-z%$€]/gi, ""));       // 5- (trailing minus)
    var t = m[0].replace(/[\s']/g, "");
    var out = [];
    var hasDot = t.indexOf(".") >= 0, hasComma = t.indexOf(",") >= 0;
    if (hasDot && hasComma) {
      var decimal = t.lastIndexOf(".") > t.lastIndexOf(",") ? "." : ",";
      var thousands = decimal === "." ? "," : ".";
      out.push(Number(t.split(thousands).join("").replace(decimal, ".")));
    } else if (hasComma || hasDot) {
      var sep = hasComma ? "," : ".";
      var parts = t.split(sep);
      if (parts.length > 2) {
        out.push(Number(parts.join("")));                    // 1.234.567 or 1,234,567
      } else {
        out.push(Number(parts[0] + "." + parts[1]));         // decimal separator
        if (parts[1].length === 3 && parts[0] !== "0") out.push(Number(parts.join(""))); // or thousands
      }
    } else {
      out.push(Number(t));
    }
    out = out.filter(function (v) { return isFinite(v); }).map(function (v) { return neg ? -v : v; });
    return out.map(function (v) { return { value: v, percent: percent }; });
  }

  function numClose(a, b, tol) {
    var t = Math.max(Number(tol) || 0, 1e-9);
    return Math.abs(a - b) <= t + 1e-9 * Math.max(1, Math.abs(b));
  }

  // ---------- text ----------
  function normText(s) {
    return String(s == null ? "" : s).toLowerCase()
      .replace(/[‘’‛`´]/g, "'").replace(/[“”]/g, '"')
      .replace(/\s+/g, " ").replace(/^[\s"']+|[\s"'.]+$/g, "").trim();
  }
  function looksLikeDate(v) { return /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(String(v)); }
  // Accept many date-time spellings for date answers: 2011-12-07 16:38, 12/7/2011 16:38 (US), 07-12-2011 16:38 / 7.12.2011 (DK)
  function dateCandidates(raw) {
    var s = String(raw).trim(), out = [];
    var time = (s.match(/(\d{1,2})[:.](\d{2})(?!.*\d{1,2}[:.]\d{2})/) || []);
    var hh = time[1] ? ("0" + time[1]).slice(-2) : null, mm = time[2] || null;
    var iso = s.match(/(\d{4})-(\d{1,2})-(\d{1,2})/);
    var pad = function (x) { return ("0" + x).slice(-2); };
    var mk = function (y, mo, d) { return y + "-" + pad(mo) + "-" + pad(d) + (hh ? " " + hh + ":" + mm : ""); };
    if (iso) out.push(mk(iso[1], iso[2], iso[3]));
    var us = s.match(/(\d{1,2})\/(\d{1,2})\/(\d{4})/);
    if (us) out.push(mk(us[3], us[1], us[2]));
    var dk = s.match(/(\d{1,2})[-.](\d{1,2})[-.](\d{4})/);
    if (dk) out.push(mk(dk[3], dk[2], dk[1]));
    var months = ["january","february","march","april","may","june","july","august","september","october","november","december"];
    var named = s.toLowerCase().match(/(\d{1,2})\.?\s+([a-z]+)\s+(\d{4})/);
    if (named && months.indexOf(named[2]) >= 0) out.push(mk(named[3], months.indexOf(named[2]) + 1, named[1]));
    return out;
  }

  // ---------- main entry ----------
  // returns {status: "correct" | "trap" | "wrong" | "empty", message, hints[]}
  function checkAnswer(q, raw) {
    if (raw == null || String(raw).trim() === "") return { status: "empty", message: "Type your answer first." };
    var a = q.answer;
    if (a.kind === "number") return checkNumber(q, raw);
    return checkText(q, raw);
  }

  function valuesFor(q, cands) {
    // percent questions: accept 7.84, 7.84% and 0.0784
    var vals = [];
    cands.forEach(function (c) {
      vals.push(c.value);
      if (q.answer.unit === "%" && !c.percent) vals.push(c.value * 100);
    });
    return vals;
  }

  function checkNumber(q, raw) {
    var cands = parseNumberCandidates(raw);
    if (!cands.length) return { status: "wrong", message: "That doesn't look like a number. This question needs a numeric answer" + (q.answer.unit ? " (in " + q.answer.unit + ")." : ".") };
    var vals = valuesFor(q, cands), a = q.answer, tol = a.tolerance;
    if (vals.some(function (v) { return numClose(v, a.value, tol); })) return { status: "correct" };
    for (var i = 0; i < q.traps.length; i++) {
      var tv = q.traps[i].value;
      if (typeof tv === "number" && vals.some(function (v) { return numClose(v, tv, tol); }))
        return { status: "trap", message: q.traps[i].message };
    }
    return { status: "wrong", message: "Not correct, and it doesn't match a mistake we know about.", hints: genericNumberHints(vals[0], a) };
  }

  function genericNumberHints(v, a) {
    var h = [], x = a.value;
    if (typeof v !== "number" || !isFinite(v)) return h;
    if (x !== 0 && numClose(v, -x, Math.abs(x) * 0.0001 + a.tolerance)) h.push("You have the right size but the wrong sign. Check how returns, credits or differences are signed in this data.");
    var ratio = x !== 0 ? v / x : 0;
    [[100, "a factor of 100 — percent vs. decimal?"], [1000, "a factor of 1,000 — thousands vs. units?"], [1e6, "a factor of 1,000,000 — millions vs. units?"], [24, "a factor of 24 — days vs. hours?"], [60, "a factor of 60 — hours vs. minutes?"]]
      .forEach(function (p) {
        if (ratio && (Math.abs(ratio / p[0] - 1) < 0.01 || Math.abs(ratio * p[0] - 1) < 0.01)) h.push("Your number is off by " + p[1]);
      });
    if (!h.length && x !== 0 && Math.abs(ratio - 1) < 0.05) h.push("You're close (within 5%). Usually this means a filter is slightly off: check > vs >=, the date range, or whether returns/blanks are included.");
    if (!h.length) h.push("Re-read the question: which rows are in scope (year, filter), which column is summed or counted, and is anything double-counted?");
    return h;
  }

  function checkText(q, raw) {
    var a = q.answer;
    var targets = [a.value].concat(q.alternatives || []);
    var inT = normText(raw);
    if (looksLikeDate(a.value)) {
      var dc = dateCandidates(raw);
      if (dc.some(function (d) { return d === a.value; })) return { status: "correct" };
      for (var i = 0; i < q.traps.length; i++) if (dc.indexOf(String(q.traps[i].value)) >= 0) return { status: "trap", message: q.traps[i].message };
      if (dc.length) return { status: "wrong", message: "Not the right date and time.", hints: ["Check that the dates were imported as real dates (right-aligned in the cell), not text, and that day and month were not swapped."] };
    }
    if (targets.some(function (t) { return normText(t) === inT; })) return { status: "correct" };
    for (var j = 0; j < q.traps.length; j++) if (normText(q.traps[j].value) === inT) return { status: "trap", message: q.traps[j].message };
    // lenient: the answer appears as a whole word inside a longer reply ("Rock genre", "Ernest is the thief")
    var main = normText(a.value);
    if (main.length >= 3 && new RegExp("(^|[^a-z0-9])" + main.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "([^a-z0-9]|$)").test(inT)) return { status: "correct" };
    return { status: "wrong", message: "Not correct, and it doesn't match a mistake we know about.", hints: ["Check spelling, and make sure you answer exactly what is asked (e.g. a code, a name, or a month)."] };
  }

  // ---------- SQL result sets ----------
  function cell(v) {
    if (v == null) return "∅";
    if (typeof v === "number") return (Math.round(v * 100) / 100).toString();
    var n = Number(v);
    if (String(v).trim() !== "" && isFinite(n) && /^[\s\-+\d.]+$/.test(String(v))) return (Math.round(n * 100) / 100).toString();
    return String(v).trim();
  }
  function rowKey(r) { return r.map(cell).join("␟"); }

  // compare a student's query output with the stored expected result
  function checkResult(q, columns, rows) {
    var exp = q.expected_result;
    if (!rows) return { status: "empty", message: "Run a query first." };
    // single-value answers: let the value checker diagnose the number
    if (rows.length === 1 && rows[0].length === 1) {
      var single = checkAnswer(q, rows[0][0]);
      if (single.status === "correct" || single.status === "trap") return single;
    }
    if (!exp) return { status: "wrong", message: "Your query ran, but its result is not the expected answer." };
    var er = exp.rows, ok = false;
    if (rows.length === er.length && rows[0] && er[0] && rows[0].length === er[0].length) {
      if (exp.ordered) ok = rows.every(function (r, i) { return rowKey(r) === rowKey(er[i]); });
      else {
        var A = rows.map(rowKey).sort(), B = er.map(rowKey).sort();
        ok = A.every(function (k, i) { return k === B[i]; });
      }
    }
    if (ok) return { status: "correct" };
    // row-count questions: the number of rows can itself be a known mistake
    if (/rows$/.test(String(q.answer.label || ""))) {
      for (var i = 0; i < q.traps.length; i++) if (q.traps[i].value === rows.length) return { status: "trap", message: q.traps[i].message };
    }
    if (rows[0] && er[0] && rows.length === 1 && er.length === 1) {
      for (var c = 0; c < rows[0].length; c++) { var r = checkAnswer(q, rows[0][c]); if (r.status !== "wrong") return r; }
    }
    var hints = [];
    if (rows.length && er.length && rows[0].length !== er[0].length) hints.push("Your result has " + rows[0].length + " column(s); the question asks for " + er[0].length + ".");
    if (rows.length > er.length) hints.push("Your result has too many rows: a filter is missing or a join is duplicating rows.");
    if (rows.length < er.length) hints.push("Your result has too few rows: a filter is too strict (check >, >=, LIKE patterns, spelling of values).");
    if (rows.length === er.length && exp.ordered) hints.push("Right number of rows. Check the sort order the question asks for.");
    if (!hints.length) hints.push("Right shape, but some values differ. Check the filter conditions and calculations.");
    return { status: "wrong", message: "Your query ran, but the result doesn't match.", hints: hints };
  }

  var api = { parseNumberCandidates: parseNumberCandidates, checkAnswer: checkAnswer, checkResult: checkResult, normText: normText, dateCandidates: dateCandidates };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.Checker = api;
})(this);
