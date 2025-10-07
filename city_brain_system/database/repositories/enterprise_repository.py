"""
企业仓储类
"""
from typing import Optional, Dict, Any, List
from .base_repository import BaseRepository
from ..models.enterprise import Enterprise


class EnterpriseRepository(BaseRepository):
    """企业数据访问仓储类"""
    
    def find_by_name(self, enterprise_name: str) -> Optional[Enterprise]:
        """根据企业名称查询企业信息"""
        query = """
        SELECT e.enterprise_id,
               e.enterprise_name,
               e.industry_id,
               e.area_id,
               i.industry_name,
               a.district_name
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        WHERE e.enterprise_name = %s
        """
        result = self._execute_single_query(query, (enterprise_name,))
        return Enterprise.from_dict(result) if result else None
    
    def find_by_id(self, enterprise_id: int) -> Optional[Enterprise]:
        """根据企业ID查询企业信息"""
        query = """
        SELECT e.enterprise_id,
               e.enterprise_name,
               e.industry_id,
               e.area_id,
               i.industry_name,
               a.district_name
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        WHERE e.enterprise_id = %s
        """
        result = self._execute_single_query(query, (enterprise_id,))
        return Enterprise.from_dict(result) if result else None
    
    def find_all(self) -> List[Enterprise]:
        """查询所有企业信息"""
        query = """
        SELECT e.enterprise_id,
               e.enterprise_name,
               e.industry_id,
               e.area_id,
               i.industry_name,
               a.district_name
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        ORDER BY e.enterprise_name
        """
        results = self._execute_query(query)
        return [Enterprise.from_dict(result) for result in results]