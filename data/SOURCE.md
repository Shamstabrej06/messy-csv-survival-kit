# Data source

**Dataset:** Inside Airbnb — Toronto `listings.csv`, release 2026-09-16
**Source URL:** https://data.insideairbnb.com/canada/on/toronto/2026-09-16/data/listings.csv.gz
**Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0)
**Download date:** 2026-11-08
**Full file:** 22,050 rows × 90 columns (63 MB uncompressed, 13 MB gzipped)

## What is committed here

`data/raw/listings_sample_2000.csv` — the first 2,000 rows of the raw
file, untouched. Headers and first/last listing ids were verified
identical to the full file. Keeping the sample small keeps the repo lean;
the CC BY 4.0 licence permits redistribution with attribution, which this
file and the README provide.

## How to get the full file

```bash
curl -L -o listings.csv.gz \
  https://data.insideairbnb.com/canada/on/toronto/2026-09-16/data/listings.csv.gz
gunzip listings.csv.gz
```

Then point `config.py`'s `RAW_PATH` at the downloaded file — the lesson
scripts run unchanged against the full file.

## Attribution

Inside Airbnb (insideairbnb.com). Data compiled from publicly available
information on Airbnb. This project is a self-directed learning project
built on public open data; it is not client or employer work.
