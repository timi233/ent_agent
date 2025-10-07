"""
重构后的数据库查询接口
使用仓储模式提供数据访问功能，保持向后兼容性
"""
from typing import Optional, Dict, Any
from .repositories.customer_repository import CustomerRepository
from .repositories.enterprise_repository import EnterpriseRepository


def get_customer_by_name(customer_name: str) -> Optional[Dict[str, Any]]:
    """
    根据企业名称查询客户信息，支持精确匹配和模糊匹配
    同时搜索QD_customer表和QD_enterprise_chain_leader表
    
    保持与原有接口的兼容性
    """
    with CustomerRepository() as repo:
        customer = repo.find_by_name(customer_name)
        return customer.to_dict() if customer else None


def get_customer_by_id(customer_id: int) -> Optional[Dict[str, Any]]:
    """
    根据客户ID查询客户信息
    
    保持与原有接口的兼容性
    """
    with CustomerRepository() as repo:
        customer = repo.find_by_id(customer_id)
        return customer.to_dict() if customer else None


def update_customer_info(customer_id: int, updates: Dict[str, Any]) -> bool:
    """
    更新客户信息
    
    保持与原有接口的兼容性
    """
    with CustomerRepository() as repo:
        success = repo.update(customer_id, updates)
        if success:
            print(f"更新客户信息成功: customer_id={customer_id}, 更新字段={list(updates.keys())}")
        else:
            print(f"更新客户信息失败: customer_id={customer_id}")
        return success


def insert_customer(customer_data: Dict[str, Any]) -> int:
    """
    插入新的客户信息
    
    保持与原有接口的兼容性
    """
    with CustomerRepository() as repo:
        return repo.insert(customer_data)


def get_enterprise_by_name(enterprise_name: str) -> Optional[Dict[str, Any]]:
    """
    根据企业名称查询企业信息
    """
    with EnterpriseRepository() as repo:
        enterprise = repo.find_by_name(enterprise_name)
        return enterprise.to_dict() if enterprise else None


def get_enterprise_by_id(enterprise_id: int) -> Optional[Dict[str, Any]]:
    """
    根据企业ID查询企业信息
    """
    with EnterpriseRepository() as repo:
        enterprise = repo.find_by_id(enterprise_id)
        return enterprise.to_dict() if enterprise else None