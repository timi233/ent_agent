"""Import industry brain and chain leader data from Excel into City_Brain_DB."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

import mysql.connector
import pandas as pd

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class BrainRecord:
    brain_name: str
    city: str
    district: str
    year: Optional[int]
    industry_name: str
    sources: Set[str] = field(default_factory=set)
    chain_leaders: Set[str] = field(default_factory=set)


@dataclass
class LeaderRecord:
    name: str
    industries: Set[str] = field(default_factory=set)
    cities: Set[str] = field(default_factory=set)
    districts: Set[str] = field(default_factory=set)
    brains: Set[str] = field(default_factory=set)
    statuses: Set[str] = field(default_factory=set)

    def primary_city(self) -> Optional[str]:
        return next(iter(self.cities), None)

    def primary_district(self) -> Optional[str]:
        return next(iter(self.districts), None)

    def primary_industry(self) -> Optional[str]:
        return next(iter(self.industries), None)

    def remark(self) -> Optional[str]:
        parts: List[str] = []
        if self.statuses:
            parts.append(f"链主状态: {'、'.join(sorted(self.statuses))}")
        if self.brains:
            parts.append(f"关联产业大脑: {'、'.join(sorted(self.brains))}")
        if not parts:
            return None
        return '；'.join(parts)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

INVALID_CITY_TOKENS = ("省国资委", "驻鲁央企")
PLACEHOLDER_LEADER_TOKENS = ("无明确链主", "链主已参与其他配对")


def normalize_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    text = str(value).strip()
    return text or None


def normalize_city(city: Optional[str]) -> Optional[str]:
    text = normalize_text(city)
    if text is None:
        return None
    if any(token in text for token in INVALID_CITY_TOKENS):
        return None
    if text.endswith("市") or text.endswith("盟") or text.endswith("地区"):
        return text
    return text + "市"


def normalize_district(district: Optional[str]) -> Optional[str]:
    return normalize_text(district)


def parse_year(value) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, float):
        if math.isnan(value):
            return None
        try:
            year = int(round(value))
        except Exception:
            return None
    else:
        text = str(value).strip()
        if not text:
            return None
        try:
            year = int(float(text))
        except Exception:
            digits = re.findall(r"(20\d{2})", text)
            year = int(digits[0]) if digits else None
    if year and 2000 <= year <= 2035:
        return year
    return None


def is_placeholder_leader(name: Optional[str]) -> bool:
    if not name:
        return True
    return any(token in name for token in PLACEHOLDER_LEADER_TOKENS)


INDUSTRY_TYPE_RULES: List[Tuple[re.Pattern[str], str]] = [
    (re.compile(r"信息|智能|电子|数据|AI|软件|网络|通信"), "高新技术产业"),
    (re.compile(r"医|药|健康|生命"), "生命健康产业"),
    (re.compile(r"农|粮|花生|茶|牧|食品"), "现代农业"),
    (re.compile(r"服务|物流|零售|贸易|商务"), "现代服务业"),
    (re.compile(r"能源|电力|风|低空|绿色"), "能源与新兴产业"),
    (re.compile(r"纺织|服装|橡胶|机械|装备|制造|加工|金属|汽车|轨道|造纸|木|设备"), "先进制造业"),
]
DEFAULT_INDUSTRY_TYPE = "其他产业"


def infer_industry_type(industry_name: str) -> str:
    name = industry_name or ""
    for pattern, category in INDUSTRY_TYPE_RULES:
        if pattern.search(name):
            return category
    return DEFAULT_INDUSTRY_TYPE


# ---------------------------------------------------------------------------
# Data ingestion
# ---------------------------------------------------------------------------

DATA_DIR = Path("data")
BASELINE_FILE = DATA_DIR / "产业大脑信息baseline.xlsx"
QINGDAO_FILE = DATA_DIR / "产业大脑与链主企业-青岛.xlsx"


def load_baseline() -> List[BrainRecord]:
    df = pd.read_excel(BASELINE_FILE, sheet_name="产业大脑", header=4)
    df = df.rename(columns={"Unnamed: 5": "区县"})
    for col in ("地区", "区县", "时间", "产业大脑", "行业"):
        df[col] = df[col].ffill()
    records: Dict[Tuple[str, str, str], BrainRecord] = {}
    for _, row in df.iterrows():
        city = normalize_city(row.get("地区"))
        district = normalize_district(row.get("区县"))
        brain_name = normalize_text(row.get("产业大脑"))
        industry = normalize_text(row.get("行业"))
        year = parse_year(row.get("时间"))
        if not (city and district and brain_name and industry):
            continue
        key = (brain_name, city, district)
        record = records.get(key)
        if record is None:
            record = BrainRecord(
                brain_name=brain_name,
                city=city,
                district=district,
                year=year,
                industry_name=industry,
                sources={"baseline"},
            )
            records[key] = record
        else:
            record.sources.add("baseline")
            if record.year is None and year is not None:
                record.year = year
    return list(records.values())


def load_qingdao() -> Tuple[List[BrainRecord], Dict[str, LeaderRecord]]:
    df = pd.read_excel(QINGDAO_FILE, sheet_name="产业大脑和链主企业名单")
    df = df.rename(columns={"行业分类": "行业"})
    for col in ("城市", "区域", "时间", "产业大脑", "行业", "链主企业", "备注"):
        df[col] = df[col].ffill()

    brain_records: Dict[Tuple[str, str, str], BrainRecord] = {}
    leader_records: Dict[str, LeaderRecord] = {}

    for _, row in df.iterrows():
        city = normalize_city(row.get("城市"))
        district = normalize_district(row.get("区域"))
        brain_name = normalize_text(row.get("产业大脑"))
        industry = normalize_text(row.get("行业"))
        year = parse_year(row.get("时间"))
        if not (city and district and brain_name and industry):
            continue
        key = (brain_name, city, district)
        record = brain_records.get(key)
        if record is None:
            record = BrainRecord(
                brain_name=brain_name,
                city=city,
                district=district,
                year=year,
                industry_name=industry,
                sources={"qingdao"},
            )
            brain_records[key] = record
        else:
            record.sources.add("qingdao")
            if record.year is None and year is not None:
                record.year = year

        leader_name = normalize_text(row.get("链主企业"))
        if leader_name and not is_placeholder_leader(leader_name):
            record.chain_leaders.add(leader_name)
            leader = leader_records.get(leader_name)
            if leader is None:
                leader = LeaderRecord(name=leader_name)
                leader_records[leader_name] = leader
            leader.cities.add(city)
            leader.districts.add(district)
            leader.industries.add(industry)
            leader.brains.add(brain_name)
            remark = normalize_text(row.get("备注"))
            if remark:
                leader.statuses.add(remark)
    return list(brain_records.values()), leader_records


def merge_brain_records(baseline: Iterable[BrainRecord], qingdao: Iterable[BrainRecord]) -> Dict[Tuple[str, str, str], BrainRecord]:
    merged: Dict[Tuple[str, str, str], BrainRecord] = {}
    for record in baseline:
        key = (record.brain_name, record.city, record.district)
        merged[key] = record
    for record in qingdao:
        key = (record.brain_name, record.city, record.district)
        existing = merged.get(key)
        if existing is None:
            merged[key] = record
        else:
            existing.sources.update(record.sources)
            existing.chain_leaders.update(record.chain_leaders)
            if existing.year is None and record.year is not None:
                existing.year = record.year
            if not existing.industry_name and record.industry_name:
                existing.industry_name = record.industry_name
    return merged


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

@dataclass
class DatabaseContext:
    connection: mysql.connector.MySQLConnection
    area_cache: Dict[Tuple[str, str], int]
    industry_cache: Dict[str, int]
    brain_cache: Dict[Tuple[str, int], int]
    leader_cache: Dict[str, int]
    relation_cache: Set[Tuple[int, int]]


def connect_database() -> mysql.connector.MySQLConnection:
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="City_Brain_user_mysql",
        password="CityBrain@2024",
        database="City_Brain_DB",
        charset="utf8mb4",
    )


def load_caches(cursor) -> Tuple[Dict[Tuple[str, str], int], Dict[str, int], Dict[Tuple[str, int], int], Dict[str, int], Set[Tuple[int, int]]]:
    cursor.execute("SELECT area_id, city_name, district_name FROM QD_area")
    area_cache = {(row[1], row[2]): row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT industry_id, industry_name FROM QD_industry")
    industry_cache = {row[1]: row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT brain_id, brain_name, area_id FROM QD_industry_brain")
    brain_cache = {(row[1], row[2]): row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT enterprise_id, enterprise_name FROM QD_enterprise_chain_leader")
    leader_cache = {row[1]: row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT brain_id, industry_id FROM QD_brain_industry_rel")
    relation_cache = {(row[0], row[1]) for row in cursor.fetchall()}

    return area_cache, industry_cache, brain_cache, leader_cache, relation_cache


def get_or_create_area(ctx: DatabaseContext, cursor, city: str, district: str) -> Tuple[int, bool]:
    key = (city, district)
    area_id = ctx.area_cache.get(key)
    if area_id is not None:
        return area_id, False
    cursor.execute(
        "INSERT INTO QD_area (city_name, district_name) VALUES (%s, %s)",
        (city, district),
    )
    area_id = cursor.lastrowid
    ctx.area_cache[key] = area_id
    return area_id, True


def get_or_create_industry(ctx: DatabaseContext, cursor, industry_name: str) -> Tuple[int, bool]:
    industry_name = industry_name.strip()
    industry_id = ctx.industry_cache.get(industry_name)
    if industry_id is not None:
        return industry_id, False
    industry_type = infer_industry_type(industry_name)
    cursor.execute(
        "INSERT INTO QD_industry (industry_name, industry_type) VALUES (%s, %s)",
        (industry_name, industry_type),
    )
    industry_id = cursor.lastrowid
    ctx.industry_cache[industry_name] = industry_id
    return industry_id, True


def get_or_create_brain(ctx: DatabaseContext, cursor, record: BrainRecord, area_id: int) -> Tuple[int, bool]:
    key = (record.brain_name, area_id)
    brain_id = ctx.brain_cache.get(key)
    if brain_id is not None:
        return brain_id, False
    remark_parts = [f"来源: {','.join(sorted(record.sources))}"]
    if record.chain_leaders:
        leaders = "、".join(sorted(record.chain_leaders))
        remark_parts.append("链主企业: " + leaders)
    remark = "；".join(remark_parts)
    cursor.execute(
        "INSERT INTO QD_industry_brain (brain_name, area_id, build_year, brain_remark) VALUES (%s, %s, %s, %s)",
        (record.brain_name, area_id, record.year, remark),
    )
    brain_id = cursor.lastrowid
    ctx.brain_cache[key] = brain_id
    return brain_id, True


def ensure_brain_industry_relation(ctx: DatabaseContext, cursor, brain_id: int, industry_id: int) -> bool:
    key = (brain_id, industry_id)
    if key in ctx.relation_cache:
        return False
    cursor.execute(
        "INSERT INTO QD_brain_industry_rel (brain_id, industry_id) VALUES (%s, %s)",
        (brain_id, industry_id),
    )
    ctx.relation_cache.add(key)
    return True


def get_or_create_leader(ctx: DatabaseContext, cursor, leader: LeaderRecord, area_id: Optional[int], industry_id: Optional[int]) -> Tuple[int, bool]:
    leader_id = ctx.leader_cache.get(leader.name)
    if leader_id is not None:
        return leader_id, False
    cursor.execute(
        "INSERT INTO QD_enterprise_chain_leader (enterprise_name, industry_id, area_id, enterprise_remark) VALUES (%s, %s, %s, %s)",
        (
            leader.name,
            industry_id,
            area_id,
            leader.remark(),
        ),
    )
    leader_id = cursor.lastrowid
    ctx.leader_cache[leader.name] = leader_id
    return leader_id, True


# ---------------------------------------------------------------------------
# Main routine
# ---------------------------------------------------------------------------

def main() -> None:
    print("Loading Excel data...")
    baseline_records = load_baseline()
    qingdao_records, leader_records = load_qingdao()
    merged_brains = merge_brain_records(baseline_records, qingdao_records)

    print(f"Baseline brains: {len(baseline_records)}")
    print(f"Qingdao brains: {len(qingdao_records)}")
    print(f"Merged brains: {len(merged_brains)}")
    print(f"Leader records: {len(leader_records)}")

    connection = connect_database()
    connection.autocommit = False
    cursor = connection.cursor()
    try:
        area_cache, industry_cache, brain_cache, leader_cache, relation_cache = load_caches(cursor)
        ctx = DatabaseContext(connection, area_cache, industry_cache, brain_cache, leader_cache, relation_cache)

        new_areas = new_industries = new_brains = new_relations = new_leaders = 0

        for record in merged_brains.values():
            area_id, created_area = get_or_create_area(ctx, cursor, record.city, record.district)
            if created_area:
                new_areas += 1
            industry_id, created_industry = get_or_create_industry(ctx, cursor, record.industry_name)
            if created_industry:
                new_industries += 1
            brain_id, created_brain = get_or_create_brain(ctx, cursor, record, area_id)
            if created_brain:
                new_brains += 1
            if ensure_brain_industry_relation(ctx, cursor, brain_id, industry_id):
                new_relations += 1

        for leader in leader_records.values():
            primary_city = leader.primary_city()
            primary_district = leader.primary_district()
            area_id = None
            if primary_city and primary_district:
                area_id, created_area = get_or_create_area(ctx, cursor, primary_city, primary_district)
                if created_area:
                    new_areas += 1
            industry_name = leader.primary_industry() or "未分类"
            industry_id, created_industry = get_or_create_industry(ctx, cursor, industry_name)
            if created_industry:
                new_industries += 1
            _, created_leader = get_or_create_leader(ctx, cursor, leader, area_id, industry_id)
            if created_leader:
                new_leaders += 1

        connection.commit()

        print("Import completed")
        print(f"New areas inserted: {new_areas}")
        print(f"New industries inserted: {new_industries}")
        print(f"New brains inserted: {new_brains}")
        print(f"New brain-industry relations inserted: {new_relations}")
        print(f"New chain leaders inserted: {new_leaders}")
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
