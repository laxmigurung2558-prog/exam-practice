"""SQL Part 1: Chinook (PwC), CS50 songs, movies and Fiftyville.
For the small databases (chinook, songs, fiftyville) the full expected result
is stored so the website can run the student's query in the browser and compare."""
import sqlite3, json, sys
sys.path.insert(0, "/home/claude/work")
from kit import make, scalar, rows

BASE = "/home/claude/mat/2__SQL_part_1/2. SQL part 1/Assignments/"
DBS = {"chinook": BASE + "pwc assignment/Chinook_Sqlite.sqlite",
       "songs": BASE + "cs50 assignment/songs/songs.db",
       "movies": BASE + "cs50 assignment/movies/movies.db",
       "fiftyville": BASE + "cs50 assignment/mystery (OPTIONAL)/fiftyville.db"}
CON = {k: sqlite3.connect(v) for k, v in DBS.items()}
BROWSER_RUNNABLE = {"chinook", "songs", "fiftyville"}
CASES = {"chinook": "SQL Part 1 · Chinook (PwC)", "songs": "SQL Part 1 · CS50 songs",
         "movies": "SQL Part 1 · CS50 movies", "fiftyville": "SQL Part 1 · Fiftyville (optional)"}
Q = []

def add(qid, ds, prompt, sql, traps=(), answer=None, ordered=False, check="value", **kw):
    con = CON[ds]
    cols, data = rows(con, sql)
    single = len(data) == 1 and len(cols) == 1
    is_rowcount = answer is None and not single
    if answer is None:
        answer = data[0][0] if single else len(data)
    if is_rowcount:
        kw.setdefault("answer_label", f"{len(data)} rows")
    t = []
    for tsql, msg in traps:
        tc, td = rows(con, tsql)
        if is_rowcount or not (len(td) == 1 and len(tc) == 1):
            tv = len(td)
        else:
            tv = td[0][0]
        t.append((tv, msg))
    extra = kw.pop("extra", {}) or {}
    if ds in BROWSER_RUNNABLE and len(data) <= 400:
        extra["expected_result"] = {"columns": cols, "rows": [list(r) for r in data], "ordered": ordered}
    extra["runnable_in_browser"] = ds in BROWSER_RUNNABLE
    Q.append(make(qid, ds, "SQL", CASES[ds], prompt, answer, {"sql": sql.strip()}, t, extra=extra, **kw))

# ---------------------------------------------------------------- Chinook
add("CH01", "chinook", "How many columns does the Customer table have?",
    "SELECT COUNT(*) FROM pragma_table_info('Customer');", tol=0)
add("CH02", "chinook", "If you select only the first 5 rows of the Customer table, what is the Country in the last of those rows?",
    "SELECT Country FROM (SELECT * FROM Customer LIMIT 5) LIMIT 1 OFFSET 4;",
    [("SELECT Country FROM (SELECT * FROM Customer ORDER BY Country LIMIT 5) LIMIT 1 OFFSET 4",
      "You sorted before taking the first 5 rows. The question asks for the first 5 rows as stored (no ORDER BY).")])
add("CH03", "chinook", "If you sort the Customer table on last name (A to Z), what is the last name in the third row?",
    "SELECT LastName FROM Customer ORDER BY LastName LIMIT 1 OFFSET 2;",
    [("SELECT LastName FROM Customer ORDER BY LastName DESC LIMIT 1 OFFSET 2",
      "You sorted Z to A. ORDER BY is ascending by default; don't add DESC."),
     ("SELECT LastName FROM Customer ORDER BY LastName LIMIT 1 OFFSET 3",
      "Off by one: OFFSET 2 skips two rows and returns the third. OFFSET 3 returns the fourth.")])
add("CH04", "chinook", "How many rows are in the Invoice table?", "SELECT COUNT(*) FROM Invoice;", tol=0)
add("CH05", "chinook", "How many invoices have totals greater than $20?", "SELECT COUNT(*) FROM Invoice WHERE Total > 20;", tol=0)
add("CH06", "chinook", "How many invoices have totals greater than $10 and less than $20?",
    "SELECT COUNT(*) FROM Invoice WHERE Total > 10 AND Total < 20;",
    [("SELECT COUNT(*) FROM Invoice WHERE Total > 10 OR Total < 20",
      "You used OR. Every invoice is either above 10 or below 20, so OR returns (almost) everything. Both conditions must hold: AND.")], tol=0)
add("CH07", "chinook", "How many invoices are from customers in Brazil, Argentina or Chile?",
    "SELECT COUNT(*) FROM Invoice WHERE BillingCountry IN ('Brazil','Argentina','Chile');",
    [("SELECT COUNT(*) FROM Invoice WHERE BillingCountry = 'Brazil' AND BillingCountry = 'Argentina'",
      "A single invoice can't be in two countries at once, so AND returns 0. Use IN (...) or OR.")], tol=0)
add("CH08", "chinook", "How many invoices have a billing country that starts with 'C'?",
    "SELECT COUNT(*) FROM Invoice WHERE BillingCountry LIKE 'C%';",
    [("SELECT COUNT(*) FROM Invoice WHERE BillingCountry LIKE '%C%'",
      "'%C%' finds a C anywhere (and LIKE ignores case in SQLite, so every 'c' counts too). 'Starts with' is 'C%'.")], tol=0)
add("CH09", "chinook", "How many customers list their company?",
    "SELECT COUNT(Company) FROM Customer;",
    [("SELECT COUNT(*) FROM Customer",
      "COUNT(*) counts every customer. COUNT(Company) counts only the rows where Company is filled in (not NULL).")], tol=0)
add("CH10", "chinook", "How many employees does Chinook have?", "SELECT COUNT(*) FROM Employee;", tol=0)
add("CH11", "chinook", "How long (in characters) is the longest employee last name?",
    "SELECT MAX(LENGTH(LastName)) FROM Employee;",
    [("SELECT MAX(LENGTH(LastName)) FROM Customer",
      "You measured the Customer table. The question is about employees.")], tol=0)
add("CH12", "chinook", "How many employees were born on a Sunday?",
    "SELECT COUNT(*) FROM Employee WHERE strftime('%w', BirthDate) = '0';",
    [("SELECT COUNT(*) FROM Employee WHERE strftime('%w', BirthDate) = '7'",
      "In SQLite strftime('%w') returns 0-6 with Sunday = 0. There is no 7."),
     ("SELECT COUNT(*) FROM Employee WHERE strftime('%w', BirthDate) = '1'",
      "Sunday is '0' in strftime('%w'); '1' is Monday. (Excel's WEEKDAY uses Sunday = 1, so it's easy to mix up.)")], tol=0)
add("CH13", "chinook", "How old (in years) was the oldest employee when they were hired? Round to one decimal.",
    "SELECT ROUND(MAX((julianday(HireDate) - julianday(BirthDate)) / 365.25), 1) FROM Employee;",
    [("SELECT MAX(CAST(strftime('%Y',HireDate) AS INT) - CAST(strftime('%Y',BirthDate) AS INT)) FROM Employee",
      "You subtracted calendar years only. That ignores whether the birthday had passed. Use the difference in days / 365.25."),
     ("SELECT ROUND(MAX((julianday('now') - julianday(BirthDate)) / 365.25), 1) FROM Employee",
      "You computed age today, not age at the hire date.")], tol=0.1, unit="years")
add("CH14", "chinook", "Which billing country has the highest total invoice value?",
    "SELECT BillingCountry FROM Invoice GROUP BY BillingCountry ORDER BY SUM(Total) DESC LIMIT 1;",
    [("SELECT BillingCountry FROM Invoice GROUP BY BillingCountry ORDER BY SUM(Total) ASC LIMIT 1",
      "You sorted ascending, which gives the lowest total.")],
    extra={"follow_up_sql": "SELECT BillingCountry, ROUND(SUM(Total),2) AS TotalValue FROM Invoice GROUP BY BillingCountry ORDER BY TotalValue DESC;"})
add("CH15", "chinook", "How many invoice line items are there?", "SELECT COUNT(*) FROM InvoiceLine;",
    [("SELECT COUNT(*) FROM Invoice", "That's the number of invoices. Each invoice has several line items in InvoiceLine.")], tol=0)
add("CH16", "chinook", "How many downloads at the $0.99 price have happened?",
    "SELECT SUM(Quantity) FROM InvoiceLine WHERE UnitPrice = 0.99;",
    [("SELECT COUNT(*) FROM Track WHERE UnitPrice = 0.99",
      "You counted tracks in the catalogue. Downloads are sales, which are in InvoiceLine.")], tol=0)
add("CH17", "chinook", "How many tracks have been downloaded the maximum number of times (i.e. are tied for most downloads)?",
    """SELECT COUNT(*) FROM (SELECT TrackId, SUM(Quantity) AS n FROM InvoiceLine GROUP BY TrackId)
WHERE n = (SELECT MAX(n) FROM (SELECT SUM(Quantity) AS n FROM InvoiceLine GROUP BY TrackId));""",
    [("SELECT COUNT(DISTINCT TrackId) FROM InvoiceLine",
      "That's the number of tracks downloaded at least once. Find the maximum downloads per track, then count tracks at that maximum."),
     ("SELECT MAX(n) FROM (SELECT SUM(Quantity) n FROM InvoiceLine GROUP BY TrackId)",
      "That's the maximum number of downloads (2), not the number of tracks that reached it. 'Top 5' would be misleading here: hundreds of tracks are tied.")], tol=0)
add("CH18", "chinook", "How many days separate the first and the last invoice date?",
    "SELECT julianday(MAX(InvoiceDate)) - julianday(MIN(InvoiceDate)) FROM Invoice;",
    [("SELECT MAX(InvoiceDate) - MIN(InvoiceDate) FROM Invoice",
      "Subtracting the date text gives the difference in years only (2013 - 2009). Convert with julianday() to get days.")], tol=0, unit="days",
    extra={"note": "About 5 years."})
strict = """SELECT COUNT(DISTINCT a.AlbumId) FROM Album a
WHERE EXISTS (
  SELECT 1 FROM InvoiceLine il JOIN Track t ON t.TrackId = il.TrackId
  WHERE t.AlbumId = a.AlbumId GROUP BY il.InvoiceId
  HAVING COUNT(DISTINCT il.TrackId) = (SELECT COUNT(*) FROM Track t2 WHERE t2.AlbumId = a.AlbumId));"""
add("CH19", "chinook", "An album counts as downloaded when ALL its tracks appear on a single invoice. How many distinct albums have been downloaded?",
    strict,
    [("SELECT COUNT(DISTINCT t.AlbumId) FROM InvoiceLine il JOIN Track t USING (TrackId)",
      "You counted albums with at least one track sold. Under the stated definition, all the album's tracks must be on the same invoice."),
     ("""WITH per AS (SELECT il.InvoiceId, t.AlbumId, COUNT(*) n FROM InvoiceLine il JOIN Track t USING(TrackId) GROUP BY 1,2),
alb AS (SELECT AlbumId, COUNT(*) total FROM Track GROUP BY 1)
SELECT COUNT(*) FROM per JOIN alb USING(AlbumId) WHERE n = total""",
      "You counted complete-album purchases (invoice + album pairs). Some albums were bought on more than one invoice, so count DISTINCT AlbumId. (The PwC answer sheet reports 49, which is this purchase count.)")], tol=0,
    extra={"note": "Every album that qualifies has only one track, so the definition is weaker than it sounds."})
add("CH20", "chinook", "What is the most popular genre (by tracks sold)?",
    """SELECT g.Name FROM InvoiceLine il JOIN Track t ON t.TrackId = il.TrackId JOIN Genre g ON g.GenreId = t.GenreId
GROUP BY g.Name ORDER BY SUM(il.Quantity) DESC LIMIT 1;""")
add("CH21", "chinook", "Show customer names (first and last), invoice IDs and totals for invoices billed to the United Kingdom. How many rows?",
    """SELECT c.FirstName, c.LastName, i.InvoiceId, i.Total FROM Invoice i JOIN Customer c ON c.CustomerId = i.CustomerId
WHERE i.BillingCountry = 'United Kingdom';""",
    [("SELECT * FROM Invoice WHERE BillingCountry = 'UK'",
      "The data spells it 'United Kingdom'. Check the values first with SELECT DISTINCT BillingCountry."),
     ("SELECT c.FirstName FROM Invoice i, Customer c WHERE i.BillingCountry='United Kingdom'",
      "You listed both tables without a join condition (a cross join), so every invoice was paired with every customer. Join ON CustomerId.")],
    tol=0)

# ---------------------------------------------------------------- songs
add("SG01", "songs", "List the names and energy of all songs.", "SELECT name, energy FROM songs;", tol=0)
add("SG02", "songs", "List the names of all songs in decreasing order of tempo.", "SELECT name FROM songs ORDER BY tempo DESC;", ordered=True,
    traps=[], tol=0)
add("SG03", "songs", "List the names of the 3 longest songs, longest first. What is the name of the longest song?",
    "SELECT name FROM songs ORDER BY duration_ms DESC LIMIT 3;", ordered=True,
    answer=scalar(CON["songs"], "SELECT name FROM songs ORDER BY duration_ms DESC LIMIT 1"),
    traps=[("SELECT name FROM songs ORDER BY duration_ms ASC LIMIT 1", "You sorted ascending, which gives the shortest songs.")])
add("SG04", "songs", "List the names of songs with danceability, energy and valence all greater than 0.6. How many songs?",
    "SELECT name FROM songs WHERE danceability > 0.6 AND energy > 0.6 AND valence > 0.6;",
    [("SELECT name FROM songs WHERE danceability > 0.6 OR energy > 0.6 OR valence > 0.6",
      "All three conditions must hold, so combine them with AND, not OR.")], tol=0)
add("SG05", "songs", "What is the average tempo of all songs?", "SELECT AVG(tempo) FROM songs;")
add("SG06", "songs", "List the names of songs by Drake (don't assume his artist_id). How many songs?",
    "SELECT name FROM songs WHERE artist_id = (SELECT id FROM artists WHERE name = 'Drake');",
    [("SELECT name FROM songs WHERE name LIKE '%Drake%'",
      "You searched the song titles. The artist is in the artists table: look up Drake's id there (subquery or JOIN).")], tol=0)
add("SG07", "songs", "What is the average energy of songs by Post Malone?",
    "SELECT AVG(energy) FROM songs WHERE artist_id = (SELECT id FROM artists WHERE name = 'Post Malone');",
    [("SELECT AVG(energy) FROM songs", "You averaged every song. Filter to Post Malone's artist_id.")])
add("SG08", "songs", "List the names of songs that feature other artists ('feat.' in the name). How many songs?",
    "SELECT name FROM songs WHERE name LIKE '%feat.%';",
    [("SELECT name FROM songs WHERE name LIKE 'feat.%'", "'feat.' appears in the middle of the title, so you need a wildcard on both sides: '%feat.%'.")], tol=0)

# ---------------------------------------------------------------- movies (too large for the browser: students enter the number)
add("MV01", "movies", "How many movies were released in 2007?", "SELECT COUNT(*) FROM movies WHERE year = 2007;", tol=0)
add("MV02", "movies", "What is Johnny Depp's birth year?", "SELECT birth FROM people WHERE name = 'Johnny Depp';", tol=0)
add("MV03", "movies", "How many movies have a release year of 2017 or later?", "SELECT COUNT(*) FROM movies WHERE year >= 2017;",
    [("SELECT COUNT(*) FROM movies WHERE year > 2017", "'On or after 2017' includes 2017: use >=.")], tol=0)
add("MV04", "movies", "How many movies have an IMDb rating greater than 9.0?",
    "SELECT COUNT(*) FROM ratings WHERE rating > 9.0;",
    [("SELECT COUNT(*) FROM ratings WHERE rating >= 9.0", "'Greater than 9.0' excludes 9.0 itself.")], tol=0)
add("MV05", "movies", "How many Toy Story movies are there (titles beginning with 'Toy Story')?",
    "SELECT COUNT(*) FROM movies WHERE title LIKE 'Toy Story%';",
    [("SELECT COUNT(*) FROM movies WHERE title LIKE '%Toy Story%'", "'%Toy Story%' also finds titles that merely contain the phrase. The question says the title begins with it.")], tol=0)
add("MV06", "movies", "What is the average rating of movies released in 2012? (round to 2 decimals)",
    "SELECT ROUND(AVG(rating),2) FROM ratings JOIN movies ON movies.id = ratings.movie_id WHERE year = 2012;",
    [("SELECT ROUND(AVG(rating),2) FROM ratings", "You averaged all years. Join to movies and filter on year.")])
add("MV07", "movies", "How many movies released in 2010 have a rating?",
    "SELECT COUNT(*) FROM movies JOIN ratings ON movies.id = ratings.movie_id WHERE year = 2010;",
    [("SELECT COUNT(*) FROM movies WHERE year = 2010", "You counted all 2010 movies, including those without a rating. An inner JOIN with ratings keeps only rated movies.")], tol=0)
add("MV08", "movies", "How many people starred in 'Harry Potter and the Sorcerer''s Stone'?",
    "SELECT COUNT(*) FROM stars WHERE movie_id = (SELECT id FROM movies WHERE title = 'Harry Potter and the Sorcerer''s Stone');", tol=0)
add("MV09", "movies", "How many different people starred in a movie released in 2004?",
    "SELECT COUNT(DISTINCT person_id) FROM stars JOIN movies ON movies.id = stars.movie_id WHERE year = 2004;",
    [("SELECT COUNT(person_id) FROM stars JOIN movies ON movies.id = stars.movie_id WHERE year = 2004",
      "People who starred in several 2004 movies were counted more than once. Use COUNT(DISTINCT person_id).")], tol=0)
add("MV10", "movies", "How many different people have directed a movie with a rating of at least 9.0?",
    "SELECT COUNT(DISTINCT d.person_id) FROM directors d JOIN ratings r ON r.movie_id = d.movie_id WHERE r.rating >= 9.0;",
    [("SELECT COUNT(DISTINCT d.person_id) FROM directors d JOIN ratings r ON r.movie_id = d.movie_id WHERE r.rating > 9.0",
      "'At least 9.0' includes 9.0: use >=."),
     ("SELECT COUNT(d.person_id) FROM directors d JOIN ratings r ON r.movie_id = d.movie_id WHERE r.rating >= 9.0",
      "Directors with several such movies were counted more than once. Use DISTINCT.")], tol=0)
add("MV11", "movies", "What is the title of the highest-rated movie Helena Bonham Carter starred in?",
    """SELECT title FROM movies JOIN stars ON stars.movie_id = movies.id JOIN ratings ON ratings.movie_id = movies.id
WHERE stars.person_id = (SELECT id FROM people WHERE name = 'Helena Bonham Carter') ORDER BY rating DESC LIMIT 1;""",
    extra={"alternatives": ["Night Will Fall"], "note": "Two movies tie at 8.0 (The King's Speech and Night Will Fall); both are accepted. LIMIT 1 hides a tie — worth saying in the oral exam."})
add("MV12", "movies", "How many movies starred both Johnny Depp and Helena Bonham Carter?",
    """SELECT COUNT(*) FROM (
  SELECT movie_id FROM stars WHERE person_id = (SELECT id FROM people WHERE name = 'Johnny Depp')
  INTERSECT
  SELECT movie_id FROM stars WHERE person_id = (SELECT id FROM people WHERE name = 'Helena Bonham Carter'));""",
    [("SELECT COUNT(*) FROM stars WHERE person_id IN (SELECT id FROM people WHERE name IN ('Johnny Depp','Helena Bonham Carter'))",
      "You counted movies with EITHER actor. 'Both' needs the intersection of their two movie lists.")], tol=0)
kb = """SELECT COUNT(DISTINCT p.id) FROM people p JOIN stars s ON s.person_id = p.id
WHERE s.movie_id IN (SELECT movie_id FROM stars WHERE person_id = (SELECT id FROM people WHERE name = 'Kevin Bacon' AND birth = 1958))
AND p.id <> (SELECT id FROM people WHERE name = 'Kevin Bacon' AND birth = 1958);"""
add("MV13", "movies", "How many different people starred in a movie with Kevin Bacon (born 1958), not counting Kevin Bacon himself?",
    kb,
    [(kb.replace("\nAND p.id <> (SELECT id FROM people WHERE name = 'Kevin Bacon' AND birth = 1958)", ""),
      "You included Kevin Bacon himself. Exclude his id."),
     (kb.replace("person_id = (SELECT id FROM people WHERE name = 'Kevin Bacon' AND birth = 1958))", "person_id IN (SELECT id FROM people WHERE name = 'Kevin Bacon'))"),
      "There is more than one Kevin Bacon in the database. Use only the one born in 1958."),
     (kb.replace("COUNT(DISTINCT p.id)", "COUNT(p.id)"),
      "People who appeared with him in several movies were counted several times. Use DISTINCT.")], tol=0)

# ---------------------------------------------------------------- Fiftyville (optional mystery)
FV = open("/tmp/fv.sql").read()
Q.append(make("FV01", "fiftyville", "SQL", CASES["fiftyville"],
    "Who stole the CS50 duck? (Theft on 28 July 2020, Chamberlin Street.)", "Ernest", {"sql": FV.strip() + ";"},
    [("Danielle", "Danielle passes most checks but did not make a phone call of under a minute that day. Raymond's clue (call < 60 seconds) rules her out."),
     ("Russell", "Russell fits the car, the ATM and the short call, but he was not on the earliest flight out of Fiftyville on 29 July.")],
    extra={"note": "Start at crime_scene_reports, then follow each of the three witness interviews.", "runnable_in_browser": True,
           "expected_result": {"columns": ["name"], "rows": [["Ernest"]], "ordered": False}}))
add("FV02", "fiftyville", "Which city did the thief escape to?",
    """SELECT a.city FROM flights f JOIN airports a ON a.id = f.destination_airport_id
JOIN airports o ON o.id = f.origin_airport_id
WHERE o.city = 'Fiftyville' AND year = 2020 AND month = 7 AND day = 29 ORDER BY hour, minute LIMIT 1;""",
    [("""SELECT o.city FROM flights f JOIN airports o ON o.id = f.origin_airport_id WHERE o.city='Fiftyville' AND year=2020 AND month=7 AND day=29 ORDER BY hour, minute LIMIT 1""",
      "That's where the flight left from. Join the DESTINATION airport to get the escape city.")])
add("FV03", "fiftyville", "Who is the thief's accomplice?",
    """SELECT r.name FROM phone_calls c JOIN people t ON t.phone_number = c.caller JOIN people r ON r.phone_number = c.receiver
WHERE t.name = 'Ernest' AND year = 2020 AND month = 7 AND day = 28 AND duration < 60;""")

json.dump(Q, open("/home/claude/work/out_sql1.json", "w"), indent=1)
print(len(Q), "questions")
