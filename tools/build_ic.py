"""Excel Part 3 · IntegrateCo payroll (2015 vs 2016, two different systems)."""
import pandas as pd, numpy as np, json, sys, re
sys.path.insert(0, "/home/claude/work")
from kit import make

d = sys.argv[1]
p15 = pd.read_csv(d + "/Analytics_mindset_case_studies_IntegrateCo_2015payroll.csv", sep="|", dtype={"Job": str})
p16 = pd.read_csv(d + "/Analytics_mindset_case_studies_IntegrateCo_2016payroll.csv", sep="|", dtype={"Project": str})
jc = pd.read_csv(d + "/Analytics_mindset_case_studies_IntegrateCo_jobcodes.csv", sep="|", dtype=str)
loc = pd.read_csv(d + "/Analytics_mindset_case_studies_IntegrateCo_locations.csv", sep="|", dtype=str)
CASE = "Excel Part 3 · IntegrateCo payroll"
Q = []
def add(qid, prompt, ans, sol, traps=(), **kw):
    Q.append(make(qid, "payroll", "Excel", CASE, prompt, ans, {"excel": sol}, traps, **kw))
r2 = lambda x: round(float(x), 2)

# --- job code extraction: 2 digits (year), optional H/S, then the 3-digit job code
code = lambda s: s.astype(str).str.extract(r"^\d{2}[HS]?(\d{3})")[0]
naive = lambda s: s.astype(str).str[2:5]            # MID(Job,3,3) ignores the optional letter
p15["code"], p16["code"] = code(p15.Job), code(p16.Project)
p15["naive"], p16["naive"] = naive(p15.Job), naive(p16.Project)
p15["gross"] = p15.Reg_Pay + p15.OT_Pay
p15["hrs"] = p15.Reg_Hrs + p15.OT_Hrs
p16["hrs"] = p16.Hours + p16.OT_Hours
p15["name"] = p15.First_Name.str.strip() + " " + p15.Last_Name.str.strip()
valid = set(jc.Job_Code)
EXTRACT = ('Job code = the 3 digits after the 2-digit year and the optional H/S letter: '
           '=IF(ISNUMBER(--MID([@Job],3,1)), MID([@Job],3,3), MID([@Job],4,3)) — keep it as TEXT so "001" matches the JobCodes table.')

g15, g16 = p15.gross.sum(), p16.Gross_Wages.sum()
add("IC01", "What were total gross wages (regular + overtime pay) in the first six months of 2015?", r2(g15),
    "=SUM(2015Data[Reg_Pay]) + SUM(2015Data[OT_Pay])",
    [(r2(p15.Reg_Pay.sum()), "You only summed Reg_Pay. In 2015, gross pay = Reg_Pay + OT_Pay (2016's Gross_Wages already combines them)."),
     (r2(g15 + p15[["Futa", "Suta", "Fica_Medc", "Work_Comp"]].sum().sum()), "You added the payroll taxes and workers' comp. Gross wages are pay only.")],
    unit="USD")
add("IC02", "What were total gross wages in the first six months of 2016?", r2(g16), "=SUM(2016Data[Gross_Wages])",
    [(r2(p16.dropna(subset=["Employee_Number"]).Gross_Wages.sum()), "You excluded the rows without an employee number. They are still wages the company recorded; the question asks for the total as reported (flag them separately).")],
    unit="USD")
add("IC03", "By how much did gross wages increase from H1 2015 to H1 2016? (2016 minus 2015)", r2(g16 - g15),
    "=IC02 - IC01. Noah's 'about $266,000' should reconcile to this.",
    [(r2(g16 - p15.Reg_Pay.sum()), "Your 2015 figure left out overtime pay (Reg_Pay only)."),
     (r2(g15 - g16), "Sign reversed: the case defines differences as 2016 minus 2015 (positive = 2016 higher).")],
    unit="USD", tol=1)

by = lambda df, col, val: df.groupby(col)[val].sum()
diff = (by(p16, "code", "Gross_Wages") - by(p15, "code", "gross")).reindex(sorted(valid))
ndiff = (by(p16, "naive", "Gross_Wages") - by(p15, "naive", "gross"))
top = diff.idxmax()
add("IC04", "Which job code (3-digit text) had the largest increase in gross pay from 2015 to 2016? Also give its description.", top,
    "Add a JobCode column to both years (" + EXTRACT + "), then SUMIFS gross pay per code per year and subtract.",
    [(ndiff.idxmax() if ndiff.idxmax() != top else None, "Your job codes are wrong for codes with an H or S letter. MID(Job,3,3) on '14H002' returns 'H00'. Check for the letter first."),
     (str(int(top)), "Right code, but stored as a number. Job codes must stay as 3-digit text ('009'), or lookups to the JobCodes table fail.")],
    answer_label=f"{top} – {jc.set_index('Job_Code').Job_Description[top]} (+{diff.max():,.2f})",
    extra={"alternatives": [f"{top} {jc.set_index('Job_Code').Job_Description[top]}", jc.set_index('Job_Code').Job_Description[top]]})
pph15 = by(p15, "code", "gross") / by(p15, "code", "hrs")
pph16 = by(p16, "code", "Gross_Wages") / by(p16, "code", "hrs")
add("IC05", "What was the 2016 gross pay per hour for job code 001 (Office)? (2 decimals)", r2(pph16["001"]),
    "=SUMIFS(gross,code,\"001\") / SUMIFS(total hours,code,\"001\"), where total hours = Hours + OT_Hours.",
    [(r2(by(p16, "code", "Gross_Wages")["001"] / by(p16, "code", "Hours")["001"]), "You divided by regular hours only. Gross pay includes overtime pay, so divide by regular + overtime hours."),
     (r2(p16[p16.code == "001"].assign(r=lambda x: x.Gross_Wages / x.hrs).r.replace(np.inf, np.nan).mean()), "You averaged the row-level rates. A weighted rate is total pay / total hours.")],
    unit="USD/hour")

ph = p16[p16.Employee_Number.isna()]
add("IC06", "How many 2016 transactions were entered without an employee number ('phantom' entries)?", len(ph),
    "=COUNTBLANK(2016Data[Employee_Number])",
    [(len(p16[p16.Employee_Name.isna()]) if len(p16[p16.Employee_Name.isna()]) != len(ph) else None, "Use the employee NUMBER field.")], tol=0)
add("IC07", "What is the total gross wage amount of those phantom entries?", r2(ph.Gross_Wages.sum()),
    "=SUMIFS(2016Data[Gross_Wages],2016Data[Employee_Number],\"\")", unit="USD")

ot = p15.groupby(["Emp_No", "name"]).OT_Pay.sum().sort_values(ascending=False)
ot_name = p15.groupby("Last_Name").OT_Pay.sum().max()
add("IC08", "Which employee earned the most overtime pay in H1 2015, and how much? (enter the amount)", r2(ot.iloc[0]),
    "PivotTable on 2015Data: Emp_No and name in Rows, Sum of OT_Pay, sort descending.",
    [(r2(ot_name), "You grouped by last name only, so different employees were merged."),
     (r2(p15.groupby(["Emp_No", "name"]).OT_Hrs.sum().max()), "That's overtime HOURS. The question asks for overtime pay.")],
    unit="USD", answer_label=f"{ot.index[0][1]} (Emp_No {ot.index[0][0]}): {ot.iloc[0]:,.2f}")
otc = by(p15, "code", "OT_Pay").reindex(sorted(valid)).fillna(0)
add("IC09", "Which job code had the most overtime pay in 2015?", otc.idxmax(),
    "Add JobCode to 2015Data (" + EXTRACT + "), PivotTable with JobCode rows and Sum of OT_Pay, sort descending.",
    [(by(p15, "naive", "OT_Pay").idxmax() if by(p15, "naive", "OT_Pay").idxmax() != otc.idxmax() else None,
      "Your job codes are wrong for codes with an H or S letter (MID(Job,3,3) on '14H002' gives 'H00').")],
    answer_label=f"{otc.idxmax()} – {jc.set_index('Job_Code').Job_Description[otc.idxmax()]}: {otc.max():,.2f}",
    extra={"alternatives": [jc.set_index('Job_Code').Job_Description[otc.idxmax()]]})
pp = p15.groupby(["name", "Pay_Date"])[["Reg_Hrs", "OT_Hrs"]].sum()
add("IC10", "In 2015, how many employee/pay-date combinations show overtime hours even though fewer than 40 regular hours were worked on that pay date?",
    int(((pp.Reg_Hrs < 40) & (pp.OT_Hrs > 0)).sum()),
    "Sum Reg_Hrs and OT_Hrs per employee per Pay_Date first (PivotTable or SUMIFS), THEN test Reg < 40 and OT > 0.",
    [(int(((p15.Reg_Hrs < 40) & (p15.OT_Hrs > 0)).sum()), "You tested individual rows. Each row is only one job code; an employee's hours for the pay period are spread over several rows. Total them per employee and pay date first."),
     (int(((pp.Reg_Hrs <= 40) & (pp.OT_Hrs > 0)).sum()), "Exactly 40 regular hours is a full week, so overtime is legitimate there. Use < 40.")], tol=0)
cost16 = p16[["Gross_Wages", "SocSec_Medicare", "FUTA", "SUTA", "Work_Comp"]].sum()
add("IC11", "What was the total employee cost for all projects in H1 2016 (wages + Social Security/Medicare + FUTA + SUTA + workers' comp)?",
    r2(cost16.sum()), "=SUM over the five columns.",
    [(r2(cost16.sum() - cost16.Work_Comp), "You left out workers' compensation."),
     (r2(g16), "That's gross wages only. Employee cost adds the employer taxes and workers' comp.")], unit="USD")

# location: 2016 pay per hour by location (phantoms excluded)
L = loc.assign(Employee_Name=loc.Employee_Name.str.strip())
m16 = p16.dropna(subset=["Employee_Name"]).assign(Employee_Name=lambda x: x.Employee_Name.str.strip()).merge(L, on="Employee_Name", how="left")
g = m16.groupby("Location")[["Gross_Wages", "hrs"]].sum()
rate = (g.Gross_Wages / g.hrs)
add("IC12", "In 2016, what was the average gross pay per hour at location 1 minus location 2? (2 decimals; phantom entries excluded)",
    r2(rate["1"] - rate["2"]),
    "XLOOKUP each employee's Location from the P4 Location tab, then per location: SUM(Gross_Wages)/SUM(Hours+OT_Hours).",
    [(r2((g.Gross_Wages / m16.groupby('Location').Hours.sum())["1"] - (g.Gross_Wages / m16.groupby('Location').Hours.sum())["2"]), "You divided by regular hours only."),
     (r2(m16.assign(r=m16.Gross_Wages / m16.hrs).replace(np.inf, np.nan).groupby("Location").r.mean().pipe(lambda s: s["1"] - s["2"])), "You averaged row-level rates instead of total pay / total hours.")],
    unit="USD/hour", extra={"note": f"Location 1: {rate['1']:.2f}/h, location 2: {rate['2']:.2f}/h. Unmatched names: {int(m16.Location.isna().sum())}."})

# monthly pattern 2015 (dates are M/D/YYYY text -> locale trap)
p15["m_us"] = pd.to_datetime(p15.Pay_Date, format="%m/%d/%Y").dt.month
p15["m_dk"] = pd.to_datetime(p15.Pay_Date, format="%d/%m/%Y", errors="coerce").dt.month
mon = p15.groupby("m_us").gross.sum()
mdk = p15.groupby("m_dk").gross.sum()
names = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
add("IC13", "In which month of H1 2015 were gross wages highest (so Noah needs extra cash)?", names[mon.idxmax()],
    "Add =MONTH([@Pay_Date]) to 2015Data (check that Pay_Date imported as real dates), then SUMIFS gross pay per month.",
    [(names[mdk.idxmax()] if mdk.idxmax() != mon.idxmax() else None,
      "Your pay dates were read as day/month (Danish settings). The file uses US dates: 1/9/2015 is 9 January, not 1 September, and 1/16/2015 stays as text. Re-import with locale English (United States).")],
    extra={"note": "May is about $43,000 above the next-highest month. It had 7 pay dates (5 Friday paydays + 2 other runs), but so did January, so the pay-date count alone does not explain it — worth investigating.",
           "monthly_gross_2015": {names[k]: round(v, 2) for k, v in mon.items()}})
bad = p15[~p15.code.isin(valid) | p15.code.isna()]
add("IC14", "Job codes must be 001–012. How many 2015 rows have a job code outside that range?", len(bad),
    "After extracting the JobCode, look it up in the JobCodes table; count the #N/A results (=COUNTIF(lookup column,\"#N/A\") or ISNA).",
    [(0, "Check again: one Job value ('14S1440') contains '144' as its job code, which is not in the table.")], tol=0,
    extra={"note": "The suffixes R and SH (e.g. 14H001R, 15H010SH) are not in the case description but don't change the job code."})

json.dump(Q, open("/home/claude/work/out_ic.json", "w"), indent=1, default=float)
print(len(Q))
