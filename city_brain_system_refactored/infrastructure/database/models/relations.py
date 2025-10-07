"""
关联关系数据模型
处理各种实体之间的关联关系
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class BrainIndustryRelation:
    """产业大脑与行业关联关系模型"""
    
    # 基础字段
    rel_id: Optional[int] = None
    brain_id: Optional[int] = None
    industry_id: Optional[int] = None
    
    # 扩展字段（通过JOIN查询获得）
    brain_name: Optional[str] = None
    industry_name: Optional[str] = None
    
    # 元数据字段
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """数据验证和处理"""
        # 验证必填字段
        if self.brain_id is None or self.industry_id is None:
            raise ValueError("产业大脑ID和行业ID不能为空")
        
        if self.brain_id <= 0 or self.industry_id <= 0:
            raise ValueError("产业大脑ID和行业ID必须大于0")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['BrainIndustryRelation']:
        """从字典创建BrainIndustryRelation实例"""
        if not data:
            return None
        
        # 处理数据库字段映射
        processed_data = {}
        for key, value in data.items():
            # 处理None值
            if value is None:
                processed_data[key] = None
            # 处理字符串字段
            elif isinstance(value, str):
                processed_data[key] = value.strip() if value.strip() else None
            else:
                processed_data[key] = value
        
        try:
            return cls(**processed_data)
        except (TypeError, ValueError):
            # 忽略未知字段或验证失败
            known_fields = {field.name for field in cls.__dataclass_fields__.values()}
            filtered_data = {k: v for k, v in processed_data.items() if k in known_fields}
            try:
                return cls(**filtered_data)
            except ValueError:
                return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def to_db_dict(self) -> Dict[str, Any]:
        """转换为数据库字典（只包含数据库字段）"""
        db_fields = {'rel_id', 'brain_id', 'industry_id'}
        
        result = {}
        for field, value in asdict(self).items():
            if field in db_fields and value is not None:
                result[field] = value
        
        return result
    
    def is_valid(self) -> bool:
        """验证数据有效性"""
        try:
            # 检查必填字段
            if self.brain_id is None or self.industry_id is None:
                return False
            
            # 检查ID字段的有效性
            if self.brain_id <= 0 or self.industry_id <= 0:
                return False
            
            if self.rel_id is not None and self.rel_id <= 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        if self.brain_name and self.industry_name:
            return f"{self.brain_name} - {self.industry_name}"
        else:
            return f"关联关系(brain_id={self.brain_id}, industry_id={self.industry_id})"
    
    def __str__(self) -> str:
        return f"BrainIndustryRelation(rel_id={self.rel_id}, brain_id={self.brain_id}, industry_id={self.industry_id})"
    
    def __repr__(self) -> str:
        return (f"BrainIndustryRelation(rel_id={self.rel_id}, "
                f"brain_id={self.brain_id}, industry_id={self.industry_id})")


@dataclass
class CompanyRelationship:
    """企业关系模型（用于表示企业间的各种关系）"""
    
    # 基础字段
    relationship_id: Optional[int] = None
    source_company_id: int = 0
    target_company_id: int = 0
    relationship_type: str = ""  # 'customer_to_chain_leader', 'supplier', 'partner', etc.
    
    # 扩展字段
    source_company_name: Optional[str] = None
    target_company_name: Optional[str] = None
    source_table: Optional[str] = None  # 'customer' or 'enterprise_chain_leader'
    target_table: Optional[str] = None
    
    # 元数据字段
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """数据验证和处理"""
        if self.relationship_type:
            self.relationship_type = self.relationship_type.strip()
        
        # 验证必填字段
        if self.source_company_id <= 0 or self.target_company_id <= 0:
            raise ValueError("源企业ID和目标企业ID必须大于0")
        
        if not self.relationship_type:
            raise ValueError("关系类型不能为空")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['CompanyRelationship']:
        """从字典创建CompanyRelationship实例"""
        if not data:
            return None
        
        processed_data = {}
        for key, value in data.items():
            if value is None:
                processed_data[key] = None
            elif isinstance(value, str):
                processed_data[key] = value.strip() if value.strip() else None
            else:
                processed_data[key] = value
        
        try:
            return cls(**processed_data)
        except (TypeError, ValueError):
            known_fields = {field.name for field in cls.__dataclass_fields__.values()}
            filtered_data = {k: v for k, v in processed_data.items() if k in known_fields}
            try:
                return cls(**filtered_data)
            except ValueError:
                return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def is_valid(self) -> bool:
        """验证数据有效性"""
        try:
            return (self.source_company_id > 0 and 
                   self.target_company_id > 0 and 
                   bool(self.relationship_type.strip()))
        except Exception:
            return False
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        if self.source_company_name and self.target_company_name:
            return f"{self.source_company_name} -> {self.target_company_name} ({self.relationship_type})"
        else:
            return f"企业关系({self.source_company_id} -> {self.target_company_id})"
    
    def __str__(self) -> str:
        return f"CompanyRelationship({self.source_company_id} -> {self.target_company_id}, {self.relationship_type})"


# 工厂函数
def create_brain_industry_relation(brain_id: int, industry_id: int, **kwargs) -> BrainIndustryRelation:
    """创建产业大脑行业关联实例的工厂函数"""
    return BrainIndustryRelation(brain_id=brain_id, industry_id=industry_id, **kwargs)


def create_company_relationship(source_id: int, target_id: int, relationship_type: str, **kwargs) -> CompanyRelationship:
    """创建企业关系实例的工厂函数"""
    return CompanyRelationship(
        source_company_id=source_id, 
        target_company_id=target_id, 
        relationship_type=relationship_type, 
        **kwargs
    )