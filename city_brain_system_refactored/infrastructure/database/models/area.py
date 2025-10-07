"""
地区数据模型
新增的地区信息模型，支持城市和区县信息管理
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Area:
    """地区信息模型类"""
    
    # 基础字段
    area_id: Optional[int] = None
    city_name: str = ""
    district_name: str = ""
    district_code: Optional[str] = None
    
    # 元数据字段
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """数据验证和处理"""
        # 清理字符串字段
        if self.city_name:
            self.city_name = self.city_name.strip()
        
        if self.district_name:
            self.district_name = self.district_name.strip()
        
        if self.district_code:
            self.district_code = self.district_code.strip()
        
        # 验证必填字段
        if not self.city_name:
            raise ValueError("城市名称不能为空")
        
        if not self.district_name:
            raise ValueError("区县名称不能为空")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['Area']:
        """从字典创建Area实例"""
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
        except TypeError:
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
            'area_id', 'city_name', 'district_name', 'district_code'
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
            if not self.city_name or not self.city_name.strip():
                return False
            
            if not self.district_name or not self.district_name.strip():
                return False
            
            # 检查ID字段的有效性
            if self.area_id is not None and self.area_id <= 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        if self.city_name and self.district_name:
            return f"{self.city_name}{self.district_name}"
        elif self.district_name:
            return self.district_name
        elif self.city_name:
            return self.city_name
        else:
            return "未知地区"
    
    def get_full_name(self) -> str:
        """获取完整名称"""
        return f"{self.city_name}{self.district_name}"
    
    def is_same_city(self, other: 'Area') -> bool:
        """判断是否为同一城市"""
        if not other:
            return False
        return self.city_name == other.city_name
    
    def is_same_district(self, other: 'Area') -> bool:
        """判断是否为同一区县"""
        if not other:
            return False
        return (self.city_name == other.city_name and 
                self.district_name == other.district_name)
    
    def __str__(self) -> str:
        return f"Area(id={self.area_id}, name='{self.get_display_name()}')"
    
    def __repr__(self) -> str:
        return (f"Area(area_id={self.area_id}, "
                f"city_name='{self.city_name}', "
                f"district_name='{self.district_name}')")


# 工厂函数
def create_area(city_name: str, district_name: str, **kwargs) -> Area:
    """创建地区实例的工厂函数"""
    return Area(city_name=city_name, district_name=district_name, **kwargs)


def create_area_from_db_row(row: Dict[str, Any]) -> Optional[Area]:
    """从数据库行创建地区实例"""
    return Area.from_dict(row)