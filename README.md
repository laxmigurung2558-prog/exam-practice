# Exam Practice · Data Analytics in Accounting

A practice website for the exam in *Data Analytics in Accounting* (SDU), built only from the course materials (Excel Parts 1–4, SQL Parts 1–2).

The oral exam has two parts, and so does the site:

- **Data Manipulation:** 115 Excel and SQL questions across the course datasets (NYC film permits, ETL cases 1–4, IntegrateCo payroll, Chinook, CS50 songs/movies/Fiftyville, OSU P-cards) and 60 practice exams in the real format (3 Excel + 2 SQL questions on two data files, 8-minute timer)
- **Data Interpretation:** 16 regression questions and 12 exams (4 questions each) built on the restaurant case (Excel Part 4), using models estimated on the real case data
- Dataset downloads for every question

## The added functionality: verified answer checking with mistake diagnosis

Students type the result they got (or, for the smaller SQLite databases, run their query directly in the browser). The site tells them immediately whether it is correct and, if not, **which common mistake produces exactly that number**. Examples:

- 163 hours instead of 17 → the US-formatted dates were imported with Danish settings
- 2,583.19 instead of 2,593.74 → SQLite's `=` is case-sensitive, so `AMAZON.COM` was missed
- 278 instead of 182 → a lookup on `PreparerID` alone, which is not a unique key

179 such mistakes are recognised (for example, plugging Celsius into a model estimated in Fahrenheit, or reading a dummy coefficient as a level instead of a difference). Unknown wrong answers get a targeted hint (wrong sign, off by 100/1,000/24, too many rows from a join, …). Numbers can be typed the Danish or English way.

## How the answers were produced

Every answer was computed from the course data files with the scripts in `tools/`. Each recorded mistake was reproduced by running the mistaken query or calculation, and kept only if it gives a different number from the correct answer. All stored SQL solutions were re-run independently. See `ANSWER_KEY.md` for the full key.

## Files

| Path | Purpose |
|---|---|
| `index.html`, `style.css`, `app.js` | The website (no build step) |
| `checker.js` | Answer parsing, checking and mistake diagnosis |
| `questions.json`, `exams.json` | Question bank and exams |
| `data/` | Course data files offered for download |
| `tools/` | Scripts that computed the answers and mistakes (paths point to the unzipped course materials) |

The in-browser SQL uses [sql.js](https://github.com/sql-js/sql.js) from a CDN. `movies.db` (69 MB) is too large for the repository (GitHub web upload limit: 25 MB), so `movies.db.zip` is attached to the GitHub Release tagged `data`; the site links to it automatically.
