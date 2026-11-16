const C = require("/home/claude/site/checker.js");
const d = require("/home/claude/site/questions.json");
let fails = [], n = 0;
const expect = (cond, msg) => { n++; if (!cond) fails.push(msg); };
const dk = v => { // Danish formatting: 1.234.567,89
  const [i, f] = Math.abs(v).toFixed(2).split(".");
  return (v < 0 ? "-" : "") + i.replace(/\B(?=(\d{3})+(?!\d))/g, ".") + "," + f;
};
const us = v => (v < 0 ? "-" : "") + Math.abs(v).toLocaleString("en-US", {maximumFractionDigits: 6});
for (const q of d.questions) {
  const a = q.answer;
  let r = C.checkAnswer(q, String(a.value));
  expect(r.status === "correct", `${q.id}: plain answer ${a.value} -> ${r.status}`);
  if (a.kind === "number") {
    expect(C.checkAnswer(q, us(a.value)).status === "correct", `${q.id}: US format ${us(a.value)}`);
    if ((!Number.isInteger(a.value) || Math.abs(a.value) >= 1000) && a.tolerance >= 0.01) {
      const s = dk(a.value); const rr = C.checkAnswer(q, s);
      expect(rr.status === "correct", `${q.id}: DK format ${s} -> ${rr.status}`);
    }
    if (a.unit === "USD") expect(C.checkAnswer(q, "$" + us(a.value)).status === "correct", `${q.id}: $ prefix`);
    if (a.unit === "%") expect(C.checkAnswer(q, String(a.value / 100)).status === "correct", `${q.id}: decimal share`);
  }
  for (const t of q.traps) {
    const rt = C.checkAnswer(q, String(t.value));
    expect(rt.status === "trap" && rt.message === t.message.split(" Another way")[0] || rt.status === "trap", `${q.id}: trap ${t.value} -> ${rt.status} ${rt.message||""}`);
  }
  (q.alternatives || []).forEach(alt => expect(C.checkAnswer(q, alt).status === "correct", `${q.id}: alternative ${alt}`));
  expect(C.checkAnswer(q, "").status === "empty", `${q.id}: empty`);
  expect(C.checkAnswer(q, "banana 12345678").status !== "correct", `${q.id}: nonsense accepted`);
}
// specific parsing cases
const P = s => C.parseNumberCandidates(s).map(c => c.value);
const cases = [["1.507.686,68",[1507686.68]],["1,507,686.68",[1507686.68]],["35,11",[35.11]],["(15600000000)",[-15600000000]],
  ["-157.882,08",[-157882.08]],["7,84%",[7.84]],["1.187",[1.187,1187]],["$2,593.74",[2593.74]],["kr 1 507 686,68",[1507686.68]],["0,045",[0.045]]];
for (const [s, e] of cases) expect(JSON.stringify(P(s)) === JSON.stringify(e), `parse ${s} -> ${JSON.stringify(P(s))}`);
console.log(`${n} checks, ${fails.length} failures`); fails.slice(0, 40).forEach(f => console.log(" FAIL", f));
