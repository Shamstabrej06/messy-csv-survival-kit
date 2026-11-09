"""Single source of truth for file paths in the Messy CSV Survival Kit.

Every lesson script imports this module, so the kit runs against the
committed 2,000-row sample by default. To run the same lessons against a
locally downloaded FULL Inside Airbnb file instead, point RAW_PATH at it —
no other change is needed. (The full Toronto file is ~63 MB; the sample is
the first 2,000 rows of that file, untouched.)

Dataset: Inside Airbnb — Toronto listings.csv, release 2026-09-16.
Licence: Creative Commons Attribution 4.0 International (CC BY 4.0).
Source: https://data.insideairbnb.com/canada/on/toronto/2026-09-16/data/listings.csv.gz
Downloaded: 2026-11-08. Full file: 22,050 rows x 90 columns.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# --- Inputs ---------------------------------------------------------------
RAW_PATH = REPO_ROOT / "data" / "raw" / "listings_sample_2000.csv"
FULL_FILE_URL = (
    "https://data.insideairbnb.com/canada/on/toronto/2026-09-16"
    "/data/listings.csv.gz"
)
FULL_FILE_ROWS = 22_050
FULL_FILE_COLUMNS = 90

# --- Outputs (one file per lesson step) ------------------------------------
OUTPUTS_DIR = REPO_ROOT / "outputs"
STEP1_PATH = OUTPUTS_DIR / "step1_loaded.csv"
STEP2_PATH = OUTPUTS_DIR / "step2_numeric.csv"
STEP3_PATH = OUTPUTS_DIR / "step3_complete.csv"
STEP4_PATH = OUTPUTS_DIR / "step4_deduped.csv"
CLEAN_PATH = OUTPUTS_DIR / "clean_listings.csv"
QUARANTINE_PATH = OUTPUTS_DIR / "quarantine.csv"
SQLITE_PATH = OUTPUTS_DIR / "clean_listings.db"
SCORECARD_PATH = OUTPUTS_DIR / "Data_Quality_Scorecard.xlsx"
