"""
增强版企业仓储类
基于原有EnterpriseRepository，增加更多查询功能和数据模型集成
"""
from typing import Optional, Dict, Any, List
import logging

from .base_repository import BaseRepository
from ..models.enterprise import Enterprise
from ..models.industry_brain import IndustryBrain

logger = logging.getLogger(__name__)


class EnhancedEnterpriseRepository(BaseRepository):
    """增强版企业数据访问仓储类"""
    
    def __init__(self, connection_manager=None):
        super().__init__(connection_manager)
        self.table_name = "QD_enterprise_chain_leader"
    
    def find_by_name(self, enterprise_name: str) -> Optional[Enterprise]:
        """根据企业名称查询企业信息"""
        try:
            query = """
            SELECT e.enterprise_id,
                   e.enterprise_name,
                   e.industry_id,
                   e.area_id,
                   e.enterprise_remark,
                   i.industry_name,
                   i.industry_type,
                   a.district_name,
                   a.city_name
            FROM QD_enterprise_chain_leader e
            LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
            LEFT JOIN QD_area a ON e.area_id = a.area_id
            WHERE e.enterprise_name = %s
            """
            result = self._execute_single_query(query, (enterprise_name,))
            return self._create_enterprise_from_result(result) if result else None
        except Exception as e:
            logger.error(f"查询企业失败: {enterprise_name}, 错误: {e}")
            return None
    
    def find_by_id(self, enterprise_id: int) -> Optional[Enterprise]:
        """根据企业ID查询企业信息"""
        query = """
        SELECT e.enterprise_id,
               e.enterprise_name,
               e.industry_id,
               e.area_id,
               e.enterprise_remark,
               i.industry_name,
               i.industry_type,
               a.district_name,
               a.city_name
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        WHERE e.enterprise_id = %s
        """
        result = self._execute_single_query(query, (enterprise_id,))
        return self._create_enterprise_from_result(result) if result else None
    
    def find_by_industry(self, industry_id: int, limit: int = 100) -> List[Enterprise]:
        """根据行业ID查询企业列表"""
        query = """
        SELECT e.enterprise_id,
               e.enterprise_name,
               e.industry_id,
               e.area_id,
               e.enterprise_remark,
               i.industry_name,
               i.industry_type,
               a.district_name,
               a.city_name
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        WHERE e.industry_id = %s
        LIMIT %s
        """
        results = self._execute_query(query, (industry_id, limit))
        return [self._create_enterprise_from_result(row) for row in results]
    
    def find_by_area(self, area_id: int, limit: int = 100) -> List[Enterprise]:
        """根据地区ID查询企业列表"""
        query = """
        SELECT e.enterprise_id,
               e.enterprise_name,
               e.industry_id,
               e.area_id,
               e.enterprise_remark,
               i.industry_name,
               i.industry_type,
               a.district_name,
               a.city_name
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        WHERE e.area_id = %s
        LIMIT %s
        """
        results = self._execute_query(query, (area_id, limit))
        return [self._create_enterprise_from_result(row) for row in results]
    
    def search_by_keyword(self, keyword: str, limit: int = 50) -> List[Enterprise]:
        """根据关键词搜索企业"""
        query = """
        SELECT e.enterprise_id,
               e.enterprise_name,
               e.industry_id,
               e.area_id,
               e.enterprise_remark,
               i.industry_name,
               i.industry_type,
               a.district_name,
               a.city_name
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        WHERE e.enterprise_name LIKE %s 
           OR e.enterprise_remark LIKE %s
           OR i.industry_name LIKE %s
        LIMIT %s
        """
        keyword_pattern = f"%{keyword}%"
        results = self._execute_query(query, (keyword_pattern, keyword_pattern, keyword_pattern, limit))
        return [self._create_enterprise_from_result(row) for row in results]
    
    def create(self, enterprise: Enterprise) -> bool:
        """创建新企业"""
        query = """
        INSERT INTO QD_enterprise_chain_leader (
            enterprise_name, industry_id, area_id, enterprise_remark
        ) VALUES (%s, %s, %s, %s)
        """
        params = (
            enterprise.enterprise_name,
            enterprise.industry_id,
            enterprise.area_id,
            enterprise.enterprise_remark
        )
        return self._execute_update(query, params)
    
    def update(self, enterprise: Enterprise) -> bool:
        """更新企业信息"""
        query = """
        UPDATE QD_enterprise_chain_leader SET
            enterprise_name = %s,
            industry_id = %s,
            area_id = %s,
            enterprise_remark = %s
        WHERE enterprise_id = %s
        """
        params = (
            enterprise.enterprise_name,
            enterprise.industry_id,
            enterprise.area_id,
            enterprise.enterprise_remark,
            enterprise.enterprise_id
        )
        return self._execute_update(query, params)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取企业统计信息"""
        stats = {}
        
        # 总企业数
        total_query = "SELECT COUNT(*) as total FROM QD_enterprise_chain_leader"
        total_result = self._execute_single_query(total_query)
        stats['total_enterprises'] = total_result['total'] if total_result else 0
        
        # 按行业分组统计
        industry_query = """
        SELECT i.industry_name, COUNT(e.enterprise_id) as count
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        GROUP BY i.industry_id, i.industry_name
        ORDER BY count DESC
        """
        industry_results = self._execute_query(industry_query)
        stats['by_industry'] = {row['industry_name'] or '未分类': row['count'] for row in industry_results}
        
        # 按地区分组统计
        area_query = """
        SELECT a.city_name, a.district_name, COUNT(e.enterprise_id) as count
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        GROUP BY a.area_id, a.city_name, a.district_name
        ORDER BY count DESC
        """
        area_results = self._execute_query(area_query)
        stats['by_area'] = {f"{row['city_name']}-{row['district_name']}" if row['city_name'] else '未分类': row['count'] for row in area_results}
        
        return stats
    
    def _create_enterprise_from_result(self, result: Dict[str, Any]) -> Enterprise:
        """从查询结果创建Enterprise对象"""
        if not result:
            return None
        
        return Enterprise(
            enterprise_id=result.get('enterprise_id'),
            enterprise_name=result.get('enterprise_name'),
            industry_id=result.get('industry_id'),
            area_id=result.get('area_id'),
            enterprise_remark=result.get('enterprise_remark'),
            # 关联信息
            industry_name=result.get('industry_name'),
            industry_type=result.get('industry_type'),
            city_name=result.get('city_name'),
            district_name=result.get('district_name')
        )


class IndustryBrainRepository(BaseRepository):
    """产业大脑仓储类"""
    
    def __init__(self, connection_manager=None):
        super().__init__(connection_manager)
        self.table_name = "QD_industry_brain"
    
    def find_by_id(self, brain_id: int) -> Optional[IndustryBrain]:
        """根据产业大脑ID查询信息"""
        query = """
        SELECT ib.brain_id,
               ib.brain_name,
               ib.area_id,
               ib.build_year,
               ib.brain_remark,
               a.city_name,
               a.district_name
        FROM QD_industry_brain ib
        LEFT JOIN QD_area a ON ib.area_id = a.area_id
        WHERE ib.brain_id = %s
        """
        result = self._execute_single_query(query, (brain_id,))
        return self._create_industry_brain_from_result(result) if result else None
    
    def find_by_name(self, brain_name: str) -> Optional[IndustryBrain]:
        """根据产业大脑名称查询信息"""
        query = """
        SELECT ib.brain_id,
               ib.brain_name,
               ib.area_id,
               ib.build_year,
               ib.brain_remark,
               a.city_name,
               a.district_name
        FROM QD_industry_brain ib
        LEFT JOIN QD_area a ON ib.area_id = a.area_id
        WHERE ib.brain_name = %s
        """
        result = self._execute_single_query(query, (brain_name,))
        return self._create_industry_brain_from_result(result) if result else None
    
    def find_by_area(self, area_id: int) -> List[IndustryBrain]:
        """根据地区ID查询产业大脑列表"""
        query = """
        SELECT ib.brain_id,
               ib.brain_name,
               ib.area_id,
               ib.build_year,
               ib.brain_remark,
               a.city_name,
               a.district_name
        FROM QD_industry_brain ib
        LEFT JOIN QD_area a ON ib.area_id = a.area_id
        WHERE ib.area_id = %s
        """
        results = self._execute_query(query, (area_id,))
        return [self._create_industry_brain_from_result(row) for row in results]
    
    def find_related_industries(self, brain_id: int) -> List[Dict[str, Any]]:
        """查询产业大脑关联的行业"""
        query = """
        SELECT i.industry_id,
               i.industry_name,
               i.industry_type,
               i.industry_remark
        FROM QD_brain_industry_rel bir
        JOIN QD_industry i ON bir.industry_id = i.industry_id
        WHERE bir.brain_id = %s
        """
        return self._execute_query(query, (brain_id,))
    
    def get_all(self) -> List[IndustryBrain]:
        """获取所有产业大脑"""
        query = """
        SELECT ib.brain_id,
               ib.brain_name,
               ib.area_id,
               ib.build_year,
               ib.brain_remark,
               a.city_name,
               a.district_name
        FROM QD_industry_brain ib
        LEFT JOIN QD_area a ON ib.area_id = a.area_id
        ORDER BY ib.brain_name
        """
        results = self._execute_query(query)
        return [self._create_industry_brain_from_result(row) for row in results]
    
    def _create_industry_brain_from_result(self, result: Dict[str, Any]) -> IndustryBrain:
        """从查询结果创建IndustryBrain对象"""
        if not result:
            return None
        
        return IndustryBrain(
            brain_id=result.get('brain_id'),
            brain_name=result.get('brain_name'),
            area_id=result.get('area_id'),
            build_year=result.get('build_year'),
            brain_remark=result.get('brain_remark'),
            # 关联信息
            city_name=result.get('city_name'),
            district_name=result.get('district_name')
        )
