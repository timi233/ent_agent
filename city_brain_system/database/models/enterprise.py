"""
企业数据模型
"""
from typing import Optional, Dict, Any


class Enterprise:
    """企业信息模型类"""
    
    def __init__(self, enterprise_id: Optional[int] = None, enterprise_name: str = "",
                 industry_id: Optional[int] = None, area_id: Optional[int] = None,
                 industry_name: Optional[str] = None, district_name: Optional[str] = None):
        self.enterprise_id = enterprise_id
        self.enterprise_name = enterprise_name
        self.industry_id = industry_id
        self.area_id = area_id
        self.industry_name = industry_name
        self.district_name = district_name
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Enterprise':
        """从字典创建Enterprise实例"""
        if not data:
            return None
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'enterprise_id': self.enterprise_id,
            'enterprise_name': self.enterprise_name,
            'industry_id': self.industry_id,
            'area_id': self.area_id,
            'industry_name': self.industry_name,
            'district_name': self.district_name
        }
    
    def __repr__(self) -> str:
        return f"Enterprise(id={self.enterprise_id}, name='{self.enterprise_name}')"