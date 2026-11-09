"""Lesson 01 — Reading a hostile CSV.

Goal: load the raw sample faithfully. No silent drops, no silent type
guessing. We read EVERYTHING as text first, because a "helpful" parser
that guesses dtypes is exactly how "$1,234.00" becomes a broken float or
a date becomes a mystery.

What this script proves:
  * the file loads (encoding, quoting, embedded commas/newlines handled),
  * the row count after loading equals the raw row count (2,000),
  * how much hostile content is actually in here (embedded newlines,
    commas inside quoted fields).

Run:  python src/lesson_01_load.py
Reads:  config.RAW_PATH  (data/raw/listings_sample_2000.csv)
Writes: outputs/step1_loaded.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402


def main() -> None:
    print("Lesson 01 — Reading a hostile CSV")
    print("=" * 52)

    # Read everything as text. keep_default_na=False means an empty cell
    # stays an empty string "" instead of becoming NaN — so we can count
    # missing values ourselves later, instead of guessing what pandas did.
    df = pd.read_csv(
        config.RAW_PATH,
        dtype=str,               # no dtype guessing: everything is text
        keep_default_na=False,   # "" stays "" (we count blanks ourselves)
        encoding="utf-8",        # the file is UTF-8; say so explicitly
    )
    print(f"Loaded: {len(df):,} rows x {len(df.columns)} columns")

    # The promise of this lesson: nothing was silently dropped.
    assert len(df) == 2_000, f"Expected 2,000 rows, got {len(df)}"
    print("Row-count check: 2,000 loaded = 2,000 in the raw sample. OK.")

    # How hostile is this file, really? Count the quoting traps the CSV
    # reader had to survive: newlines and commas inside quoted fields.
    newlines_in_description = int(df["description"].str.contains("\n", regex=False).sum())
    commas_in_name = int(df["name"].str.contains(",", regex=False).sum())
    newlines_in_name = int(df["name"].str.contains("\n", regex=False).sum())
    print(f"Descriptions containing an embedded newline: {newlines_in_description}")
    print(f"Listing names containing a comma: {commas_in_name}")
    print(f"Listing names containing an embedded newline: {newlines_in_name}")
    print("All of them loaded as single rows — the quoting did its job.")

    config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.STEP1_PATH, index=False)
    print(f"Wrote {config.STEP1_PATH} ({len(df):,} rows, 0 dropped)")


if __name__ == "__main__":
    main()
