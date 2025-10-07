"""
CRM_sync_new数据库的客户和商机模型
用于访问飞书CRM同步的客户和商机数据
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class CRMCustomer:
    """CRM系统的客户模型"""

    # 基础字段
    id: Optional[int] = None
    record_id: Optional[str] = None
    name: Optional[str] = None
    industry: Optional[str] = None
    phone: Optional[str] = None
    company_size: Optional[str] = None
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None

    # 所有者信息
    owner_id: Optional[str] = None
    owner_name: Optional[str] = None
    owner_en_name: Optional[str] = None
    owner_email: Optional[str] = None

    # 标记字段
    is_public: Optional[bool] = None
    is_duplicate: Optional[bool] = None

    # 时间戳 (存储为Unix时间戳bigint)
    created_time: Optional[int] = None
    last_follow_up_time: Optional[int] = None
    maintenance_expiry_time: Optional[int] = None

    # 版本和数据管理
    latest_version: Optional[int] = None
    first_seen_at: Optional[str] = None
    last_seen_at: Optional[str] = None

    # 系统字段
    is_deleted: Optional[bool] = None
    deleted_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'record_id': self.record_id,
            'name': self.name,
            'industry': self.industry,
            'phone': self.phone,
            'company_size': self.company_size,
            'contact_name': self.contact_name,
            'contact_title': self.contact_title,
            'owner_id': self.owner_id,
            'owner_name': self.owner_name,
            'owner_en_name': self.owner_en_name,
            'owner_email': self.owner_email,
            'is_public': self.is_public,
            'is_duplicate': self.is_duplicate,
            'created_time': self.created_time,
            'last_follow_up_time': self.last_follow_up_time,
            'maintenance_expiry_time': self.maintenance_expiry_time,
            'latest_version': self.latest_version,
            'first_seen_at': self.first_seen_at,
            'last_seen_at': self.last_seen_at,
        }

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'CRMCustomer':
        """从数据库行创建实例"""
        return cls(
            id=row.get('id'),
            record_id=row.get('record_id'),
            name=row.get('name'),
            industry=row.get('industry'),
            phone=row.get('phone'),
            company_size=row.get('company_size'),
            contact_name=row.get('contact_name'),
            contact_title=row.get('contact_title'),
            owner_id=row.get('owner_id'),
            owner_name=row.get('owner_name'),
            owner_en_name=row.get('owner_en_name'),
            owner_email=row.get('owner_email'),
            is_public=bool(row.get('is_public', 0)),
            is_duplicate=bool(row.get('is_duplicate', 0)),
            created_time=row.get('created_time'),
            last_follow_up_time=row.get('last_follow_up_time'),
            maintenance_expiry_time=row.get('maintenance_expiry_time'),
            latest_version=row.get('latest_version'),
            first_seen_at=row.get('first_seen_at'),
            last_seen_at=row.get('last_seen_at'),
            is_deleted=bool(row.get('is_deleted', 0)),
            deleted_at=row.get('deleted_at'),
        )


@dataclass
class CRMOpportunity:
    """CRM系统的商机模型"""

    # 基础字段
    id: Optional[int] = None
    record_id: Optional[str] = None
    customer_id: Optional[int] = None
    customer_record_id: Optional[str] = None
    customer_name: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None

    # 商机详情
    product: Optional[str] = None
    expected_amount: Optional[Decimal] = None
    expected_deal_time: Optional[int] = None  # Unix timestamp
    status: Optional[str] = None

    # 合同信息
    has_contract: Optional[bool] = None

    # 创建人信息
    created_time: Optional[int] = None  # Unix timestamp
    creator_id: Optional[str] = None
    creator_name: Optional[str] = None
    creator_en_name: Optional[str] = None
    creator_email: Optional[str] = None

    # 父级记录
    parent_record_id: Optional[str] = None

    # 版本和数据管理
    latest_version: Optional[int] = None
    first_seen_at: Optional[str] = None
    last_seen_at: Optional[str] = None

    # 系统字段
    is_deleted: Optional[bool] = None
    deleted_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'record_id': self.record_id,
            'customer_id': self.customer_id,
            'customer_record_id': self.customer_record_id,
            'customer_name': self.customer_name,
            'name': self.name,
            'description': self.description,
            'product': self.product,
            'expected_amount': float(self.expected_amount) if self.expected_amount else None,
            'expected_deal_time': self.expected_deal_time,
            'status': self.status,
            'has_contract': self.has_contract,
            'created_time': self.created_time,
            'creator_id': self.creator_id,
            'creator_name': self.creator_name,
            'creator_en_name': self.creator_en_name,
            'creator_email': self.creator_email,
            'parent_record_id': self.parent_record_id,
            'latest_version': self.latest_version,
            'first_seen_at': self.first_seen_at,
            'last_seen_at': self.last_seen_at,
        }

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'CRMOpportunity':
        """从数据库行创建实例"""
        return cls(
            id=row.get('id'),
            record_id=row.get('record_id'),
            customer_id=row.get('customer_id'),
            customer_record_id=row.get('customer_record_id'),
            customer_name=row.get('customer_name'),
            name=row.get('name'),
            description=row.get('description'),
            product=row.get('product'),
            expected_amount=row.get('expected_amount'),
            expected_deal_time=row.get('expected_deal_time'),
            status=row.get('status'),
            has_contract=bool(row.get('has_contract', 0)),
            created_time=row.get('created_time'),
            creator_id=row.get('creator_id'),
            creator_name=row.get('creator_name'),
            creator_en_name=row.get('creator_en_name'),
            creator_email=row.get('creator_email'),
            parent_record_id=row.get('parent_record_id'),
            latest_version=row.get('latest_version'),
            first_seen_at=row.get('first_seen_at'),
            last_seen_at=row.get('last_seen_at'),
            is_deleted=bool(row.get('is_deleted', 0)),
            deleted_at=row.get('deleted_at'),
        )
