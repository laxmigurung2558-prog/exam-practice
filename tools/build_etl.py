"""Excel Part 2 · ETL cases 1-4."""
import pandas as pd, numpy as np, json, sys, re, csv
sys.path.insert(0, "/home/claude/work")
from kit import make

D = sys.argv[1]
Q = []
def add(qid, ds, case, prompt, ans, sol, traps=(), **kw):
    Q.append(make(qid, ds, "Excel", case, prompt, ans, {"excel": sol}, traps, **kw))

# ---------------------------------------------------------------- Case 1: messy balance sheet
C1 = "Excel Part 2 · ETL case 1 (messy balance sheet)"
raw = open(D + "/case 1/Analytics_mindset_case_studies_ETL_Case1.csv").read().splitlines()
rows = []
for line in raw[1:]:
    line = line.replace("Apple, Inc.", "Apple Inc.")              # unquoted comma inside a name
    rows.append(next(csv.reader([line])))
cols = next(csv.reader([raw[0]]))
c1 = pd.DataFrame(rows, columns=cols)
def money(v, unit=1):
    v = str(v).strip()
    if v in ("", "-"):
        return 0.0
    neg = v.startswith("(") and v.endswith(")")
    v = v.strip("()").replace(",", "")
    mult = {"M": 1e6, "K": 1e3}.get(v[-1], 1)
    v = v.rstrip("MK ").strip()
    x = float(v) * mult * unit
    return -x if neg else x
c1["Ticker"] = c1.Ticker.str.replace(" ", "")
c1.loc[c1.Name.str.startswith("Armada"), "Ticker"] = "AHH"
clean = c1.drop_duplicates().copy()
for c in ["Cash", "Accounts Receivables", "Inventories", "Total Depreciation"]:
    clean[c] = clean[c].map(money)
clean["Total Current Assets"] = clean["Total Current Assets"].map(lambda v: money(v, 1e6))
get = lambda t, y, c: clean[(clean.Ticker == t) & (clean.Year == str(y))][c].iloc[0]
add("E101", "etl1", C1, "After cleaning, how many data rows (company-years) remain?", len(clean),
    "Remove the duplicated APVO 2018 row (Data > Remove Duplicates).",
    [(len(rows), "One row (APVO 2018) appears twice. Duplicates must be removed.")], tol=0)
add("E102", "etl1", C1, "How many distinct companies are in the cleaned data?", clean.Name.nunique(),
    "Fix the tickers first: remove the spaces in 'A M Z N' / 'AM ZN' and fill the missing ticker for Armada Hoffler; then count unique tickers.",
    [(pd.Series([r[0] for r in rows]).nunique(), "You counted the raw tickers. 'AMZN', 'A M Z N' and 'AM ZN' are the same company, and the blank ticker is Armada Hoffler (AHH)."),
     (pd.Series([r[0] for r in rows]).replace("", np.nan).nunique(), "You counted the raw non-blank tickers. 'A M Z N' and 'AM ZN' are Amazon (AMZN).")], tol=0)
add("E103", "etl1", C1, "What was Apple's cash in 2017, in dollars?", get("AAPL", 2017, "Cash"),
    "'20300 M' means 20,300 million: strip the M and multiply by 1,000,000 (=LEFT(x,LEN(x)-2)*10^6). Watch out: the unquoted comma in 'Apple, Inc.' shifts Apple's columns on import.",
    [(20300, "You removed the 'M' but did not apply the unit. M = million, so multiply by 1,000,000."),
     (20300 * 1e3, "M stands for million (10^6), not thousand.")], unit="USD", tol=1)
add("E104", "etl1", C1, "What was Aehr Test Systems' (AEHR) cash in 2016, in dollars?", get("AEHR", 2016, "Cash"),
    "'900 K' = 900 thousand = 900,000.", [(900, "K means thousand: multiply by 1,000."), (900 * 1e6, "K is thousand, not million.")], unit="USD", tol=1)
add("E105", "etl1", C1, "What was American Airlines' (AAL) Total Depreciation in 2017, as a number?", get("AAL", 2017, "Total Depreciation"),
    "Accounting notation (15600000000) means NEGATIVE: =-SUBSTITUTE(SUBSTITUTE(x,\"(\",\"\"),\")\",\"\") or set the column format on import.",
    [(15600000000, "Parentheses mean a negative number in accounting notation. Depreciation is negative here, as in the other rows.")], tol=1)
add("E106", "etl1", C1, "What were American Airlines' (AAL) Total Current Assets in 2016, in dollars?", get("AAL", 2016, "Total Current Assets"),
    "This column is in millions (compare with Cash + Receivables + Inventories for the same row): 10300 * 1,000,000.",
    [(10300, "This column is in millions. Cash alone is $3.2 billion, so total current assets can't be $10,300. Multiply by 1,000,000."),
     (10300 * 1e3, "Check the scale: thousands would make total current assets ($10.3m) smaller than cash ($3.2bn). It's millions.")], unit="USD", tol=1)
add("E107", "etl1", C1, "What were Aerocentury's (ACY) inventories in 2017 after cleaning?", get("ACY", 2017, "Inventories"),
    "'-' is the accounting symbol for zero; replace it with 0 (Find & Replace, match entire cell).", [], tol=0)

# ---------------------------------------------------------------- Case 2: employee codes (clean)
C2 = "Excel Part 2 · ETL case 2 (text extraction)"
c2 = pd.read_excel(D + "/case 2/Analytics_mindset_case_studies_ETL_Case2_Excel.xlsx", sheet_name="Case 2")
p = c2.EmployeeCode.str.extract(r"^([A-Z]{3})(\d{4})-(\d+)([WM])$")
c2["Loc"], c2["Emp"], c2["Plant"], c2["Pay"] = p[0], p[1], p[2], p[3]
c2["LP"] = c2.Loc + "-" + c2.Plant
add("E201", "etl2", C2, "How many different plants does the company have (unique LocationPlantID such as USA-12)?", c2.LP.nunique(),
    "LocationPlantID = LEFT(code,3)&\"-\"&MID(code,FIND(\"-\",code)+1,2); then =COUNTA(UNIQUE(range)).",
    [(c2.Plant.nunique(), "You counted unique PlantIDs only. Every country numbers its plants from 10, so plant 12 in the USA and plant 12 in Japan are different plants. That's why the case asks you to build LocationPlantID as the unique identifier.")], tol=0)
top = c2.LP.value_counts()
add("E202", "etl2", C2, "Which plant (LocationPlantID) has the most employees?", top.index[0],
    "PivotTable with LocationPlantID in Rows, count of EmpID, sort descending.",
    [(c2.Plant.value_counts().index[0], "That's a PlantID without its country. Report the LocationPlantID (e.g. USA-12).")],
    answer_label=f"{top.index[0]} ({top.iloc[0]} employees)")
add("E203", "etl2", C2, "How many employees in Germany are paid weekly?", int(((c2.Loc == "GER") & (c2.Pay == "W")).sum()),
    "=COUNTIFS(Location,\"GER\",PayPeriod,\"W\") with PayPeriod = RIGHT(code,1).",
    [(int((c2.Pay == "W").sum()), "You counted weekly-paid employees in all countries.")], tol=0)

# ---------------------------------------------------------------- Case 3: employee codes (messy)
C3 = "Excel Part 2 · ETL case 3 (messy text extraction)"
c3 = pd.read_excel(D + "/case 3/Analytics_mindset_case_studies_ETL_Case3_Excel.xlsx", sheet_name="Case 3 data")
p = c3.EmployeeCode.str.extract(r"^([A-Za-z]+)(\d+)-(\d+)([A-Za-z]+)$")
std = {"US": "USA", "Japan": "JAP", "Canada": "CAN"}
c3["Loc"] = p[0].replace(std)
c3["Plant"], c3["PayRaw"] = p[2], p[3]
c3["Pay"] = c3.PayRaw.str[0]
c3["LP"] = c3.Loc + "-" + c3.Plant
add("E301", "etl3", C3, "How many employees are paid monthly?", int((c3.Pay == "M").sum()),
    "Pay period is written 'M' or 'Mo'. Standardise first: =IF(LEFT(RIGHT(code,2),1)=\"M\",\"M\",RIGHT(code,1)) or Flash Fill, then COUNTIF.",
    [(int((c3.EmployeeCode.str[-1] == "M").sum()), "RIGHT(code,1) misses the codes ending in 'Mo'. Monthly is written two ways: 'M' and 'Mo'.")], tol=0)
add("E302", "etl3", C3, "How many employees work in the USA?", int((c3.Loc == "USA").sum()),
    "Locations are written inconsistently ('US', 'Japan', 'Canada' vs 3-letter codes). Extract the letters before the first digit, then map to standard codes (a small lookup table).",
    [(int((c3.EmployeeCode.str[:3] == "USA").sum()), "LEFT(code,3) assumes a 3-letter code, but the USA is written 'US' here, so LEFT gives 'US4'.")], tol=0)
naive_lp = (c3.EmployeeCode.str[:3] + "-" + c3.EmployeeCode.str.split("-").str[1].str[:2])
add("E303", "etl3", C3, "After standardising, how many different plants (LocationPlantID) are there?", c3.LP.nunique(),
    "Location = letters before the first digit (mapped to the 3-letter code); PlantID = digits between '-' and the pay-period letters (1 or 2 digits).",
    [(naive_lp.nunique(), "You used fixed positions (LEFT 3 / 2 characters after '-'). In case 3 the location and plant lengths vary, so you got codes like 'Jap-4W'. Extract by pattern, not position."),
     (c3.assign(L=p[0]).pipe(lambda d: (d.L + "-" + d.Plant).nunique()), "You didn't standardise the country names. 'US' and 'USA' (etc.) were treated as different locations — or check whether the counts happen to match.")], tol=0)

# ---------------------------------------------------------------- Case 4: journal entries
C4 = "Excel Part 2 · ETL case 4 (journal entries)"
x = pd.read_excel(D + "/case 4/Analytics_mindset_case_studies_ETL_Case4_Excel.xlsx", sheet_name=None)
je, pi, coa, bu, src = x["JELineItems"], x["PreparerInfo"], x["ChartOfAccounts"], x["BusinessUnits"], x["Source"].dropna()
pi = pi.assign(Name=pi.PreparerName.str.replace("\xa0", " ").str.split("|").str[0].str.strip())
m = je.merge(pi, on=["PreparerID", "BusinessUnitID"], how="left")
first_by_id = pi.drop_duplicates("PreparerID").set_index("PreparerID").Name
add("E401", "etl4", C4, "How many journal lines were prepared by Carolyn Slater?", int((m.Name == "Carolyn Slater").sum()),
    "PreparerID is NOT unique: 101 is a different person in each business unit. Look up with both keys: =XLOOKUP([@PreparerID]&\"|\"&[@BusinessUnitID], PreparerInfo[PreparerID]&\"|\"&PreparerInfo[BusinessUnitID], PreparerInfo[PreparerName], \"Not found\").",
    [(int((je.PreparerID.map(first_by_id) == "Carolyn Slater").sum()), "You looked up PreparerID alone. VLOOKUP returns the FIRST 101 it finds (Carolyn Slater), so every 101 line in every business unit was assigned to her. The unique key is PreparerID + BusinessUnitID.")], tol=0)
add("E402", "etl4", C4, "How many journal lines have a PreparerID/BusinessUnitID combination that does not exist in PreparerInfo?", int(m.Name.isna().sum()),
    "With the two-key lookup, count the 'Not found' (or #N/A) results.",
    [(0, "A lookup on PreparerID alone always finds something, which hides these exceptions. With the correct two-part key, 148 lines have no valid preparer — an audit finding.")], tol=0)
mc = je.merge(coa, on="GLAccountNumber", how="left")
exp = mc[mc.AccountType == "Expenses"]
add("E403", "etl4", C4, "What is the net amount (debits minus credits) posted to Expense accounts?", round(exp.Amount.sum(), 2),
    "XLOOKUP AccountType from ChartOfAccounts on GLAccountNumber, then =SUMIFS(Amount, AccountType, \"Expenses\"). Amount is already signed (credits negative).",
    [(round(exp.Debit.sum(), 2), "You summed the Debit column only. Net amount = debits minus credits, which is the signed Amount column."),
     (round(exp.Debit.sum() - exp.Credit.sum(), 2), "Credits are already stored as negative numbers. Debit - Credit double-counts them; use Debit + Credit (or the Amount column).")], unit="USD")
add("E404", "etl4", C4, "What is the sum of the Amount column over all journal lines? (A balanced journal should give 0.)", round(je.Amount.sum(), 2),
    "=SUM(JELineItems[Amount]) — every entry's debits and credits should net to zero.", [(round(je.Debit.sum(), 2), "That's total debits. The signed Amount column should sum to 0 if every entry balances.")], unit="USD")
cleanlen = len("Carolyn Slater|Food Operations Manager")
add("E405", "etl4", C4, "After cleaning PreparerName, how many characters long is Carolyn Slater's full entry 'Carolyn Slater|Food Operations Manager'?", cleanlen,
    "The names are padded with non-breaking spaces (CHAR(160)), which TRIM does not remove: =TRIM(SUBSTITUTE(A2,CHAR(160),\" \")).",
    [(len(pi.PreparerName[0].strip(" ")), "TRIM only removes normal spaces (CHAR(32)). The padding here is CHAR(160), a non-breaking space; replace it first with SUBSTITUTE."),
     (len(pi.PreparerName[0]), "You didn't clean the name at all: it has trailing non-breaking spaces (CHAR(160)) and a normal space.")], tol=0)

json.dump(Q, open("/home/claude/work/out_etl.json", "w"), indent=1, default=float)
print(len(Q))
