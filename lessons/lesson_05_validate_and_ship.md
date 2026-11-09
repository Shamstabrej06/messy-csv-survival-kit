# Lesson 05 — Validate and ship

**Script:** `src/lesson_05_validate.py` · **Reads:** `outputs/step4_deduped.csv` ·
**Writes:** `outputs/clean_listings.csv`, `outputs/quarantine.csv`,
`outputs/clean_listings.db`, `outputs/Data_Quality_Scorecard.xlsx`

## The problem

Passing the earlier lessons does not guarantee sane values. A price of
`$8,714.41` parsed perfectly in Lesson 02 — it is still a number that
will dominate every average it touches. Validation is the last gate:
every row must pass a set of range checks, or it goes to quarantine
**with a reason**, where a human can look at it. Nothing is silently
deleted at this step.

## Why it matters

This is the difference between "cleaned" and "trusted". A clean table
with no validation is a promise nobody checked. A quarantine file turns
every rejection into a to-do list for the data owner instead of a
mystery.

## The fix — the rules

| Rule | Reason if it fails |
| --- | --- |
| `price_usd` present and > 0 | Missing or non-positive price |
| `price_usd` ≤ $5,000 | Price over $5,000 — held for review |
| `minimum_nights` between 1 and 365 | minimum_nights out of range (1-365) |
| `host_response_rate_pct` between 0 and 100 (when present) | host_response_rate_pct out of range (0-100) |
| `host_acceptance_rate_pct` between 0 and 100 (when present) | host_acceptance_rate_pct out of range (0-100) |
| `review_scores_rating` between 0 and 5 (when present) | review_scores_rating out of range (0-5) |
| `accommodates` between 1 and 16 | accommodates out of range (1-16) |
| `availability_365` between 0 and 365 | availability_365 out of range (0-365) |

The $5,000 price rule needs a word of explanation. It is a **review
threshold, not a claim the listing is wrong**. Toronto has genuine
luxury listings, and the 5 rows it catches are probably real:

| id | name | price_usd |
| --- | --- | --- |
| 42037807 | Pantages Hotel, Newly Renovated City King Room | 7,000.00 |
| 1320285399993595113 | Cozy Basement Studio \| Easy Access to Everything | 8,714.41 |
| 1771838993400347817 | 3 bedroom Beside CN Tower with Parking + | 5,433.00 |
| 1065379856168955470 | Beautiful 3 Bedroom Bungalow | 5,075.00 |
| 1079650206184425990 | Luxury Co-Living Toronto House | 7,752.00 |

Quarantining them for review is the honest middle ground between
deleting real data and letting one $8,714 night drag the mean price
up. The other rules caught nothing in this sample — the 3 rows with
`minimum_nights` over 365 had already left with the price-missing rows
in Lesson 03, and the rate columns are blank, so those checks pass
vacuously. The checks stay in the script for the next release that has
data.

**A trap this lesson deliberately does not fall into:**
`estimated_occupancy_l365d` looks like a percentage, but in this release
its values run 0–255 (median 18 in the sample). It behaves like a count
of nights, not a 0–100 rate. This script does not divide it by 100 and
does not validate it as a percentage. Checking the range before assuming
the unit is the whole lesson.

## What actually happened

| Outcome | Rows |
| --- | --- |
| Clean | 1,430 |
| Quarantined (all 5: price over $5,000) | 5 |
| Chain check: clean + quarantined = step 4 rows | 1,430 + 5 = 1,435 ✓ |

Clean price after validation: median $150.76, mean $226.81, range
$19.90–$3,897.96.

## The four shipped artefacts

1. **`outputs/clean_listings.csv`** — 1,430 rows × 80 columns, the final
   clean table.
2. **`outputs/quarantine.csv`** — the 5 held rows with `rejection_reason`.
3. **`outputs/clean_listings.db`** — SQLite database, table
   `clean_listings`, 1,430 rows. Query it with
   `SELECT COUNT(*) FROM clean_listings;` or
   `SELECT AVG(price_usd) FROM clean_listings;`.
4. **`outputs/Data_Quality_Scorecard.xlsx`** — the before/after
   scorecard: the row-count chain (with a live `BALANCED` check) and
   issues found vs fixed per category, where "Fixed" is a live formula
   (`Found − Remaining`). Open it and read the "How to read this" sheet
   first.

## Code walkthrough

- `validate()` — builds one reason string per row. A row can fail more
  than one rule; all its reasons are joined with `"; "`. The `add()`
  helper appends a reason only to rows matching that rule's mask.
- The split — `df[reasons != ""]` is quarantine, the rest is clean.
  The quarantine keeps every original column plus `rejection_reason`.
- `to_sql("clean_listings", ...)` — booleans are converted back to real
  booleans first, so SQLite stores 0/1 instead of the strings
  `"True"`/`"False"`.
- `build_scorecard()` — recomputes the "found" counts from the actual
  step files, so the scorecard can never drift from the run. The chain
  section uses cell formulas (`=B10+B11`, `=IF(...,"BALANCED",...)`)
  instead of typed-in totals.

## Try it yourself

1. Open the scorecard and change one "Rows remaining" value. What
   happens to "Rows fixed" and why? (It is a formula, not a typed
   number.)
2. Query the SQLite database: which neighbourhood has the highest
   median price? (`SELECT neighbourhood_cleansed, AVG(price_usd) ...
   GROUP BY neighbourhood_cleansed ORDER BY 2 DESC LIMIT 5;`)
3. Add a rule of your own — for example, `bedrooms <= 10` — re-run
   Lesson 05 and see what changes. Does anything get quarantined?
   (Answer: no, the maximum is 8.)

## PROJECT STATE update — FINAL

```
Sample chain: raw 2,000 -> step1 2,000 -> step2 2,000 -> step3 1,435 ->
  step4 1,435 -> clean 1,430 + quarantined 5
Final clean rows: 1,430 (71.5% of the sample)
Clean price: median $150.76, mean $226.81, range $19.90-$3,897.96
Quarantine: 5 rows, all "Price over $5,000 — held for review"
```
