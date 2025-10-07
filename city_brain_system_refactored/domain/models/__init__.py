"""
领域模型包
定义核心业务实体和值对象
"""
from .enterprise import (
    EnterpriseBasicInfo,
    EnterpriseNewsInfo,
    EnterpriseComprehensiveInfo
)

__all__ = [
    'EnterpriseBasicInfo',
    'EnterpriseNewsInfo',
    'EnterpriseComprehensiveInfo'
]
