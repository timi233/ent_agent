"""
数据模型模块
提供所有数据模型的统一导入接口
"""

# 核心实体模型
from .customer import Customer, create_customer, create_customer_from_db_row
from .enterprise import Enterprise, create_enterprise, create_enterprise_from_db_row
from .industry import Industry, IndustryBrain, create_industry, create_industry_brain
from .area import Area, create_area, create_area_from_db_row

# 关联关系模型
from .relations import (
    BrainIndustryRelation, 
    CompanyRelationship,
    create_brain_industry_relation,
    create_company_relationship
)

# 导出所有模型类
__all__ = [
    # 核心实体模型
    'Customer',
    'Enterprise', 
    'Industry',
    'IndustryBrain',
    'Area',
    
    # 关联关系模型
    'BrainIndustryRelation',
    'CompanyRelationship',
    
    # 工厂函数
    'create_customer',
    'create_customer_from_db_row',
    'create_enterprise', 
    'create_enterprise_from_db_row',
    'create_industry',
    'create_industry_brain',
    'create_area',
    'create_area_from_db_row',
    'create_brain_industry_relation',
    'create_company_relationship',
]

# 模型注册表（用于动态创建和验证）
MODEL_REGISTRY = {
    'customer': Customer,
    'enterprise': Enterprise,
    'industry': Industry,
    'industry_brain': IndustryBrain,
    'area': Area,
    'brain_industry_relation': BrainIndustryRelation,
    'company_relationship': CompanyRelationship,
}

# 表名映射
TABLE_MODEL_MAPPING = {
    'QD_customer': Customer,
    'QD_enterprise_chain_leader': Enterprise,
    'QD_industry': Industry,
    'QD_industry_brain': IndustryBrain,
    'QD_area': Area,
    'QD_brain_industry_rel': BrainIndustryRelation,
}


def get_model_by_table_name(table_name: str):
    """根据表名获取对应的模型类"""
    return TABLE_MODEL_MAPPING.get(table_name)


def get_model_by_name(model_name: str):
    """根据模型名获取对应的模型类"""
    return MODEL_REGISTRY.get(model_name)