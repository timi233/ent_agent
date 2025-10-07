"""Normalize Excel data for database import."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "processed"


def clean_text(value: object) -> Optional[str]:
    """Normalize strings and preserve None."""
    if pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def normalize_phone(value: object) -> Optional[str]:
    text = clean_text(value)
    if not text:
        return None
    primary_matches = re.findall(r"(?:\d{2,}(?:[-]\d+)*)", text)
    fallback_matches = re.findall(r"\d+", text) if not primary_matches else []
    candidates = primary_matches or fallback_matches
    combined: List[str] = []
    for match in candidates:
        digits = re.sub(r"[^0-9+]", "", match)
        digits = digits.replace("-", "").replace("—", "").replace("–", "")
        if not digits:
            continue
        if combined and len(digits) <= 3 and len(combined[-1]) >= 7:
            combined[-1] = combined[-1] + digits
        else:
            combined.append(digits)
    if not combined:
        return None
    unique_numbers = list(dict.fromkeys(combined))
    return "|".join(unique_numbers)


def generate_md5(*parts: object) -> str:
    joined = "|".join(clean_text(p) or "" for p in parts)
    return hashlib.md5(joined.encode("utf-8")).hexdigest()


def to_decimal(value: object) -> Optional[Decimal]:
    text = clean_text(value)
    if text is None:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def to_int(value: object) -> Optional[int]:
    decimal_value = to_decimal(value)
    if decimal_value is None:
        return None
    try:
        return int(decimal_value)
    except (ValueError, OverflowError):
        return None


def parse_decimal_list(value: object) -> List[Decimal]:
    text = clean_text(value)
    if not text:
        return []
    parts: Iterable[str] = (segment.strip() for segment in text.split(","))
    decimals: List[Decimal] = []
    for part in parts:
        if not part:
            continue
        decimal_value = to_decimal(part)
        if decimal_value is None:
            continue
        decimals.append(decimal_value)
    return decimals


def split_multi_values(value: object) -> List[str]:
    text = clean_text(value)
    if not text:
        return []
    return [segment.strip() for segment in text.split(",") if segment.strip()]


@dataclass
class ExportedFrame:
    name: str
    frame: pd.DataFrame


class DataExporter:
    def __init__(self) -> None:
        self.ingested_at = (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )
        OUTPUT_DIR.mkdir(exist_ok=True)

    def export(self, frames: Iterable[ExportedFrame]) -> None:
        for exported in frames:
            path = OUTPUT_DIR / f"{exported.name}.csv"
            frame = exported.frame.copy()
            if not frame.empty:
                frame = frame.drop_duplicates()
            frame.to_csv(path, index=False)


def process_aishu_customers(exporter: DataExporter) -> None:
    source = DATA_DIR / "爱数客户_去重填充.xlsx"
    raw = pd.read_excel(source)
    raw = raw.drop(columns=[col for col in raw.columns if col.startswith("Unnamed")])

    rename_map = {
        "客户名称": "customer_name",
        "是否是服务过的客户": "is_serviced",
        "地区": "region",
        "行业": "industry",
        "对接人": "contact_name",
        "电话": "contact_phone",
        "职位": "contact_title",
        "产品": "product",
        "业务类型": "business_type_raw",
        "后续需求": "followup_needs",
        "跟进情况": "followup_status",
    }
    df = raw.rename(columns=rename_map)
    for column in df.columns:
        if column not in {"is_serviced", "contact_phone"}:
            df[column] = df[column].apply(clean_text)
    df["contact_phone"] = df["contact_phone"].apply(normalize_phone)
    df["is_serviced"] = df["is_serviced"].map({"是": True, "否": False})
    df["customer_id"] = df.apply(
        lambda row: generate_md5(row["customer_name"], row["region"]), axis=1
    )
    df["source_system"] = "AISHU"
    df["ingested_at"] = exporter.ingested_at

    business_types = []
    for _, row in df.iterrows():
        customer_id = row["customer_id"]
        for entry in split_multi_values(row.get("business_type_raw")):
            business_types.append(
                {
                    "customer_id": customer_id,
                    "business_type": entry,
                    "ingested_at": exporter.ingested_at,
                }
            )
    df = df.drop(columns=["business_type_raw"])

    exporter.export(
        [
            ExportedFrame(
                name="aishu_customers",
                frame=df[
                    [
                        "customer_id",
                        "customer_name",
                        "is_serviced",
                        "region",
                        "industry",
                        "contact_name",
                        "contact_phone",
                        "contact_title",
                        "product",
                        "followup_needs",
                        "followup_status",
                        "source_system",
                        "ingested_at",
                    ]
                ],
            ),
            ExportedFrame(
                name="aishu_customer_business_types",
                frame=pd.DataFrame(
                    business_types,
                    columns=["customer_id", "business_type", "ingested_at"],
                ),
            ),
        ]
    )


def process_ipg_customers(exporter: DataExporter) -> None:
    source = DATA_DIR / "IPG客户_去重填充.xlsx"
    raw = pd.read_excel(source)
    raw = raw.drop(columns=[col for col in raw.columns if col.startswith("Unnamed")])

    rename_map = {
        "客户名称": "customer_name",
        "地区": "region",
        "项目状态": "project_status",
        "产品": "product",
        "采购用户数": "users_purchased",
        "采购明细": "purchase_details",
        "联系人": "contact_name",
        "手机号": "contact_phone",
        "现场环境": "deployment_env",
        "跟进记录": "followup_notes",
    }
    df = raw.rename(columns=rename_map)
    for column in df.columns:
        if column not in {"users_purchased", "contact_phone"}:
            df[column] = df[column].apply(clean_text)
    df["contact_phone"] = df["contact_phone"].apply(normalize_phone)
    df["users_purchased"] = df["users_purchased"].apply(to_int)
    df["users_purchased"] = df["users_purchased"].astype("Int64")
    df["customer_id"] = df.apply(
        lambda row: generate_md5(row["customer_name"], row["region"]), axis=1
    )
    df["source_system"] = "IPG"
    df["ingested_at"] = exporter.ingested_at

    exporter.export(
        [
            ExportedFrame(
                name="ipg_customers",
                frame=df[
                    [
                        "customer_id",
                        "customer_name",
                        "region",
                        "project_status",
                        "product",
                        "users_purchased",
                        "purchase_details",
                        "contact_name",
                        "contact_phone",
                        "deployment_env",
                        "followup_notes",
                        "source_system",
                        "ingested_at",
                    ]
                ],
            )
        ]
    )


def process_aishu_opportunities(exporter: DataExporter) -> None:
    source = DATA_DIR / "爱数商机_去重填充.xlsx"
    raw = pd.read_excel(source)

    rename_map = {
        "客户名称": "customer_name",
        "地址": "address",
        "地区": "region",
        "行业": "industry",
        "产品": "product",
        "预算": "budget_raw",
        "需求": "needs",
        "关联项目": "related_project",
        "关联客户": "related_customer",
    }
    df = raw.rename(columns=rename_map)
    for column in df.columns:
        if column not in {"budget_raw"}:
            df[column] = df[column].apply(clean_text)

    df["opportunity_id"] = df.apply(
        lambda row: generate_md5(row["customer_name"], row["address"], row["product"]),
        axis=1,
    )
    df["source_system"] = "AISHU"
    df["ingested_at"] = exporter.ingested_at

    budget_rows = []
    totals = []
    for _, row in df.iterrows():
        amounts = parse_decimal_list(row.get("budget_raw"))
        if not amounts:
            totals.append(None)
        else:
            for amount in amounts:
                budget_rows.append(
                    {
                        "opportunity_id": row["opportunity_id"],
                        "budget_amount": f"{amount:.2f}",
                        "ingested_at": exporter.ingested_at,
                    }
                )
            total = sum(amounts)
            totals.append(f"{total:.2f}")
    df["budget_total"] = totals
    df = df.drop(columns=["budget_raw"])

    exporter.export(
        [
            ExportedFrame(
                name="aishu_opportunities",
                frame=df[
                    [
                        "opportunity_id",
                        "customer_name",
                        "address",
                        "region",
                        "industry",
                        "product",
                        "budget_total",
                        "needs",
                        "related_project",
                        "related_customer",
                        "source_system",
                        "ingested_at",
                    ]
                ],
            ),
            ExportedFrame(
                name="aishu_opportunity_budgets",
                frame=pd.DataFrame(
                    budget_rows,
                    columns=["opportunity_id", "budget_amount", "ingested_at"],
                ),
            ),
        ]
    )


def process_ipg_opportunities(exporter: DataExporter) -> None:
    source = DATA_DIR / "IPG商机_去重填充.xlsx"
    raw = pd.read_excel(source)
    raw = raw.drop(columns=[col for col in raw.columns if col.startswith("Unnamed")])

    rename_map = {
        "客户名称": "customer_name",
        "行业大类": "industry_major",
        "行业子类": "industry_minor",
        "地区": "region",
        "地址": "address",
        "对接人": "contact_name",
        "手机号": "contact_phone",
        "IPG点位": "ipg_points_raw",
        "客户状态": "status_raw",
        "销售的产品": "product_sold",
        "信心度": "confidence_raw",
    }
    df = raw.rename(columns=rename_map)
    for column in df.columns:
        if column not in {"ipg_points_raw", "status_raw", "confidence_raw"}:
            df[column] = df[column].apply(clean_text)
    df["contact_phone"] = df["contact_phone"].apply(normalize_phone)
    df["opportunity_id"] = df.apply(
        lambda row: generate_md5(row["customer_name"], row["address"], row["product_sold"]),
        axis=1,
    )
    df["source_system"] = "IPG"
    df["ingested_at"] = exporter.ingested_at

    # Confidence mapping
    confidence_map = {"高": "high", "中": "medium", "低": "low"}
    df["confidence_level"] = df["confidence_raw"].apply(
        lambda value: confidence_map.get(clean_text(value))
    )

    status_rows = []
    for _, row in df.iterrows():
        for status in split_multi_values(row.get("status_raw")):
            status_rows.append(
                {
                    "opportunity_id": row["opportunity_id"],
                    "status": status,
                    "ingested_at": exporter.ingested_at,
                }
            )

    point_rows = []
    totals = []
    for _, row in df.iterrows():
        points = parse_decimal_list(row.get("ipg_points_raw"))
        if not points:
            totals.append(None)
        else:
            for point in points:
                point_rows.append(
                    {
                        "opportunity_id": row["opportunity_id"],
                        "ipg_point": f"{point:.2f}",
                        "ingested_at": exporter.ingested_at,
                    }
                )
            totals.append(f"{sum(points):.2f}")
    df["ipg_point_total"] = totals

    df = df.drop(columns=["status_raw", "ipg_points_raw", "confidence_raw"])

    exporter.export(
        [
            ExportedFrame(
                name="ipg_opportunities",
                frame=df[
                    [
                        "opportunity_id",
                        "customer_name",
                        "industry_major",
                        "industry_minor",
                        "region",
                        "address",
                        "contact_name",
                        "contact_phone",
                        "product_sold",
                        "confidence_level",
                        "ipg_point_total",
                        "source_system",
                        "ingested_at",
                    ]
                ],
            ),
            ExportedFrame(
                name="ipg_opportunity_statuses",
                frame=pd.DataFrame(
                    status_rows,
                    columns=["opportunity_id", "status", "ingested_at"],
                ),
            ),
            ExportedFrame(
                name="ipg_opportunity_ipg_points",
                frame=pd.DataFrame(
                    point_rows,
                    columns=["opportunity_id", "ipg_point", "ingested_at"],
                ),
            ),
        ]
    )


def process_orders(exporter: DataExporter) -> None:
    source = DATA_DIR / "项目订单_去重填充.xlsx"
    raw = pd.read_excel(source)

    rename_map = {
        "客户名称": "customer_name",
        "品牌": "brand",
        "销售": "sales_rep",
        "产品": "product",
        "金额": "amount_raw",
        "客户地点": "customer_location",
        "客户分类": "category_raw",
    }
    df = raw.rename(columns=rename_map)
    for column in df.columns:
        if column not in {"amount_raw", "category_raw"}:
            df[column] = df[column].apply(clean_text)

    df["order_id"] = df.apply(
        lambda row: generate_md5(
            row["customer_name"], row["product"], row["amount_raw"], row["sales_rep"]
        ),
        axis=1,
    )
    df["source_system"] = "MIXED"
    df["ingested_at"] = exporter.ingested_at

    amounts = []
    for _, row in df.iterrows():
        decimal_value = to_decimal(row.get("amount_raw"))
        amounts.append(f"{decimal_value:.2f}" if decimal_value is not None else None)
    df["order_amount"] = amounts

    category_rows = []
    for _, row in df.iterrows():
        for category in split_multi_values(row.get("category_raw")):
            category_rows.append(
                {
                    "order_id": row["order_id"],
                    "category": category,
                    "ingested_at": exporter.ingested_at,
                }
            )

    df = df.drop(columns=["amount_raw", "category_raw"])

    exporter.export(
        [
            ExportedFrame(
                name="orders",
                frame=df[
                    [
                        "order_id",
                        "customer_name",
                        "brand",
                        "sales_rep",
                        "product",
                        "order_amount",
                        "customer_location",
                        "source_system",
                        "ingested_at",
                    ]
                ],
            ),
            ExportedFrame(
                name="order_categories",
                frame=pd.DataFrame(
                    category_rows,
                    columns=["order_id", "category", "ingested_at"],
                ),
            ),
        ]
    )


def main() -> None:
    exporter = DataExporter()
    process_aishu_customers(exporter)
    process_ipg_customers(exporter)
    process_aishu_opportunities(exporter)
    process_ipg_opportunities(exporter)
    process_orders(exporter)


if __name__ == "__main__":
    main()
