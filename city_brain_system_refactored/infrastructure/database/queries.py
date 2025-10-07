"""
向后兼容的数据库查询接口
使用新的增强版仓储层，保持原有接口不变
"""
from typing import Optional, Dict, Any, List
import logging
import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from infrastructure.database.repositories.fully_standalone_repository import (
        StandaloneCustomerRepository,
        StandaloneEnterpriseRepository,
        StandaloneIndustryRepository,
        StandaloneAreaRepository,
        StandaloneBrainRepository
    )
except ImportError:
    # 如果导入失败，创建模拟的仓储类
    class MockRepository:
        def find_by_name(self, name): return None
        def find_by_id(self, id): return None
        def update(self, obj): return False
        def create(self, obj): return False
        def update_address(self, id, address): return False
        def search_by_keyword(self, keyword, limit=50): return []
        def get_statistics(self): return {}
        def get_all(self): return []
        def get_all_cities(self): return []
        def find_related_industries(self, id): return []
        def get_related_customers_count(self, id): return 0
        def get_related_enterprises_count(self, id): return 0
        def get_related_brains(self, id): return []
    
    StandaloneCustomerRepository = MockRepository
    StandaloneEnterpriseRepository = MockRepository
    StandaloneIndustryRepository = MockRepository
    StandaloneAreaRepository = MockRepository
    StandaloneBrainRepository = MockRepository

logger = logging.getLogger(__name__)

# 全局仓储实例（单例模式）
_customer_repo = None
_enterprise_repo = None
_industry_repo = None
_area_repo = None
_brain_repo = None

def _get_customer_repo():
    """获取客户仓储实例"""
    global _customer_repo
    if _customer_repo is None:
        _customer_repo = StandaloneCustomerRepository()
    return _customer_repo

def _get_enterprise_repo():
    """获取企业仓储实例"""
    global _enterprise_repo
    if _enterprise_repo is None:
        _enterprise_repo = StandaloneEnterpriseRepository()
    return _enterprise_repo

def _get_industry_repo():
    """获取行业仓储实例"""
    global _industry_repo
    if _industry_repo is None:
        _industry_repo = StandaloneIndustryRepository()
    return _industry_repo

def _get_area_repo():
    """获取地区仓储实例"""
    global _area_repo
    if _area_repo is None:
        _area_repo = StandaloneAreaRepository()
    return _area_repo

def _get_brain_repo():
    """获取产业大脑仓储实例"""
    global _brain_repo
    if _brain_repo is None:
        _brain_repo = StandaloneBrainRepository()
    return _brain_repo

# ==================== 客户相关查询接口 ====================

def get_customer_by_name(customer_name: str) -> Optional[Dict[str, Any]]:
    """
    根据企业名称查询客户信息，支持精确匹配和模糊匹配
    同时搜索QD_customer表和QD_enterprise_chain_leader表
    
    保持与原有接口的兼容性
    
    Args:
        customer_name: 企业名称
        
    Returns:
        客户信息字典或None
    """
    try:
        repo = _get_customer_repo()
        customer = repo.find_by_name(customer_name)
        return customer.to_dict() if customer else None
    except Exception as e:
        logger.error(f"查询客户失败: {customer_name}, 错误: {e}")
        return None

def get_customer_by_id(customer_id: int) -> Optional[Dict[str, Any]]:
    """
    根据客户ID查询客户信息
    
    保持与原有接口的兼容性
    
    Args:
        customer_id: 客户ID
        
    Returns:
        客户信息字典或None
    """
    try:
        repo = _get_customer_repo()
        customer = repo.find_by_id(customer_id)
        return customer.to_dict() if customer else None
    except Exception as e:
        logger.error(f"查询客户失败: {customer_id}, 错误: {e}")
        return None

def update_customer_info(customer_id: int, updates: Dict[str, Any]) -> bool:
    """
    更新客户信息
    
    保持与原有接口的兼容性
    
    Args:
        customer_id: 客户ID
        updates: 更新的字段字典
        
    Returns:
        更新是否成功
    """
    try:
        repo = _get_customer_repo()
        # 先获取现有客户信息
        customer = repo.find_by_id(customer_id)
        if not customer:
            logger.warning(f"客户不存在: {customer_id}")
            return False
        
        # 更新字段
        for key, value in updates.items():
            if hasattr(customer, key):
                setattr(customer, key, value)
        
        # 保存更新
        success = repo.update(customer)
        if success:
            logger.info(f"更新客户信息成功: customer_id={customer_id}, 更新字段={list(updates.keys())}")
        else:
            logger.error(f"更新客户信息失败: customer_id={customer_id}")
        return success
    except Exception as e:
        logger.error(f"更新客户信息异常: {customer_id}, 错误: {e}")
        return False

def update_customer_address(customer_id: int, new_address: str) -> bool:
    """
    更新客户地址（专用接口）
    
    Args:
        customer_id: 客户ID
        new_address: 新地址
        
    Returns:
        更新是否成功
    """
    try:
        repo = _get_customer_repo()
        success = repo.update_address(customer_id, new_address)
        if success:
            logger.info(f"更新客户地址成功: customer_id={customer_id}, 新地址={new_address}")
        return success
    except Exception as e:
        logger.error(f"更新客户地址失败: {customer_id}, 错误: {e}")
        return False

def insert_customer(customer_data: Dict[str, Any]) -> bool:
    """
    插入新的客户信息
    
    保持与原有接口的兼容性
    
    Args:
        customer_data: 客户数据字典
        
    Returns:
        插入是否成功
    """
    try:
        # 创建一个简单的客户对象（字典形式）
        customer = {
            'customer_id': customer_data.get('customer_id'),
            'customer_name': customer_data.get('customer_name', ''),
            'data_source': customer_data.get('data_source', ''),
            'address': customer_data.get('address', ''),
            'tag_result': customer_data.get('tag_result', 0),
            'industry_id': customer_data.get('industry_id'),
            'brain_id': customer_data.get('brain_id'),
            'chain_leader_id': customer_data.get('chain_leader_id')
        }
        
        # 插入数据库
        repo = _get_customer_repo()
        success = repo.create(customer)
        if success:
            logger.info(f"插入客户成功: {customer_data.get('customer_name', 'Unknown')}")
        return success
    except Exception as e:
        logger.error(f"插入客户失败: {e}")
        return False

def search_customers_by_keyword(keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    根据关键词搜索客户
    
    Args:
        keyword: 搜索关键词
        limit: 返回结果数量限制
        
    Returns:
        客户信息列表
    """
    try:
        repo = _get_customer_repo()
        customers = repo.search_by_keyword(keyword, limit)
        return [customer.to_dict() for customer in customers]
    except Exception as e:
        logger.error(f"搜索客户失败: {keyword}, 错误: {e}")
        return []

def get_customer_statistics() -> Dict[str, Any]:
    """
    获取客户统计信息
    
    Returns:
        统计信息字典
    """
    try:
        repo = _get_customer_repo()
        return repo.get_statistics()
    except Exception as e:
        logger.error(f"获取客户统计失败: {e}")
        return {}

# ==================== 企业相关查询接口 ====================

def get_enterprise_by_name(enterprise_name: str) -> Optional[Dict[str, Any]]:
    """
    根据企业名称查询企业信息
    
    保持与原有接口的兼容性
    """
    try:
        repo = _get_enterprise_repo()
        enterprise = repo.find_by_name(enterprise_name)
        return enterprise.to_dict() if enterprise else None
    except Exception as e:
        logger.error(f"查询企业失败: {enterprise_name}, 错误: {e}")
        return None

def get_enterprise_by_id(enterprise_id: int) -> Optional[Dict[str, Any]]:
    """
    根据企业ID查询企业信息
    
    保持与原有接口的兼容性
    """
    try:
        repo = _get_enterprise_repo()
        enterprise = repo.find_by_id(enterprise_id)
        return enterprise.to_dict() if enterprise else None
    except Exception as e:
        logger.error(f"查询企业失败: {enterprise_id}, 错误: {e}")
        return None

def search_enterprises_by_keyword(keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    根据关键词搜索企业
    
    Args:
        keyword: 搜索关键词
        limit: 返回结果数量限制
        
    Returns:
        企业信息列表
    """
    try:
        repo = _get_enterprise_repo()
        enterprises = repo.search_by_keyword(keyword, limit)
        return [enterprise.to_dict() for enterprise in enterprises]
    except Exception as e:
        logger.error(f"搜索企业失败: {keyword}, 错误: {e}")
        return []

def get_enterprise_statistics() -> Dict[str, Any]:
    """
    获取企业统计信息
    
    Returns:
        统计信息字典
    """
    try:
        repo = _get_enterprise_repo()
        return repo.get_statistics()
    except Exception as e:
        logger.error(f"获取企业统计失败: {e}")
        return {}

# ==================== 行业相关查询接口 ====================

def get_industry_by_id(industry_id: int) -> Optional[Dict[str, Any]]:
    """
    根据行业ID查询行业信息
    
    Args:
        industry_id: 行业ID
        
    Returns:
        行业信息字典或None
    """
    try:
        repo = _get_industry_repo()
        industry = repo.find_by_id(industry_id)
        return industry.to_dict() if industry else None
    except Exception as e:
        logger.error(f"查询行业失败: {industry_id}, 错误: {e}")
        return None

def get_industry_by_name(industry_name: str) -> Optional[Dict[str, Any]]:
    """
    根据行业名称查询行业信息
    
    Args:
        industry_name: 行业名称
        
    Returns:
        行业信息字典或None
    """
    try:
        repo = _get_industry_repo()
        industry = repo.find_by_name(industry_name)
        return industry.to_dict() if industry else None
    except Exception as e:
        logger.error(f"查询行业失败: {industry_name}, 错误: {e}")
        return None

def get_all_industries() -> List[Dict[str, Any]]:
    """
    获取所有行业信息
    
    Returns:
        行业信息列表
    """
    try:
        repo = _get_industry_repo()
        industries = repo.get_all()
        return [industry.to_dict() for industry in industries]
    except Exception as e:
        logger.error(f"获取所有行业失败: {e}")
        return []

def get_industry_related_info(industry_id: int) -> Dict[str, Any]:
    """
    获取行业相关信息（客户数、企业数、产业大脑等）
    
    Args:
        industry_id: 行业ID
        
    Returns:
        行业相关信息字典
    """
    try:
        repo = _get_industry_repo()
        info = {
            'industry': None,
            'customer_count': 0,
            'enterprise_count': 0,
            'related_brains': []
        }
        
        # 获取行业基本信息
        industry = repo.find_by_id(industry_id)
        if industry:
            info['industry'] = industry.to_dict()
            
            # 获取关联统计
            info['customer_count'] = repo.get_related_customers_count(industry_id)
            info['enterprise_count'] = repo.get_related_enterprises_count(industry_id)
            info['related_brains'] = repo.get_related_brains(industry_id)
        
        return info
    except Exception as e:
        logger.error(f"获取行业相关信息失败: {industry_id}, 错误: {e}")
        return {}

# ==================== 地区相关查询接口 ====================

def get_area_by_id(area_id: int) -> Optional[Dict[str, Any]]:
    """
    根据地区ID查询地区信息
    
    Args:
        area_id: 地区ID
        
    Returns:
        地区信息字典或None
    """
    try:
        repo = _get_area_repo()
        area = repo.find_by_id(area_id)
        return area.to_dict() if area else None
    except Exception as e:
        logger.error(f"查询地区失败: {area_id}, 错误: {e}")
        return None

def get_area_by_name(city_name: str, district_name: str = None) -> Optional[Dict[str, Any]]:
    """
    根据城市和区县名称查询地区信息
    
    Args:
        city_name: 城市名称
        district_name: 区县名称（可选）
        
    Returns:
        地区信息字典或None
    """
    try:
        repo = _get_area_repo()
        area = repo.find_by_name(city_name, district_name)
        return area.to_dict() if area else None
    except Exception as e:
        logger.error(f"查询地区失败: {city_name}-{district_name}, 错误: {e}")
        return None

def get_all_cities() -> List[str]:
    """
    获取所有城市名称
    
    Returns:
        城市名称列表
    """
    try:
        repo = _get_area_repo()
        return repo.get_all_cities()
    except Exception as e:
        logger.error(f"获取所有城市失败: {e}")
        return []

def get_all_areas() -> List[Dict[str, Any]]:
    """
    获取所有地区信息
    
    Returns:
        地区信息列表
    """
    try:
        repo = _get_area_repo()
        areas = repo.get_all()
        return [area.to_dict() for area in areas]
    except Exception as e:
        logger.error(f"获取所有地区失败: {e}")
        return []

# ==================== 产业大脑相关查询接口 ====================

def get_industry_brain_by_id(brain_id: int) -> Optional[Dict[str, Any]]:
    """
    根据产业大脑ID查询信息
    
    Args:
        brain_id: 产业大脑ID
        
    Returns:
        产业大脑信息字典或None
    """
    try:
        repo = _get_brain_repo()
        brain = repo.find_by_id(brain_id)
        return brain.to_dict() if brain else None
    except Exception as e:
        logger.error(f"查询产业大脑失败: {brain_id}, 错误: {e}")
        return None

def get_industry_brain_by_name(brain_name: str) -> Optional[Dict[str, Any]]:
    """
    根据产业大脑名称查询信息
    
    Args:
        brain_name: 产业大脑名称
        
    Returns:
        产业大脑信息字典或None
    """
    try:
        repo = _get_brain_repo()
        brain = repo.find_by_name(brain_name)
        return brain.to_dict() if brain else None
    except Exception as e:
        logger.error(f"查询产业大脑失败: {brain_name}, 错误: {e}")
        return None

def get_all_industry_brains() -> List[Dict[str, Any]]:
    """
    获取所有产业大脑信息
    
    Returns:
        产业大脑信息列表
    """
    try:
        repo = _get_brain_repo()
        brains = repo.get_all()
        return [brain.to_dict() for brain in brains]
    except Exception as e:
        logger.error(f"获取所有产业大脑失败: {e}")
        return []

def get_industry_brain_related_industries(brain_id: int) -> List[Dict[str, Any]]:
    """
    获取产业大脑关联的行业
    
    Args:
        brain_id: 产业大脑ID
        
    Returns:
        关联行业列表
    """
    try:
        repo = _get_brain_repo()
        return repo.find_related_industries(brain_id)
    except Exception as e:
        logger.error(f"获取产业大脑关联行业失败: {brain_id}, 错误: {e}")
        return []

# ==================== 综合查询接口 ====================

def get_comprehensive_enterprise_info(enterprise_name: str) -> Dict[str, Any]:
    """
    获取企业的综合信息（包括关联的行业、地区、产业大脑等）
    
    Args:
        enterprise_name: 企业名称
        
    Returns:
        综合信息字典
    """
    try:
        result = {
            'enterprise': None,
            'industry': None,
            'area': None,
            'industry_brain': None,
            'related_customers': [],
            'statistics': {}
        }
        
        # 首先尝试在客户表中查找
        customer = get_customer_by_name(enterprise_name)
        if customer:
            result['enterprise'] = customer
            
            # 获取关联的行业信息
            if customer.get('industry_id'):
                result['industry'] = get_industry_by_id(customer['industry_id'])
            
            # 获取关联的产业大脑信息
            if customer.get('brain_id'):
                result['industry_brain'] = get_industry_brain_by_id(customer['brain_id'])
        
        # 如果在客户表中没找到，尝试在企业表中查找
        if not result['enterprise']:
            enterprise = get_enterprise_by_name(enterprise_name)
            if enterprise:
                result['enterprise'] = enterprise
                
                # 获取关联的行业信息
                if enterprise.get('industry_id'):
                    result['industry'] = get_industry_by_id(enterprise['industry_id'])
                
                # 获取关联的地区信息
                if enterprise.get('area_id'):
                    result['area'] = get_area_by_id(enterprise['area_id'])
        
        return result
    except Exception as e:
        logger.error(f"获取企业综合信息失败: {enterprise_name}, 错误: {e}")
        return {}

# ==================== 向后兼容的别名 ====================

# 为了保持与原有代码的完全兼容，提供一些别名
find_customer_by_name = get_customer_by_name
find_customer_by_id = get_customer_by_id
find_enterprise_by_name = get_enterprise_by_name
find_enterprise_by_id = get_enterprise_by_id