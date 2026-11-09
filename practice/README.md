# Practice set

Clean these yourself, using the five lessons. Every file is a slice of
the REAL clean output (`outputs/clean_listings.csv`) with extra problems
**seeded** in for practice — the seeded problems are listed below, and
nothing else in these files is fake. The correct cleaned outputs are in
`answer_keys/` so you can self-check.

## How to use it

1. Pick a file. Clean it with the kit's rules (Lessons 02–05).
2. Compare your result with the matching answer key: same rows in the
   same order, same values in the columns the seeds touched.
3. If a row count differs, check the seeded issues list — a missing row
   is usually a dropped duplicate or a dropped no-price row you forgot.

## The files

| File | Rows | Difficulty | Seeded problems |
| --- | --- | --- | --- |
| `practice_easy.csv` | 42 | Easy | 6 `price_usd` values as `"$X,XXX.XX"` strings · 3 `beds` blanked (median-fill with 1, the file median) · 2 `license` blanked (fill `"Unknown"`) · 3 names with double spaces · 2 duplicate rows appended |
| `practice_medium.csv` | 62 | Medium | 8 `price_usd` as `"$"` strings · 5 `host_response_rate_pct` as `"95%"`-style strings · 4 `license` blanked · 2 `host_is_superhost` as `"t"`/`"f"` strings · 3 names with double spaces · 2 duplicate rows · 1 `price_usd` blanked (drop the row — price is essential) |
| `practice_hard.csv` | 83 | Hard | 10 `price_usd` as `"$"` strings · 6 `host_response_rate_pct` as `"%"` strings · 5 `license` blanked · 2 `host_location` blanked · 3 `host_is_superhost` as `"t"`/`"f"` strings · 4 names with double spaces · 3 duplicate rows · 2 `price_usd` blanked · 1 `price_usd` set to `"N/A"` (fails to parse → drop) · 2 `minimum_nights` set to 400/900 (quarantine, range is 1–365) |

## Answer keys

| Practice file | Answer key | Rows |
| --- | --- | --- |
| `practice_easy.csv` (42) | `answer_keys/practice_easy_answers.csv` | 40 |
| `practice_medium.csv` (62) | `answer_keys/practice_medium_answers.csv` | 59 |
| `practice_hard.csv` (83) | `answer_keys/practice_hard_answers.csv` | 75 |
| `practice_hard.csv` quarantine | `answer_keys/practice_hard_quarantine_answers.csv` | 2 |

Why the counts differ: duplicates are dropped (easy −2, medium −2,
hard −3), rows with no price are dropped (medium −1, hard −3: two blank
plus one `"N/A"`), and hard's two out-of-range `minimum_nights` rows go
to quarantine instead of the clean answer key.

Note for the careful reader: blanking a `license` or `host_location`
destroys the original value, so the answer key holds `"Unknown"` there —
the correct cleaned value under the kit's rules — not the original
string. The same applies to seeded `"t"`/`"f"` values: the answer key
holds the mapped boolean. These answer keys were verified by cleaning
each practice file with the kit's own rules and comparing the result
cell by cell.
