# Lesson 03 — Missing values without lying

**Script:** `src/lesson_03_missing.py` · **Reads:** `outputs/step2_numeric.csv` ·
**Writes:** `outputs/step3_complete.csv`

## The problem

Blanks are not all the same. In this sample:

| Column | Blank rows | What blank means |
| --- | --- | --- |
| `price_usd` | 565 | No price quoted |
| `license` | 1,116 | No licence number listed |
| `host_location` | 630 | Host gave no location |
| `beds` | 33 | Not stated |
| `bedrooms` | 1 | Not stated |
| `minimum_nights` | 3 | Not stated |
| `bathrooms_text` | 6 | Not stated |
| `description` | 42 | No description written |
| `review_scores_rating` | 683 | Never reviewed |
| 13 whole columns | 2,000 each | Empty in this release |

One blanket rule — "fill everything with 0" or "drop every row with a
blank" — would be wrong in five different ways. So this lesson uses four
different strategies, one per meaning.

## Why it matters

Missing-value handling is where most beginners accidentally invent data.
Fill a missing rating with 0 and you have just told the world that 683
listings are terrible. Drop every row with any blank and you throw away
a third of the dataset. Each choice below is justified in words, not
just in code.

## The fix

**1. Drop the 13 columns that are 100% empty.** `neighborhood_overview`,
`host_since`, `host_response_time`, `host_response_rate`,
`host_acceptance_rate`, `host_thumbnail_url`, `host_neighbourhood`,
`host_total_listings_count`, `neighbourhood`,
`neighbourhood_group_cleansed`, `bathrooms`, `calendar_updated`,
`instant_bookable`. A column with zero values carries zero information.
The script verifies each one really is empty before dropping it — if a
future release fills one in, the script fails loudly instead of deleting
real data.

**2. Drop rows with no price (565 rows).** Price is the essential field
for this kit's analysis. A listing with no price cannot be priced,
averaged or ranked, and guessing a price would be inventing data. The
rows are gone from the clean table, but they are not hidden: the count
is printed, and the same rows are still in `step2_numeric.csv` for
anyone who wants them.

**3. Median-fill the small numeric gaps.** `bedrooms` (1 row → 1),
`beds` (24 rows → 1), `minimum_nights` (2 rows → 28). Medians, not
means: these are small counts, and the median is the value a typical
listing actually has. Only 27 rows are affected, so no average moves.

**4. `"Unknown"` for categories.** `license` (669 rows), `host_location`
(492 rows), `bathrooms_text` (6 rows). `"Unknown"` is honest: it says
"we don't know" instead of pretending the value is something else.

**5. Leave blank on purpose.** `description` (16 rows — there is nothing
honest to fill free text with) and `review_scores_rating` /
`first_review` / `last_review` (465 rows — blank means "never
reviewed"). Filling the rating with 0 would be a lie with a number
attached: the mean rating of reviewed listings is 4.74, but filled with
0 it drops to 3.20. That 1.5-point drop is invented entirely by the
fill.

Before / after (real rows):

| id | field | before | after |
| --- | --- | --- | --- |
| 1092352202113212073 | `license` | *(blank)* | `Unknown` |
| 1092352202113212073 | `host_location` | *(blank)* | `Unknown` |
| 1066654035322408628 | `license` | *(blank)* | `Unknown` |
| 1066718 | `minimum_nights` | *(blank)* | 28 |
| 1277504204375944889 | `bedrooms` | *(blank)* | 1 |

One side effect to know about: after a median fill, `beds` and
`bedrooms` become float columns (`2` is written as `2.0`), because a
median can be fractional. If you need integers downstream, cast back
with `.astype("Int64")` — the nullable integer type, which still allows
missing values.

## What actually happened

| Action | Count |
| --- | --- |
| Columns dropped (100% empty) | 13 |
| Rows dropped (no price) | 565 → 2,000 → 1,435 rows |
| Median-filled | bedrooms 1, beds 24, minimum_nights 2 |
| Filled with `"Unknown"` | license 669, host_location 492, bathrooms_text 6 |
| Left blank by design | description 16, review data 465 |

## Code walkthrough

- The `assert` on the empty columns — the script checks its own
  assumption before deleting anything.
- `df[~missing_price]` — the drop, with the count printed before and
  after so the chain stays auditable.
- Medians computed on the rows that remain, so the fill reflects the
  kept data, not the dropped rows.
- `df[col].replace("", "Unknown")` — only for the three categorical
  columns, never for numbers or dates.

## Try it yourself

1. Compute the mean of `review_scores_rating` in `step3_complete.csv`
   twice: once ignoring blanks, once with blanks filled as 0. How far
   apart are they? (Answer: 4.74 vs 3.20.)
2. Re-run Lesson 03 but median-fill `price_usd` instead of dropping
   those rows. How many rows do you keep, and what does the median price
   become? Why is that a worse choice?
3. Pick one of the 13 dropped columns and check the full-file diagnosis
   in `docs/data_quality_report.md`. Is there any value in it at all?

## PROJECT STATE update

```
Sample chain: raw 2,000 -> step1 2,000 -> step2 2,000 -> step3 1,435
  (565 rows dropped: no price; 13 columns dropped: 100% empty)
```
