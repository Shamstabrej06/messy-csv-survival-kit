"""Lesson 04 — Duplicates and categories.

Goal: make sure each listing appears once, text means the same thing
everywhere, and t/f stops pretending to be a string.

  * DEDUP on id (exact + key-based). A listing id must be unique. In this
    sample the check finds ZERO duplicates — that is a result, not a
    skipped step: the script still runs the check, prints the count, and
    only then moves on. (Duplicates DO appear across scrapes in other
    releases, and the practice set seeds some.)
  * TEXT normalisation: strip leading/trailing whitespace and collapse
    internal runs of spaces ("Large Studio Style Room   Mins to Yorkville"
    -> "Large Studio Style Room Mins to Yorkville") on the free-text and
    categorical columns. We deliberately do NOT force title case on
    property_type or room_type: "Entire home/apt" title-cased would
    become "Entire Home/Apt", which corrupts the value.
  * t/f -> REAL booleans: host_is_superhost, host_has_profile_pic,
    host_identity_verified and has_availability become True/False.
    A blank has_availability becomes pd.NA (nullable boolean), because
    "unknown" is not the same as "no".

Run:  python src/lesson_04_dedup.py
Reads:  outputs/step3_complete.csv
Writes: outputs/step4_deduped.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

TEXT_COLUMNS = [
    "name",
    "host_name",
    "property_type",
    "room_type",
    "neighbourhood_cleansed",
    "host_location",
]

BOOLEAN_COLUMNS = [
    "host_is_superhost",
    "host_has_profile_pic",
    "host_identity_verified",
    "has_availability",
]


def collapse_spaces(value: str) -> str:
    """Strip ends and collapse any run of spaces to a single space."""
    return " ".join(str(value).split())


def main() -> None:
    print("Lesson 04 — Duplicates and categories")
    print("=" * 52)
    df = pd.read_csv(config.STEP3_PATH, dtype=str, keep_default_na=False)
    print(f"Read {len(df):,} rows from step 3.")

    # 1. Duplicates: exact rows first, then key-based on id.
    n_exact_dupes = int(df.duplicated().sum())
    df = df.drop_duplicates()
    print(f"Exact duplicate rows found and removed: {n_exact_dupes}")

    n_id_dupes = int(df["id"].duplicated().sum())
    df = df.drop_duplicates(subset=["id"], keep="first")
    print(f"Duplicate listing ids found and removed: {n_id_dupes} "
          f"(keep first occurrence)")
    print(f"Rows after dedup: {len(df):,}")

    # 2. Text normalisation (strip + collapse spaces), counting changes.
    for col in TEXT_COLUMNS:
        before = df[col].copy()
        df[col] = df[col].apply(collapse_spaces)
        n_changed = int((before != df[col]).sum())
        print(f"Normalised {col}: {n_changed} values changed")

    # 3. t/f -> real booleans (nullable: blank stays unknown, not False).
    for col in BOOLEAN_COLUMNS:
        counts = df[col].value_counts(dropna=False).to_dict()
        df[col] = df[col].map({"t": True, "f": False, "": pd.NA}).astype("boolean")
        print(f"Converted {col} to boolean: {counts}")

    df.to_csv(config.STEP4_PATH, index=False)
    print(f"Wrote {config.STEP4_PATH} ({len(df):,} rows)")


if __name__ == "__main__":
    main()
