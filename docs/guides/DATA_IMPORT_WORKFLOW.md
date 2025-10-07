# Data Import Workflow

Use this guide to refresh the staging layer from the Excel datasets stored in `data/`.

## 1. Prepare normalized CSV extracts
1. Install Python dependencies if needed:
   ```bash
   pip install pandas openpyxl
   ```
2. Run the cleaner to regenerate normalized files under `data/processed/`:
   ```bash
   python scripts/prepare_data_for_import.py
   ```
   The script drops orphaned Excel columns, harmonises enums, generates MD5 keys, and emits bridge tables for multi-value fields.

## 2. Ensure the database schema is ready
1. Export a Postgres `DATABASE_URL` (e.g. `postgresql+psycopg2://user:pass@host:5432/db`).
2. Apply the staging DDL once per environment:
   ```bash
   psql "$DATABASE_URL" -f scripts/staging_schema.sql
   ```
   This creates the `staging` schema with typed tables that match the CSV headers.

## 3. Load processed files into staging
1. Install loader dependencies:
   ```bash
   pip install pandas sqlalchemy psycopg2-binary
   ```
2. Execute the loader:
   ```bash
   python scripts/load_processed_data.py
   ```
   The script truncates staging tables, casts numeric/boolean/timestamp columns, and bulk-inserts each CSV.

## 4. Post-load validation
- Verify row counts against CSVs:
  ```bash
  \\copy (
     SELECT 'staging.aishu_customers' AS table, COUNT(*) FROM staging.aishu_customers
     UNION ALL SELECT 'staging.orders', COUNT(*) FROM staging.orders
  ) TO STDOUT WITH CSV HEADER
  ```
- Spot-check critical columns (e.g., `contact_phone`, `order_amount`) for nulls using SQL or pandas.
- Archive the processed CSVs or tag the git commit to retain provenance.

## 5. Scheduling tips
- Wrap steps 1–3 in a cron or CI job; log outputs under `logs/` for traceability.
- Fail fast if new Excel files appear without a matching mapping—extend `prepare_data_for_import.py` before running the loader.
- Prefer Alembic migrations for schema evolution; update both `staging_schema.sql` and downstream models in lockstep.
