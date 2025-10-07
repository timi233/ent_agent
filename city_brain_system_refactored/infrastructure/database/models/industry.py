"""
行业数据模型
重构自原有的 database/models/industry.py，增强数据验证和类型安全
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Industry:
    """行业信息模型类"""
    
    # 基础字段
    industry_id: Optional[int] = None
    industry_name: str = ""
    industry_type: Optional[str] = None
    industry_remark: Optional[str] = None
    
    # 元数据字段
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """数据验证和处理"""
        # 清理字符串字段
        if self.industry_name:
            self.industry_name = self.industry_name.strip()
        
        if self.industry_type:
            self.industry_type = self.industry_type.strip()
        
        if self.industry_remark:
            self.industry_remark = self.industry_remark.strip()
        
        # 验证必填字段
        if not self.industry_name:
            raise ValueError("行业名称不能为空")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['Industry']:
        """从字典创建Industry实例"""
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
            'industry_id', 'industry_name', 'industry_type', 'industry_remark'
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
            if not self.industry_name or not self.industry_name.strip():
                return False
            
            # 检查ID字段的有效性
            if self.industry_id is not None and self.industry_id <= 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return self.industry_name or "未知行业"
    
    def get_full_description(self) -> str:
        """获取完整描述"""
        parts = [self.industry_name]
        
        if self.industry_type:
            parts.append(f"({self.industry_type})")
        
        if self.industry_remark:
            parts.append(f" - {self.industry_remark}")
        
        return "".join(parts)
    
    def __str__(self) -> str:
        return f"Industry(id={self.industry_id}, name='{self.industry_name}')"
    
    def __repr__(self) -> str:
        return (f"Industry(industry_id={self.industry_id}, "
                f"industry_name='{self.industry_name}', "
                f"industry_type='{self.industry_type}')")


@dataclass
class IndustryBrain:
    """产业大脑模型类"""
    
    # 基础字段
    brain_id: Optional[int] = None
    brain_name: str = ""
    area_id: Optional[int] = None
    build_year: Optional[int] = None
    brain_remark: Optional[str] = None
    
    # 扩展字段
    area_name: Optional[str] = None
    city_name: Optional[str] = None
    district_name: Optional[str] = None
    
    # 元数据字段
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """数据验证和处理"""
        if self.brain_name:
            self.brain_name = self.brain_name.strip()
        
        if self.brain_remark:
            self.brain_remark = self.brain_remark.strip()
        
        if not self.brain_name:
            raise ValueError("产业大脑名称不能为空")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['IndustryBrain']:
        """从字典创建IndustryBrain实例"""
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
        except TypeError:
            known_fields = {field.name for field in cls.__dataclass_fields__.values()}
            filtered_data = {k: v for k, v in processed_data.items() if k in known_fields}
            return cls(**filtered_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return self.brain_name or "未知产业大脑"
    
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
        return f"IndustryBrain(id={self.brain_id}, name='{self.brain_name}')"


# 工厂函数
def create_industry(name: str, **kwargs) -> Industry:
    """创建行业实例的工厂函数"""
    return Industry(industry_name=name, **kwargs)


def create_industry_brain(name: str, **kwargs) -> IndustryBrain:
    """创建产业大脑实例的工厂函数"""
    return IndustryBrain(brain_name=name, **kwargs)