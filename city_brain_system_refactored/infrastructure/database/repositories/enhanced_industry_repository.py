"""
增强版行业仓储类
基于原有IndustryRepository，增加更多查询功能和数据模型集成
"""
from typing import Optional, Dict, Any, List
import logging

from .base_repository import BaseRepository
from ..models.industry import Industry

logger = logging.getLogger(__name__)


class EnhancedIndustryRepository(BaseRepository):
    """增强版行业数据访问仓储类"""
    
    def __init__(self, connection_manager=None):
        super().__init__(connection_manager)
        self.table_name = "QD_industry"
    
    def find_by_id(self, industry_id: int) -> Optional[Industry]:
        """根据行业ID查询行业信息"""
        query = """
        SELECT industry_id, industry_name, industry_type, industry_remark
        FROM QD_industry
        WHERE industry_id = %s
        """
        result = self._execute_single_query(query, (industry_id,))
        return self._create_industry_from_result(result) if result else None
    
    def find_by_name(self, industry_name: str) -> Optional[Industry]:
        """根据行业名称查询行业信息"""
        query = """
        SELECT industry_id, industry_name, industry_type, industry_remark
        FROM QD_industry
        WHERE industry_name = %s
        """
        result = self._execute_single_query(query, (industry_name,))
        return self._create_industry_from_result(result) if result else None
    
    def find_by_type(self, industry_type: str) -> List[Industry]:
        """根据行业类型查询行业列表"""
        query = """
        SELECT industry_id, industry_name, industry_type, industry_remark
        FROM QD_industry
        WHERE industry_type = %s
        ORDER BY industry_name
        """
        results = self._execute_query(query, (industry_type,))
        return [self._create_industry_from_result(row) for row in results]
    
    def search_by_keyword(self, keyword: str) -> List[Industry]:
        """根据关键词搜索行业"""
        query = """
        SELECT industry_id, industry_name, industry_type, industry_remark
        FROM QD_industry
        WHERE industry_name LIKE %s 
           OR industry_type LIKE %s
           OR industry_remark LIKE %s
        ORDER BY industry_name
        """
        keyword_pattern = f"%{keyword}%"
        results = self._execute_query(query, (keyword_pattern, keyword_pattern, keyword_pattern))
        return [self._create_industry_from_result(row) for row in results]
    
    def get_all_types(self) -> List[str]:
        """获取所有行业类型"""
        query = "SELECT DISTINCT industry_type FROM QD_industry WHERE industry_type IS NOT NULL ORDER BY industry_type"
        results = self._execute_query(query)
        return [row['industry_type'] for row in results if row['industry_type']]
    
    def get_all(self) -> List[Industry]:
        """获取所有行业"""
        query = """
        SELECT industry_id, industry_name, industry_type, industry_remark
        FROM QD_industry
        ORDER BY industry_name
        """
        results = self._execute_query(query)
        return [self._create_industry_from_result(row) for row in results]
    
    def create(self, industry: Industry) -> bool:
        """创建新行业"""
        query = """
        INSERT INTO QD_industry (industry_name, industry_type, industry_remark)
        VALUES (%s, %s, %s)
        """
        params = (industry.industry_name, industry.industry_type, industry.industry_remark)
        return self._execute_update(query, params)
    
    def update(self, industry: Industry) -> bool:
        """更新行业信息"""
        query = """
        UPDATE QD_industry SET
            industry_name = %s,
            industry_type = %s,
            industry_remark = %s
        WHERE industry_id = %s
        """
        params = (industry.industry_name, industry.industry_type, industry.industry_remark, industry.industry_id)
        return self._execute_update(query, params)
    
    def get_related_customers_count(self, industry_id: int) -> int:
        """获取该行业关联的客户数量"""
        query = "SELECT COUNT(*) as count FROM QD_customer WHERE industry_id = %s"
        result = self._execute_single_query(query, (industry_id,))
        return result['count'] if result else 0
    
    def get_related_enterprises_count(self, industry_id: int) -> int:
        """获取该行业关联的企业数量"""
        query = "SELECT COUNT(*) as count FROM QD_enterprise_chain_leader WHERE industry_id = %s"
        result = self._execute_single_query(query, (industry_id,))
        return result['count'] if result else 0
    
    def get_related_brains(self, industry_id: int) -> List[Dict[str, Any]]:
        """获取该行业关联的产业大脑"""
        query = """
        SELECT ib.brain_id, ib.brain_name, ib.build_year, ib.brain_remark
        FROM QD_brain_industry_rel bir
        JOIN QD_industry_brain ib ON bir.brain_id = ib.brain_id
        WHERE bir.industry_id = %s
        """
        try:
            return self._execute_query(query, (industry_id,))
        except Exception as e:
            logger.error(f"获取行业关联产业大脑失败: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取行业统计信息"""
        stats = {}
        
        # 总行业数
        total_query = "SELECT COUNT(*) as total FROM QD_industry"
        total_result = self._execute_single_query(total_query)
        stats['total_industries'] = total_result['total'] if total_result else 0
        
        # 按类型分组统计
        type_query = """
        SELECT industry_type, COUNT(*) as count
        FROM QD_industry
        WHERE industry_type IS NOT NULL
        GROUP BY industry_type
        ORDER BY count DESC
        """
        type_results = self._execute_query(type_query)
        stats['by_type'] = {row['industry_type']: row['count'] for row in type_results}
        
        # 每个行业的客户数量统计
        customer_query = """
        SELECT i.industry_name, COUNT(c.customer_id) as customer_count
        FROM QD_industry i
        LEFT JOIN QD_customer c ON i.industry_id = c.industry_id
        GROUP BY i.industry_id, i.industry_name
        ORDER BY customer_count DESC
        LIMIT 10
        """
        customer_results = self._execute_query(customer_query)
        stats['top_industries_by_customers'] = {row['industry_name']: row['customer_count'] for row in customer_results}
        
        # 每个行业的企业数量统计
        enterprise_query = """
        SELECT i.industry_name, COUNT(e.enterprise_id) as enterprise_count
        FROM QD_industry i
        LEFT JOIN QD_enterprise_chain_leader e ON i.industry_id = e.industry_id
        GROUP BY i.industry_id, i.industry_name
        ORDER BY enterprise_count DESC
        LIMIT 10
        """
        enterprise_results = self._execute_query(enterprise_query)
        stats['top_industries_by_enterprises'] = {row['industry_name']: row['enterprise_count'] for row in enterprise_results}
        
        return stats
    
    def _create_industry_from_result(self, result: Dict[str, Any]) -> Industry:
        """从查询结果创建Industry对象"""
        if not result:
            return None
        
        return Industry(
            industry_id=result.get('industry_id'),
            industry_name=result.get('industry_name'),
            industry_type=result.get('industry_type'),
            industry_remark=result.get('industry_remark')
        )