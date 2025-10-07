"""
CRM相关的数据模型定义
"""
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field


class OpportunityBase(BaseModel):
    """商机基础模型"""
    opportunity_name: Optional[str] = Field(None, description="机会名称")
    customer_name: Optional[str] = Field(None, description="客户名称")
    status: Optional[str] = Field(None, description="项目状态")
    product: Optional[str] = Field(None, description="产品")
    description: Optional[str] = Field(None, description="商机描述")
    owner_name: Optional[str] = Field(None, description="商机创建人")
    expected_amount_wan: Optional[str] = Field(None, description="预计合同额（万元）")
    contract_opportunity_name: Optional[str] = Field(None, description="合同管理-商机名称")


class OpportunityResponse(OpportunityBase):
    """商机响应模型"""
    id: str = Field(..., description="商机ID")
    created_time: Optional[datetime] = Field(None, description="商机创建时间")
    expected_deal_date: Optional[datetime] = Field(None, description="预计交易日期")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class OpportunityDetailResponse(OpportunityResponse):
    """商机详情响应模型"""
    record_data: Optional[dict] = Field(None, description="原始记录数据")
    created_at: Optional[datetime] = Field(None, description="记录创建时间")


class PaginationInfo(BaseModel):
    """分页信息模型"""
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_count: int = Field(..., description="总记录数")
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


class OpportunityListResponse(BaseModel):
    """商机列表响应模型"""
    opportunities: List[OpportunityResponse] = Field(..., description="商机列表")
    pagination: PaginationInfo = Field(..., description="分页信息")


class OpportunitySearchRequest(BaseModel):
    """商机搜索请求模型"""
    company_name: Optional[str] = Field(None, description="企业名称（模糊匹配）")
    status: Optional[str] = Field(None, description="项目状态过滤")
    page: int = Field(1, ge=1, description="页码（从1开始）")
    page_size: int = Field(20, ge=1, le=100, description="每页大小（1-100）")


class StatusListResponse(BaseModel):
    """状态列表响应模型"""
    statuses: List[str] = Field(..., description="可用状态列表")


class CRMHealthResponse(BaseModel):
    """CRM健康检查响应模型"""
    status: str = Field(..., description="连接状态")
    database: str = Field(..., description="数据库名称")
    host: str = Field(..., description="数据库主机")
    message: str = Field(..., description="状态消息")
    timestamp: datetime = Field(..., description="检查时间")