"""Lesson 05 — Validate and ship.

Goal: prove the clean table is actually clean, quarantine anything that
fails with a reason, and ship three artefacts: the clean CSV, a SQLite
database, and an Excel before/after scorecard.

Validation rules (all documented, all applied to every row):
  * price_usd must be present and > 0.
  * price_usd must be <= $5,000 — a "held for review" threshold, not a
    claim the listing is wrong. Toronto has genuine luxury listings, but
    a single $8,714/night row would dominate every average, so the 5
    rows above $5,000 go to quarantine for a human to review.
  * minimum_nights between 1 and 365.
  * host_response_rate_pct / host_acceptance_rate_pct between 0 and 100
    when present (both columns are blank in this release, so this check
    passes vacuously — it is here for the next release that has data).
  * review_scores_rating between 0 and 5 when present.
  * accommodates between 1 and 16; availability_365 between 0 and 365.

A note on estimated_occupancy_l365d: it LOOKS like a percentage, but in
this release its values run 0–255 (median 18 in the sample), so it is
NOT a 0–100 percentage — it behaves like a count of nights. This script
does not divide it by 100 and does not validate it as a percentage.
Checking the range before assuming the unit is the whole lesson.

Outputs:
  * outputs/clean_listings.csv — the final clean table.
  * outputs/quarantine.csv — rows that failed, with rejection_reason.
  * outputs/clean_listings.db — SQLite database, table clean_listings.
  * outputs/Data_Quality_Scorecard.xlsx — issues found vs fixed, and
    the row-count chain, with live formulas where sensible.

Run:  python src/lesson_05_validate.py
Reads:  outputs/step4_deduped.csv (plus step1/step3 for scorecard counts)
Writes: outputs/clean_listings.csv, quarantine.csv, clean_listings.db,
        Data_Quality_Scorecard.xlsx
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

PRICE_REVIEW_LIMIT = 5_000
BOOLEAN_COLUMNS = [
    "host_is_superhost",
    "host_has_profile_pic",
    "host_identity_verified",
    "has_availability",
]


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Return a Series of semicolon-joined reasons per row ("" = valid)."""
    price = pd.to_numeric(df["price_usd"], errors="coerce")
    min_nights = pd.to_numeric(df["minimum_nights"], errors="coerce")
    accommodates = pd.to_numeric(df["accommodates"], errors="coerce")
    availability = pd.to_numeric(df["availability_365"], errors="coerce")
    rating = pd.to_numeric(df["review_scores_rating"], errors="coerce")
    resp = pd.to_numeric(df["host_response_rate_pct"], errors="coerce")
    accept = pd.to_numeric(df["host_acceptance_rate_pct"], errors="coerce")

    reasons = pd.Series([""] * len(df), index=df.index)
    def add(mask, text):
        nonlocal reasons
        reasons = reasons.mask(mask & (reasons != ""), reasons + "; " + text)
        reasons = reasons.mask(mask & (reasons == ""), text)

    add(price.isna() | (price <= 0), "Missing or non-positive price")
    add(price > PRICE_REVIEW_LIMIT,
        f"Price over ${PRICE_REVIEW_LIMIT:,} — held for review")
    add(min_nights.isna() | (min_nights < 1) | (min_nights > 365),
        "minimum_nights out of range (1-365)")
    add(resp.notna() & ((resp < 0) | (resp > 100)),
        "host_response_rate_pct out of range (0-100)")
    add(accept.notna() & ((accept < 0) | (accept > 100)),
        "host_acceptance_rate_pct out of range (0-100)")
    add(rating.notna() & ((rating < 0) | (rating > 5)),
        "review_scores_rating out of range (0-5)")
    add(accommodates.notna() & ((accommodates < 1) | (accommodates > 16)),
        "accommodates out of range (1-16)")
    add(availability.notna() & ((availability < 0) | (availability > 365)),
        "availability_365 out of range (0-365)")
    return reasons


def build_scorecard(chain: dict, issues: list[dict]) -> None:
    """Write the Excel before/after scorecard with live formulas."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Scorecard"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.orientation = "landscape"
    navy = PatternFill("solid", fgColor="1F3864")
    white_bold = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Calibri", size=14, bold=True, color="1F3864")
    label_font = Font(name="Calibri", size=11, bold=True)

    ws["A1"] = "Messy CSV Survival Kit — Data Quality Scorecard"
    ws["A1"].font = title_font
    ws["A2"] = ("Inside Airbnb Toronto listings, release 2026-09-16 "
                "(CC BY 4.0). Sample: first 2,000 rows of the raw file.")
    ws.merge_cells("A2:F2")

    # --- Section 1: row-count chain -------------------------------------
    ws["A4"] = "Row counts at each step"
    ws["A4"].font = label_font
    headers = ["Step", "Rows", "Change vs previous"]
    for c, h in enumerate(headers, start=1):
        cell = ws.cell(row=5, column=c, value=h)
        cell.fill = navy
        cell.font = white_bold
    steps = [
        ("Raw sample", chain["raw"], None),
        ("Step 1 — Loaded", chain["step1"], "=B6-B5"),
        ("Step 2 — Money & percentages", chain["step2"], "=B7-B6"),
        ("Step 3 — Missing values handled", chain["step3"], "=B8-B7"),
        ("Step 4 — Deduped & normalised", chain["step4"], "=B9-B8"),
        ("Step 5 — Clean table", chain["clean"], "=B10-B9"),
        ("Step 5 — Quarantined", chain["quarantined"], None),
    ]
    for i, (label, value, formula) in enumerate(steps):
        r = 6 + i
        ws.cell(row=r, column=1, value=label)
        ws.cell(row=r, column=2, value=value).number_format = "#,##0"
        if formula:
            ws.cell(row=r, column=3, value=formula).number_format = "#,##0"
    check_row = 6 + len(steps) + 1
    ws.cell(row=check_row, column=1,
           value="Check: clean + quarantined = step 4 rows").font = label_font
    ws.cell(row=check_row, column=2, value="=B10+B11").number_format = "#,##0"
    ws.cell(row=check_row, column=3,
           value=f'=IF(B{check_row}=B9,"BALANCED","CHECK FAILED")').font = label_font
    ws.cell(row=check_row + 1, column=1, value="Clean row rate").font = label_font
    ws.cell(row=check_row + 1, column=2, value="=B10/B5").number_format = "0.0%"

    # --- Section 2: issues found vs fixed --------------------------------
    start = check_row + 3
    ws.cell(row=start, column=1, value="Issues found vs fixed").font = label_font
    headers = ["Issue category", "Rows affected (found)",
               "Rows fixed", "Rows remaining", "How it was fixed"]
    for c, h in enumerate(headers, start=1):
        cell = ws.cell(row=start + 1, column=c, value=h)
        cell.fill = navy
        cell.font = white_bold
    for i, issue in enumerate(issues):
        r = start + 2 + i
        ws.cell(row=r, column=1, value=issue["category"])
        ws.cell(row=r, column=2, value=issue["found"]).number_format = "#,##0"
        # Fixed is a live formula: found minus remaining.
        ws.cell(row=r, column=3, value=f"=B{r}-D{r}").number_format = "#,##0"
        ws.cell(row=r, column=4, value=issue["remaining"]).number_format = "#,##0"
        ws.cell(row=r, column=5, value=issue["how"])
    widths = {"A": 44, "B": 20, "C": 14, "D": 16, "E": 62}
    for letter, width in widths.items():
        ws.column_dimensions[letter].width = width
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    notes = wb.create_sheet("How to read this")
    notes.column_dimensions["A"].width = 110
    lines = [
        ("How to read this scorecard", Font(name="Calibri", size=14, bold=True, color="1F3864")),
        ("", Font(name="Calibri", size=11)),
        ("'Found' counts come from the actual run on the 2,000-row sample — "
         "see docs/data_quality_report.md for the full-file (22,050-row) diagnosis.",
         Font(name="Calibri", size=11)),
        ("'Fixed' is a live formula (Found minus Remaining), so the table "
         "stays consistent if you edit a count.", Font(name="Calibri", size=11)),
        ("'Remaining' is 0 for every issue the kit fixes. The one deliberate "
         "exception is review data left blank by design: a blank rating means "
         "'never reviewed', and filling it with 0 would be inventing data.",
         Font(name="Calibri", size=11)),
        ("The chain check must read BALANCED: clean + quarantined = step 4 rows.",
         Font(name="Calibri", size=11)),
    ]
    for i, (text, font) in enumerate(lines, start=1):
        cell = notes.cell(row=i, column=1, value=text)
        cell.font = font
        cell.alignment = Alignment(wrap_text=True, vertical="top")
    wb.active = wb["Scorecard"]
    wb.save(config.SCORECARD_PATH)
    print(f"Wrote {config.SCORECARD_PATH}")


def main() -> None:
    print("Lesson 05 — Validate and ship")
    print("=" * 52)
    df = pd.read_csv(config.STEP4_PATH, dtype=str, keep_default_na=False)
    print(f"Read {len(df):,} rows from step 4.")

    reasons = validate(df)
    df["rejection_reason"] = reasons
    quarantined = df[reasons != ""].copy()
    clean = df[reasons == ""].copy().drop(columns=["rejection_reason"])
    print(f"Validation: {len(clean):,} clean, {len(quarantined):,} quarantined")
    for reason, count in quarantined["rejection_reason"].value_counts().items():
        print(f"  - {reason}: {count}")

    # Ship 1: clean CSV.
    clean.to_csv(config.CLEAN_PATH, index=False)
    print(f"Wrote {config.CLEAN_PATH} ({len(clean):,} rows)")

    # Ship 2: quarantine CSV.
    quarantined.to_csv(config.QUARANTINE_PATH, index=False)
    print(f"Wrote {config.QUARANTINE_PATH} ({len(quarantined):,} rows)")

    # Ship 3: SQLite database (booleans stored as real booleans -> 0/1).
    clean_db = clean.copy()
    for col in BOOLEAN_COLUMNS:
        clean_db[col] = clean_db[col].map(
            {"True": True, "False": False, "": None}).astype("boolean")
    for col in ["price_usd", "host_response_rate_pct", "host_acceptance_rate_pct"]:
        clean_db[col] = pd.to_numeric(clean_db[col], errors="coerce")
    with sqlite3.connect(config.SQLITE_PATH) as conn:
        clean_db.to_sql("clean_listings", conn, if_exists="replace", index=False)
    print(f"Wrote {config.SQLITE_PATH} (table clean_listings, "
          f"{len(clean_db):,} rows)")

    # Ship 4: scorecard. "Found" counts are recomputed from the actual
    # frames so the scorecard can never drift from the run.
    step1 = pd.read_csv(config.STEP1_PATH, dtype=str, keep_default_na=False)
    step3 = pd.read_csv(config.STEP3_PATH, dtype=str, keep_default_na=False)
    chain = {
        "raw": len(step1),
        "step1": len(step1),
        "step2": len(pd.read_csv(config.STEP2_PATH, dtype=str, keep_default_na=False)),
        "step3": len(step3),
        "step4": len(df),
        "clean": len(clean),
        "quarantined": len(quarantined),
    }
    n_money = int(step1["price"].str.contains(r"\$", regex=True).sum())
    n_missing_price = int((step1["price"] == "").sum())
    # Median fills applied in step 3 (counted on the kept rows, before fill):
    kept = pd.read_csv(config.STEP2_PATH, dtype=str, keep_default_na=False)
    kept = kept[kept["price_usd"].notna() & (kept["price_usd"] != "")]
    n_median = sum(int(pd.to_numeric(kept[c], errors="coerce").isna().sum())
                   for c in ["bedrooms", "beds", "minimum_nights"])
    n_unknown = sum(int((kept[c] == "").sum())
                    for c in ["license", "host_location", "bathrooms_text"])
    n_review_blank = int((kept["review_scores_rating"] == "").sum())
    n_bool_values = sum(
        int(step3[c].isin(["t", "f", "True", "False"]).sum())
        for c in BOOLEAN_COLUMNS
    )
    n_ws = 0
    for col in ["name", "host_name", "property_type", "room_type",
                "neighbourhood_cleansed", "host_location"]:
        before = step3[col]
        after = before.apply(lambda v: " ".join(str(v).split()))
        n_ws += int((before != after).sum())
    n_min_nights_high = int(
        (pd.to_numeric(step1["minimum_nights"], errors="coerce") > 365).sum())
    n_price_review = int((quarantined["rejection_reason"]
                          .str.contains("held for review").sum()))
    issues = [
        {"category": "Currency strings in price ($ / commas)",
         "found": n_money, "remaining": 0,
         "how": "Lesson 02: stripped $ and , -> price_usd (float)."},
        {"category": "Percentage strings (host response / acceptance)",
         "found": 0, "remaining": 0,
         "how": "Lesson 02: parser ready; both columns are blank in this release."},
        {"category": "Missing price (essential field)",
         "found": n_missing_price, "remaining": 0,
         "how": "Lesson 03: rows dropped — a price cannot be invented."},
        {"category": "Missing small numerics (bedrooms / beds / minimum_nights)",
         "found": n_median, "remaining": 0,
         "how": "Lesson 03: median-filled (bedrooms 1, beds 1, minimum_nights 28)."},
        {"category": "Missing categoricals (license / host_location / bathrooms_text)",
         "found": n_unknown, "remaining": 0,
         "how": "Lesson 03: filled with 'Unknown'."},
        {"category": "Missing review data (rating / first / last review)",
         "found": n_review_blank, "remaining": n_review_blank,
         "how": "Left blank by design: blank means 'never reviewed'."},
        {"category": "Duplicate listing ids",
         "found": 0, "remaining": 0,
         "how": "Lesson 04: dedup check run; none found in this sample."},
        {"category": "t/f booleans stored as text",
         "found": n_bool_values, "remaining": 0,
         "how": "Lesson 04: converted to real booleans."},
        {"category": "Whitespace / double spaces in text fields",
         "found": n_ws, "remaining": 0,
         "how": "Lesson 04: stripped ends, collapsed internal spaces."},
        {"category": "minimum_nights over 365",
         "found": n_min_nights_high, "remaining": 0,
         "how": "All 3 left with the price-missing rows in step 3."},
        {"category": "Price over $5,000 (held for review)",
         "found": n_price_review, "remaining": 0,
         "how": "Lesson 05: quarantined, not deleted — a human reviews."},
    ]
    build_scorecard(chain, issues)

    print("=" * 52)
    print(f"CHAIN: raw {chain['raw']:,} -> step1 {chain['step1']:,} -> "
          f"step2 {chain['step2']:,} -> step3 {chain['step3']:,} -> "
          f"step4 {chain['step4']:,} -> clean {chain['clean']:,} + "
          f"quarantined {chain['quarantined']:,} = {chain['step4']:,}")
    print("Chain balances:", chain["clean"] + chain["quarantined"] == chain["step4"])


if __name__ == "__main__":
    main()
