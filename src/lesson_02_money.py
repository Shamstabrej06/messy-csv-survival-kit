"""Lesson 02 — Money and percentages.

Goal: turn text that LOOKS like a number into a real number, and keep an
audit trail of every value that did not survive the conversion.

  * price "$1,234.00"  -> price_usd 1234.00  (strip "$" and ",")
  * host_response_rate "95%" -> host_response_rate_pct 95.0 (strip "%")

The original text columns are KEPT alongside the new numeric ones, so
anyone can audit the conversion row by row.

Honest finding about this release: in the Toronto 2026-09-16 file,
host_response_rate and host_acceptance_rate are blank for EVERY row
(22,050 of 22,050 in the full file, 2,000 of 2,000 in the sample).
The percentage parser below still runs — it converts zero values and
records 2,000 missing in its audit — and it is written to handle "95%"
strings correctly, because other Inside Airbnb releases DO contain them.
A blank column is a finding, not a failure: report it, don't invent data.

Run:  python src/lesson_02_money.py
Reads:  outputs/step1_loaded.csv
Writes: outputs/step2_numeric.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402


def parse_money(series: pd.Series) -> tuple[pd.Series, dict]:
    """Strip "$" and "," then convert to float.

    Returns the numeric series and an audit dict with counts of values
    that parsed, values that failed to parse, and values that were blank.
    """
    cleaned = series.str.replace("$", "", regex=False).str.replace(",", "", regex=False)
    numeric = pd.to_numeric(cleaned, errors="coerce")
    audit = {
        "parsed": int(numeric.notna().sum()),
        "failed_to_parse": int(((series != "") & numeric.isna()).sum()),
        "blank": int((series == "").sum()),
    }
    return numeric, audit


def parse_percent(series: pd.Series) -> tuple[pd.Series, dict]:
    """Strip "%" then convert to float (0-100 scale, NOT 0-1).

    "95%" becomes 95.0. Keeping the 0-100 scale avoids a classic beginner
    mistake: dividing by 100 twice and ending up with 0.95% instead of 95%.
    """
    cleaned = series.str.replace("%", "", regex=False)
    numeric = pd.to_numeric(cleaned, errors="coerce")
    audit = {
        "parsed": int(numeric.notna().sum()),
        "failed_to_parse": int(((series != "") & numeric.isna()).sum()),
        "blank": int((series == "").sum()),
    }
    return numeric, audit


def main() -> None:
    print("Lesson 02 — Money and percentages")
    print("=" * 52)
    df = pd.read_csv(config.STEP1_PATH, dtype=str, keep_default_na=False)
    print(f"Read {len(df):,} rows from step 1.")

    df["price_usd"], price_audit = parse_money(df["price"])
    print(f"price -> price_usd: {price_audit['parsed']:,} parsed, "
          f"{price_audit['failed_to_parse']} failed to parse, "
          f"{price_audit['blank']:,} blank")

    df["host_response_rate_pct"], r_audit = parse_percent(df["host_response_rate"])
    print(f"host_response_rate -> host_response_rate_pct: "
          f"{r_audit['parsed']:,} parsed, {r_audit['failed_to_parse']} failed, "
          f"{r_audit['blank']:,} blank (column is empty in this release)")

    df["host_acceptance_rate_pct"], a_audit = parse_percent(df["host_acceptance_rate"])
    print(f"host_acceptance_rate -> host_acceptance_rate_pct: "
          f"{a_audit['parsed']:,} parsed, {a_audit['failed_to_parse']} failed, "
          f"{a_audit['blank']:,} blank (column is empty in this release)")

    # Worked example of the percentage parser, so the mechanism is visible
    # even though this release has no "%" values to show it on:
    demo = parse_percent(pd.Series(["95%", "100%", "80%"]))[0].tolist()
    print(f"Parser demo on literal values ['95%', '100%', '80%'] -> {demo}")

    df.to_csv(config.STEP2_PATH, index=False)
    print(f"Wrote {config.STEP2_PATH} ({len(df):,} rows, 0 dropped)")


if __name__ == "__main__":
    main()
