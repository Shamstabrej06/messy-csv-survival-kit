# Lesson 02 — Money and percentages

**Script:** `src/lesson_02_money.py` · **Reads:** `outputs/step1_loaded.csv` ·
**Writes:** `outputs/step2_numeric.csv`

## The problem

The `price` column looks like money, but it is text:

| id | name | price (before) | price_usd (after) |
| --- | --- | --- | --- |
| 1027121053462854548 | Luxury Stay in King West | `"$3,897.96"` | 3897.96 |
| 1164699152419223248 | 2-storey Penthouse w/2 parking and lake/city views | `"$1,799.00"` | 1799.00 |
| 1322124007467552144 | Bright & Stylish 2BR + Den in Downtown \| CN Tower | `"$1,223.69"` | 1223.69 |

A dollar sign, a thousands comma, and (for 565 rows) nothing at all.
You cannot average, sum or chart a column like that — and if you just
delete the `$` with a careless replace, `"$1,799.00"` still fails to
parse because of the comma.

## Why it matters

Price is the column this whole kit analyses. Every average, median and
chart downstream depends on this conversion being right — and on knowing
exactly which rows could not be converted, instead of discovering it
three lessons later.

## The fix

Strip the decorations, then convert — and keep an audit:

```python
cleaned = series.str.replace("$", "", regex=False).str.replace(",", "", regex=False)
numeric = pd.to_numeric(cleaned, errors="coerce")
```

`errors="coerce"` turns anything that still won't parse into `NaN`
instead of crashing. The audit then counts three buckets per column:
parsed, failed to parse, blank. The original text column is **kept**
next to the new numeric one, so anyone can check the conversion row by
row.

Percentages work the same way, with one extra rule: keep the 0–100
scale. `"95%"` becomes `95.0`, not `0.95`. Dividing by 100 twice is a
classic beginner mistake, and keeping 0–100 makes the range check in
Lesson 05 read naturally ("between 0 and 100").

## What actually happened

| Conversion | Parsed | Failed to parse | Blank |
| --- | --- | --- | --- |
| `price` → `price_usd` | 1,435 | 0 | 565 |
| `host_response_rate` → `host_response_rate_pct` | 0 | 0 | 2,000 |
| `host_acceptance_rate` → `host_acceptance_rate_pct` | 0 | 0 | 2,000 |

The honest surprise: **both rate columns are blank for every row** in
this release (22,050 of 22,050 in the full file). The percentage parser
still runs — and the script proves it works with a demo on literal
values, `['95%', '100%', '80%']` → `[95.0, 100.0, 80.0]` — but here it
converts zero values. A blank column is a finding, not a failure: report
it, don't invent data for it.

Price after conversion: median $152.00, range $19.90–$8,714.41.

## Code walkthrough

- `parse_money()` — two `str.replace` calls (`$`, then `,`) and one
  `pd.to_numeric(..., errors="coerce")`. Order matters: strip `$`
  first, then commas.
- `parse_percent()` — the same shape, stripping `%` and keeping the
  0–100 scale.
- The audit dicts — `parsed`, `failed_to_parse`, `blank` — printed for
  every column. If `failed_to_parse` is ever above zero, stop and look
  at those rows before continuing.
- The demo line — the parser run on literal values, so the mechanism is
  visible even though this release has no `%` values to show it on.

## Try it yourself

1. In Python, run `float("$1,799.00")` and read the error. Then run
   `float("$1,799.00".replace("$", ""))` — it still fails. Why?
2. Change `parse_percent` to divide by 100 and re-run the demo. What
   does the Lesson 05 range check (0–100) do to those values?
3. Find a row where `price` is blank and check its
   `price_quote_price_per_night`. Is there a price hiding in the quote
   columns? (Answer for this sample: no — all 565 blank-price rows have
   blank quotes too.)

## PROJECT STATE update

```
Sample chain: raw 2,000 -> step1 2,000 -> step2 2,000 (0 dropped)
price_usd: 1,435 parsed, 0 failed, 565 blank
```
