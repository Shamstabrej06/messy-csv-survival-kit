"""Lesson 03 — Missing values without lying.

Goal: handle blanks with a deliberate strategy per column — never one
blanket rule, because each blank means something different.

The strategies, and why:
  * DROP the 13 columns that are 100% empty in this release (listed
    below). A column with zero values carries zero information; keeping
    it only confuses the next person. The drop is recorded, not silent.
  * DROP rows where price_usd is missing. Price is the essential field
    for this kit's analysis; a listing with no price cannot be priced,
    averaged or ranked. Guessing a price would be inventing data.
  * MEDIAN-FILL bedrooms, beds and minimum_nights. These are small
    counts with a clear centre (medians 1, 1 and 28 in this sample), and
    only a handful of rows are affected — the fill moves no averages.
  * "Unknown" for license, host_location and bathrooms_text. These are
    categories, and "Unknown" is honest: it says "we don't know" instead
    of pretending the value is something else.
  * LEAVE BLANK description (free text — there is nothing honest to fill
    it with) and review_scores_rating / first_review / last_review
    (blank means "never reviewed" — filling 0 would lie about the
    listing's rating).

Run:  python src/lesson_03_missing.py
Reads:  outputs/step2_numeric.csv
Writes: outputs/step3_complete.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

# Columns that are 100% empty in the Toronto 2026-09-16 release (verified
# in docs/data_quality_report.md). Dropping them is a cleaning decision,
# recorded here in the open — not a silent schema change.
FULLY_EMPTY_COLUMNS = [
    "neighborhood_overview",
    "host_since",
    "host_response_time",
    "host_response_rate",
    "host_acceptance_rate",
    "host_thumbnail_url",
    "host_neighbourhood",
    "host_total_listings_count",
    "neighbourhood",
    "neighbourhood_group_cleansed",
    "bathrooms",
    "calendar_updated",
    "instant_bookable",
]

UNKNOWN_FILL_COLUMNS = ["license", "host_location", "bathrooms_text"]
MEDIAN_FILL_COLUMNS = ["bedrooms", "beds", "minimum_nights"]


def main() -> None:
    print("Lesson 03 — Missing values without lying")
    print("=" * 52)
    df = pd.read_csv(config.STEP2_PATH, dtype=str, keep_default_na=False)
    print(f"Read {len(df):,} rows x {len(df.columns)} columns from step 2.")

    # 1. Drop the fully-empty columns (verify the claim first).
    actually_empty = [c for c in FULLY_EMPTY_COLUMNS if (df[c] == "").all()]
    assert len(actually_empty) == len(FULLY_EMPTY_COLUMNS), (
        "A supposedly empty column has values — stop and investigate, "
        "do not drop it blindly."
    )
    df = df.drop(columns=FULLY_EMPTY_COLUMNS)
    print(f"Dropped {len(FULLY_EMPTY_COLUMNS)} columns that are 100% empty "
          f"in this release: {', '.join(FULLY_EMPTY_COLUMNS)}")

    # 2. Drop rows with no price (essential field — see module docstring).
    before = len(df)
    missing_price = df["price_usd"].isna() | (df["price_usd"] == "")
    n_dropped = int(missing_price.sum())
    df = df[~missing_price].copy()
    print(f"Dropped {n_dropped:,} rows with no price "
          f"({before:,} -> {len(df):,} rows)")

    # 3. Median-fill the small numeric gaps (medians computed on the
    #    rows that remain, so the fill reflects the kept data).
    for col in MEDIAN_FILL_COLUMNS:
        numeric = pd.to_numeric(df[col], errors="coerce")
        median = float(numeric.median())
        n_missing = int(numeric.isna().sum())
        df[col] = numeric.fillna(median)
        print(f"Median-filled {col}: {n_missing} missing -> {median:g}")

    # 4. "Unknown" for the categorical gaps.
    for col in UNKNOWN_FILL_COLUMNS:
        n_missing = int((df[col] == "").sum())
        df[col] = df[col].replace("", "Unknown")
        print(f"Filled {col} with 'Unknown': {n_missing} rows")

    # 5. Left blank on purpose (see module docstring).
    left_blank = {
        "description": int((df["description"] == "").sum()),
        "review_scores_rating": int((df["review_scores_rating"] == "").sum()),
        "first_review": int((df["first_review"] == "").sum()),
        "last_review": int((df["last_review"] == "").sum()),
    }
    print("Left blank on purpose (blank is the honest value here): "
          + ", ".join(f"{k} {v}" for k, v in left_blank.items()))

    df.to_csv(config.STEP3_PATH, index=False)
    print(f"Wrote {config.STEP3_PATH} ({len(df):,} rows)")


if __name__ == "__main__":
    main()
