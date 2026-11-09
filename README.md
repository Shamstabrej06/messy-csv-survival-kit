# Messy CSV Survival Kit

**Real messy data in. Clean data out. Every step taught.**

A teach-by-doing kit that takes one real, messy, public dataset — Inside
Airbnb's Toronto listings — and turns it into clean, analysis-ready data,
teaching every cleaning step along the way. Each of the five lessons is a
runnable Python script plus a short markdown lesson explaining **what**
was wrong, **why** it matters, and **how** the fix works, with
before/after samples taken from the real data. Finish the lessons, then
test yourself on the practice set.

## The dataset

| | |
| --- | --- |
| **Dataset** | Inside Airbnb — Toronto `listings.csv`, release 2026-09-16 |
| **Source** | https://data.insideairbnb.com/canada/on/toronto/2026-09-16/data/listings.csv.gz |
| **Licence** | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| **Downloaded** | 2026-11-08 |
| **Full file** | 22,050 rows × 90 columns |
| **Committed sample** | `data/raw/listings_sample_2000.csv` — the first 2,000 rows, untouched |

Inside Airbnb compiles publicly available information from Airbnb; the
data is shared under CC BY 4.0 with attribution, which this repo gives
above and in `data/SOURCE.md`. The full file is 63 MB, so the repo
commits a 2,000-row sample and links the source — the lesson scripts run
unchanged against a locally downloaded full file (just point
`config.py`'s `RAW_PATH` at it).

## Before / after — the scorecard

The sample run, verified by re-running every script from a clean state:

| Step | Rows |
| --- | --- |
| Raw sample | 2,000 |
| Step 1 — Loaded | 2,000 |
| Step 2 — Money & percentages | 2,000 |
| Step 3 — Missing values handled | 1,435 |
| Step 4 — Deduped & normalised | 1,435 |
| **Step 5 — Clean table** | **1,430** |
| Step 5 — Quarantined | 5 |

| Issue | Found | Fixed |
| --- | --- | --- |
| Currency strings in price (`$` / commas) | 1,435 | 1,435 |
| Percentage strings | 0 (both rate columns are blank in this release) | 0 |
| Missing price (essential field) | 565 | 565 rows dropped |
| Missing small numerics (bedrooms / beds / minimum_nights) | 27 | 27 median-filled |
| Missing categoricals (license / host_location / bathrooms_text) | 1,167 | 1,167 filled `"Unknown"` |
| Missing review data (rating / first / last review) | 465 | 0 — left blank by design |
| Duplicate listing ids | 0 | 0 |
| `t`/`f` booleans stored as text | 5,740 | 5,740 converted |
| Whitespace / double spaces in text | 20 | 20 fixed |
| `minimum_nights` over 365 | 3 | 3 (left with the price-missing rows) |
| Price over $5,000 (held for review) | 5 | 5 quarantined |

Clean price after validation: median **$150.76**, mean **$226.81**, range
**$19.90–$3,897.96**. The full diagnosis — including the full-file
22,050-row counts — is in `docs/data_quality_report.md`, and the Excel
scorecard with live formulas is
`outputs/Data_Quality_Scorecard.xlsx`.

## The five lessons

| Lesson | What you learn | Script |
| --- | --- | --- |
| [01 — Reading a hostile CSV](lessons/lesson_01_reading_a_hostile_csv.md) | Read everything as text first, prove the row count, survive quoted commas | `src/lesson_01_load.py` |
| [02 — Money and percentages](lessons/lesson_02_money_and_percentages.md) | Strip `$`, `,` and `%` into real numbers — with an audit of every value that fails | `src/lesson_02_money.py` |
| [03 — Missing values without lying](lessons/lesson_03_missing_values.md) | Drop, median-fill, `"Unknown"`, or leave blank — a different answer per column, each justified | `src/lesson_03_missing.py` |
| [04 — Duplicates and categories](lessons/lesson_04_duplicates_and_categories.md) | Dedup on id, collapse double spaces, turn `t`/`f` into real booleans | `src/lesson_04_dedup.py` |
| [05 — Validate and ship](lessons/lesson_05_validate_and_ship.md) | Range checks, a quarantine file with reasons, SQLite, and the Excel scorecard | `src/lesson_05_validate.py` |

## Quickstart

```bash
git clone https://github.com/Shamstabrej06/messy-csv-survival-kit.git
cd messy-csv-survival-kit
pip install -r requirements.txt

python src/lesson_01_load.py
python src/lesson_02_money.py
python src/lesson_03_missing.py
python src/lesson_04_dedup.py
python src/lesson_05_validate.py
```

Then check yourself with the practice set in `practice/` — three messy
CSVs (easy / medium / hard) made from the real clean output with extra
problems seeded in, and answer keys in `practice/answer_keys/`.

Requirements: Python 3, pandas, openpyxl (SQLite is built in). No paid
tools, no fictional software.

## Repo structure

```
messy-csv-survival-kit/
├── README.md                  # this file
├── config.py                  # single source of truth for file paths
├── requirements.txt           # pandas, openpyxl
├── data/
│   ├── SOURCE.md              # source URL, licence, download date, attribution
│   └── raw/listings_sample_2000.csv   # first 2,000 rows, untouched
├── docs/
│   ├── data_quality_report.md # full diagnosis with real counts
│   └── upwork_portfolio.md    # portfolio copy for Upwork / LinkedIn
├── lessons/                   # one beginner lesson per cleaning step
├── src/                       # one runnable script per lesson
├── outputs/                   # step files, clean table, quarantine, SQLite DB, scorecard
└── practice/                  # 3 seeded practice CSVs + answer keys
```

## What I learned

I started this project thinking data cleaning was the boring part you do
before the "real" analysis. It isn't — the cleaning *is* the analysis
most of the time, and the decisions in it are judgement calls, not
button clicks. The biggest lesson was that blanks are not all the same:
a blank price means "drop the row", a blank rating means "never
reviewed" and filling it with 0 would have dragged the mean rating from
4.74 to 3.20 — a lie with a number attached. I also learned to check
ranges before assuming units: a column that looked like a percentage ran
0–255, so it wasn't one, and dividing it by 100 would have been wrong.
And I learned that a check that finds zero duplicates is still worth
running, because the next file you receive might not be so clean. Every
number in this repo comes from code I actually ran, and the scorecard
proves the chain balances: 2,000 rows in, 1,430 clean rows and 5
quarantined rows out.

## A note on honesty

This is a **self-directed learning project built on public open data**.
It is not client work and never was for an employer — the dataset is
Inside Airbnb's open Toronto listings, cited and licensed above, and the
seeded problems in the practice set are labelled as seeded. The point of
the kit is to teach, not to impress with borrowed credibility.

## PROJECT STATE

```
Dataset: Inside Airbnb Toronto listings.csv, release 2026-09-16
Source URL: https://data.insideairbnb.com/canada/on/toronto/2026-09-16/data/listings.csv.gz
Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)
Download date: 2026-11-08
Full file: 22,050 rows x 90 columns
Committed sample: data/raw/listings_sample_2000.csv (first 2,000 rows, untouched)
Full-file issues: price $ strings 16,760 | price blank 5,290 | rate columns 100% blank |
  13 columns 100% empty | duplicate ids 0 | minimum_nights > 365: 19 | price max $9,049.10
Sample chain: raw 2,000 -> step1 2,000 -> step2 2,000 -> step3 1,435 ->
  step4 1,435 -> clean 1,430 + quarantined 5
Final clean rows: 1,430 (71.5% of the sample)
Clean price: median $150.76, mean $226.81, range $19.90-$3,897.96
Quarantine: 5 rows, all "Price over $5,000 — held for review"
```
