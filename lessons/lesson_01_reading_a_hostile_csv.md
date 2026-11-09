# Lesson 01 — Reading a hostile CSV

**Script:** `src/lesson_01_load.py` · **Reads:** `data/raw/listings_sample_2000.csv` ·
**Writes:** `outputs/step1_loaded.csv`

## The problem

A CSV looks simple — commas separate columns, one row per line — until a
real file arrives. Inside Airbnb's Toronto listings file has 90 columns,
free-text descriptions, and listing names like:

| id | name |
| --- | --- |
| 42037807 | Pantages Hotel, Newly Renovated City King Room |

That comma inside the name is *inside* a quoted field. A naive reader
that splits every line on commas would chop that name into two columns
and shift every field after it. In the full 22,050-row file, **2,428
listing names contain a comma** (185 in our 2,000-row sample). There are
no embedded newlines in this release (0 in the full file) — but the next
file you receive might have them, and the same quoting rules handle both.

The second trap is dtype guessing. If you let the reader guess, `price`
(`"$54.26"`, `"$1,799.00"`, blank) becomes an unusable mix, dates become
objects, and `t`/`f` become strings. You spend the rest of the project
undoing guesses you never asked for.

## Why it matters

Every later lesson assumes the load was faithful. If the load silently
drops a row or mangles a field, no amount of clever cleaning fixes it —
you are analysing a different dataset than the one you downloaded.

## The fix

Read everything as **text**, explicitly, and prove the row count:

```python
df = pd.read_csv(
    config.RAW_PATH,
    dtype=str,              # no dtype guessing: everything is text
    keep_default_na=False,  # "" stays "" (we count blanks ourselves)
    encoding="utf-8",       # the file is UTF-8; say so explicitly
)
assert len(df) == 2_000
```

`dtype=str` means pandas does not guess. `keep_default_na=False` means
an empty cell stays an empty string `""` instead of becoming `NaN`, so
later lessons can count missing values themselves instead of wondering
what pandas decided. The `assert` is the whole point of this lesson: the
script refuses to continue if the load lost a row.

## What actually happened

| Check | Result |
| --- | --- |
| Rows loaded | 2,000 |
| Columns | 90 |
| Rows dropped | 0 |
| Listing names containing a comma | 185 |
| Descriptions with an embedded newline | 0 |
| Names with an embedded newline | 0 |

All 185 comma-containing names loaded as single rows — the CSV quoting
did its job, because we used a real CSV reader instead of splitting
lines by hand.

## Code walkthrough

- `pd.read_csv(..., dtype=str, keep_default_na=False, encoding="utf-8")`
  — the faithful load. Three arguments, each one preventing a different
  silent mistake.
- The `assert len(df) == 2_000` — a tripwire. If the sample ever changes
  size, the script fails loudly instead of producing wrong numbers.
- The three `str.contains` counts — measuring the hostility instead of
  assuming it. This is where the numbers in the data quality report
  come from.
- `df.to_csv(config.STEP1_PATH, index=False)` — step 1's output, the
  input to Lesson 02.

## Try it yourself

1. Open `data/raw/listings_sample_2000.csv` in a plain text editor and
   find a listing name with a comma. Count the commas on that line —
   there are more than 89, because the quoted commas don't count.
2. In Python, run `pd.read_csv("data/raw/listings_sample_2000.csv")`
   with NO arguments and inspect `df["price"].dtype` and
   `df["price"].head()`. What did pandas guess, and what did it do with
   the blanks?
3. Change `dtype=str` to nothing and re-run Lesson 01. Which of the
   printed counts change, and why?

## PROJECT STATE update

```
Sample chain: raw 2,000 -> step1 2,000 (0 dropped)
```
