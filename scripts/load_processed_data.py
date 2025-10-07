"""Load processed CSVs into the staging schema defined in scripts/staging_schema.sql."""
from __future__ import annotations

import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import pandas as pd
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

Converter = Callable[[pd.Series], pd.Series]


def ensure_inputs() -> None:
    if not PROCESSED_DIR.exists():
        raise FileNotFoundError(f"Processed directory not found: {PROCESSED_DIR}")


def to_bool(series: pd.Series) -> pd.Series:
    truthy = {"true", "1", "t", "yes", "y"}
    falsy = {"false", "0", "f", "no", "n"}
    def convert(value: object) -> object:
        if pd.isna(value):
            return None
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text in truthy:
            return True
        if text in falsy:
            return False
        return None
    return series.apply(convert)


def to_int(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype("Int64")


def to_decimal_series(series: pd.Series) -> pd.Series:
    def convert(value: object) -> object:
        if pd.isna(value):
            return None
        text = str(value).strip()
        if not text:
            return None
        try:
            return Decimal(text)
        except Exception:  # noqa: BLE001
            return None
    return series.apply(convert)


def to_timestamp(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True, errors="coerce")


LOAD_CONFIG: List[Tuple[str, str, Dict[str, Converter]]] = [
    (
        "aishu_customers",
        "aishu_customers.csv",
        {
            "is_serviced": to_bool,
            "ingested_at": to_timestamp,
        },
    ),
    (
        "aishu_customer_business_types",
        "aishu_customer_business_types.csv",
        {
            "ingested_at": to_timestamp,
        },
    ),
    (
        "ipg_customers",
        "ipg_customers.csv",
        {
            "users_purchased": to_int,
            "ingested_at": to_timestamp,
        },
    ),
    (
        "aishu_opportunities",
        "aishu_opportunities.csv",
        {
            "budget_total": to_decimal_series,
            "ingested_at": to_timestamp,
        },
    ),
    (
        "aishu_opportunity_budgets",
        "aishu_opportunity_budgets.csv",
        {
            "budget_amount": to_decimal_series,
            "ingested_at": to_timestamp,
        },
    ),
    (
        "ipg_opportunities",
        "ipg_opportunities.csv",
        {
            "ipg_point_total": to_decimal_series,
            "ingested_at": to_timestamp,
        },
    ),
    (
        "ipg_opportunity_statuses",
        "ipg_opportunity_statuses.csv",
        {
            "ingested_at": to_timestamp,
        },
    ),
    (
        "ipg_opportunity_ipg_points",
        "ipg_opportunity_ipg_points.csv",
        {
            "ipg_point": to_decimal_series,
            "ingested_at": to_timestamp,
        },
    ),
    (
        "orders",
        "orders.csv",
        {
            "order_amount": to_decimal_series,
            "ingested_at": to_timestamp,
        },
    ),
    (
        "order_categories",
        "order_categories.csv",
        {
            "ingested_at": to_timestamp,
        },
    ),
]


TRUNCATE_ORDER = [
    "order_categories",
    "orders",
    "ipg_opportunity_ipg_points",
    "ipg_opportunity_statuses",
    "ipg_opportunities",
    "aishu_opportunity_budgets",
    "aishu_opportunities",
    "ipg_customers",
    "aishu_customer_business_types",
    "aishu_customers",
]


def normalize_empty_strings(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.columns:
        if df[column].dtype == object:
            df[column] = df[column].apply(
                lambda value: value.strip() if isinstance(value, str) else value
            )
            df[column] = df[column].replace({"": None, "nan": None, "NaN": None})
    return df


def load_dataframe(engine, table: str, csv_name: str, conversions: Dict[str, Converter]) -> None:
    path = PROCESSED_DIR / csv_name
    if not path.exists():
        raise FileNotFoundError(f"Missing processed file: {path}")
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df = normalize_empty_strings(df)
    for column, converter in conversions.items():
        if column in df.columns:
            df[column] = converter(df[column])
    df.to_sql(table, engine, schema="staging", if_exists="append", index=False, method="multi")


def truncate_tables(engine) -> None:
    with engine.begin() as conn:
        for table in TRUNCATE_ORDER:
            conn.execute(text(f"TRUNCATE TABLE staging.{table} RESTART IDENTITY CASCADE"))


def main() -> None:
    ensure_inputs()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set. Export it before running this script.", file=sys.stderr)
        sys.exit(1)

    engine = create_engine(database_url)
    truncate_tables(engine)

    for table, csv_name, converters in LOAD_CONFIG:
        load_dataframe(engine, table, csv_name, converters)
        print(f"Loaded staging.{table}")


if __name__ == "__main__":
    main()
