"""Excel Part 1 · PwC NYC film permits. Answers recomputed from the data and
checked against the official solutions.xlsx. Traps are computed, including what
a Danish-locale import of the US-formatted .txt file produces."""
import pandas as pd, numpy as np, json, sys
sys.path.insert(0, "/home/claude/work")
from kit import make

X, T = sys.argv[1], sys.argv[2]
df = pd.read_excel(X)
txt = pd.read_csv(T, dtype=str)
s = df[df.EventType == "Shooting Permit"].copy()
CASE = "Excel Part 1 · NYC film permits (PwC)"
Q = []
def add(qid, prompt, ans, sol, traps=(), **kw):
    Q.append(make(qid, "film", "Excel", CASE, prompt, ans, {"excel": sol}, traps, **kw))

# Danish-locale import of the .txt (D/M/YYYY): impossible dates stay as text and are skipped
st = txt[txt.EventType == "Shooting Permit"]
dk = lambda c: pd.to_datetime(st[c], format="%d/%m/%Y %H:%M", errors="coerce")
dk_start, dk_end, dk_ent = dk("StartDateTime"), dk("EndDateTime"), dk("EnteredOn")
DK = ("Your dates were imported with Danish settings. The file uses US dates (month/day/year), so 7/5/2016 became 7 May "
      "and 7/18/2016 stayed as text (and was silently skipped). Re-import with Data > From Text/CSV and set the locale "
      "to English (United States), or use Text to Columns with date format MDY. Always check: are the dates right-aligned?")
half = lambda h: round(h * 2) / 2
pct = lambda x: round(100 * x, 2)

z = df.ZipCode
add("FP01", "How many records does the table have?", len(df), "=ROWS(Table1) or the count in the status bar minus the header row",
    [(len(df) + 1, "You counted the header row as a record.")], tol=0)
add("FP02", "How many columns does the table have?", df.shape[1], "=COLUMNS(Table1)", tol=0)
add("FP03", "How many records have a missing value for ZipCode?", int(z.isna().sum()),
    "=COUNTBLANK(Table1[ZipCode])", [(int(z.isna().sum() + ((z < 10000) | (z > 99999)).sum()),
     "You mixed blank zip codes with invalid ones. Missing = blank; invalid is the next question.")], tol=0)
inv = int(((z < 10000) | (z > 99999)).sum())
add("FP04", "How many records have an invalid value for ZipCode (not a 5-digit code)?", inv,
    "Filter ZipCode, or =COUNTIFS(Table1[ZipCode],\"<10000\") + COUNTIFS(Table1[ZipCode],\">99999\"). The invalid value is 83.",
    [(inv + int(z.isna().sum()), "You included the blank zip codes. Blanks are 'missing', not 'invalid'.")], tol=0)
add("FP05", "Which column has the same value for every record? (exact column name)", "EventAgency",
    "Filter each column or use =COUNTA(UNIQUE(column)) = 1.")
add("FP06", "What is the oldest EnteredOn value? (date and time, YYYY-MM-DD HH:MM)", df.EnteredOn.min().strftime("%Y-%m-%d %H:%M"),
    "=MIN(Table1[EnteredOn]) formatted as date-time",
    [(dk_ent.min().strftime("%Y-%m-%d %H:%M"), DK)], extra={"alternatives": ["12/7/2011 16:38", "07-12-2011 16:38", "7 December 2011 16:38"]})
add("FP07", "What is the newest EnteredOn value? (YYYY-MM-DD HH:MM)", df.EnteredOn.max().strftime("%Y-%m-%d %H:%M"),
    "=MAX(Table1[EnteredOn])", [(dk_ent.max().strftime("%Y-%m-%d %H:%M"), DK)],
    extra={"alternatives": ["2/9/2018 12:46", "09-02-2018 12:46", "9 February 2018 12:46"]})
add("FP08", "How many different event types are there?", df.EventType.nunique(), "PivotTable on EventType, or =COUNTA(UNIQUE(Table1[EventType]))", tol=0)
add("FP09", "What is the most common event type?", df.EventType.mode()[0], "PivotTable: EventType in Rows, Count of EventID in Values, sort descending.")
add("FP10", "What is the most common Category of shooting permit?", s.Category.mode()[0], "PivotTable filtered to EventType = Shooting Permit, Category in Rows.",
    [(df.Category.mode()[0] if df.Category.mode()[0] != s.Category.mode()[0] else None, "You did not filter to shooting permits.")])
add("FP11", "How many shooting permits have been granted for student films?", int((s.Category == "Student").sum()),
    "=COUNTIFS(Table1[EventType],\"Shooting Permit\",Table1[Category],\"Student\")",
    [(int((df.Category == "Student").sum()), "You did not filter to shooting permits.")], tol=0)
cb = lambda d: d["CommunityBoard(s)"].astype(str).str.contains(",").mean()
add("FP12", "What percentage of shooting permits required approval by more than one Community Board? (percent, 2 decimals)", pct(cb(s)),
    "More than one board = the CommunityBoard(s) cell contains a comma: =COUNTIFS(Table1[EventType],\"Shooting Permit\",Table1[CommunityBoard(s)],\"*,*\") / COUNTIFS(Table1[EventType],\"Shooting Permit\")",
    [(pct(cb(df)), "You used all event types as the base. The question is about shooting permits only.")],
    unit="%", tol=0.01, extra={"alternatives_scale": 0.01})
yr = s.assign(y=s.StartDateTime.dt.year).groupby(["y", "Borough"]).size().unstack()
first = int(yr.index[(yr.Brooklyn > yr.Manhattan)][0])
add("FP13", "In what year did shooting permits in Brooklyn first outnumber those in Manhattan (by start date)?", first,
    "PivotTable: YEAR(StartDateTime) in Rows, Borough in Columns, filtered to Shooting Permit.", tol=0)
man = s[s.Borough == "Manhattan"]
bw = lambda d: d.ParkingHeld.str.upper().str.contains("BROADWAY").mean()
add("FP14", "What percentage of Manhattan shooting permits take place on or near Broadway (BROADWAY in ParkingHeld)? Round to the nearest percent.",
    round(100 * bw(man)), "=COUNTIFS(Table1[EventType],\"Shooting Permit\",Table1[Borough],\"Manhattan\",Table1[ParkingHeld],\"*BROADWAY*\") / COUNTIFS(Table1[EventType],\"Shooting Permit\",Table1[Borough],\"Manhattan\")",
    [(round(100 * bw(s)), "Your denominator was all shooting permits. The question asks for the share of MANHATTAN permits.")],
    unit="%", tol=0, extra={"alternatives_scale": 0.01})
foreign = lambda d: (d.Country != "United States of America")
add("FP15", "How many shooting permits since 2013 (by EnteredOn) were submitted from a foreign country?",
    int((foreign(s) & (s.EnteredOn.dt.year >= 2013)).sum()),
    "=COUNTIFS(Table1[EventType],\"Shooting Permit\",Table1[Country],\"<>United States of America\",Table1[EnteredOn],\">=\"&DATE(2013,1,1))",
    [(int(foreign(s).sum()), "You counted all years. 'Since 2013' means EnteredOn on or after 1 Jan 2013."),
     (int((foreign(df) & (df.EnteredOn.dt.year >= 2013)).sum()), "You included non-shooting permits.")], tol=0)
dur = lambda a, b: (b - a).dt.total_seconds() / 3600
add("FP16", "What is the average duration of a shooting permit, in hours, rounded to the nearest half hour?",
    half(dur(s.StartDateTime, s.EndDateTime).mean()),
    "Helper column =([@EndDateTime]-[@StartDateTime])*24, then AVERAGEIFS over shooting permits; round with =MROUND(x,0.5).",
    [(half(dur(df.StartDateTime, df.EndDateTime).mean()), "You averaged all event types, not only shooting permits."),
     (half(dur(dk_start, dk_end).mean()), DK),
     (round(dur(s.StartDateTime, s.EndDateTime).mean() / 24 * 2) / 2, "Excel stores date differences in DAYS. Multiply by 24 to get hours.")],
    unit="hours", tol=0)
add("FP17", "What was the duration of the shortest shoot, in minutes?", round(dur(s.StartDateTime, s.EndDateTime).min() * 60),
    "=MIN(helper duration column)*60 if the helper is in hours (or *1440 if in days).",
    [(round(dur(dk_start, dk_end).min() * 60), DK + " (Negative durations are a sure sign of swapped day and month.)")], unit="minutes", tol=0)
lead = lambda a, b: (b - a).dt.total_seconds() / 86400
add("FP18", "What is the average lead time in days between EnteredOn and StartDateTime for shooting permits? Round to the nearest day.",
    round(lead(s.EnteredOn, s.StartDateTime).mean()),
    "Helper column =[@StartDateTime]-[@EnteredOn], AVERAGEIFS over shooting permits, ROUND(x,0).",
    [(round(lead(df.EnteredOn, df.StartDateTime).mean()), "You averaged all event types, not only shooting permits."),
     (round(lead(dk_ent, dk_start).mean()), DK)], unit="days", tol=0)
add("FP19", "What is the most common day of the week for a shooting permit to start? (full day name)",
    s.StartDateTime.dt.day_name().mode()[0], "Helper column =TEXT([@StartDateTime],\"dddd\") then a PivotTable (set Excel to English or the names will be Danish).",
    [(dk_start.dt.day_name().mode()[0], DK)])
def any_fri(a, b):
    return np.mean([(pd.date_range(x.normalize(), y.normalize()).dayofweek == 4).any() for x, y in zip(a, b)])
add("FP20", "What percentage of shooting permits include shooting on at least part of a Friday? (percent, 2 decimals)",
    pct(any_fri(s.StartDateTime, s.EndDateTime)),
    "A permit covers a Friday if any calendar day from INT(Start) to INT(End) is a Friday: e.g. =OR(WEEKDAY([@StartDateTime],2)=5, AND(INT([@EndDateTime])-INT([@StartDateTime])>=MOD(5-WEEKDAY([@StartDateTime],2),7))).",
    [(pct((s.StartDateTime.dt.dayofweek == 4).mean()), "You only counted permits STARTING on a Friday. Multi-day permits that start earlier and run into Friday count too.")],
    unit="%", tol=0.01, extra={"alternatives_scale": 0.01})

json.dump(Q, open("/home/claude/work/out_film.json", "w"), indent=1)
print(len(Q))
