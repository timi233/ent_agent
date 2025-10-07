"""
企业数据模型
重构自原有的 database/models/enterprise.py，增强数据验证和类型安全
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Enterprise:
    """企业信息模型类（链主企业）"""
    
    # 基础字段
    enterprise_id: Optional[int] = None
    enterprise_name: str = ""
    area_id: Optional[int] = None
    industry_id: Optional[int] = None
    enterprise_remark: Optional[str] = None
    
    # 扩展字段（通过JOIN查询获得）
    industry_name: Optional[str] = None
    district_name: Optional[str] = None
    city_name: Optional[str] = None
    
    # 元数据字段
    source_table: str = "enterprise_chain_leader"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """数据验证和处理"""
        # 清理字符串字段
        if self.enterprise_name:
            self.enterprise_name = self.enterprise_name.strip()
        
        if self.enterprise_remark:
            self.enterprise_remark = self.enterprise_remark.strip()
        
        # 验证必填字段
        if not self.enterprise_name:
            raise ValueError("企业名称不能为空")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['Enterprise']:
        """从字典创建Enterprise实例"""
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
        except TypeError as e:
            # 忽略未知字段
            known_fields = {field.name for field in cls.__dataclass_fields__.values()}
            filtered_data = {k: v for k, v in processed_data.items() if k in known_fields}
            return cls(**filtered_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def to_db_dict(self) -> Dict[str, Any]:
        """转换为数据库字典（只包含数据库字段）"""
        db_fields = {
            'enterprise_id', 'enterprise_name', 'area_id', 
            'industry_id', 'enterprise_remark'
        }
        
        result = {}
        for field, value in asdict(self).items():
            if field in db_fields and value is not None:
                result[field] = value
        
        return result
    
    def is_valid(self) -> bool:
        """验证数据有效性"""
        try:
            # 检查必填字段
            if not self.enterprise_name or not self.enterprise_name.strip():
                return False
            
            # 检查ID字段的有效性
            if self.enterprise_id is not None and self.enterprise_id <= 0:
                return False
            
            if self.area_id is not None and self.area_id <= 0:
                return False
            
            if self.industry_id is not None and self.industry_id <= 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return self.enterprise_name or "未知企业"
    
    def has_complete_info(self) -> bool:
        """检查是否有完整信息"""
        return all([
            self.enterprise_name,
            self.industry_name,
            self.district_name
        ])
    
    def is_chain_leader(self) -> bool:
        """判断是否为链主企业"""
        return self.source_table == "enterprise_chain_leader"
    
    def get_location_info(self) -> str:
        """获取位置信息"""
        if self.city_name and self.district_name:
            return f"{self.city_name}{self.district_name}"
        elif self.district_name:
            return self.district_name
        elif self.city_name:
            return self.city_name
        else:
            return "位置未知"
    
    def __str__(self) -> str:
        return f"Enterprise(id={self.enterprise_id}, name='{self.enterprise_name}')"
    
    def __repr__(self) -> str:
        return (f"Enterprise(enterprise_id={self.enterprise_id}, "
                f"enterprise_name='{self.enterprise_name}', "
                f"source_table='{self.source_table}')")


# 工厂函数
def create_enterprise(name: str, **kwargs) -> Enterprise:
    """创建企业实例的工厂函数"""
    return Enterprise(enterprise_name=name, **kwargs)


def create_enterprise_from_db_row(row: Dict[str, Any]) -> Optional[Enterprise]:
    """从数据库行创建企业实例"""
    return Enterprise.from_dict(row)