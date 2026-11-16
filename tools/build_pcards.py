import sqlite3, json, sys
sys.path.insert(0, "/home/claude/work")
from kit import make, scalar

DB = sys.argv[1]
con = sqlite3.connect(DB)
S = lambda q: scalar(con, q)
CASE = "SQL Part 2 · OSU P-cards"
Q = []

def add(qid, prompt, sql, traps, **kw):
    ans = S(sql)
    Q.append(make(qid, "pcards", "SQL", CASE, prompt, ans,
                  {"sql": sql.strip()}, [(S(t), m) for t, m in traps], **kw))

# ISO date built from the text column 'M/D/YYYY 0:00:00'
def iso(col):
    rest = f"substr({col}, instr({col},'/')+1)"
    return (f"printf('%04d-%02d-%02d', cast(substr({rest}, instr({rest},'/')+1) as int), "
            f"cast({col} as int), cast({rest} as int))")
TD, PD = iso("TransactionDate"), iso("PostedDate")

# ---------------- Task 4: querying basics ----------------
add("PC01", "What is the total number of P-card transactions in the database? (TotalTrans)",
    "SELECT COUNT(*) AS TotalTrans FROM pcards;",
    [("SELECT COUNT(Description) FROM pcards",
      "You counted a column that contains blanks. COUNT(column) skips NULLs, and 135 transactions have no Description. Use COUNT(*) (the case itself warns about this)."),
     ("SELECT COUNT(*) FROM pcards WHERE Amount > 0",
      "You left out the returns. Returns are transactions too; they are stored as negative amounts.")],
    topics=["count", "nulls"], tol=0)

add("PC02", "How many P-card transactions are for amounts of $5,000 or more? (TotalTransGT5k)",
    "SELECT COUNT(*) AS TotalTransGT5k FROM pcards WHERE Amount >= 5000;",
    [("SELECT COUNT(*) FROM pcards WHERE Amount > 5000",
      "The question says 'more than or equal to $5,000'. You used > instead of >=, which drops transactions of exactly $5,000."),
     ("SELECT COUNT(*) FROM pcards WHERE ABS(Amount) >= 5000",
      "You also counted large returns (negative amounts) by using ABS(). Only charges of $5,000 or more are asked for.")],
    topics=["filter", "count"], tol=0)

add("PC03", "What is the total dollar amount of returns from January to March 2014, inclusive? (TotalReturns2014Q1)",
    "SELECT ROUND(SUM(Amount),2) AS TotalReturns2014Q1 FROM pcards WHERE Year = 2014 AND Month BETWEEN 1 AND 3 AND Amount < 0;",
    [("SELECT ROUND(SUM(Amount),2) FROM pcards WHERE Year = 2014 AND Month BETWEEN 1 AND 3",
      "You summed all transactions in the quarter (purchases minus returns). Returns are the negative amounts: add WHERE Amount < 0."),
     ("SELECT ROUND(SUM(Amount),2) FROM pcards WHERE Month BETWEEN 1 AND 3 AND Amount < 0",
      "You included January to March of every year in the database, not only 2014."),
     ("SELECT ROUND(SUM(Amount),2) FROM pcards WHERE Year = 2014 AND Month < 3 AND Amount < 0",
      "'January to March, inclusive' includes March. Use Month BETWEEN 1 AND 3 (or <= 3)."),
     ("SELECT -ROUND(SUM(Amount),2) FROM pcards WHERE Year = 2014 AND Month BETWEEN 1 AND 3 AND Amount < 0",
      "Right amount, wrong sign. Returns are stored as negative numbers, so the total of returns is negative. Saying 'returns of $X' in words is fine; the query result is negative.")],
    topics=["filter", "sum", "returns"], unit="USD")

add("PC04", "How many P-card transactions took place in the 2013 calendar year (by TransactionDate)?",
    "SELECT COUNT(*) AS TotalTrans FROM pcards WHERE Year = 2013;",
    [(f"SELECT COUNT(*) FROM pcards WHERE {PD} BETWEEN '2013-01-01' AND '2013-12-31'",
      "You used PostedDate. The case says to use TransactionDate for all date questions unless stated otherwise."),
     ("SELECT COUNT(*) FROM pcards WHERE TransactionDate BETWEEN '1/1/2013' AND '12/31/2013'",
      "TransactionDate is stored as TEXT ('7/26/2014 0:00:00'), so BETWEEN compares letters, not dates. Use the Year column or convert the text to a real date first.")],
    topics=["dates", "count"], tol=0)

add("PC05", "Which cardholder had the most transactions in 2014? Give the number of transactions (NumTrans).",
    "SELECT CardholderFirstInitial||' '||CardholderLastName AS Name, COUNT(*) AS NumTrans FROM pcards WHERE Year = 2014 GROUP BY Name ORDER BY NumTrans DESC LIMIT 1;",
    [], topics=["group by", "ranking"], tol=0)
# answer is a row; make it numeric (NumTrans) and keep the name as extra
r = con.execute("SELECT CardholderFirstInitial||' '||CardholderLastName, COUNT(*) n FROM pcards WHERE Year=2014 GROUP BY 1 ORDER BY n DESC LIMIT 1").fetchone()
ln = con.execute("SELECT CardholderLastName, COUNT(*) n FROM pcards WHERE Year=2014 GROUP BY 1 ORDER BY n DESC LIMIT 1").fetchone()
allyr = con.execute("SELECT CardholderFirstInitial||' '||CardholderLastName, COUNT(*) n FROM pcards GROUP BY 1 ORDER BY n DESC LIMIT 1").fetchone()
Q[-1] = make("PC05", "pcards", "SQL", CASE,
    "Which cardholder had the most transactions in 2014? Enter the number of transactions (NumTrans).",
    r[1], {"sql": Q[-1]["solution"]["sql"], "expected_row": list(r)},
    [(ln[1], f"You grouped by last name only, so different people with the same surname were merged (top: {ln[0]}). The case says a person is the combination of first initial AND last name."),
     (allyr[1], "You counted every year in the database. Restrict to 2014.")],
    topics=["group by", "ranking"], tol=0, answer_label=f"{r[0]} with {r[1]} transactions")

add("PC06", "Who returned the greatest dollar amount of goods in 2014? Enter that total returned amount (ReturnedGoodsValue).",
    "SELECT CardholderFirstInitial||' '||CardholderLastName AS Name, ROUND(SUM(Amount),2) AS ReturnedGoodsValue, COUNT(*) AS ReturnedGoodsCount FROM pcards WHERE Year = 2014 AND Amount < 0 GROUP BY Name ORDER BY ReturnedGoodsValue ASC LIMIT 1;",
    [], topics=["group by", "returns"])
r = con.execute("SELECT CardholderFirstInitial||' '||CardholderLastName, ROUND(SUM(Amount),2), COUNT(*) FROM pcards WHERE Year=2014 AND Amount<0 GROUP BY 1 ORDER BY 2 ASC LIMIT 1").fetchone()
wrongsort = con.execute("SELECT ROUND(SUM(Amount),2) FROM pcards WHERE Year=2014 AND Amount<0 GROUP BY CardholderFirstInitial||' '||CardholderLastName ORDER BY 1 DESC LIMIT 1").fetchone()[0]
Q[-1] = make("PC06", "pcards", "SQL", CASE, Q[-1]["prompt"], r[1],
    {"sql": Q[-1]["solution"]["sql"], "expected_row": list(r)},
    [(wrongsort, "You sorted descending. Returns are negative, so the LARGEST return is the most negative number: sort ascending (or sort by ABS)."),
     (-r[1], "Right person and amount, but the sign is flipped. Returns are negative in this data.")],
    topics=["group by", "returns", "sorting negatives"], answer_label=f"{r[0]}: {r[1]} over {r[2]} returns")

add("PC07", "How many cardholders had more than 10 transactions in 2014?",
    "SELECT COUNT(*) FROM (SELECT CardholderFirstInitial||' '||CardholderLastName AS Name FROM pcards WHERE Year = 2014 GROUP BY Name HAVING COUNT(*) > 10);",
    [("SELECT COUNT(*) FROM (SELECT 1 FROM pcards WHERE Year=2014 GROUP BY CardholderFirstInitial||' '||CardholderLastName HAVING COUNT(*) >= 10)",
      "'More than 10' means 11 or more. You used >= 10."),
     ("SELECT COUNT(*) FROM (SELECT 1 FROM pcards WHERE Year=2014 GROUP BY CardholderLastName HAVING COUNT(*) > 10)",
      "You grouped by last name only, merging different people. Use first initial + last name."),
     ("SELECT COUNT(*) FROM (SELECT 1 FROM pcards GROUP BY CardholderFirstInitial||' '||CardholderLastName HAVING COUNT(*) > 10)",
      "You used all years. Restrict to 2014 BEFORE grouping (WHERE), then filter groups with HAVING.")],
    topics=["having"], tol=0)

add("PC08", "Assume all purchases are net of the 4.5% state sales tax. How much sales tax did OSU avoid on P-card transactions in 2014? (SalesTaxSaved)",
    "SELECT ROUND(SUM(Amount)*0.045,2) AS SalesTaxSaved FROM pcards WHERE Year = 2014;",
    [("SELECT ROUND(SUM(Amount)*0.045,2) FROM pcards WHERE Year = 2014 AND Amount > 0",
      "You excluded returns. Returned goods were never really bought, so no tax was saved on them: use the net total including the negative amounts."),
     ("SELECT ROUND(SUM(Amount)*0.45,2) FROM pcards WHERE Year = 2014",
      "4.5% is 0.045, not 0.45."),
     ("SELECT ROUND(SUM(Amount)*0.045*0.7,2) FROM pcards WHERE Year = 2014",
      "That is the 70% version (OSU pays tax in other states 30% of the time). This question asks for 100%.")],
    topics=["calculated field"], unit="USD")

add("PC09", "OSU would earn 0.75% on Amazon.com transactions of $500 and more and 0.50% on those under $500. What would OSU have earned in 2014? (AmazonEarnings)",
    "SELECT ROUND(SUM(CASE WHEN Amount >= 500 THEN Amount*0.0075 ELSE Amount*0.005 END),2) AS AmazonEarnings FROM pcards WHERE Year = 2014 AND LOWER(Vendor) = 'amazon.com';",
    [("SELECT ROUND(SUM(CASE WHEN Amount >= 500 THEN Amount*0.0075 ELSE Amount*0.005 END),2) FROM pcards WHERE Year = 2014 AND Vendor = 'Amazon.com'",
      "In SQLite, = is case-sensitive, so 'AMAZON.COM' (28 transactions) was left out. The case was written for Access, where comparisons ignore case. Use LOWER(Vendor) = 'amazon.com'."),
     ("SELECT ROUND(SUM(CASE WHEN Amount >= 500 THEN Amount*0.0075 ELSE Amount*0.005 END),2) FROM pcards WHERE Year = 2014 AND Vendor LIKE '%amazon%'",
      "LIKE '%amazon%' also catches Marketplace, Kindle, Prime, Amazon Web Services and claim adjustments. The question is about the vendor Amazon.com only."),
     ("SELECT ROUND(SUM(CASE WHEN Amount > 500 THEN Amount*0.0075 ELSE Amount*0.005 END),2) FROM pcards WHERE Year = 2014 AND LOWER(Vendor) = 'amazon.com'",
      "'$500 and more' includes exactly $500. You used > 500."),
     ("SELECT ROUND(SUM(CASE WHEN Amount >= 500 THEN Amount*0.0075 ELSE Amount*0.005 END),2) FROM pcards WHERE Year = 2014 AND LOWER(Vendor) = 'amazon.com' AND Amount > 0",
      "You dropped Amazon returns. Commission is clawed back when goods are returned, so returns reduce earnings.")],
    topics=["case when", "text matching"], unit="USD")

add("PC10", "How many 2014 transactions are greater than the average transaction amount for 2014?",
    "SELECT COUNT(*) FROM pcards WHERE Year = 2014 AND Amount > (SELECT AVG(Amount) FROM pcards WHERE Year = 2014);",
    [("SELECT COUNT(*) FROM pcards WHERE Year = 2014 AND Amount > (SELECT AVG(Amount) FROM pcards)",
      "Your subquery averaged ALL years. The benchmark must be the 2014 average, so the subquery also needs WHERE Year = 2014."),
     ("SELECT COUNT(*) FROM pcards WHERE Year = 2014 AND Amount > (SELECT AVG(Amount) FROM pcards WHERE Year = 2014 AND Amount > 0)",
      "Your average excluded returns, which raises the benchmark. The average transaction includes returns.")],
    topics=["subquery"], tol=0)

# ---------------- Task 5: internal-control tests (2014) ----------------
add("PC11", "Control: a user shall not spend more than $50,000 per year. How many cardholders spent more than $50,000 in 2014?",
    "SELECT COUNT(*) FROM (SELECT CardholderFirstInitial||' '||CardholderLastName AS Name, SUM(Amount) AS Total FROM pcards WHERE Year = 2014 GROUP BY Name HAVING Total > 50000);",
    [("SELECT COUNT(*) FROM (SELECT SUM(Amount) t FROM pcards WHERE Year=2014 AND Amount>0 GROUP BY CardholderFirstInitial||' '||CardholderLastName HAVING t > 50000)",
      "You ignored returns. Spending against a limit is net of credits; gross charges overstate violations."),
     ("SELECT COUNT(*) FROM (SELECT SUM(Amount) t FROM pcards WHERE Year=2014 GROUP BY CardholderLastName HAVING t > 50000)",
      "You grouped by last name only. Several people share a surname, so their spending was added together, creating false violations.")],
    topics=["internal control", "having"], tol=0)

add("PC12", "Control: no more than $10,000 per month without approval. How many cardholder-months in 2014 exceeded $10,000?",
    "SELECT COUNT(*) FROM (SELECT CardholderFirstInitial||' '||CardholderLastName AS Name, Month, SUM(Amount) AS Total FROM pcards WHERE Year = 2014 GROUP BY Name, Month HAVING Total > 10000);",
    [("SELECT COUNT(DISTINCT n) FROM (SELECT CardholderFirstInitial||' '||CardholderLastName n FROM pcards WHERE Year=2014 GROUP BY n, Month HAVING SUM(Amount) > 10000)",
      "You counted people, not person-months. The test is per month, so someone over the limit in 3 months counts 3 times."),
     ("SELECT COUNT(*) FROM (SELECT 1 FROM pcards WHERE Year=2014 AND Amount>0 GROUP BY CardholderFirstInitial||' '||CardholderLastName, Month HAVING SUM(Amount) > 10000)",
      "You ignored returns, which overstates monthly spending.")],
    topics=["internal control", "group by two fields"], tol=0)

add("PC13", "Control: no single transaction above $5,000. How many 2014 transactions were for more than $5,000?",
    "SELECT COUNT(*) FROM pcards WHERE Year = 2014 AND Amount > 5000;",
    [("SELECT COUNT(*) FROM pcards WHERE Year = 2014 AND Amount >= 5000",
      "The limit is 'more than $5,000'. A transaction of exactly $5,000 is within the limit, so it is not a violation."),
     ("SELECT COUNT(*) FROM pcards WHERE Amount > 5000",
      "You tested every year. The audit covers 2014.")],
    topics=["internal control", "filter"], tol=0)

split_same = """SELECT COUNT(*) FROM pcards p JOIN (
  SELECT CardholderFirstInitial, CardholderLastName, Vendor, TransactionDate
  FROM pcards WHERE Year = 2014
  GROUP BY CardholderFirstInitial, CardholderLastName, Vendor, TransactionDate
  HAVING COUNT(*) > 1 AND SUM(Amount) > 5000) g
 ON p.CardholderFirstInitial = g.CardholderFirstInitial AND p.CardholderLastName = g.CardholderLastName
 AND p.Vendor = g.Vendor AND p.TransactionDate = g.TransactionDate;"""
add("PC14", "Control: a purchase over $5,000 must not be split between several swipes by the same person. How many 2014 transactions are flagged (same person, same vendor, same day, more than one transaction, combined total over $5,000)?",
    split_same,
    [("SELECT COUNT(*) FROM (SELECT 1 FROM pcards WHERE Year=2014 GROUP BY CardholderFirstInitial, CardholderLastName, Vendor, TransactionDate HAVING COUNT(*)>1 AND SUM(Amount)>5000)",
      "You counted the groups (person-vendor-days), but the test asks you to display all transaction details, i.e. every transaction in those groups. Join the groups back to the transactions."),
     (split_same.replace("COUNT(*) > 1 AND ", ""),
      "You forgot 'more than one transaction for the day'. A single $6,000 swipe is a limit breach (control 3), not a split purchase."),
     (split_same.replace(" Vendor,", "").replace("AND p.Vendor = g.Vendor ", ""),
      "You did not require the same vendor. Buying from two different shops on one day is a different test (control 6).")],
    topics=["internal control", "split purchases", "join back"], tol=0)

# ---------------- Task 7: forensic tests ----------------
benford = """SELECT ROUND(100.0*SUM(substr(CAST(Amount AS TEXT),1,1)='1')/COUNT(*),3) AS PctDigit1
FROM pcards WHERE Year = 2014 AND Amount >= 1;"""
add("PC15", "Benford's law: among 2014 transactions of $1.00 or more, what percentage start with the digit 1? (round to three decimals)",
    benford,
    [("SELECT ROUND(100.0*SUM(substr(CAST(ABS(Amount) AS TEXT),1,1)='1')/COUNT(*),3) FROM pcards WHERE Year=2014 AND ABS(Amount) >= 1",
      "You included returns by taking the absolute value. The case says to exclude all numbers less than 1.00, and negative numbers are less than 1."),
     ("SELECT ROUND(100.0*SUM(substr(CAST(Amount AS TEXT),1,1)='1')/COUNT(*),3) FROM pcards WHERE Year=2014 AND Amount > 0",
      "You excluded negatives but kept amounts between $0 and $0.99, whose first character is '0'. Use Amount >= 1."),
     ("SELECT ROUND(100.0*SUM(substr(CAST(Amount AS TEXT),1,1)='1')/COUNT(*),3) FROM pcards WHERE Amount >= 1",
      "You used every year; the forensic test covers 2014.")],
    topics=["forensics", "benford"], unit="%", tol=0.001,
    extra={"note": "Benford expects 30.103% for digit 1."})

dups = """SELECT COUNT(*) FROM pcards p JOIN (
  SELECT TransactionDate, Vendor, CardholderFirstInitial, CardholderLastName, Amount
  FROM pcards WHERE Year = 2014 AND Amount > 0
  GROUP BY TransactionDate, Vendor, CardholderFirstInitial, CardholderLastName, Amount
  HAVING COUNT(*) > 1) d
 USING (TransactionDate, Vendor, CardholderFirstInitial, CardholderLastName, Amount)
WHERE p.Year = 2014;"""
add("PC16", "Duplicate payments: same day, same vendor, same cardholder, same amount (returns excluded). How many 2014 transactions are possible duplicates?",
    dups,
    [("SELECT COUNT(*) FROM (SELECT 1 FROM pcards WHERE Year=2014 AND Amount>0 GROUP BY TransactionDate, Vendor, CardholderFirstInitial, CardholderLastName, Amount HAVING COUNT(*)>1)",
      "You counted duplicate GROUPS. The case says that when there are more than two charges, all of them are possible duplicates, so list every transaction in each group."),
     ("SELECT COUNT(*) FROM pcards p JOIN (SELECT TransactionDate, Vendor, CardholderFirstInitial, CardholderLastName, Amount FROM pcards WHERE Year=2014 GROUP BY 1,2,3,4,5 HAVING COUNT(*)>1) d USING (TransactionDate, Vendor, CardholderFirstInitial, CardholderLastName, Amount) WHERE p.Year=2014",
      "You did not exclude returns. A purchase and a matching refund are not duplicates, and two identical refunds are not payments."),
     ("SELECT COUNT(*) - COUNT(DISTINCT TransactionDate||Vendor||CardholderFirstInitial||CardholderLastName||Amount) FROM pcards WHERE Year=2014 AND Amount>0",
      "You counted only the 'extra' copies. The case asks for all possible duplicate payments for follow-up, including the first one.")],
    topics=["forensics", "duplicates"], tol=0)

add("PC17", "Round-number test: how many 2014 transactions have a four-digit dollar amount ending in 000 (no cents)?",
    "SELECT COUNT(*) FROM pcards WHERE Year = 2014 AND Amount BETWEEN 1000 AND 9999 AND Amount = CAST(Amount AS INTEGER) AND CAST(Amount AS INTEGER) % 1000 = 0;",
    [("SELECT COUNT(*) FROM pcards WHERE Year=2014 AND Amount = CAST(Amount AS INTEGER) AND CAST(Amount AS INTEGER) % 1000 = 0",
      "You did not limit to four digits, so $10,000+ amounts and $0 adjustments were included."),
     ("SELECT COUNT(*) FROM pcards WHERE Year=2014 AND ABS(Amount) BETWEEN 1000 AND 9999 AND Amount = CAST(Amount AS INTEGER) AND CAST(Amount AS INTEGER) % 1000 = 0",
      "You included returns (negative amounts) by using ABS().")],
    topics=["forensics", "round numbers"], tol=0)

lag = f"SELECT MAX(julianday({PD}) - julianday({TD})) FROM pcards WHERE Year = 2014 AND Month = 11;"
add("PC18", "For November 2014 transactions, what is the largest number of days between TransactionDate and PostedDate (TimeDif)?",
    lag,
    [("SELECT MAX(CAST(PostedDate AS INT) - CAST(TransactionDate AS INT)) FROM pcards WHERE Year=2014 AND Month=11",
      "You subtracted the text dates directly. '11/28/2014' - '12/2/2014' only compares the leading month numbers. Convert the text to a date first (e.g. julianday on an ISO date)."),
     (f"SELECT MAX(julianday({TD}) - julianday({PD})) FROM pcards WHERE Year=2014 AND Month=11",
      "You subtracted in the wrong order. The case says TimeDif is positive when PostedDate is after TransactionDate: PostedDate - TransactionDate.")],
    topics=["dates", "date arithmetic"], tol=0, unit="days")

json.dump(Q, open("/home/claude/work/out_pcards.json", "w"), indent=1)
print(len(Q), "questions")
