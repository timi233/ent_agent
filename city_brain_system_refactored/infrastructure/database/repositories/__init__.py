"""
仓储层模块
提供所有数据访问仓储类的统一导入接口
"""

# 基础仓储类
from .base_repository import BaseRepository

# 原有仓储类（保持向后兼容）
try:
    from .customer_repository import CustomerRepository
    from .enterprise_repository import EnterpriseRepository
    from .industry_repository import IndustryRepository
except ImportError:
    # 如果原有仓储类导入失败，使用增强版替代
    pass

# 增强版仓储类
from .enhanced_customer_repository import EnhancedCustomerRepository
from .enhanced_enterprise_repository import EnhancedEnterpriseRepository, IndustryBrainRepository
from .enhanced_industry_repository import EnhancedIndustryRepository
from .area_repository import AreaRepository

# 完全独立的仓储类（用于测试和特殊场景）
from .fully_standalone_repository import FullyStandaloneCustomerRepository

# 仓储类注册表
REPOSITORY_REGISTRY = {
    'customer': EnhancedCustomerRepository,
    'enterprise': EnhancedEnterpriseRepository,
    'industry': EnhancedIndustryRepository,
    'area': AreaRepository,
    'industry_brain': IndustryBrainRepository,
    'standalone_customer': FullyStandaloneCustomerRepository,
}

def get_repository(repo_type: str, connection_manager=None):
    """
    获取指定类型的仓储实例
    
    Args:
        repo_type: 仓储类型 ('customer', 'enterprise', 'industry', 'area', 'industry_brain')
        connection_manager: 数据库连接管理器
    
    Returns:
        对应的仓储实例
    """
    if repo_type not in REPOSITORY_REGISTRY:
        raise ValueError(f"未知的仓储类型: {repo_type}")
    
    repo_class = REPOSITORY_REGISTRY[repo_type]
    return repo_class(connection_manager)

# 导出所有仓储类
__all__ = [
    'BaseRepository',
    'EnhancedCustomerRepository',
    'EnhancedEnterpriseRepository',
    'EnhancedIndustryRepository',
    'AreaRepository',
    'IndustryBrainRepository',
    'FullyStandaloneCustomerRepository',
    'REPOSITORY_REGISTRY',
    'get_repository'
]