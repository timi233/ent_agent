"""
客户数据模型
重构自原有的 database/models/customer.py，增强数据验证和类型安全
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Customer:
    """客户信息模型类"""
    
    # 基础字段
    customer_id: Optional[int] = None
    customer_name: str = ""
    data_source: Optional[str] = None
    address: Optional[str] = None
    tag_result: Optional[int] = None
    
    # 关联字段
    industry_id: Optional[int] = None
    brain_id: Optional[int] = None
    chain_leader_id: Optional[int] = None
    
    # 扩展字段（通过JOIN查询获得）
    industry_name: Optional[str] = None
    brain_name: Optional[str] = None
    chain_leader_name: Optional[str] = None
    district_name: Optional[str] = None
    
    # 元数据字段
    source_table: str = "customer"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """数据验证和处理"""
        # 清理字符串字段
        if self.customer_name:
            self.customer_name = self.customer_name.strip()
        
        if self.address:
            self.address = self.address.strip()
        
        # 验证必填字段
        if not self.customer_name:
            raise ValueError("客户名称不能为空")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['Customer']:
        """从字典创建Customer实例"""
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
            'customer_id', 'customer_name', 'data_source', 'address', 
            'tag_result', 'industry_id', 'brain_id', 'chain_leader_id'
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
            if not self.customer_name or not self.customer_name.strip():
                return False
            
            # 检查ID字段的有效性
            if self.customer_id is not None and self.customer_id <= 0:
                return False
            
            if self.industry_id is not None and self.industry_id <= 0:
                return False
            
            if self.brain_id is not None and self.brain_id <= 0:
                return False
            
            if self.chain_leader_id is not None and self.chain_leader_id <= 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return self.customer_name or "未知客户"
    
    def has_complete_info(self) -> bool:
        """检查是否有完整信息"""
        return all([
            self.customer_name,
            self.address,
            self.industry_name,
            self.district_name
        ])
    
    def __str__(self) -> str:
        return f"Customer(id={self.customer_id}, name='{self.customer_name}')"
    
    def __repr__(self) -> str:
        return (f"Customer(customer_id={self.customer_id}, "
                f"customer_name='{self.customer_name}', "
                f"source_table='{self.source_table}')")


# 工厂函数
def create_customer(name: str, **kwargs) -> Customer:
    """创建客户实例的工厂函数"""
    return Customer(customer_name=name, **kwargs)


def create_customer_from_db_row(row: Dict[str, Any]) -> Optional[Customer]:
    """从数据库行创建客户实例"""
    return Customer.from_dict(row)