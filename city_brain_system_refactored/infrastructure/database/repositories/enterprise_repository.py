"""
企业仓储类
重构自原有的 database/repositories/enterprise_repository.py，增强查询功能
"""
from typing import Optional, Dict, Any, List
import logging

from .base_repository import BaseRepository
from ..models.enterprise import Enterprise, create_enterprise_from_db_row

logger = logging.getLogger(__name__)


class EnterpriseRepository(BaseRepository):
    """企业数据访问仓储类"""
    
    def find_by_name(self, enterprise_name: str) -> Optional[Enterprise]:
        """
        根据企业名称查询企业信息
        
        Args:
            enterprise_name: 企业名称
            
        Returns:
            企业信息或None
        """
        query = """
        SELECT e.enterprise_id,
               e.enterprise_name,
               e.industry_id,
               e.area_id,
               e.enterprise_remark,
               i.industry_name,
               a.district_name,
               a.city_name
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        WHERE e.enterprise_name = %s
        """
        result = self._execute_single_query(query, (enterprise_name,))
        return create_enterprise_from_db_row(result) if result else None
    
    def find_by_id(self, enterprise_id: int) -> Optional[Enterprise]:
        """
        根据企业ID查询企业信息
        
        Args:
            enterprise_id: 企业ID
            
        Returns:
            企业信息或None
        """
        query = """
        SELECT e.enterprise_id,
               e.enterprise_name,
               e.industry_id,
               e.area_id,
               e.enterprise_remark,
               i.industry_name,
               a.district_name,
               a.city_name
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        WHERE e.enterprise_id = %s
        """
        result = self._execute_single_query(query, (enterprise_id,))
        return create_enterprise_from_db_row(result) if result else None
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Enterprise]:
        """
        查询所有企业信息（分页）
        
        Args:
            limit: 每页记录数
            offset: 偏移量
            
        Returns:
            企业信息列表
        """
        query = """
        SELECT e.enterprise_id,
               e.enterprise_name,
               e.industry_id,
               e.area_id,
               e.enterprise_remark,
               i.industry_name,
               a.district_name,
               a.city_name
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        ORDER BY e.enterprise_name
        LIMIT %s OFFSET %s
        """
        results = self._execute_query(query, (limit, offset))
        return [create_enterprise_from_db_row(result) for result in results]
    
    def find_by_industry(self, industry_id: int) -> List[Enterprise]:
        """
        根据行业ID查询企业列表
        
        Args:
            industry_id: 行业ID
            
        Returns:
            企业信息列表
        """
        query = """
        SELECT e.enterprise_id,
               e.enterprise_name,
               e.industry_id,
               e.area_id,
               e.enterprise_remark,
               i.industry_name,
               a.district_name,
               a.city_name
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        WHERE e.industry_id = %s
        ORDER BY e.enterprise_name
        """
        results = self._execute_query(query, (industry_id,))
        return [create_enterprise_from_db_row(result) for result in results]
    
    def find_by_area(self, area_id: int) -> List[Enterprise]:
        """
        根据地区ID查询企业列表
        
        Args:
            area_id: 地区ID
            
        Returns:
            企业信息列表
        """
        query = """
        SELECT e.enterprise_id,
               e.enterprise_name,
               e.industry_id,
               e.area_id,
               e.enterprise_remark,
               i.industry_name,
               a.district_name,
               a.city_name
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        WHERE e.area_id = %s
        ORDER BY e.enterprise_name
        """
        results = self._execute_query(query, (area_id,))
        return [create_enterprise_from_db_row(result) for result in results]
    
    def update(self, enterprise_id: int, updates: Dict[str, Any]) -> bool:
        """
        更新企业信息
        
        Args:
            enterprise_id: 企业ID
            updates: 更新字段字典
            
        Returns:
            是否更新成功
        """
        # 只处理QD_enterprise_chain_leader表中实际存在的字段
        allowed_fields = {
            'enterprise_name': 'enterprise_name',
            'industry_id': 'industry_id',
            'area_id': 'area_id',
            'enterprise_remark': 'enterprise_remark'
        }
        
        set_clauses = []
        values = []
        
        for field, value in updates.items():
            if field in allowed_fields:
                db_field = allowed_fields[field]
                set_clauses.append(f"{db_field} = %s")
                values.append(value)
        
        if not set_clauses:
            logger.debug("没有需要更新的字段")
            return True  # 没有需要更新的字段，返回成功
        
        values.append(enterprise_id)
        query = f"UPDATE QD_enterprise_chain_leader SET {', '.join(set_clauses)} WHERE enterprise_id = %s"
        
        logger.debug(f"更新企业 {enterprise_id}，字段: {list(updates.keys())}")
        return self._execute_update(query, tuple(values))
    
    def insert(self, enterprise_data: Dict[str, Any]) -> int:
        """
        插入新的企业信息
        
        Args:
            enterprise_data: 企业数据字典
            
        Returns:
            新插入记录的ID
        """
        query = """
        INSERT INTO QD_enterprise_chain_leader 
        (enterprise_name, industry_id, area_id, enterprise_remark)
        VALUES (%s, %s, %s, %s)
        """
        
        logger.debug(f"插入新企业: {enterprise_data.get('enterprise_name')}")
        return self._execute_insert(query, (
            enterprise_data['enterprise_name'],
            enterprise_data.get('industry_id'),
            enterprise_data.get('area_id'),
            enterprise_data.get('enterprise_remark')
        ))
    
    def count_all(self) -> int:
        """
        统计企业总数
        
        Returns:
            企业总数
        """
        return self._count_records("QD_enterprise_chain_leader")
    
    def count_by_industry(self, industry_id: int) -> int:
        """
        统计指定行业的企业数量
        
        Args:
            industry_id: 行业ID
            
        Returns:
            企业数量
        """
        return self._count_records("QD_enterprise_chain_leader", "industry_id = %s", (industry_id,))
    
    def count_by_area(self, area_id: int) -> int:
        """
        统计指定地区的企业数量
        
        Args:
            area_id: 地区ID
            
        Returns:
            企业数量
        """
        return self._count_records("QD_enterprise_chain_leader", "area_id = %s", (area_id,))