"""
客户数据模型
"""
from typing import Optional, Dict, Any


class Customer:
    """客户信息模型类"""
    
    def __init__(self, customer_id: Optional[int] = None, customer_name: str = "", 
                 data_source: Optional[str] = None, address: Optional[str] = None,
                 tag_result: Optional[int] = None, industry_id: Optional[int] = None,
                 brain_id: Optional[int] = None, chain_leader_id: Optional[int] = None,
                 industry_name: Optional[str] = None, brain_name: Optional[str] = None,
                 chain_leader_name: Optional[str] = None, district_name: Optional[str] = None,
                 source_table: str = "customer"):
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.data_source = data_source
        self.address = address
        self.tag_result = tag_result
        self.industry_id = industry_id
        self.brain_id = brain_id
        self.chain_leader_id = chain_leader_id
        self.industry_name = industry_name
        self.brain_name = brain_name
        self.chain_leader_name = chain_leader_name
        self.district_name = district_name
        self.source_table = source_table
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Customer':
        """从字典创建Customer实例"""
        if not data:
            return None
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'data_source': self.data_source,
            'address': self.address,
            'tag_result': self.tag_result,
            'industry_id': self.industry_id,
            'brain_id': self.brain_id,
            'chain_leader_id': self.chain_leader_id,
            'industry_name': self.industry_name,
            'brain_name': self.brain_name,
            'chain_leader_name': self.chain_leader_name,
            'district_name': self.district_name,
            'source_table': self.source_table
        }
    
    def __repr__(self) -> str:
        return f"Customer(id={self.customer_id}, name='{self.customer_name}')"