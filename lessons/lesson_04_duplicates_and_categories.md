# Lesson 04 — Duplicates and categories

**Script:** `src/lesson_04_dedup.py` · **Reads:** `outputs/step3_complete.csv` ·
**Writes:** `outputs/step4_deduped.csv`

## The problem

Three different kinds of "same thing, written differently":

1. **The same listing twice.** Inside Airbnb scrapes overlap, and a
   listing id can appear in two scrapes. If it does and you don't dedup,
   you count one home as two.
2. **The same text, spaced differently.** Real rows from this sample:

   | id | name (before) | name (after) |
   | --- | --- | --- |
   | 560848623202367352 | `201B1  Basement Bedroom with private bathroom` | `201B1 Basement Bedroom with private bathroom` |
   | 45343283 | `stunning 1br  downtown` | `stunning 1br downtown` |
   | 38932657 | `Large Studio Style Room   Mins to Yorkville` | `Large Studio Style Room Mins to Yorkville` |

   Double spaces break exact matching and grouping: `"stunning 1br
   downtown"` and `"stunning 1br  downtown"` are different strings to a
   computer.
3. **Booleans pretending to be text.** `host_is_superhost` is `"t"` or
   `"f"` — a one-character string, not a boolean. Filtering on it as a
   boolean fails, and sorting it is meaningless.

## Why it matters

Duplicates inflate every count downstream: listings, revenue, averages.
Inconsistent text splits one category into two. Text booleans break
every filter a beginner writes first (`df[df.host_is_superhost]` raises
an error on a string column). All three are cheap to fix and expensive
to miss.

## The fix

**Dedup — and report the zero.** The script checks exact duplicate rows
and duplicate `id` values, drops what it finds (keeping the first
occurrence), and prints the counts. In this sample both counts are **0**:

| Check | Found |
| --- | --- |
| Exact duplicate rows | 0 |
| Duplicate listing ids | 0 |

A check that finds nothing is still a check. The full file has no
duplicates either — but other Inside Airbnb releases do, and the
practice set seeds duplicates so you can watch the fix work.

**Text normalisation — strip ends, collapse internal spaces.** Applied
to `name`, `host_name`, `property_type`, `room_type`,
`neighbourhood_cleansed` and `host_location`. In this sample it changed
20 values, all of them in `name`. One deliberate non-fix: the script
does **not** force title case on `property_type` or `room_type`.
`"Entire home/apt"` title-cased becomes `"Entire Home/Apt"` — that
corrupts the value instead of cleaning it. And the 54 `property_type`
variants (`"Entire rental unit"`, `"Entire home"`, `"Entire condo"`,
…) are left exactly as the source wrote them; collapsing them would be
inventing a taxonomy.

**`t`/`f` → real booleans.** `host_is_superhost`, `host_has_profile_pic`,
`host_identity_verified` and `has_availability` become `True`/`False`
with pandas' nullable boolean type. A blank `has_availability` becomes
unknown (`pd.NA`), not `False` — "unknown" and "no" are different
answers. (In the kept rows there turned out to be no blanks left for
`has_availability`, but the mapping handles them if they appear.)

| Column | `True` | `False` | Unknown |
| --- | --- | --- | --- |
| `host_is_superhost` | 455 | 980 | 0 |
| `host_has_profile_pic` | 1,329 | 106 | 0 |
| `host_identity_verified` | 1,416 | 19 | 0 |
| `has_availability` | 1,434 | 1 | 0 |

## Code walkthrough

- `df.duplicated()` then `df.duplicated(subset=["id"])` — exact rows
  first, then key-based. `keep="first"` keeps the earliest occurrence.
- `collapse_spaces()` — `" ".join(str(value).split())`. `split()` with
  no arguments splits on any run of whitespace and drops the empties,
  so one line handles leading, trailing and double spaces.
- `.map({"t": True, "f": False, "": pd.NA}).astype("boolean")` — the
  mapping is explicit, and the nullable `"boolean"` dtype (lowercase
  `b`, with quotes) is what allows `pd.NA` to exist.

## Try it yourself

1. In `step3_complete.csv`, find the 20 rows whose `name` changed in
   this lesson. Are any of them the same listing with a different
   spacing, or are they all single rows with sloppy typing?
2. Run `df["property_type"].value_counts()` before and after this
   lesson. Why didn't the number of distinct values change?
3. Open `practice/practice_easy.csv` and find its 2 seeded duplicate
   rows. Which `id` repeats, and which copy should you keep?

## PROJECT STATE update

```
Sample chain: raw 2,000 -> step1 2,000 -> step2 2,000 -> step3 1,435 ->
  step4 1,435 (0 duplicates removed; 20 names normalised)
```
