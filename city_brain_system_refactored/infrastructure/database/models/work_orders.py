"""
工单数据模型 - Task_sync_new数据库
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date


@dataclass
class WorkOrder:
    """工单服务记录"""
    record_id: str
    source_id: Optional[str] = None
    application_no: Optional[str] = None
    application_link: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    workflow_name: Optional[str] = None
    customer_company: Optional[str] = None
    customer_contact: Optional[str] = None
    customer_phone_secondary: Optional[str] = None
    work_content: Optional[str] = None
    work_mode: Optional[str] = None
    work_type: Optional[str] = None
    engineer_identity: Optional[str] = None
    has_channel: Optional[bool] = None
    channel_name: Optional[str] = None
    channel_contact: Optional[str] = None
    channel_phone_secondary: Optional[str] = None
    initiator_department: Optional[str] = None
    initiated_at: Optional[datetime] = None
    initiator_primary_id: Optional[str] = None
    initiator_primary_name: Optional[str] = None
    initiator_primary_email: Optional[str] = None
    completed_at: Optional[datetime] = None
    service_start_date: Optional[date] = None
    service_start_datetime: Optional[datetime] = None
    service_start_period: Optional[str] = None
    service_end_date: Optional[date] = None
    service_end_datetime: Optional[datetime] = None
    service_end_period: Optional[str] = None
    after_sales_engineer_primary_id: Optional[str] = None
    after_sales_engineer_primary_name: Optional[str] = None
    after_sales_engineer_primary_email: Optional[str] = None
    fetched_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self):
        """转换为字典"""
        return {
            'record_id': self.record_id,
            'source_id': self.source_id,
            'application_no': self.application_no,
            'application_link': self.application_link,
            'status': self.status,
            'priority': self.priority,
            'workflow_name': self.workflow_name,
            'customer_company': self.customer_company,
            'customer_contact': self.customer_contact,
            'customer_phone_secondary': self.customer_phone_secondary,
            'work_content': self.work_content,
            'work_mode': self.work_mode,
            'work_type': self.work_type,
            'engineer_identity': self.engineer_identity,
            'has_channel': self.has_channel,
            'channel_name': self.channel_name,
            'channel_contact': self.channel_contact,
            'channel_phone_secondary': self.channel_phone_secondary,
            'initiator_department': self.initiator_department,
            'initiated_at': self.initiated_at.isoformat() if self.initiated_at else None,
            'initiator_primary_id': self.initiator_primary_id,
            'initiator_primary_name': self.initiator_primary_name,
            'initiator_primary_email': self.initiator_primary_email,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'service_start_date': self.service_start_date.isoformat() if self.service_start_date else None,
            'service_start_datetime': self.service_start_datetime.isoformat() if self.service_start_datetime else None,
            'service_start_period': self.service_start_period,
            'service_end_date': self.service_end_date.isoformat() if self.service_end_date else None,
            'service_end_datetime': self.service_end_datetime.isoformat() if self.service_end_datetime else None,
            'service_end_period': self.service_end_period,
            'after_sales_engineer_primary_id': self.after_sales_engineer_primary_id,
            'after_sales_engineer_primary_name': self.after_sales_engineer_primary_name,
            'after_sales_engineer_primary_email': self.after_sales_engineer_primary_email,
            'fetched_at': self.fetched_at.isoformat() if self.fetched_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_db_row(cls, row):
        """从数据库行创建实例"""
        return cls(
            record_id=row[0],
            source_id=row[1],
            application_no=row[2],
            application_link=row[3],
            status=row[4],
            priority=row[5],
            workflow_name=row[6],
            customer_company=row[7],
            customer_contact=row[8],
            customer_phone_secondary=row[9],
            work_content=row[10],
            work_mode=row[11],
            work_type=row[12],
            engineer_identity=row[13],
            has_channel=bool(row[14]) if row[14] is not None else None,
            channel_name=row[15],
            channel_contact=row[16],
            channel_phone_secondary=row[17],
            initiator_department=row[18],
            initiated_at=row[19],
            initiator_primary_id=row[20],
            initiator_primary_name=row[21],
            initiator_primary_email=row[22],
            completed_at=row[23],
            service_start_date=row[24],
            service_start_datetime=row[25],
            service_start_period=row[26],
            service_end_date=row[27],
            service_end_datetime=row[28],
            service_end_period=row[29],
            after_sales_engineer_primary_id=row[30],
            after_sales_engineer_primary_name=row[31],
            after_sales_engineer_primary_email=row[32],
            fetched_at=row[33],
            created_at=row[34],
            updated_at=row[35],
        )
