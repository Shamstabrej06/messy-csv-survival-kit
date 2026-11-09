# Data quality report — Inside Airbnb Toronto listings

**Dataset:** Inside Airbnb — Toronto `listings.csv`, release **2026-09-16**
**Source URL:** https://data.insideairbnb.com/canada/on/toronto/2026-09-16/data/listings.csv.gz
**Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0)
**Download date:** 2026-11-08
**Full file:** 22,050 rows × 90 columns
**Committed sample:** `data/raw/listings_sample_2000.csv` — the first 2,000
rows of the raw file, untouched (headers and first/last listing ids verified
identical to the full file).

Every count below comes from reading the real file. "Full file" means all
22,050 rows; "sample" means the committed 2,000-row extract the lessons run
on. Where the two disagree, both numbers are shown — the difference is
usually just scale.

## 1. Currency stored as text

| Check | Full file | Sample |
| --- | --- | --- |
| `price` values containing `$` | 16,760 | 1,435 |
| `price` values containing `,` (thousands separator) | 224 | 26 |
| `price` blank | 5,290 (24.0%) | 565 (28.3%) |
| `price` values that cannot be parsed as a number | 0 | 0 |

Example: listing `1027121053462854548`, "Luxury Stay in King West",
`price` = `"$3,897.96"` — a string, not a number. Any mean, sum or chart
computed on the raw column would fail or silently drop these rows.
Lesson 02 fixes this. Price range (non-blank): $17.31–$9,049.10,
median $161.00.

## 2. Percentages stored as text — and a surprise

| Check | Full file | Sample |
| --- | --- | --- |
| `host_response_rate` values containing `%` | 0 | 0 |
| `host_acceptance_rate` values containing `%` | 0 | 0 |
| `host_response_rate` blank | 22,050 (100%) | 2,000 (100%) |
| `host_acceptance_rate` blank | 22,050 (100%) | 2,000 (100%) |

There are **no** percentage strings in this release at all — both rate
columns are entirely blank. That is itself a finding: the lesson's
percentage parser still runs (and is written to handle `"95%"` strings,
because other Inside Airbnb releases do contain them), but here it
converts zero values and records the blanks in its audit. A blank column
is reported, never papered over with invented data.

Related trap: `estimated_occupancy_l365d` looks like a percentage but is
not one. Its values run 0–255 (median 42 full file, 18 sample) — it
behaves like a count of nights, not a 0–100 rate. Dividing it by 100
would be wrong. Lesson 05 documents this.

## 3. Missing values per key column

| Column | Full file blank | Sample blank | What it means |
| --- | --- | --- | --- |
| `id` | 0 | 0 | — |
| `name` | 0 | 0 | — |
| `description` | 126 | 42 | No description written |
| `neighbourhood` (raw) | 22,050 (100%) | 2,000 (100%) | Column empty in this release; use `neighbourhood_cleansed` |
| `neighbourhood_cleansed` | 0 | 0 | — |
| `latitude` / `longitude` | 0 | 0 | — |
| `property_type` / `room_type` | 0 | 0 | — |
| `price` | 5,290 | 565 | No price quoted (see §1) |
| `minimum_nights` | 51 | 3 | Not stated |
| `host_location` | 6,492 | 630 | Host gave no location |
| `license` | 10,222 | 1,116 | No licence number listed |
| `bedrooms` | 9 | 1 | Not stated |
| `beds` | 363 | 33 | Not stated |
| `bathrooms_text` | 42 | 6 | Not stated |
| `review_scores_rating` | 4,286 | 683 | Never reviewed |
| `first_review` / `last_review` | 4,286 | 683 | Never reviewed |
| `estimated_revenue_l365d` | 5,290 | 565 | Same rows as blank `price` |

Lesson 03 handles each of these differently — drop, median-fill,
`"Unknown"`, or leave blank — with the reasoning written out per column.

## 4. Booleans stored as `t` / `f` text

| Column | Full file | Sample |
| --- | --- | --- |
| `host_is_superhost` | t 7,890 / f 14,160 | t 523 / f 1,477 |
| `host_has_profile_pic` | t 21,187 / f 863 | t 1,868 / f 132 |
| `host_identity_verified` | t 21,654 / f 396 | t 1,976 / f 24 |
| `has_availability` | t 21,837 / f 63 / blank 150 | t 1,970 / f 2 / blank 28 |
| `instant_bookable` | blank 22,050 (100%) | blank 2,000 (100%) |

`"t"` is a one-character string, not a boolean — filtering on it as a
boolean fails. Lesson 04 converts these to real booleans (blank
`has_availability` becomes unknown, not `False`).

## 5. Dates

`last_scraped`, `calendar_last_scraped`, `host_since`, `first_review` and
`last_review` are all ISO dates (`2026-09-18`). **Zero unparseable dates**
in the full file. `first_review` / `last_review` are blank for 4,286
listings — the same listings with no review score, i.e. never reviewed.
No date repair was needed; the report records that instead of inventing
a problem.

## 6. Duplicates

| Check | Full file | Sample |
| --- | --- | --- |
| Duplicate listing `id` values | 0 | 0 |
| Exact duplicate rows (all columns) | 0 | 0 |

No duplicates in this release. Lesson 04 still runs the dedup check and
prints the zero — a check that finds nothing is still a check, and the
practice set seeds duplicates so learners can see the fix work.

## 7. Whitespace and casing in categorical text

| Check | Full file | Sample |
| --- | --- | --- |
| `name` with leading/trailing whitespace | 1 | 0 |
| `name` with double (or triple) internal spaces | 408 | 26 |
| `host_name` with double internal spaces | 6 | 0 |
| `property_type` / `room_type` / `neighbourhood_cleansed` with leading/trailing whitespace | 0 | 0 |

Examples (real rows): `"stunning 1br  downtown"` → `"stunning 1br
downtown"`; `"Large Studio Style Room   Mins to Yorkville"` →
`"Large Studio Style Room Mins to Yorkville"`. Double spaces break exact
matching and grouping, so Lesson 04 collapses them.

Related: `property_type` has 54 distinct values in the full file
(31 in the sample), including near-synonyms such as `"Entire rental
unit"` (6,132), `"Entire home"` (3,615) and `"Entire condo"` (3,548).
The kit normalises whitespace only and leaves these labels as the
source wrote them — collapsing them would be inventing a taxonomy.

## 8. Out-of-range numerics

| Check | Full file | Sample |
| --- | --- | --- |
| `price` ≤ 0 | 0 | 0 |
| `price` > $1,000 | 224 | 26 |
| `price` > $5,000 | 16 | 5 |
| `minimum_nights` < 1 | 0 | 0 |
| `minimum_nights` > 365 (max 1,125) | 19 | 3 |
| `accommodates` outside 1–16 | 0 | 0 |
| `availability_365` outside 0–365 | 0 | 0 |
| `number_of_reviews` < 0 | 0 | 0 |
| `review_scores_rating` outside 0–5 | 0 | 0 |

The 3 sample rows with `minimum_nights` over 365 also have no price, so
they leave with the price-missing rows in Lesson 03. The 5 sample rows
with a price over $5,000 (up to $8,714.41) are quarantined in Lesson 05
for human review — they are probably genuine luxury listings, which is
exactly why they are reviewed rather than deleted.

## 9. Columns that are 100% empty in this release (13)

`neighborhood_overview`, `host_since`, `host_response_time`,
`host_response_rate`, `host_acceptance_rate`, `host_thumbnail_url`,
`host_neighbourhood`, `host_total_listings_count`, `neighbourhood`,
`neighbourhood_group_cleansed`, `bathrooms`, `calendar_updated`,
`instant_bookable`. Lesson 03 drops these with the drop recorded in the
open — a column with zero values carries zero information.

## 10. Nested data inside a cell

`price_quote_raw` holds a JSON blob per row (quote breakdown, taxes,
fees, `"price_string": "$1,680.00 CAD"`). It is real data, but it is not
a flat column — the kit does not try to flatten it. It is listed here
so nobody is surprised by it, and the lessons use the flat `price`
column instead.

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
