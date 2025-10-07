"""
增强版客户仓储类
基于原有CustomerRepository，增加更多查询功能和数据模型集成
"""
from typing import Optional, Dict, Any, List, Tuple
import logging
from datetime import datetime

from .base_repository import BaseRepository
from ..models.customer import Customer
from ..models.area import Area
from ..models.industry import Industry
from ..models.industry_brain import IndustryBrain

logger = logging.getLogger(__name__)


class EnhancedCustomerRepository(BaseRepository):
    """增强版客户数据访问仓储类"""
    
    def __init__(self, connection_manager=None):
        super().__init__(connection_manager)
        self.table_name = "QD_customer"
        self.chain_leader_table = "QD_enterprise_chain_leader"
    
    def find_by_name(self, customer_name: str) -> Optional[Customer]:
        """
        根据企业名称查询客户信息，支持精确匹配和模糊匹配
        同时搜索QD_customer表和QD_enterprise_chain_leader表
        
        Args:
            customer_name: 企业名称
            
        Returns:
            客户信息或None
        """
        try:
            logger.debug(f"开始查询客户: {customer_name}")
            
            # 首先在QD_customer表中尝试精确匹配
            result = self._find_in_customer_table_exact(customer_name)
            
            # 如果在customer表中没找到，搜索链主企业表
            if not result:
                result = self._find_in_chain_leader_table_exact(customer_name)
            
            # 如果精确匹配都没有结果，尝试模糊匹配
            if not result:
                result = self._find_with_fuzzy_matching(customer_name)
            
            if result:
                logger.debug(f"找到客户信息，来源: {result.get('source_table', 'unknown')}")
                return self._create_customer_from_result(result)
            else:
                logger.debug(f"未找到客户: {customer_name}")
                return None
        except Exception as e:
            logger.error(f"查询客户失败: {customer_name}, 错误: {e}")
            return None
    
    def find_by_id(self, customer_id: int) -> Optional[Customer]:
        """根据客户ID查询客户信息"""
        query = """
        SELECT c.customer_id,
               c.customer_name,
               c.data_source,
               c.address,
               c.tag_result,
               c.industry_id,
               c.brain_id,
               c.chain_leader_id,
               i.industry_name,
               i.industry_type,
               a.city_name,
               a.district_name,
               ib.brain_name,
               ib.build_year,
               el.enterprise_name as chain_leader_name
        FROM QD_customer c
        LEFT JOIN QD_industry i ON c.industry_id = i.industry_id
        LEFT JOIN QD_area a ON c.area_id = a.area_id
        LEFT JOIN QD_industry_brain ib ON c.brain_id = ib.brain_id
        LEFT JOIN QD_enterprise_chain_leader el ON c.chain_leader_id = el.enterprise_id
        WHERE c.customer_id = %s
        """
        result = self._execute_single_query(query, (customer_id,))
        return self._create_customer_from_result(result) if result else None
    
    def find_by_industry(self, industry_id: int, limit: int = 100) -> List[Customer]:
        """根据行业ID查询客户列表"""
        query = """
        SELECT c.customer_id,
               c.customer_name,
               c.data_source,
               c.address,
               c.tag_result,
               c.industry_id,
               c.brain_id,
               c.chain_leader_id,
               i.industry_name,
               i.industry_type
        FROM QD_customer c
        LEFT JOIN QD_industry i ON c.industry_id = i.industry_id
        WHERE c.industry_id = %s
        LIMIT %s
        """
        results = self._execute_query(query, (industry_id, limit))
        return [self._create_customer_from_result(row) for row in results]
    
    def find_by_area(self, area_id: int, limit: int = 100) -> List[Customer]:
        """根据地区ID查询客户列表"""
        query = """
        SELECT c.customer_id,
               c.customer_name,
               c.data_source,
               c.address,
               c.tag_result,
               c.industry_id,
               c.brain_id,
               c.chain_leader_id,
               a.city_name,
               a.district_name
        FROM QD_customer c
        LEFT JOIN QD_area a ON c.area_id = a.area_id
        WHERE c.area_id = %s
        LIMIT %s
        """
        results = self._execute_query(query, (area_id, limit))
        return [self._create_customer_from_result(row) for row in results]
    
    def search_by_keyword(self, keyword: str, limit: int = 50) -> List[Customer]:
        """根据关键词搜索客户"""
        query = """
        SELECT c.customer_id,
               c.customer_name,
               c.data_source,
               c.address,
               c.tag_result,
               c.industry_id,
               c.brain_id,
               c.chain_leader_id,
               i.industry_name,
               a.city_name,
               a.district_name
        FROM QD_customer c
        LEFT JOIN QD_industry i ON c.industry_id = i.industry_id
        LEFT JOIN QD_area a ON c.area_id = a.area_id
        WHERE c.customer_name LIKE %s 
           OR c.address LIKE %s
           OR i.industry_name LIKE %s
        LIMIT %s
        """
        keyword_pattern = f"%{keyword}%"
        results = self._execute_query(query, (keyword_pattern, keyword_pattern, keyword_pattern, limit))
        return [self._create_customer_from_result(row) for row in results]
    
    def create(self, customer: Customer) -> bool:
        """创建新客户"""
        query = """
        INSERT INTO QD_customer (
            customer_name, data_source, address, tag_result,
            industry_id, brain_id, chain_leader_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            customer.customer_name,
            customer.data_source,
            customer.address,
            customer.tag_result,
            customer.industry_id,
            customer.brain_id,
            customer.chain_leader_id
        )
        return self._execute_update(query, params)
    
    def update(self, customer: Customer) -> bool:
        """更新客户信息"""
        query = """
        UPDATE QD_customer SET
            customer_name = %s,
            data_source = %s,
            address = %s,
            tag_result = %s,
            industry_id = %s,
            brain_id = %s,
            chain_leader_id = %s
        WHERE customer_id = %s
        """
        params = (
            customer.customer_name,
            customer.data_source,
            customer.address,
            customer.tag_result,
            customer.industry_id,
            customer.brain_id,
            customer.chain_leader_id,
            customer.customer_id
        )
        return self._execute_update(query, params)
    
    def update_address(self, customer_id: int, new_address: str) -> bool:
        """更新客户地址"""
        query = "UPDATE QD_customer SET address = %s WHERE customer_id = %s"
        return self._execute_update(query, (new_address, customer_id))
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取客户统计信息"""
        stats = {}
        
        # 总客户数
        total_query = "SELECT COUNT(*) as total FROM QD_customer"
        total_result = self._execute_single_query(total_query)
        stats['total_customers'] = total_result['total'] if total_result else 0
        
        # 按行业分组统计
        industry_query = """
        SELECT i.industry_name, COUNT(c.customer_id) as count
        FROM QD_customer c
        LEFT JOIN QD_industry i ON c.industry_id = i.industry_id
        GROUP BY i.industry_id, i.industry_name
        ORDER BY count DESC
        """
        industry_results = self._execute_query(industry_query)
        stats['by_industry'] = {row['industry_name'] or '未分类': row['count'] for row in industry_results}
        
        # 按地区分组统计
        area_query = """
        SELECT a.city_name, a.district_name, COUNT(c.customer_id) as count
        FROM QD_customer c
        LEFT JOIN QD_area a ON c.area_id = a.area_id
        GROUP BY a.area_id, a.city_name, a.district_name
        ORDER BY count DESC
        """
        area_results = self._execute_query(area_query)
        stats['by_area'] = {f"{row['city_name']}-{row['district_name']}" if row['city_name'] else '未分类': row['count'] for row in area_results}
        
        return stats
    
    def _find_in_customer_table_exact(self, customer_name: str) -> Optional[Dict[str, Any]]:
        """在客户表中精确查找"""
        query = """
        SELECT c.customer_id,
               c.customer_name,
               c.data_source,
               c.address,
               c.tag_result,
               c.industry_id,
               c.brain_id,
               c.chain_leader_id,
               i.industry_name,
               i.industry_type,
               a.city_name,
               a.district_name,
               ib.brain_name,
               el.enterprise_name as chain_leader_name,
               'QD_customer' as source_table
        FROM QD_customer c
        LEFT JOIN QD_industry i ON c.industry_id = i.industry_id
        LEFT JOIN QD_area a ON c.area_id = a.area_id
        LEFT JOIN QD_industry_brain ib ON c.brain_id = ib.brain_id
        LEFT JOIN QD_enterprise_chain_leader el ON c.chain_leader_id = el.enterprise_id
        WHERE c.customer_name = %s
        """
        return self._execute_single_query(query, (customer_name,))
    
    def _find_in_chain_leader_table_exact(self, customer_name: str) -> Optional[Dict[str, Any]]:
        """在链主企业表中精确查找"""
        query = """
        SELECT el.enterprise_id as customer_id,
               el.enterprise_name as customer_name,
               'chain_leader' as data_source,
               NULL as address,
               1 as tag_result,
               el.industry_id,
               NULL as brain_id,
               el.enterprise_id as chain_leader_id,
               i.industry_name,
               i.industry_type,
               a.city_name,
               a.district_name,
               NULL as brain_name,
               el.enterprise_name as chain_leader_name,
               'QD_enterprise_chain_leader' as source_table
        FROM QD_enterprise_chain_leader el
        LEFT JOIN QD_industry i ON el.industry_id = i.industry_id
        LEFT JOIN QD_area a ON el.area_id = a.area_id
        WHERE el.enterprise_name = %s
        """
        return self._execute_single_query(query, (customer_name,))
    
    def _find_with_fuzzy_matching(self, customer_name: str) -> Optional[Dict[str, Any]]:
        """模糊匹配查找"""
        # 先尝试客户表的模糊匹配
        query = """
        SELECT c.customer_id,
               c.customer_name,
               c.data_source,
               c.address,
               c.tag_result,
               c.industry_id,
               c.brain_id,
               c.chain_leader_id,
               i.industry_name,
               a.city_name,
               a.district_name,
               'QD_customer' as source_table
        FROM QD_customer c
        LEFT JOIN QD_industry i ON c.industry_id = i.industry_id
        LEFT JOIN QD_area a ON c.area_id = a.area_id
        WHERE c.customer_name LIKE %s
        LIMIT 1
        """
        result = self._execute_single_query(query, (f"%{customer_name}%",))
        
        if not result:
            # 再尝试链主企业表的模糊匹配
            query = """
            SELECT el.enterprise_id as customer_id,
                   el.enterprise_name as customer_name,
                   'chain_leader' as data_source,
                   NULL as address,
                   1 as tag_result,
                   el.industry_id,
                   NULL as brain_id,
                   el.enterprise_id as chain_leader_id,
                   i.industry_name,
                   a.city_name,
                   a.district_name,
                   'QD_enterprise_chain_leader' as source_table
            FROM QD_enterprise_chain_leader el
            LEFT JOIN QD_industry i ON el.industry_id = i.industry_id
            LEFT JOIN QD_area a ON el.area_id = a.area_id
            WHERE el.enterprise_name LIKE %s
            LIMIT 1
            """
            result = self._execute_single_query(query, (f"%{customer_name}%",))
        
        return result
    
    def _create_customer_from_result(self, result: Dict[str, Any]) -> Customer:
        """从查询结果创建Customer对象"""
        if not result:
            return None
        
        return Customer(
            customer_id=result.get('customer_id'),
            customer_name=result.get('customer_name'),
            data_source=result.get('data_source'),
            address=result.get('address'),
            tag_result=result.get('tag_result', 0),
            industry_id=result.get('industry_id'),
            brain_id=result.get('brain_id'),
            chain_leader_id=result.get('chain_leader_id'),
            # 关联信息
            industry_name=result.get('industry_name'),
            industry_type=result.get('industry_type'),
            city_name=result.get('city_name'),
            district_name=result.get('district_name'),
            brain_name=result.get('brain_name'),
            chain_leader_name=result.get('chain_leader_name'),
            source_table=result.get('source_table', 'QD_customer')
        )
