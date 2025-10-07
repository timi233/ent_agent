from typing import Optional, List, Dict, Any, Tuple
import pymysql
from pymysql.cursors import DictCursor
from ..simple_connection import get_database_connection
from ...utils.simple_logger import get_logger

logger = get_logger("industry_mapping")

class IndustryMappingRepository:
    """
    行业大脑与产业链映射仓储
    数据库：City_Brain_DB
    相关表：
      - QD_area:            id, area_name
      - QD_industry:        id, industry_name
      - QD_industry_brain:  brain_id, brain_name, area_id, build_year, brain_remark
      - QD_brain_industry_rel: brain_id, industry_id
      - QD_enterprise_chain_leader: id, chain_name, industry_name, area_id, remark
    """

    def __init__(self):
        self.db = get_database_connection()

    def _conn(self) -> pymysql.Connection:
        return self.db.get_connection()

    def _find_area_and_industry_by_company(self, company_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        解析企业所在地区与行业。
        优先从 QD_customer / QD_enterprise_chain_leader 等本地数据中获取；
        若无直接映射，这里先用模糊回退到地址解析模块之外的方法（留空，由上层传递或后续增强）。
        目前简单策略：不在此做复杂解析，仅返回 None，交由上层或外部模块补充。
        """
        # 可扩展：通过 customer/enterprise 表进行模糊查询，这里占位返回 None
        return None, None

    def normalize_industry(self, name: Optional[str]) -> Optional[str]:
        if not name:
            return None
        return name.strip()

    def normalize_area(self, name: Optional[str]) -> Optional[str]:
        if not name:
            return None
        return name.strip()

    def get_area_id_by_name(self, area_name: str) -> Optional[int]:
        sql = "SELECT id FROM QD_area WHERE area_name = %s LIMIT 1"
        with self._conn().cursor(DictCursor) as cur:
            cur.execute(sql, (area_name,))
            row = cur.fetchone()
            return row["id"] if row else None

    def get_industry_id_by_name(self, industry_name: str) -> Optional[int]:
        sql = "SELECT id FROM QD_industry WHERE industry_name = %s LIMIT 1"
        with self._conn().cursor(DictCursor) as cur:
            cur.execute(sql, (industry_name,))
            row = cur.fetchone()
            return row["id"] if row else None

    def get_brains_by_area(self, area_id: int) -> List[Dict[str, Any]]:
        """
        查询地区下的产业大脑，并附带其关联产业列表
        """
        sql_brains = """
            SELECT b.brain_id, b.brain_name, b.area_id, b.build_year, b.brain_remark
            FROM QD_industry_brain b
            WHERE b.area_id = %s
            ORDER BY b.brain_name
        """
        result: List[Dict[str, Any]] = []
        with self._conn().cursor(DictCursor) as cur:
            cur.execute(sql_brains, (area_id,))
            brains = cur.fetchall() or []
            for b in brains:
                # 取关联产业
                sql_rel = """
                    SELECT i.industry_name
                    FROM QD_brain_industry_rel r
                    JOIN QD_industry i ON i.id = r.industry_id
                    WHERE r.brain_id = %s
                    ORDER BY i.industry_name
                """
                cur.execute(sql_rel, (b["brain_id"],))
                inds = [row["industry_name"] for row in (cur.fetchall() or [])]
                b["related_industries"] = inds
                result.append(b)
        return result

    def get_chains_by_area_or_industry(self, area_id: Optional[int], industry_name: Optional[str]) -> List[Dict[str, Any]]:
        """
        优先按地区筛选产业链，其次按行业名称模糊匹配
        """
        result: List[Dict[str, Any]] = []
        with self._conn().cursor(DictCursor) as cur:
            if area_id is not None:
                sql_area = """
                    SELECT id, chain_name, industry_name, area_id, remark
                    FROM QD_enterprise_chain_leader
                    WHERE area_id = %s
                    ORDER BY chain_name
                """
                cur.execute(sql_area, (area_id,))
                result = cur.fetchall() or []

            # 如果按地区没有结果或需要补充，按行业名称模糊匹配
            if industry_name:
                sql_ind = """
                    SELECT id, chain_name, industry_name, area_id, remark
                    FROM QD_enterprise_chain_leader
                    WHERE industry_name LIKE %s
                    ORDER BY chain_name
                """
                cur.execute(sql_ind, (f"%{industry_name}%",))
                rows = cur.fetchall() or []
                # 去重合并
                seen = {(r["id"]) for r in result}
                for r in rows:
                    if r["id"] not in seen:
                        result.append(r)
        return result

    def find_brain_chain(self, company_name: str, region: Optional[str], industry: Optional[str]) -> Dict[str, Any]:
        """
        主查询逻辑：先解析地区与行业（来自参数或外部解析），再匹配产业大脑与产业链。
        """
        region = self.normalize_area(region) or None
        industry = self.normalize_industry(industry) or None

        if not region or not industry:
            # 尝试本仓储内部的简易解析（当前返回 None, None）
            guessed_region, guessed_industry = self._find_area_and_industry_by_company(company_name)
            region = region or guessed_region
            industry = industry or guessed_industry

        area_id = self.get_area_id_by_name(region) if region else None
        brains: List[Dict[str, Any]] = []
        chains: List[Dict[str, Any]] = []

        if area_id is not None:
            brains = self.get_brains_by_area(area_id)

        chains = self.get_chains_by_area_or_industry(area_id, industry)

        # 过滤产业大脑：仅保留其关联产业中与企业行业匹配的项（若提供行业）
        if industry and brains:
            filtered = []
            for b in brains:
                inds = b.get("related_industries", [])
                if any(industry in x or x in industry for x in inds):
                    filtered.append(b)
            brains = filtered or brains  # 无匹配则保留原始，避免空白

        return {
            "region": region,
            "company_industry": industry,
            "industry_brains": [
                {
                    "brain_id": b.get("brain_id"),
                    "brain_name": b.get("brain_name"),
                    "area_id": b.get("area_id"),
                    "build_year": b.get("build_year"),
                    "industries": b.get("related_industries", []),
                    "source": "City_Brain_DB"
                } for b in brains
            ],
            "industry_chains": [
                {
                    "id": c.get("id"),
                    "chain_name": c.get("chain_name"),
                    "industry_name": c.get("industry_name"),
                    "area_id": c.get("area_id"),
                    "remark": c.get("remark"),
                    "source": "City_Brain_DB"
                } for c in chains
            ]
        }