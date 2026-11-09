# Upwork portfolio copy — Messy CSV Survival Kit

## Portfolio title (61 characters)

Messy CSV Survival Kit — Real Airbnb Data, 5 Cleaning Lessons

## Role

Data Engineer — design, build, documentation

## Description (578 characters — Upwork's field limit is 540–580)

A teach-by-doing kit that turns Inside Airbnb's real Toronto listings file (22,050 rows, CC BY 4.0) into clean, analysis-ready data. Five runnable lessons cover hostile CSV loading, money and percentage parsing, honest missing-value handling, dedup and category normalisation, and validation with quarantine. Each lesson pairs a Python script with a plain-language guide and real before/after rows. The verified run takes a 2,000-row sample to 1,430 clean rows plus 5 quarantined, with an Excel scorecard proving every step. Includes a three-level practice set with answer keys.

## About this project

Most data-cleaning tutorials use tidy toy data. This kit does the opposite:
it starts from Inside Airbnb's real Toronto listings file — 22,050 rows of
genuinely messy public data, shared under CC BY 4.0 — and cleans it in
five runnable lessons, each one a Python script plus a beginner-friendly
guide that explains what was wrong, why it matters, and how the fix works,
with before/after rows taken from the real data.

The mess is real: prices stored as `"$1,799.00"` strings, two rate columns
that turned out to be blank for every row, 13 columns that are 100% empty,
5,290 listings with no price at all, `t`/`f` booleans, double spaces in
listing names, and minimum-night values up to 1,125. The kit handles each
problem with a different, justified strategy — drop rows only where the
field is essential, median-fill small numeric gaps, use an explicit
`"Unknown"` for categories, and leave review data blank because blank
means "never reviewed" (filling it with 0 would have dragged the mean
rating from 4.74 to 3.20).

Everything is verified, not asserted. The scripts were re-run from a clean
state and the chain balances exactly: 2,000 sample rows → 2,000 loaded →
2,000 parsed → 1,435 after missing-value handling → 1,435 deduped →
1,430 clean rows plus 5 quarantined for human review, with an Excel
scorecard whose totals are live formulas. The clean table ships as CSV and
SQLite, and a three-level practice set (easy / medium / hard) with answer
keys lets learners test themselves on the same techniques.

This is a self-directed learning project built on public open data — not
client work. The dataset is cited and licensed in the repo, and the seeded
practice problems are labelled as seeded.

## Skills (exactly 5)

1. Data Cleaning
2. Python
3. pandas
4. SQLite
5. Microsoft Excel

## Proposal snippet (for CSV / data-cleaning jobs)

I build cleaning pipelines that prove their own work. In my Messy CSV
Survival Kit I took Inside Airbnb's real Toronto listings file and, in
five documented stages, turned a 2,000-row sample into 1,430 verified
clean rows with 5 quarantined for review — every step reproducible, with
an Excel scorecard whose totals are live formulas. I can apply the same
approach to your files: currency and percentage strings parsed with an
audit trail, missing values handled per column instead of one blanket
rule, duplicates removed, and anything suspicious quarantined with a
reason rather than silently deleted. This work supports my $75 SQL &
Data Cleaning catalog listing, and I'd be glad to start with a small
sample of your data so you can see the before/after before committing.

## LinkedIn post draft

I kept getting the same question from students and junior analysts: "I
got handed an ugly CSV — where do I even start?" So I built the answer.

The Messy CSV Survival Kit takes Inside Airbnb's real Toronto listings
(22,050 rows of gloriously messy public data) and cleans it in 5 taught
steps: hostile CSV loading, money & percentages, missing values without
lying, duplicates & categories, and validation with quarantine. Every
lesson is a runnable Python script + a plain-language guide with real
before/after rows — and the verified run takes 2,000 sample rows to 1,430
clean rows, with an Excel scorecard proving the chain balances.

There's also a practice set (easy / medium / hard) with answer keys, so
you can test yourself. Repo link in the comments — it's free, open data,
and built to teach. If you've ever stared at a `"$1,799.00"` in a column
that should be a number, this one's for you. 🧹📊
