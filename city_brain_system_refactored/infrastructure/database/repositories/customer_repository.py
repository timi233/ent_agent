"""
客户仓储类
重构自原有的 database/repositories/customer_repository.py，增强查询逻辑和错误处理
实现ICustomerRepository接口（依赖倒置原则）
"""
from typing import Optional, Dict, Any, List
import logging
import sys
import os

# 添加domain路径以便导入接口
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from domain.repositories.customer_repository_interface import ICustomerRepository
from .base_repository import BaseRepository
from ..models.customer import Customer, create_customer_from_db_row

logger = logging.getLogger(__name__)


class CustomerRepository(BaseRepository, ICustomerRepository):
    """客户数据访问仓储类"""
    
    def find_by_name(self, customer_name: str) -> Optional[Customer]:
        """
        根据企业名称查询客户信息，支持精确匹配和模糊匹配
        同时搜索QD_customer表和QD_enterprise_chain_leader表
        
        Args:
            customer_name: 企业名称
            
        Returns:
            客户信息或None
        """
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
            return create_customer_from_db_row(result)
        else:
            logger.debug(f"未找到客户: {customer_name}")
            return None
    
    def _find_in_customer_table_exact(self, customer_name: str) -> Optional[Dict[str, Any]]:
        """在客户表中精确查找"""
        query = """
        SELECT c.*, 
               i.industry_name,
               b.brain_name,
               e.enterprise_name as chain_leader_name,
               a.district_name,
               'customer' as source_table
        FROM QD_customer c
        LEFT JOIN QD_industry i ON c.industry_id = i.industry_id
        LEFT JOIN QD_industry_brain b ON c.brain_id = b.brain_id
        LEFT JOIN QD_enterprise_chain_leader e ON c.chain_leader_id = e.enterprise_id
        LEFT JOIN QD_area a ON b.area_id = a.area_id
        WHERE c.customer_name = %s
        """
        return self._execute_single_query(query, (customer_name,))
    
    def _find_in_chain_leader_table_exact(self, customer_name: str) -> Optional[Dict[str, Any]]:
        """在链主企业表中精确查找"""
        query = """
        SELECT e.enterprise_id as customer_id,
               e.enterprise_name as customer_name,
               NULL as data_source,
               NULL as address,
               1 as tag_result,
               e.industry_id,
               NULL as brain_id,
               e.enterprise_id as chain_leader_id,
               i.industry_name,
               NULL as brain_name,
               e.enterprise_name as chain_leader_name,
               a.district_name,
               'chain_leader' as source_table
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        WHERE e.enterprise_name = %s
        """
        return self._execute_single_query(query, (customer_name,))
    
    def _find_with_fuzzy_matching(self, customer_name: str) -> Optional[Dict[str, Any]]:
        """使用模糊匹配查找"""
        # 移除常见的企业后缀进行模糊匹配
        base_name = self._remove_company_suffixes(customer_name)
        
        # 先在customer表中模糊匹配
        result = self._find_in_customer_table_fuzzy(customer_name, base_name)
        
        # 如果customer表中模糊匹配也没找到，在链主企业表中模糊匹配
        if not result:
            result = self._find_in_chain_leader_table_fuzzy(customer_name, base_name)
        
        return result
    
    def _find_in_customer_table_fuzzy(self, customer_name: str, base_name: str) -> Optional[Dict[str, Any]]:
        """在客户表中模糊查找"""
        query = """
        SELECT c.*, 
               i.industry_name,
               b.brain_name,
               e.enterprise_name as chain_leader_name,
               a.district_name,
               'customer' as source_table
        FROM QD_customer c
        LEFT JOIN QD_industry i ON c.industry_id = i.industry_id
        LEFT JOIN QD_industry_brain b ON c.brain_id = b.brain_id
        LEFT JOIN QD_enterprise_chain_leader e ON c.chain_leader_id = e.enterprise_id
        LEFT JOIN QD_area a ON b.area_id = a.area_id
        WHERE c.customer_name LIKE %s
        ORDER BY 
            CASE 
                WHEN c.customer_name = %s THEN 1
                WHEN c.customer_name LIKE %s THEN 2
                ELSE 3
            END
        LIMIT 1
        """
        like_pattern = f"%{base_name}%"
        starts_with_pattern = f"{base_name}%"
        return self._execute_single_query(query, (like_pattern, customer_name, starts_with_pattern))
    
    def _find_in_chain_leader_table_fuzzy(self, customer_name: str, base_name: str) -> Optional[Dict[str, Any]]:
        """在链主企业表中模糊查找"""
        query = """
        SELECT e.enterprise_id as customer_id,
               e.enterprise_name as customer_name,
               NULL as data_source,
               NULL as address,
               1 as tag_result,
               e.industry_id,
               NULL as brain_id,
               e.enterprise_id as chain_leader_id,
               i.industry_name,
               NULL as brain_name,
               e.enterprise_name as chain_leader_name,
               a.district_name,
               'chain_leader' as source_table
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        WHERE e.enterprise_name LIKE %s
        ORDER BY 
            CASE 
                WHEN e.enterprise_name = %s THEN 1
                WHEN e.enterprise_name LIKE %s THEN 2
                ELSE 3
            END
        LIMIT 1
        """
        like_pattern = f"%{base_name}%"
        starts_with_pattern = f"{base_name}%"
        return self._execute_single_query(query, (like_pattern, customer_name, starts_with_pattern))
    
    def _remove_company_suffixes(self, company_name: str) -> str:
        """移除常见的企业后缀"""
        suffixes_to_remove = [
            '股份有限公司', '有限公司', '集团有限公司', '控股有限公司', 
            '股份公司', '集团', '公司', '企业', '厂', '店'
        ]
        
        for suffix in suffixes_to_remove:
            if company_name.endswith(suffix):
                return company_name[:-len(suffix)]
        
        return company_name
    
    def find_by_id(self, customer_id: int) -> Optional[Customer]:
        """
        根据客户ID查询客户信息
        
        Args:
            customer_id: 客户ID
            
        Returns:
            客户信息或None
        """
        query = """
        SELECT c.*, 
               i.industry_name,
               b.brain_name,
               e.enterprise_name as chain_leader_name,
               a.district_name,
               'customer' as source_table
        FROM QD_customer c
        LEFT JOIN QD_industry i ON c.industry_id = i.industry_id
        LEFT JOIN QD_industry_brain b ON c.brain_id = b.brain_id
        LEFT JOIN QD_enterprise_chain_leader e ON c.chain_leader_id = e.enterprise_id
        LEFT JOIN QD_area a ON b.area_id = a.area_id
        WHERE c.customer_id = %s
        """
        result = self._execute_single_query(query, (customer_id,))
        return create_customer_from_db_row(result) if result else None
    
    def update(self, customer_id: int, updates: Dict[str, Any]) -> bool:
        """
        更新客户信息
        
        Args:
            customer_id: 客户ID
            updates: 更新字段字典
            
        Returns:
            是否更新成功
        """
        # 只处理QD_customer表中实际存在的字段
        allowed_fields = {
            'address': 'address',
            'customer_name': 'customer_name',
            'data_source': 'data_source',
            'tag_result': 'tag_result',
            'industry_id': 'industry_id',
            'brain_id': 'brain_id',
            'chain_leader_id': 'chain_leader_id'
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
        
        values.append(customer_id)
        query = f"UPDATE QD_customer SET {', '.join(set_clauses)} WHERE customer_id = %s"
        
        logger.debug(f"更新客户 {customer_id}，字段: {list(updates.keys())}")
        return self._execute_update(query, tuple(values))
    
    def insert(self, customer_data: Dict[str, Any]) -> int:
        """
        插入新的客户信息
        
        Args:
            customer_data: 客户数据字典
            
        Returns:
            新插入记录的ID
        """
        query = """
        INSERT INTO QD_customer 
        (customer_name, data_source, address, tag_result, industry_id, brain_id, chain_leader_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        logger.debug(f"插入新客户: {customer_data.get('customer_name')}")
        return self._execute_insert(query, (
            customer_data['customer_name'],
            customer_data.get('data_source'),
            customer_data.get('address'),
            customer_data.get('tag_result', 1),
            customer_data.get('industry_id'),
            customer_data.get('brain_id'),
            customer_data.get('chain_leader_id')
        ))
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Customer]:
        """
        查询所有客户信息（分页）
        
        Args:
            limit: 每页记录数
            offset: 偏移量
            
        Returns:
            客户信息列表
        """
        query = """
        SELECT c.*, 
               i.industry_name,
               b.brain_name,
               e.enterprise_name as chain_leader_name,
               a.district_name,
               'customer' as source_table
        FROM QD_customer c
        LEFT JOIN QD_industry i ON c.industry_id = i.industry_id
        LEFT JOIN QD_industry_brain b ON c.brain_id = b.brain_id
        LEFT JOIN QD_enterprise_chain_leader e ON c.chain_leader_id = e.enterprise_id
        LEFT JOIN QD_area a ON b.area_id = a.area_id
        ORDER BY c.customer_name
        LIMIT %s OFFSET %s
        """
        results = self._execute_query(query, (limit, offset))
        return [create_customer_from_db_row(result) for result in results]
    
    def count_all(self) -> int:
        """
        统计客户总数
        
        Returns:
            客户总数
        """
        return self._count_records("QD_customer")