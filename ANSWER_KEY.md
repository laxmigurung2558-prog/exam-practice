# Answer key with common mistakes

115 questions · 144 diagnosed mistakes · every answer computed from the course data.

Each wrong answer listed under a question is the exact number that the described mistake produces, so the website can tell students which trap they fell into.

## Findings worth knowing

- **Dates are US-formatted** (month/day/year) in the film-permit .txt and the 2015 payroll file. Imported on Danish settings, the average shoot is 163 hours instead of 17, lead time is 105 days instead of 5, the busiest start day becomes Friday instead of Thursday, and about 60% of dates silently stay as text.
- **The PwC Chinook key's '49 albums'** counts album purchases. The number of *distinct* albums is 41, and every qualifying album has only one track.
- **The PwC film-permit key** reproduces exactly (20/20).
- **IntegrateCo:** the 2016 − 2015 gross-wage increase is $266,055.56 (Noah's 'about $266,000'). Job codes carry undocumented suffixes (R, SH) and one corrupt code (14S1440). 68 phantom 2016 rows total $32,951.29.
- **P-cards:** the database is already filtered to OSU with no blank dates, so those case instructions don't change any answer. The real traps are text dates, negative returns, > vs ≥, and SQLite's case-sensitive '=' ('Amazon.com' ≠ 'AMAZON.COM'), whereas Access ignores case.
- **Journal entries:** PreparerID is not unique (101 is five different people). The key is PreparerID + BusinessUnitID, and 148 lines have no valid preparer. Names are padded with CHAR(160), which TRIM does not remove.
- **Tie:** Helena Bonham Carter's top-rated film is a tie (The King's Speech / Night Will Fall, both 8.0). Both are accepted.

## Excel Part 1 · NYC film permits (PwC)

### FP01 — How many records does the table have?

**Answer:** 33,502

*How:* =ROWS(Table1) or the count in the status bar minus the header row

| If the student gets… | Diagnosis |
|---|---|
| 33,503 | You counted the header row as a record. |

### FP02 — How many columns does the table have?

**Answer:** 14

*How:* =COLUMNS(Table1)

### FP03 — How many records have a missing value for ZipCode?

**Answer:** 11

*How:* =COUNTBLANK(Table1[ZipCode])

| If the student gets… | Diagnosis |
|---|---|
| 13 | You mixed blank zip codes with invalid ones. Missing = blank; invalid is the next question. |

### FP04 — How many records have an invalid value for ZipCode (not a 5-digit code)?

**Answer:** 2

*How:* Filter ZipCode, or =COUNTIFS(Table1[ZipCode],"<10000") + COUNTIFS(Table1[ZipCode],">99999"). The invalid value is 83.

| If the student gets… | Diagnosis |
|---|---|
| 13 | You included the blank zip codes. Blanks are 'missing', not 'invalid'. |

### FP05 — Which column has the same value for every record? (exact column name)

**Answer:** EventAgency

*How:* Filter each column or use =COUNTA(UNIQUE(column)) = 1.

### FP06 — What is the oldest EnteredOn value? (date and time, YYYY-MM-DD HH:MM)

**Answer:** 2011-12-07 16:38
*Also accepted:* 12/7/2011 16:38, 07-12-2011 16:38, 7 December 2011 16:38

*How:* =MIN(Table1[EnteredOn]) formatted as date-time

| If the student gets… | Diagnosis |
|---|---|
| 2011-09-12 14:08 | Your dates were imported with Danish settings. The file uses US dates (month/day/year), so 7/5/2016 became 7 May and 7/18/2016 stayed as text (and was silently skipped). Re-import with Data > From Text/CSV and set the locale to English (United States), or use Text to Columns with date format MDY. Always check: are the dates right-aligned? |

### FP07 — What is the newest EnteredOn value? (YYYY-MM-DD HH:MM)

**Answer:** 2018-02-09 12:46
*Also accepted:* 2/9/2018 12:46, 09-02-2018 12:46, 9 February 2018 12:46

*How:* =MAX(Table1[EnteredOn])

| If the student gets… | Diagnosis |
|---|---|
| 2018-12-01 21:43 | Your dates were imported with Danish settings. The file uses US dates (month/day/year), so 7/5/2016 became 7 May and 7/18/2016 stayed as text (and was silently skipped). Re-import with Data > From Text/CSV and set the locale to English (United States), or use Text to Columns with date format MDY. Always check: are the dates right-aligned? |

### FP08 — How many different event types are there?

**Answer:** 4

*How:* PivotTable on EventType, or =COUNTA(UNIQUE(Table1[EventType]))

### FP09 — What is the most common event type?

**Answer:** Shooting Permit

*How:* PivotTable: EventType in Rows, Count of EventID in Values, sort descending.

### FP10 — What is the most common Category of shooting permit?

**Answer:** Television

*How:* PivotTable filtered to EventType = Shooting Permit, Category in Rows.

### FP11 — How many shooting permits have been granted for student films?

**Answer:** 193

*How:* =COUNTIFS(Table1[EventType],"Shooting Permit",Table1[Category],"Student")

| If the student gets… | Diagnosis |
|---|---|
| 282 | You did not filter to shooting permits. |

### FP12 — What percentage of shooting permits required approval by more than one Community Board? (percent, 2 decimals)

**Answer:** 7.84 %

*How:* More than one board = the CommunityBoard(s) cell contains a comma: =COUNTIFS(Table1[EventType],"Shooting Permit",Table1[CommunityBoard(s)],"*,*") / COUNTIFS(Table1[EventType],"Shooting Permit")

| If the student gets… | Diagnosis |
|---|---|
| 7.43 | You used all event types as the base. The question is about shooting permits only. |

### FP13 — In what year did shooting permits in Brooklyn first outnumber those in Manhattan (by start date)?

**Answer:** 2,017

*How:* PivotTable: YEAR(StartDateTime) in Rows, Borough in Columns, filtered to Shooting Permit.

### FP14 — What percentage of Manhattan shooting permits take place on or near Broadway (BROADWAY in ParkingHeld)? Round to the nearest percent.

**Answer:** 20 %

*How:* =COUNTIFS(Table1[EventType],"Shooting Permit",Table1[Borough],"Manhattan",Table1[ParkingHeld],"*BROADWAY*") / COUNTIFS(Table1[EventType],"Shooting Permit",Table1[Borough],"Manhattan")

| If the student gets… | Diagnosis |
|---|---|
| 9 | Your denominator was all shooting permits. The question asks for the share of MANHATTAN permits. |

### FP15 — How many shooting permits since 2013 (by EnteredOn) were submitted from a foreign country?

**Answer:** 7

*How:* =COUNTIFS(Table1[EventType],"Shooting Permit",Table1[Country],"<>United States of America",Table1[EnteredOn],">="&DATE(2013,1,1))

| If the student gets… | Diagnosis |
|---|---|
| 26 | You counted all years. 'Since 2013' means EnteredOn on or after 1 Jan 2013. |

### FP16 — What is the average duration of a shooting permit, in hours, rounded to the nearest half hour?

**Answer:** 17 hours

*How:* Helper column =([@EndDateTime]-[@StartDateTime])*24, then AVERAGEIFS over shooting permits; round with =MROUND(x,0.5).

| If the student gets… | Diagnosis |
|---|---|
| 20.50 | You averaged all event types, not only shooting permits. |
| 163 | Your dates were imported with Danish settings. The file uses US dates (month/day/year), so 7/5/2016 became 7 May and 7/18/2016 stayed as text (and was silently skipped). Re-import with Data > From Text/CSV and set the locale to English (United States), or use Text to Columns with date format MDY. Always check: are the dates right-aligned? |
| 0.5 | Excel stores date differences in DAYS. Multiply by 24 to get hours. |

### FP17 — What was the duration of the shortest shoot, in minutes?

**Answer:** 1 minutes

*How:* =MIN(helper duration column)*60 if the helper is in hours (or *1440 if in days).

| If the student gets… | Diagnosis |
|---|---|
| -478,081 | Your dates were imported with Danish settings. The file uses US dates (month/day/year), so 7/5/2016 became 7 May and 7/18/2016 stayed as text (and was silently skipped). Re-import with Data > From Text/CSV and set the locale to English (United States), or use Text to Columns with date format MDY. Always check: are the dates right-aligned? (Negative durations are a sure sign of swapped day and month.) |

### FP18 — What is the average lead time in days between EnteredOn and StartDateTime for shooting permits? Round to the nearest day.

**Answer:** 5 days

*How:* Helper column =[@StartDateTime]-[@EnteredOn], AVERAGEIFS over shooting permits, ROUND(x,0).

| If the student gets… | Diagnosis |
|---|---|
| 6 | You averaged all event types, not only shooting permits. |
| 105 | Your dates were imported with Danish settings. The file uses US dates (month/day/year), so 7/5/2016 became 7 May and 7/18/2016 stayed as text (and was silently skipped). Re-import with Data > From Text/CSV and set the locale to English (United States), or use Text to Columns with date format MDY. Always check: are the dates right-aligned? |

### FP19 — What is the most common day of the week for a shooting permit to start? (full day name)

**Answer:** Thursday

*How:* Helper column =TEXT([@StartDateTime],"dddd") then a PivotTable (set Excel to English or the names will be Danish).

| If the student gets… | Diagnosis |
|---|---|
| Friday | Your dates were imported with Danish settings. The file uses US dates (month/day/year), so 7/5/2016 became 7 May and 7/18/2016 stayed as text (and was silently skipped). Re-import with Data > From Text/CSV and set the locale to English (United States), or use Text to Columns with date format MDY. Always check: are the dates right-aligned? |

### FP20 — What percentage of shooting permits include shooting on at least part of a Friday? (percent, 2 decimals)

**Answer:** 23.65 %

*How:* A permit covers a Friday if any calendar day from INT(Start) to INT(End) is a Friday: e.g. =OR(WEEKDAY([@StartDateTime],2)=5, AND(INT([@EndDateTime])-INT([@StartDateTime])>=MOD(5-WEEKDAY([@StartDateTime],2),7))).

| If the student gets… | Diagnosis |
|---|---|
| 17.93 | You only counted permits STARTING on a Friday. Multi-day permits that start earlier and run into Friday count too. |

## Excel Part 2 · ETL case 1 (messy balance sheet)

### E101 — After cleaning, how many data rows (company-years) remain?

**Answer:** 21

*How:* Remove the duplicated APVO 2018 row (Data > Remove Duplicates).

| If the student gets… | Diagnosis |
|---|---|
| 22 | One row (APVO 2018) appears twice. Duplicates must be removed. |

### E102 — How many distinct companies are in the cleaned data?

**Answer:** 7

*How:* Fix the tickers first: remove the spaces in 'A M Z N' / 'AM ZN' and fill the missing ticker for Armada Hoffler; then count unique tickers.

| If the student gets… | Diagnosis |
|---|---|
| 9 | You counted the raw tickers. 'AMZN', 'A M Z N' and 'AM ZN' are the same company, and the blank ticker is Armada Hoffler (AHH). |
| 8 | You counted the raw non-blank tickers. 'A M Z N' and 'AM ZN' are Amazon (AMZN). |

### E103 — What was Apple's cash in 2017, in dollars?

**Answer:** 20,300,000,000 USD

*How:* '20300 M' means 20,300 million: strip the M and multiply by 1,000,000 (=LEFT(x,LEN(x)-2)*10^6). Watch out: the unquoted comma in 'Apple, Inc.' shifts Apple's columns on import.

| If the student gets… | Diagnosis |
|---|---|
| 20,300 | You removed the 'M' but did not apply the unit. M = million, so multiply by 1,000,000. |
| 20,300,000 | M stands for million (10^6), not thousand. |

### E104 — What was Aehr Test Systems' (AEHR) cash in 2016, in dollars?

**Answer:** 900,000 USD

*How:* '900 K' = 900 thousand = 900,000.

| If the student gets… | Diagnosis |
|---|---|
| 900 | K means thousand: multiply by 1,000. |
| 900,000,000 | K is thousand, not million. |

### E105 — What was American Airlines' (AAL) Total Depreciation in 2017, as a number?

**Answer:** -15,600,000,000

*How:* Accounting notation (15600000000) means NEGATIVE: =-SUBSTITUTE(SUBSTITUTE(x,"(",""),")","") or set the column format on import.

| If the student gets… | Diagnosis |
|---|---|
| 15,600,000,000 | Parentheses mean a negative number in accounting notation. Depreciation is negative here, as in the other rows. |

### E106 — What were American Airlines' (AAL) Total Current Assets in 2016, in dollars?

**Answer:** 10,300,000,000 USD

*How:* This column is in millions (compare with Cash + Receivables + Inventories for the same row): 10300 * 1,000,000.

| If the student gets… | Diagnosis |
|---|---|
| 10,300 | This column is in millions. Cash alone is $3.2 billion, so total current assets can't be $10,300. Multiply by 1,000,000. |
| 10,300,000 | Check the scale: thousands would make total current assets ($10.3m) smaller than cash ($3.2bn). It's millions. |

### E107 — What were Aerocentury's (ACY) inventories in 2017 after cleaning?

**Answer:** 0

*How:* '-' is the accounting symbol for zero; replace it with 0 (Find & Replace, match entire cell).

## Excel Part 2 · ETL case 2 (text extraction)

### E201 — How many different plants does the company have (unique LocationPlantID such as USA-12)?

**Answer:** 133

*How:* LocationPlantID = LEFT(code,3)&"-"&MID(code,FIND("-",code)+1,2); then =COUNTA(UNIQUE(range)).

| If the student gets… | Diagnosis |
|---|---|
| 17 | You counted unique PlantIDs only. Every country numbers its plants from 10, so plant 12 in the USA and plant 12 in Japan are different plants. That's why the case asks you to build LocationPlantID as the unique identifier. |

### E202 — Which plant (LocationPlantID) has the most employees?

**Answer:** ARG-15 (11 employees)

*How:* PivotTable with LocationPlantID in Rows, count of EmpID, sort descending.

| If the student gets… | Diagnosis |
|---|---|
| 24 | That's a PlantID without its country. Report the LocationPlantID (e.g. USA-12). |

### E203 — How many employees in Germany are paid weekly?

**Answer:** 29

*How:* =COUNTIFS(Location,"GER",PayPeriod,"W") with PayPeriod = RIGHT(code,1).

| If the student gets… | Diagnosis |
|---|---|
| 258 | You counted weekly-paid employees in all countries. |

## Excel Part 2 · ETL case 3 (messy text extraction)

### E301 — How many employees are paid monthly?

**Answer:** 339

*How:* Pay period is written 'M' or 'Mo'. Standardise first: =IF(LEFT(RIGHT(code,2),1)="M","M",RIGHT(code,1)) or Flash Fill, then COUNTIF.

| If the student gets… | Diagnosis |
|---|---|
| 158 | RIGHT(code,1) misses the codes ending in 'Mo'. Monthly is written two ways: 'M' and 'Mo'. |

### E302 — How many employees work in the USA?

**Answer:** 86

*How:* Locations are written inconsistently ('US', 'Japan', 'Canada' vs 3-letter codes). Extract the letters before the first digit, then map to standard codes (a small lookup table).

| If the student gets… | Diagnosis |
|---|---|
| 0 | LEFT(code,3) assumes a 3-letter code, but the USA is written 'US' here, so LEFT gives 'US4'. |

### E303 — After standardising, how many different plants (LocationPlantID) are there?

**Answer:** 133

*How:* Location = letters before the first digit (mapped to the 3-letter code); PlantID = digits between '-' and the pay-period letters (1 or 2 digits).

| If the student gets… | Diagnosis |
|---|---|
| 229 | You used fixed positions (LEFT 3 / 2 characters after '-'). In case 3 the location and plant lengths vary, so you got codes like 'Jap-4W'. Extract by pattern, not position. |

## Excel Part 2 · ETL case 4 (journal entries)

### E401 — How many journal lines were prepared by Carolyn Slater?

**Answer:** 182

*How:* PreparerID is NOT unique: 101 is a different person in each business unit. Look up with both keys: =XLOOKUP([@PreparerID]&"|"&[@BusinessUnitID], PreparerInfo[PreparerID]&"|"&PreparerInfo[BusinessUnitID], PreparerInfo[PreparerName], "Not found").

| If the student gets… | Diagnosis |
|---|---|
| 278 | You looked up PreparerID alone. VLOOKUP returns the FIRST 101 it finds (Carolyn Slater), so every 101 line in every business unit was assigned to her. The unique key is PreparerID + BusinessUnitID. |

### E402 — How many journal lines have a PreparerID/BusinessUnitID combination that does not exist in PreparerInfo?

**Answer:** 148

*How:* With the two-key lookup, count the 'Not found' (or #N/A) results.

| If the student gets… | Diagnosis |
|---|---|
| 0 | A lookup on PreparerID alone always finds something, which hides these exceptions. With the correct two-part key, 148 lines have no valid preparer — an audit finding. |

### E403 — What is the net amount (debits minus credits) posted to Expense accounts?

**Answer:** 529,608.13 USD

*How:* XLOOKUP AccountType from ChartOfAccounts on GLAccountNumber, then =SUMIFS(Amount, AccountType, "Expenses"). Amount is already signed (credits negative).

| If the student gets… | Diagnosis |
|---|---|
| 574,505.84 | You summed the Debit column only. Net amount = debits minus credits, which is the signed Amount column. |
| 619,403.55 | Credits are already stored as negative numbers. Debit - Credit double-counts them; use Debit + Credit (or the Amount column). |

### E404 — What is the sum of the Amount column over all journal lines? (A balanced journal should give 0.)

**Answer:** 0 USD

*How:* =SUM(JELineItems[Amount]) — every entry's debits and credits should net to zero.

| If the student gets… | Diagnosis |
|---|---|
| 1,130,428.13 | That's total debits. The signed Amount column should sum to 0 if every entry balances. |

### E405 — After cleaning PreparerName, how many characters long is Carolyn Slater's full entry 'Carolyn Slater|Food Operations Manager'?

**Answer:** 38

*How:* The names are padded with non-breaking spaces (CHAR(160)), which TRIM does not remove: =TRIM(SUBSTITUTE(A2,CHAR(160)," ")).

| If the student gets… | Diagnosis |
|---|---|
| 44 | TRIM only removes normal spaces (CHAR(32)). The padding here is CHAR(160), a non-breaking space; replace it first with SUBSTITUTE. |
| 45 | You didn't clean the name at all: it has trailing non-breaking spaces (CHAR(160)) and a normal space. |

## Excel Part 3 · IntegrateCo payroll

### IC01 — What were total gross wages (regular + overtime pay) in the first six months of 2015?

**Answer:** 1,086,734.19 USD

*How:* =SUM(2015Data[Reg_Pay]) + SUM(2015Data[OT_Pay])

| If the student gets… | Diagnosis |
|---|---|
| 1,072,201.16 | You only summed Reg_Pay. In 2015, gross pay = Reg_Pay + OT_Pay (2016's Gross_Wages already combines them). |
| 1,225,566.22 | You added the payroll taxes and workers' comp. Gross wages are pay only. |

### IC02 — What were total gross wages in the first six months of 2016?

**Answer:** 1,352,789.75 USD

*How:* =SUM(2016Data[Gross_Wages])

| If the student gets… | Diagnosis |
|---|---|
| 1,319,838.46 | You excluded the rows without an employee number. They are still wages the company recorded; the question asks for the total as reported (flag them separately). |

### IC03 — By how much did gross wages increase from H1 2015 to H1 2016? (2016 minus 2015)

**Answer:** 266,055.56 USD

*How:* =IC02 - IC01. Noah's 'about $266,000' should reconcile to this.

| If the student gets… | Diagnosis |
|---|---|
| 280,588.59 | Your 2015 figure left out overtime pay (Reg_Pay only). |
| -266,055.56 | Sign reversed: the case defines differences as 2016 minus 2015 (positive = 2016 higher). |

### IC04 — Which job code (3-digit text) had the largest increase in gross pay from 2015 to 2016? Also give its description.

**Answer:** 009 – New Foreign Manufacturing Plant (+132,294.35)
*Also accepted:* 009 New Foreign Manufacturing Plant, New Foreign Manufacturing Plant

*How:* Add a JobCode column to both years (Job code = the 3 digits after the 2-digit year and the optional H/S letter: =IF(ISNUMBER(--MID([@Job],3,1)), MID([@Job],3,3), MID([@Job],4,3)) — keep it as TEXT so "001" matches the JobCodes table.), then SUMIFS gross pay per code per year and subtract.

| If the student gets… | Diagnosis |
|---|---|
| H00 | Your job codes are wrong for codes with an H or S letter. MID(Job,3,3) on '14H002' returns 'H00'. Check for the letter first. |
| 9 | Right code, but stored as a number. Job codes must stay as 3-digit text ('009'), or lookups to the JobCodes table fail. |

### IC05 — What was the 2016 gross pay per hour for job code 001 (Office)? (2 decimals)

**Answer:** 35.11 USD/hour

*How:* =SUMIFS(gross,code,"001") / SUMIFS(total hours,code,"001"), where total hours = Hours + OT_Hours.

| If the student gets… | Diagnosis |
|---|---|
| 35.40 | You divided by regular hours only. Gross pay includes overtime pay, so divide by regular + overtime hours. |
| 30.05 | You averaged the row-level rates. A weighted rate is total pay / total hours. |

### IC06 — How many 2016 transactions were entered without an employee number ('phantom' entries)?

**Answer:** 68

*How:* =COUNTBLANK(2016Data[Employee_Number])

### IC07 — What is the total gross wage amount of those phantom entries?

**Answer:** 32,951.29 USD

*How:* =SUMIFS(2016Data[Gross_Wages],2016Data[Employee_Number],"")

### IC08 — Which employee earned the most overtime pay in H1 2015, and how much? (enter the amount)

**Answer:** Cindy Lunt (Emp_No 27): 4,186.24

*How:* PivotTable on 2015Data: Emp_No and name in Rows, Sum of OT_Pay, sort descending.

| If the student gets… | Diagnosis |
|---|---|
| 91.50 | That's overtime HOURS. The question asks for overtime pay. |

### IC09 — Which job code had the most overtime pay in 2015?

**Answer:** 006 – Service: 6,007.52
*Also accepted:* Service

*How:* Add JobCode to 2015Data (Job code = the 3 digits after the 2-digit year and the optional H/S letter: =IF(ISNUMBER(--MID([@Job],3,1)), MID([@Job],3,3), MID([@Job],4,3)) — keep it as TEXT so "001" matches the JobCodes table.), PivotTable with JobCode rows and Sum of OT_Pay, sort descending.

| If the student gets… | Diagnosis |
|---|---|
| H00 | Your job codes are wrong for codes with an H or S letter (MID(Job,3,3) on '14H002' gives 'H00'). |

### IC10 — In 2015, how many employee/pay-date combinations show overtime hours even though fewer than 40 regular hours were worked on that pay date?

**Answer:** 103

*How:* Sum Reg_Hrs and OT_Hrs per employee per Pay_Date first (PivotTable or SUMIFS), THEN test Reg < 40 and OT > 0.

| If the student gets… | Diagnosis |
|---|---|
| 190 | You tested individual rows. Each row is only one job code; an employee's hours for the pay period are spread over several rows. Total them per employee and pay date first. |
| 130 | Exactly 40 regular hours is a full week, so overtime is legitimate there. Use < 40. |

### IC11 — What was the total employee cost for all projects in H1 2016 (wages + Social Security/Medicare + FUTA + SUTA + workers' comp)?

**Answer:** 1,486,454.83 USD

*How:* =SUM over the five columns.

| If the student gets… | Diagnosis |
|---|---|
| 1,476,400.65 | You left out workers' compensation. |
| 1,352,789.75 | That's gross wages only. Employee cost adds the employer taxes and workers' comp. |

### IC12 — In 2016, what was the average gross pay per hour at location 1 minus location 2? (2 decimals; phantom entries excluded)

**Answer:** -4.81 USD/hour
*Note:* Location 1: 30.84/h, location 2: 35.65/h. Unmatched names: 0.

*How:* XLOOKUP each employee's Location from the P4 Location tab, then per location: SUM(Gross_Wages)/SUM(Hours+OT_Hours).

| If the student gets… | Diagnosis |
|---|---|
| -4.76 | You divided by regular hours only. |
| -14.81 | You averaged row-level rates instead of total pay / total hours. |

### IC13 — In which month of H1 2015 were gross wages highest (so Noah needs extra cash)?

**Answer:** May
*Note:* May is about $43,000 above the next-highest month. It had 7 pay dates (5 Friday paydays + 2 other runs), but so did January, so the pay-date count alone does not explain it — worth investigating.

*How:* Add =MONTH([@Pay_Date]) to 2015Data (check that Pay_Date imported as real dates), then SUMIFS gross pay per month.

| If the student gets… | Diagnosis |
|---|---|
| June | Your pay dates were read as day/month (Danish settings). The file uses US dates: 1/9/2015 is 9 January, not 1 September, and 1/16/2015 stays as text. Re-import with locale English (United States). |

### IC14 — Job codes must be 001–012. How many 2015 rows have a job code outside that range?

**Answer:** 1
*Note:* The suffixes R and SH (e.g. 14H001R, 15H010SH) are not in the case description but don't change the job code.

*How:* After extracting the JobCode, look it up in the JobCodes table; count the #N/A results (=COUNTIF(lookup column,"#N/A") or ISNA).

| If the student gets… | Diagnosis |
|---|---|
| 0 | Check again: one Job value ('14S1440') contains '144' as its job code, which is not in the table. |

## SQL Part 1 · Chinook (PwC)

### CH01 — How many columns does the Customer table have?

**Answer:** 13

```sql
SELECT COUNT(*) FROM pragma_table_info('Customer');
```

### CH02 — If you select only the first 5 rows of the Customer table, what is the Country in the last of those rows?

**Answer:** Czech Republic

```sql
SELECT Country FROM (SELECT * FROM Customer LIMIT 5) LIMIT 1 OFFSET 4;
```

| If the student gets… | Diagnosis |
|---|---|
| Brazil | You sorted before taking the first 5 rows. The question asks for the first 5 rows as stored (no ORDER BY). |

### CH03 — If you sort the Customer table on last name (A to Z), what is the last name in the third row?

**Answer:** Bernard

```sql
SELECT LastName FROM Customer ORDER BY LastName LIMIT 1 OFFSET 2;
```

| If the student gets… | Diagnosis |
|---|---|
| Wichterlová | You sorted Z to A. ORDER BY is ascending by default; don't add DESC. |
| Brooks | Off by one: OFFSET 2 skips two rows and returns the third. OFFSET 3 returns the fourth. |

### CH04 — How many rows are in the Invoice table?

**Answer:** 412

```sql
SELECT COUNT(*) FROM Invoice;
```

### CH05 — How many invoices have totals greater than $20?

**Answer:** 4

```sql
SELECT COUNT(*) FROM Invoice WHERE Total > 20;
```

### CH06 — How many invoices have totals greater than $10 and less than $20?

**Answer:** 60

```sql
SELECT COUNT(*) FROM Invoice WHERE Total > 10 AND Total < 20;
```

| If the student gets… | Diagnosis |
|---|---|
| 412 | You used OR. Every invoice is either above 10 or below 20, so OR returns (almost) everything. Both conditions must hold: AND. |

### CH07 — How many invoices are from customers in Brazil, Argentina or Chile?

**Answer:** 49

```sql
SELECT COUNT(*) FROM Invoice WHERE BillingCountry IN ('Brazil','Argentina','Chile');
```

| If the student gets… | Diagnosis |
|---|---|
| 0 | A single invoice can't be in two countries at once, so AND returns 0. Use IN (...) or OR. |

### CH08 — How many invoices have a billing country that starts with 'C'?

**Answer:** 77

```sql
SELECT COUNT(*) FROM Invoice WHERE BillingCountry LIKE 'C%';
```

| If the student gets… | Diagnosis |
|---|---|
| 112 | '%C%' finds a C anywhere (and LIKE ignores case in SQLite, so every 'c' counts too). 'Starts with' is 'C%'. |

### CH09 — How many customers list their company?

**Answer:** 10

```sql
SELECT COUNT(Company) FROM Customer;
```

| If the student gets… | Diagnosis |
|---|---|
| 59 | COUNT(*) counts every customer. COUNT(Company) counts only the rows where Company is filled in (not NULL). |

### CH10 — How many employees does Chinook have?

**Answer:** 8

```sql
SELECT COUNT(*) FROM Employee;
```

### CH11 — How long (in characters) is the longest employee last name?

**Answer:** 8

```sql
SELECT MAX(LENGTH(LastName)) FROM Employee;
```

| If the student gets… | Diagnosis |
|---|---|
| 12 | You measured the Customer table. The question is about employees. |

### CH12 — How many employees were born on a Sunday?

**Answer:** 2

```sql
SELECT COUNT(*) FROM Employee WHERE strftime('%w', BirthDate) = '0';
```

| If the student gets… | Diagnosis |
|---|---|
| 0 | In SQLite strftime('%w') returns 0-6 with Sunday = 0. There is no 7. |
| 1 | Sunday is '0' in strftime('%w'); '1' is Monday. (Excel's WEEKDAY uses Sunday = 1, so it's easy to mix up.) |

### CH13 — How old (in years) was the oldest employee when they were hired? Round to one decimal.

**Answer:** 55.60 years

```sql
SELECT ROUND(MAX((julianday(HireDate) - julianday(BirthDate)) / 365.25), 1) FROM Employee;
```

| If the student gets… | Diagnosis |
|---|---|
| 56 | You subtracted calendar years only. That ignores whether the birthday had passed. Use the difference in days / 365.25. |
| 79.20 | You computed age today, not age at the hire date. |

### CH14 — Which billing country has the highest total invoice value?

**Answer:** USA

```sql
SELECT BillingCountry FROM Invoice GROUP BY BillingCountry ORDER BY SUM(Total) DESC LIMIT 1;
```

| If the student gets… | Diagnosis |
|---|---|
| Argentina | You sorted ascending, which gives the lowest total. |

### CH15 — How many invoice line items are there?

**Answer:** 2,240

```sql
SELECT COUNT(*) FROM InvoiceLine;
```

| If the student gets… | Diagnosis |
|---|---|
| 412 | That's the number of invoices. Each invoice has several line items in InvoiceLine. |

### CH16 — How many downloads at the $0.99 price have happened?

**Answer:** 2,129

```sql
SELECT SUM(Quantity) FROM InvoiceLine WHERE UnitPrice = 0.99;
```

| If the student gets… | Diagnosis |
|---|---|
| 3,290 | You counted tracks in the catalogue. Downloads are sales, which are in InvoiceLine. |

### CH17 — How many tracks have been downloaded the maximum number of times (i.e. are tied for most downloads)?

**Answer:** 256

```sql
SELECT COUNT(*) FROM (SELECT TrackId, SUM(Quantity) AS n FROM InvoiceLine GROUP BY TrackId)
WHERE n = (SELECT MAX(n) FROM (SELECT SUM(Quantity) AS n FROM InvoiceLine GROUP BY TrackId));
```

| If the student gets… | Diagnosis |
|---|---|
| 1,984 | That's the number of tracks downloaded at least once. Find the maximum downloads per track, then count tracks at that maximum. |
| 2 | That's the maximum number of downloads (2), not the number of tracks that reached it. 'Top 5' would be misleading here: hundreds of tracks are tied. |

### CH18 — How many days separate the first and the last invoice date?

**Answer:** 1,816 days
*Note:* About 5 years.

```sql
SELECT julianday(MAX(InvoiceDate)) - julianday(MIN(InvoiceDate)) FROM Invoice;
```

| If the student gets… | Diagnosis |
|---|---|
| 4 | Subtracting the date text gives the difference in years only (2013 - 2009). Convert with julianday() to get days. |

### CH19 — An album counts as downloaded when ALL its tracks appear on a single invoice. How many distinct albums have been downloaded?

**Answer:** 41
*Note:* Every album that qualifies has only one track, so the definition is weaker than it sounds.

```sql
SELECT COUNT(DISTINCT a.AlbumId) FROM Album a
WHERE EXISTS (
  SELECT 1 FROM InvoiceLine il JOIN Track t ON t.TrackId = il.TrackId
  WHERE t.AlbumId = a.AlbumId GROUP BY il.InvoiceId
  HAVING COUNT(DISTINCT il.TrackId) = (SELECT COUNT(*) FROM Track t2 WHERE t2.AlbumId = a.AlbumId));
```

| If the student gets… | Diagnosis |
|---|---|
| 304 | You counted albums with at least one track sold. Under the stated definition, all the album's tracks must be on the same invoice. |
| 49 | You counted complete-album purchases (invoice + album pairs). Some albums were bought on more than one invoice, so count DISTINCT AlbumId. (The PwC answer sheet reports 49, which is this purchase count.) |

### CH20 — What is the most popular genre (by tracks sold)?

**Answer:** Rock

```sql
SELECT g.Name FROM InvoiceLine il JOIN Track t ON t.TrackId = il.TrackId JOIN Genre g ON g.GenreId = t.GenreId
GROUP BY g.Name ORDER BY SUM(il.Quantity) DESC LIMIT 1;
```

### CH21 — Show customer names (first and last), invoice IDs and totals for invoices billed to the United Kingdom. How many rows?

**Answer:** 21 rows

```sql
SELECT c.FirstName, c.LastName, i.InvoiceId, i.Total FROM Invoice i JOIN Customer c ON c.CustomerId = i.CustomerId
WHERE i.BillingCountry = 'United Kingdom';
```

| If the student gets… | Diagnosis |
|---|---|
| 0 | The data spells it 'United Kingdom'. Check the values first with SELECT DISTINCT BillingCountry. |
| 1,239 | You listed both tables without a join condition (a cross join), so every invoice was paired with every customer. Join ON CustomerId. |

## SQL Part 1 · CS50 songs

### SG01 — List the names and energy of all songs.

**Answer:** 100 rows

```sql
SELECT name, energy FROM songs;
```

### SG02 — List the names of all songs in decreasing order of tempo.

**Answer:** 100 rows

```sql
SELECT name FROM songs ORDER BY tempo DESC;
```

### SG03 — List the names of the 3 longest songs, longest first. What is the name of the longest song?

**Answer:** Te Bote - Remix

```sql
SELECT name FROM songs ORDER BY duration_ms DESC LIMIT 3;
```

| If the student gets… | Diagnosis |
|---|---|
| Everybody Dies In Their Nightmares | You sorted ascending, which gives the shortest songs. |

### SG04 — List the names of songs with danceability, energy and valence all greater than 0.6. How many songs?

**Answer:** 23 rows

```sql
SELECT name FROM songs WHERE danceability > 0.6 AND energy > 0.6 AND valence > 0.6;
```

| If the student gets… | Diagnosis |
|---|---|
| 91 | All three conditions must hold, so combine them with AND, not OR. |

### SG05 — What is the average tempo of all songs?

**Answer:** 119.90

```sql
SELECT AVG(tempo) FROM songs;
```

### SG06 — List the names of songs by Drake (don't assume his artist_id). How many songs?

**Answer:** 4 rows

```sql
SELECT name FROM songs WHERE artist_id = (SELECT id FROM artists WHERE name = 'Drake');
```

| If the student gets… | Diagnosis |
|---|---|
| 1 | You searched the song titles. The artist is in the artists table: look up Drake's id there (subquery or JOIN). |

### SG07 — What is the average energy of songs by Post Malone?

**Answer:** 0.6088

```sql
SELECT AVG(energy) FROM songs WHERE artist_id = (SELECT id FROM artists WHERE name = 'Post Malone');
```

| If the student gets… | Diagnosis |
|---|---|
| 0.6591 | You averaged every song. Filter to Post Malone's artist_id. |

### SG08 — List the names of songs that feature other artists ('feat.' in the name). How many songs?

**Answer:** 18 rows

```sql
SELECT name FROM songs WHERE name LIKE '%feat.%';
```

| If the student gets… | Diagnosis |
|---|---|
| 0 | 'feat.' appears in the middle of the title, so you need a wildcard on both sides: '%feat.%'. |

## SQL Part 1 · CS50 movies

### MV01 — How many movies were released in 2007?

**Answer:** 8,214

```sql
SELECT COUNT(*) FROM movies WHERE year = 2007;
```

### MV02 — What is Johnny Depp's birth year?

**Answer:** 1,963

```sql
SELECT birth FROM people WHERE name = 'Johnny Depp';
```

### MV03 — How many movies have a release year of 2017 or later?

**Answer:** 68,236

```sql
SELECT COUNT(*) FROM movies WHERE year >= 2017;
```

| If the student gets… | Diagnosis |
|---|---|
| 50,863 | 'On or after 2017' includes 2017: use >=. |

### MV04 — How many movies have an IMDb rating greater than 9.0?

**Answer:** 1,297

```sql
SELECT COUNT(*) FROM ratings WHERE rating > 9.0;
```

| If the student gets… | Diagnosis |
|---|---|
| 1,890 | 'Greater than 9.0' excludes 9.0 itself. |

### MV05 — How many Toy Story movies are there (titles beginning with 'Toy Story')?

**Answer:** 5

```sql
SELECT COUNT(*) FROM movies WHERE title LIKE 'Toy Story%';
```

| If the student gets… | Diagnosis |
|---|---|
| 6 | '%Toy Story%' also finds titles that merely contain the phrase. The question says the title begins with it. |

### MV06 — What is the average rating of movies released in 2012? (round to 2 decimals)

**Answer:** 6.25

```sql
SELECT ROUND(AVG(rating),2) FROM ratings JOIN movies ON movies.id = ratings.movie_id WHERE year = 2012;
```

| If the student gets… | Diagnosis |
|---|---|
| 6.15 | You averaged all years. Join to movies and filter on year. |

### MV07 — How many movies released in 2010 have a rating?

**Answer:** 6,864

```sql
SELECT COUNT(*) FROM movies JOIN ratings ON movies.id = ratings.movie_id WHERE year = 2010;
```

| If the student gets… | Diagnosis |
|---|---|
| 11,708 | You counted all 2010 movies, including those without a rating. An inner JOIN with ratings keeps only rated movies. |

### MV08 — How many people starred in 'Harry Potter and the Sorcerer''s Stone'?

**Answer:** 4

```sql
SELECT COUNT(*) FROM stars WHERE movie_id = (SELECT id FROM movies WHERE title = 'Harry Potter and the Sorcerer''s Stone');
```

### MV09 — How many different people starred in a movie released in 2004?

**Answer:** 18,251

```sql
SELECT COUNT(DISTINCT person_id) FROM stars JOIN movies ON movies.id = stars.movie_id WHERE year = 2004;
```

| If the student gets… | Diagnosis |
|---|---|
| 21,484 | People who starred in several 2004 movies were counted more than once. Use COUNT(DISTINCT person_id). |

### MV10 — How many different people have directed a movie with a rating of at least 9.0?

**Answer:** 1,887

```sql
SELECT COUNT(DISTINCT d.person_id) FROM directors d JOIN ratings r ON r.movie_id = d.movie_id WHERE r.rating >= 9.0;
```

| If the student gets… | Diagnosis |
|---|---|
| 1,282 | 'At least 9.0' includes 9.0: use >=. |
| 1,975 | Directors with several such movies were counted more than once. Use DISTINCT. |

### MV11 — What is the title of the highest-rated movie Helena Bonham Carter starred in?

**Answer:** The King's Speech
*Also accepted:* Night Will Fall
*Note:* Two movies tie at 8.0 (The King's Speech and Night Will Fall); both are accepted. LIMIT 1 hides a tie — worth saying in the oral exam.

```sql
SELECT title FROM movies JOIN stars ON stars.movie_id = movies.id JOIN ratings ON ratings.movie_id = movies.id
WHERE stars.person_id = (SELECT id FROM people WHERE name = 'Helena Bonham Carter') ORDER BY rating DESC LIMIT 1;
```

### MV12 — How many movies starred both Johnny Depp and Helena Bonham Carter?

**Answer:** 6

```sql
SELECT COUNT(*) FROM (
  SELECT movie_id FROM stars WHERE person_id = (SELECT id FROM people WHERE name = 'Johnny Depp')
  INTERSECT
  SELECT movie_id FROM stars WHERE person_id = (SELECT id FROM people WHERE name = 'Helena Bonham Carter'));
```

| If the student gets… | Diagnosis |
|---|---|
| 100 | You counted movies with EITHER actor. 'Both' needs the intersection of their two movie lists. |

### MV13 — How many different people starred in a movie with Kevin Bacon (born 1958), not counting Kevin Bacon himself?

**Answer:** 176

```sql
SELECT COUNT(DISTINCT p.id) FROM people p JOIN stars s ON s.person_id = p.id
WHERE s.movie_id IN (SELECT movie_id FROM stars WHERE person_id = (SELECT id FROM people WHERE name = 'Kevin Bacon' AND birth = 1958))
AND p.id <> (SELECT id FROM people WHERE name = 'Kevin Bacon' AND birth = 1958);
```

| If the student gets… | Diagnosis |
|---|---|
| 177 | You included Kevin Bacon himself. Exclude his id. |
| 180 | There is more than one Kevin Bacon in the database. Use only the one born in 1958. |
| 183 | People who appeared with him in several movies were counted several times. Use DISTINCT. |

## SQL Part 1 · Fiftyville (optional)

### FV01 — Who stole the CS50 duck? (Theft on 28 July 2020, Chamberlin Street.)

**Answer:** Ernest
*Note:* Start at crime_scene_reports, then follow each of the three witness interviews.

```sql
WITH lot AS (SELECT license_plate FROM courthouse_security_logs WHERE year=2020 AND month=7 AND day=28 AND hour=10 AND minute BETWEEN 15 AND 25 AND activity='exit'),
atm AS (SELECT b.person_id FROM atm_transactions a JOIN bank_accounts b USING(account_number) WHERE year=2020 AND month=7 AND day=28 AND atm_location='Fifer Street' AND transaction_type='withdraw'),
calls AS (SELECT caller, receiver FROM phone_calls WHERE year=2020 AND month=7 AND day=28 AND duration < 60),
flight AS (SELECT f.id FROM flights f JOIN airports a ON a.id=f.origin_airport_id WHERE a.city='Fiftyville' AND year=2020 AND month=7 AND day=29 ORDER BY hour, minute LIMIT 1)
SELECT p.name FROM people p
WHERE p.license_plate IN (SELECT license_plate FROM lot)
AND p.id IN (SELECT person_id FROM atm)
AND p.phone_number IN (SELECT caller FROM calls)
AND p.passport_number IN (SELECT passport_number FROM passengers WHERE flight_id = (SELECT id FROM flight));
```

| If the student gets… | Diagnosis |
|---|---|
| Danielle | Danielle passes most checks but did not make a phone call of under a minute that day. Raymond's clue (call < 60 seconds) rules her out. |
| Russell | Russell fits the car, the ATM and the short call, but he was not on the earliest flight out of Fiftyville on 29 July. |

### FV02 — Which city did the thief escape to?

**Answer:** London

```sql
SELECT a.city FROM flights f JOIN airports a ON a.id = f.destination_airport_id
JOIN airports o ON o.id = f.origin_airport_id
WHERE o.city = 'Fiftyville' AND year = 2020 AND month = 7 AND day = 29 ORDER BY hour, minute LIMIT 1;
```

| If the student gets… | Diagnosis |
|---|---|
| Fiftyville | That's where the flight left from. Join the DESTINATION airport to get the escape city. |

### FV03 — Who is the thief's accomplice?

**Answer:** Berthold

```sql
SELECT r.name FROM phone_calls c JOIN people t ON t.phone_number = c.caller JOIN people r ON r.phone_number = c.receiver
WHERE t.name = 'Ernest' AND year = 2020 AND month = 7 AND day = 28 AND duration < 60;
```

## SQL Part 2 · OSU P-cards

### PC01 — What is the total number of P-card transactions in the database? (TotalTrans)

**Answer:** 489,178

```sql
SELECT COUNT(*) AS TotalTrans FROM pcards;
```

| If the student gets… | Diagnosis |
|---|---|
| 489,043 | You counted a column that contains blanks. COUNT(column) skips NULLs, and 135 transactions have no Description. Use COUNT(*) (the case itself warns about this). |
| 473,336 | You left out the returns. Returns are transactions too; they are stored as negative amounts. |

### PC02 — How many P-card transactions are for amounts of $5,000 or more? (TotalTransGT5k)

**Answer:** 1,187

```sql
SELECT COUNT(*) AS TotalTransGT5k FROM pcards WHERE Amount >= 5000;
```

| If the student gets… | Diagnosis |
|---|---|
| 1,098 | The question says 'more than or equal to $5,000'. You used > instead of >=, which drops transactions of exactly $5,000. |
| 1,195 | You also counted large returns (negative amounts) by using ABS(). Only charges of $5,000 or more are asked for. |

### PC03 — What is the total dollar amount of returns from January to March 2014, inclusive? (TotalReturns2014Q1)

**Answer:** -157,882.08 USD

```sql
SELECT ROUND(SUM(Amount),2) AS TotalReturns2014Q1 FROM pcards WHERE Year = 2014 AND Month BETWEEN 1 AND 3 AND Amount < 0;
```

| If the student gets… | Diagnosis |
|---|---|
| 8,260,485.47 | You summed all transactions in the quarter (purchases minus returns). Returns are the negative amounts: add WHERE Amount < 0. |
| -700,159.33 | You included January to March of every year in the database, not only 2014. |
| -100,928.82 | 'January to March, inclusive' includes March. Use Month BETWEEN 1 AND 3 (or <= 3). |
| 157,882.08 | Right amount, wrong sign. Returns are stored as negative numbers, so the total of returns is negative. Saying 'returns of $X' in words is fine; the query result is negative. |

### PC04 — How many P-card transactions took place in the 2013 calendar year (by TransactionDate)?

**Answer:** 116,595

```sql
SELECT COUNT(*) AS TotalTrans FROM pcards WHERE Year = 2013;
```

| If the student gets… | Diagnosis |
|---|---|
| 116,565 | You used PostedDate. The case says to use TransactionDate for all date questions unless stated otherwise. |
| 149,274 | TransactionDate is stored as TEXT ('7/26/2014 0:00:00'), so BETWEEN compares letters, not dates. Use the Year column or convert the text to a real date first. |

### PC05 — Which cardholder had the most transactions in 2014? Enter the number of transactions (NumTrans).

**Answer:** G Hines with 3510 transactions

```sql
SELECT CardholderFirstInitial||' '||CardholderLastName AS Name, COUNT(*) AS NumTrans FROM pcards WHERE Year = 2014 GROUP BY Name ORDER BY NumTrans DESC LIMIT 1;
```

| If the student gets… | Diagnosis |
|---|---|
| 3,634 | You grouped by last name only, so different people with the same surname were merged (top: Hines). The case says a person is the combination of first initial AND last name. |
| 6,316 | You counted every year in the database. Restrict to 2014. |

### PC06 — Who returned the greatest dollar amount of goods in 2014? Enter that total returned amount (ReturnedGoodsValue).

**Answer:** J Heusel: -21898.28 over 126 returns

```sql
SELECT CardholderFirstInitial||' '||CardholderLastName AS Name, ROUND(SUM(Amount),2) AS ReturnedGoodsValue, COUNT(*) AS ReturnedGoodsCount FROM pcards WHERE Year = 2014 AND Amount < 0 GROUP BY Name ORDER BY ReturnedGoodsValue ASC LIMIT 1;
```

| If the student gets… | Diagnosis |
|---|---|
| -0.01 | You sorted descending. Returns are negative, so the LARGEST return is the most negative number: sort ascending (or sort by ABS). |
| 21,898.28 | Right person and amount, but the sign is flipped. Returns are negative in this data. |

### PC07 — How many cardholders had more than 10 transactions in 2014?

**Answer:** 1,515

```sql
SELECT COUNT(*) FROM (SELECT CardholderFirstInitial||' '||CardholderLastName AS Name FROM pcards WHERE Year = 2014 GROUP BY Name HAVING COUNT(*) > 10);
```

| If the student gets… | Diagnosis |
|---|---|
| 1,541 | 'More than 10' means 11 or more. You used >= 10. |
| 1,266 | You grouped by last name only, merging different people. Use first initial + last name. |
| 3,884 | You used all years. Restrict to 2014 BEFORE grouping (WHERE), then filter groups with HAVING. |

### PC08 — Assume all purchases are net of the 4.5% state sales tax. How much sales tax did OSU avoid on P-card transactions in 2014? (SalesTaxSaved)

**Answer:** 1,507,686.68 USD

```sql
SELECT ROUND(SUM(Amount)*0.045,2) AS SalesTaxSaved FROM pcards WHERE Year = 2014;
```

| If the student gets… | Diagnosis |
|---|---|
| 1,536,011.71 | You excluded returns. Returned goods were never really bought, so no tax was saved on them: use the net total including the negative amounts. |
| 15,076,866.75 | 4.5% is 0.045, not 0.45. |
| 1,055,380.67 | That is the 70% version (OSU pays tax in other states 30% of the time). This question asks for 100%. |

### PC09 — OSU would earn 0.75% on Amazon.com transactions of $500 and more and 0.50% on those under $500. What would OSU have earned in 2014? (AmazonEarnings)

**Answer:** 2,593.74 USD

```sql
SELECT ROUND(SUM(CASE WHEN Amount >= 500 THEN Amount*0.0075 ELSE Amount*0.005 END),2) AS AmazonEarnings FROM pcards WHERE Year = 2014 AND LOWER(Vendor) = 'amazon.com';
```

| If the student gets… | Diagnosis |
|---|---|
| 2,583.19 | In SQLite, = is case-sensitive, so 'AMAZON.COM' (28 transactions) was left out. The case was written for Access, where comparisons ignore case. Use LOWER(Vendor) = 'amazon.com'. |
| 5,215.06 | LIKE '%amazon%' also catches Marketplace, Kindle, Prime, Amazon Web Services and claim adjustments. The question is about the vendor Amazon.com only. |
| 2,632.80 | You dropped Amazon returns. Commission is clawed back when goods are returned, so returns reduce earnings. |

### PC10 — How many 2014 transactions are greater than the average transaction amount for 2014?

**Answer:** 29,640

```sql
SELECT COUNT(*) FROM pcards WHERE Year = 2014 AND Amount > (SELECT AVG(Amount) FROM pcards WHERE Year = 2014);
```

| If the student gets… | Diagnosis |
|---|---|
| 25,900 | Your subquery averaged ALL years. The benchmark must be the 2014 average, so the subquery also needs WHERE Year = 2014. |
| 28,148 | Your average excluded returns, which raises the benchmark. The average transaction includes returns. |

### PC11 — Control: a user shall not spend more than $50,000 per year. How many cardholders spent more than $50,000 in 2014?

**Answer:** 127

```sql
SELECT COUNT(*) FROM (SELECT CardholderFirstInitial||' '||CardholderLastName AS Name, SUM(Amount) AS Total FROM pcards WHERE Year = 2014 GROUP BY Name HAVING Total > 50000);
```

| If the student gets… | Diagnosis |
|---|---|
| 130 | You ignored returns. Spending against a limit is net of credits; gross charges overstate violations. |
| 141 | You grouped by last name only. Several people share a surname, so their spending was added together, creating false violations. |

### PC12 — Control: no more than $10,000 per month without approval. How many cardholder-months in 2014 exceeded $10,000?

**Answer:** 457

```sql
SELECT COUNT(*) FROM (SELECT CardholderFirstInitial||' '||CardholderLastName AS Name, Month, SUM(Amount) AS Total FROM pcards WHERE Year = 2014 GROUP BY Name, Month HAVING Total > 10000);
```

| If the student gets… | Diagnosis |
|---|---|
| 161 | You counted people, not person-months. The test is per month, so someone over the limit in 3 months counts 3 times. |
| 464 | You ignored returns, which overstates monthly spending. |

### PC13 — Control: no single transaction above $5,000. How many 2014 transactions were for more than $5,000?

**Answer:** 33

```sql
SELECT COUNT(*) FROM pcards WHERE Year = 2014 AND Amount > 5000;
```

| If the student gets… | Diagnosis |
|---|---|
| 53 | The limit is 'more than $5,000'. A transaction of exactly $5,000 is within the limit, so it is not a violation. |
| 1,098 | You tested every year. The audit covers 2014. |

### PC14 — Control: a purchase over $5,000 must not be split between several swipes by the same person. How many 2014 transactions are flagged (same person, same vendor, same day, more than one transaction, combined total over $5,000)?

**Answer:** 254

```sql
SELECT COUNT(*) FROM pcards p JOIN (
  SELECT CardholderFirstInitial, CardholderLastName, Vendor, TransactionDate
  FROM pcards WHERE Year = 2014
  GROUP BY CardholderFirstInitial, CardholderLastName, Vendor, TransactionDate
  HAVING COUNT(*) > 1 AND SUM(Amount) > 5000) g
 ON p.CardholderFirstInitial = g.CardholderFirstInitial AND p.CardholderLastName = g.CardholderLastName
 AND p.Vendor = g.Vendor AND p.TransactionDate = g.TransactionDate;
```

| If the student gets… | Diagnosis |
|---|---|
| 66 | You counted the groups (person-vendor-days), but the test asks you to display all transaction details, i.e. every transaction in those groups. Join the groups back to the transactions. |
| 285 | You forgot 'more than one transaction for the day'. A single $6,000 swipe is a limit breach (control 3), not a split purchase. |
| 6,394 | You did not require the same vendor. Buying from two different shops on one day is a different test (control 6). |

### PC15 — Benford's law: among 2014 transactions of $1.00 or more, what percentage start with the digit 1? (round to three decimals)

**Answer:** 29.53 %
*Note:* Benford expects 30.103% for digit 1.

```sql
SELECT ROUND(100.0*SUM(substr(CAST(Amount AS TEXT),1,1)='1')/COUNT(*),3) AS PctDigit1
FROM pcards WHERE Year = 2014 AND Amount >= 1;
```

| If the student gets… | Diagnosis |
|---|---|
| 29.57 | You included returns by taking the absolute value. The case says to exclude all numbers less than 1.00, and negative numbers are less than 1. |
| 29.50 | You excluded negatives but kept amounts between $0 and $0.99, whose first character is '0'. Use Amount >= 1. |
| 29.50 | You used every year; the forensic test covers 2014. |

### PC16 — Duplicate payments: same day, same vendor, same cardholder, same amount (returns excluded). How many 2014 transactions are possible duplicates?

**Answer:** 4,924

```sql
SELECT COUNT(*) FROM pcards p JOIN (
  SELECT TransactionDate, Vendor, CardholderFirstInitial, CardholderLastName, Amount
  FROM pcards WHERE Year = 2014 AND Amount > 0
  GROUP BY TransactionDate, Vendor, CardholderFirstInitial, CardholderLastName, Amount
  HAVING COUNT(*) > 1) d
 USING (TransactionDate, Vendor, CardholderFirstInitial, CardholderLastName, Amount)
WHERE p.Year = 2014;
```

| If the student gets… | Diagnosis |
|---|---|
| 1,732 | You counted duplicate GROUPS. The case says that when there are more than two charges, all of them are possible duplicates, so list every transaction in each group. |
| 5,210 | You did not exclude returns. A purchase and a matching refund are not duplicates, and two identical refunds are not payments. |
| 3,192 | You counted only the 'extra' copies. The case asks for all possible duplicate payments for follow-up, including the first one. |

### PC17 — Round-number test: how many 2014 transactions have a four-digit dollar amount ending in 000 (no cents)?

**Answer:** 149

```sql
SELECT COUNT(*) FROM pcards WHERE Year = 2014 AND Amount BETWEEN 1000 AND 9999 AND Amount = CAST(Amount AS INTEGER) AND CAST(Amount AS INTEGER) % 1000 = 0;
```

| If the student gets… | Diagnosis |
|---|---|
| 151 | You did not limit to four digits, so $10,000+ amounts and $0 adjustments were included. |

### PC18 — For November 2014 transactions, what is the largest number of days between TransactionDate and PostedDate (TimeDif)?

**Answer:** 33 days

```sql
SELECT MAX(julianday(printf('%04d-%02d-%02d', cast(substr(substr(PostedDate, instr(PostedDate,'/')+1), instr(substr(PostedDate, instr(PostedDate,'/')+1),'/')+1) as int), cast(PostedDate as int), cast(substr(PostedDate, instr(PostedDate,'/')+1) as int))) - julianday(printf('%04d-%02d-%02d', cast(substr(substr(TransactionDate, instr(TransactionDate,'/')+1), instr(substr(TransactionDate, instr(TransactionDate,'/')+1),'/')+1) as int), cast(TransactionDate as int), cast(substr(TransactionDate, instr(TransactionDate,'/')+1) as int)))) FROM pcards WHERE Year = 2014 AND Month = 11;
```

| If the student gets… | Diagnosis |
|---|---|
| 1 | You subtracted the text dates directly. '11/28/2014' - '12/2/2014' only compares the leading month numbers. Convert the text to a date first (e.g. julianday on an ISO date). |
| 0 | You subtracted in the wrong order. The case says TimeDif is positive when PostedDate is after TransactionDate: PostedDate - TransactionDate. |
