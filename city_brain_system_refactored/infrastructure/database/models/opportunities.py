"""
AS和IPG商机数据模型
用于访问feishu_crm数据库中的as_opportunities和ipg_clients表
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class ASOpportunity:
    """AS系统商机模型"""

    # 主键
    id: Optional[int] = None
    report_id: Optional[int] = None

    # 客户信息
    customer_name: Optional[str] = None
    contact_person: Optional[str] = None
    mobile: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None

    # 地理位置
    area: Optional[str] = None
    areaname: Optional[str] = None

    # 行业信息
    industry: Optional[str] = None

    # 商机信息
    product_name: Optional[str] = None
    budget: Optional[Decimal] = None
    expected_close_date: Optional[str] = None  # DATE
    status: Optional[str] = None
    statename: Optional[str] = None

    # 合作伙伴信息
    partner_name: Optional[str] = None
    creator: Optional[str] = None
    last_modifier: Optional[str] = None

    # 需求和备注
    requirements: Optional[str] = None
    notes: Optional[str] = None

    # 时间戳
    create_time: Optional[datetime] = None
    last_modify_time: Optional[datetime] = None
    submit_time: Optional[datetime] = None

    # 原始字段
    ppy_budget: Optional[str] = None
    ppy_cycle: Optional[str] = None
    ppyname_content: Optional[str] = None
    ppyname_href: Optional[str] = None

    # 元数据
    data_source: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'customer_name': self.customer_name,
            'contact_person': self.contact_person,
            'mobile': self.mobile,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'address': self.address,
            'area': self.area,
            'areaname': self.areaname,
            'industry': self.industry,
            'product_name': self.product_name,
            'budget': float(self.budget) if self.budget else None,
            'expected_close_date': str(self.expected_close_date) if self.expected_close_date else None,
            'status': self.status,
            'statename': self.statename,
            'partner_name': self.partner_name,
            'creator': self.creator,
            'last_modifier': self.last_modifier,
            'requirements': self.requirements,
            'notes': self.notes,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'last_modify_time': self.last_modify_time.isoformat() if self.last_modify_time else None,
            'submit_time': self.submit_time.isoformat() if self.submit_time else None,
            'data_source': self.data_source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'ASOpportunity':
        """从数据库行创建实例"""
        return cls(
            id=row.get('id'),
            report_id=row.get('report_id'),
            customer_name=row.get('customer_name'),
            contact_person=row.get('contact_person'),
            mobile=row.get('mobile'),
            phone=row.get('phone'),
            email=row.get('email'),
            website=row.get('website'),
            address=row.get('address'),
            area=row.get('area'),
            areaname=row.get('areaname'),
            industry=row.get('industry'),
            product_name=row.get('product_name'),
            budget=row.get('budget'),
            expected_close_date=row.get('expected_close_date'),
            status=row.get('status'),
            statename=row.get('statename'),
            partner_name=row.get('partner_name'),
            creator=row.get('creator'),
            last_modifier=row.get('last_modifier'),
            requirements=row.get('requirements'),
            notes=row.get('notes'),
            create_time=row.get('create_time'),
            last_modify_time=row.get('last_modify_time'),
            submit_time=row.get('submit_time'),
            ppy_budget=row.get('ppy_budget'),
            ppy_cycle=row.get('ppy_cycle'),
            ppyname_content=row.get('ppyname_content'),
            ppyname_href=row.get('ppyname_href'),
            data_source=row.get('data_source'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at'),
        )


@dataclass
class IPGClient:
    """IPG系统客户/商机模型"""

    # 主键
    id: Optional[int] = None
    rid: Optional[int] = None

    # 客户基本信息
    client_name: Optional[str] = None
    client_type: Optional[str] = None
    trade: Optional[str] = None
    trade2: Optional[str] = None

    # 联系信息
    contact: Optional[str] = None
    contact_position: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_mobile: Optional[str] = None
    email: Optional[str] = None
    contact_addr: Optional[str] = None

    # 地理位置
    location_area: Optional[str] = None
    location_province: Optional[str] = None
    location_city: Optional[str] = None
    area_id: Optional[int] = None
    province_id: Optional[int] = None
    city_id: Optional[int] = None

    # 业务信息
    sell_product: Optional[str] = None
    agent_num: Optional[int] = None
    sell_cycle: Optional[str] = None
    rival: Optional[str] = None
    requirement: Optional[str] = None
    need_support: Optional[str] = None
    faith_in: Optional[str] = None
    remark: Optional[str] = None
    comments: Optional[str] = None

    # 报备状态
    status: Optional[str] = None
    status_id: Optional[int] = None
    sub_status: Optional[int] = None
    sub_status_txt: Optional[str] = None

    # 时间信息
    create_time: Optional[datetime] = None
    expiration_time: Optional[datetime] = None
    is_delay: Optional[bool] = None

    # 试用信息
    is_have_first_trial: Optional[bool] = None
    first_trial_days: Optional[int] = None
    first_trial_agent_num: Optional[int] = None
    first_trial_modules: Optional[str] = None
    first_trial_is_en: Optional[str] = None

    # 代理商信息
    reseller_name: Optional[str] = None
    reseller_code: Optional[str] = None
    reseller_sale: Optional[str] = None

    # 元数据
    data_source: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'rid': self.rid,
            'client_name': self.client_name,
            'client_type': self.client_type,
            'trade': self.trade,
            'trade2': self.trade2,
            'contact': self.contact,
            'contact_position': self.contact_position,
            'contact_phone': self.contact_phone,
            'contact_mobile': self.contact_mobile,
            'email': self.email,
            'contact_addr': self.contact_addr,
            'location_area': self.location_area,
            'location_province': self.location_province,
            'location_city': self.location_city,
            'area_id': self.area_id,
            'province_id': self.province_id,
            'city_id': self.city_id,
            'sell_product': self.sell_product,
            'agent_num': self.agent_num,
            'sell_cycle': self.sell_cycle,
            'rival': self.rival,
            'requirement': self.requirement,
            'need_support': self.need_support,
            'faith_in': self.faith_in,
            'remark': self.remark,
            'comments': self.comments,
            'status': self.status,
            'status_id': self.status_id,
            'sub_status': self.sub_status,
            'sub_status_txt': self.sub_status_txt,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'expiration_time': self.expiration_time.isoformat() if self.expiration_time else None,
            'is_delay': self.is_delay,
            'is_have_first_trial': self.is_have_first_trial,
            'first_trial_days': self.first_trial_days,
            'first_trial_agent_num': self.first_trial_agent_num,
            'first_trial_modules': self.first_trial_modules,
            'first_trial_is_en': self.first_trial_is_en,
            'reseller_name': self.reseller_name,
            'reseller_code': self.reseller_code,
            'reseller_sale': self.reseller_sale,
            'data_source': self.data_source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'IPGClient':
        """从数据库行创建实例"""
        return cls(
            id=row.get('id'),
            rid=row.get('rid'),
            client_name=row.get('client_name'),
            client_type=row.get('client_type'),
            trade=row.get('trade'),
            trade2=row.get('trade2'),
            contact=row.get('contact'),
            contact_position=row.get('contact_position'),
            contact_phone=row.get('contact_phone'),
            contact_mobile=row.get('contact_mobile'),
            email=row.get('email'),
            contact_addr=row.get('contact_addr'),
            location_area=row.get('location_area'),
            location_province=row.get('location_province'),
            location_city=row.get('location_city'),
            area_id=row.get('area_id'),
            province_id=row.get('province_id'),
            city_id=row.get('city_id'),
            sell_product=row.get('sell_product'),
            agent_num=row.get('agent_num'),
            sell_cycle=row.get('sell_cycle'),
            rival=row.get('rival'),
            requirement=row.get('requirement'),
            need_support=row.get('need_support'),
            faith_in=row.get('faith_in'),
            remark=row.get('remark'),
            comments=row.get('comments'),
            status=row.get('status'),
            status_id=row.get('status_id'),
            sub_status=row.get('sub_status'),
            sub_status_txt=row.get('sub_status_txt'),
            create_time=row.get('create_time'),
            expiration_time=row.get('expiration_time'),
            is_delay=bool(row.get('is_delay', False)),
            is_have_first_trial=bool(row.get('is_have_first_trial', False)),
            first_trial_days=row.get('first_trial_days'),
            first_trial_agent_num=row.get('first_trial_agent_num'),
            first_trial_modules=row.get('first_trial_modules'),
            first_trial_is_en=row.get('first_trial_is_en'),
            reseller_name=row.get('reseller_name'),
            reseller_code=row.get('reseller_code'),
            reseller_sale=row.get('reseller_sale'),
            data_source=row.get('data_source'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at'),
            is_deleted=bool(row.get('is_deleted', False)),
        )
