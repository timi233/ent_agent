"""
行业数据模型
"""
from typing import Optional, Dict, Any


class Industry:
    """行业信息模型类"""
    
    def __init__(self, industry_id: Optional[int] = None, industry_name: str = ""):
        self.industry_id = industry_id
        self.industry_name = industry_name
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Industry':
        """从字典创建Industry实例"""
        if not data:
            return None
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'industry_id': self.industry_id,
            'industry_name': self.industry_name
        }
    
    def __repr__(self) -> str:
        return f"Industry(id={self.industry_id}, name='{self.industry_name}')"