"""
enterprise_QD数据库的企业档案模型
用于整合青岛客户的详细企业信息
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class EnterpriseQDProfile:
    """enterprise_QD数据库的企业档案模型"""

    # 基础字段
    id: Optional[bytes] = None  # UUID binary(16)
    run_id: Optional[bytes] = None
    name: str = ""
    normalized_name: str = ""
    address: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    employee_scale: Optional[str] = None

    # 营收数据
    revenue_2021: Optional[Decimal] = None
    revenue_2022: Optional[Decimal] = None
    revenue_2023: Optional[Decimal] = None

    # 排名和描述
    ranking_status: Optional[Dict[str, Any]] = None  # JSON字段
    business_summary: Optional[str] = None
    ranking_description: Optional[str] = None

    # 质量控制
    confidence_score: Optional[Decimal] = None
    is_complete: bool = False
    error_message: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None  # JSON字段

    # 时间戳
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'normalized_name': self.normalized_name,
            'address': self.address,
            'industry': self.industry,
            'region': self.region,
            'employee_scale': self.employee_scale,
            'revenue_2021': float(self.revenue_2021) if self.revenue_2021 else None,
            'revenue_2022': float(self.revenue_2022) if self.revenue_2022 else None,
            'revenue_2023': float(self.revenue_2023) if self.revenue_2023 else None,
            'ranking_status': self.ranking_status,
            'business_summary': self.business_summary,
            'ranking_description': self.ranking_description,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'is_complete': self.is_complete,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'EnterpriseQDProfile':
        """从数据库行创建实例"""
        return cls(
            id=row.get('id'),
            run_id=row.get('run_id'),
            name=row.get('name', ''),
            normalized_name=row.get('normalized_name', ''),
            address=row.get('address'),
            industry=row.get('industry'),
            region=row.get('region'),
            employee_scale=row.get('employee_scale'),
            revenue_2021=row.get('revenue_2021'),
            revenue_2022=row.get('revenue_2022'),
            revenue_2023=row.get('revenue_2023'),
            ranking_status=row.get('ranking_status'),
            business_summary=row.get('business_summary'),
            ranking_description=row.get('ranking_description'),
            confidence_score=row.get('confidence_score'),
            is_complete=bool(row.get('is_complete', 0)),
            error_message=row.get('error_message'),
            raw_payload=row.get('raw_payload'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at'),
        )
