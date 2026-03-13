# Drug Regulatory Platform - Scripts

This directory contains scripts for fetching real drug data from regulatory authorities worldwide.

## Quick Start

```bash
# Fetch real data from all regulatory authorities
python scripts/fetch_and_store_real_data.py

# Check database state
python scripts/check_db_data.py
```

## Core Scripts

### 1. Main Scripts

| Script | Purpose |
|--------|---------|
| `fetch_and_store_real_data.py` | **MAIN**: Fetch real data from FDA, EMA, EMC, etc. and store in database |
| `check_db_data.py` | Check database state, counts, and verify data exists |
| `add_country_data.py` | Initialize regulatory authorities in database |

### 2. Real Data Fetchers (Country-Specific)

| Script | Country | Authority | Status |
|--------|---------|-----------|--------|
| `search_ema.py` | EU | European Medicines Agency (EMA) | ✅ Working |
| `search_emc.py` | GB | UK Medicines Compendium (EMC) | ✅ Working |
| `search_pmda.py` | JP | PMDA (Japan) | ⚠️ Limited |
| `search_dpd.py` | CA | Health Canada DPD | ⚠️ Limited |
| `search_tga.py` | AU | TGA (Australia) | ⚠️ SSL Issues |

### 3. Data Ingestion Scripts

| Script | Purpose |
|--------|---------|
| `ingest_ema_data.py` | Ingest EMA EPAR documents with PDF parsing |
| `ingest_ema_simple.py` | Simplified EMA ingestion |
| `ingest_uk_data.py` | Ingest UK EMC data |
| `populate_all_countries_real_data.py` | Alternative populate script |
| `reingest_all_countries.py` | Re-import all country data |

### 4. Testing & Query

| Script | Purpose |
|--------|---------|
| `query.py` | Query interface for testing semantic search |
| `main.py` | Original entry point (for reference) |

## Data Sources

### Working (Real Data Available)
- **US (FDA)**: openFDA API - 23 drugs with full label data
- **EU (EMA)**: EPAR documents - 20 drugs with assessment data
- **GB (EMC)**: UK medicines database - 9 drugs with product data

### Limited/Not Working
- **CA (Health Canada)**: Scraping challenges
- **AU (TGA)**: SSL certificate issues
- **JP (PMDA)**: Language/format barriers
- **IN (CDSCO)**: Not implemented

## Usage Examples

### Fetch Real Data for All Drugs
```bash
python scripts/fetch_and_store_real_data.py
```
This fetches data from FDA, EMA, and EMC, storing only real data found.

### Check Database State
```bash
python scripts/check_db_data.py
```
Shows counts of drugs, labels, sections, and regulatory authorities.

### Search Specific Authority
```bash
# Search EMA for a drug
python scripts/search_ema.py

# Search UK EMC for a drug
python scripts/search_emc.py
```

## Removed Scripts (Cleanup)

The following 20 obsolete scripts were removed:
- Mock data scripts (5): `clear_simulated_data.py`, etc.
- Debug scripts (5): `check_placeholders.py`, etc.
- Test scripts (3): `test_comparison.py`, etc.
- Drug-specific (2): `generate_genvoya_report.py`, etc.
- Other obsolete (5): `build_vector_store.py`, etc.

## Notes

- All data fetched is **REAL** from regulatory authorities
- No mock/generated data is stored
- If a drug isn't found in a country's database, no label is created
- This reflects real-world approval differences across countries
