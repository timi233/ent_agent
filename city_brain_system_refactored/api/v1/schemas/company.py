"""
企业相关的API数据模型
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from infrastructure.utils.datetime_utils import now_utc
from datetime import datetime, timezone


class CompanyRequest(BaseModel):
    """企业信息处理请求模型"""
    input_text: str = Field(..., description="用户输入的企业查询文本", max_length=500)
    
    @field_validator('input_text', mode='before')
    def validate_input_text(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError('输入文本不能为空')
        return v.strip()


class CompanyDetails(BaseModel):
    """企业详细信息模型"""
    name: str = Field(default="", description="企业名称")
    region: str = Field(default="", description="所在地区")
    address: str = Field(default="", description="详细地址")
    industry: str = Field(default="", description="所属行业")
    industry_brain: str = Field(default="", description="产业大脑")
    chain_status: str = Field(default="", description="产业链状态")
    revenue_info: str = Field(default="", description="营收信息")
    company_status: str = Field(default="", description="企业地位")
    data_source: str = Field(default="", description="数据来源")


class NewsInfo(BaseModel):
    """新闻资讯信息模型"""
    summary: str = Field(default="", description="新闻摘要")
    references: List[str] = Field(default_factory=list, description="新闻来源链接")


class CompanyData(BaseModel):
    """企业完整数据模型"""
    company_name: str = Field(..., description="企业名称")
    summary: str = Field(default="", description="综合分析摘要")
    details: CompanyDetails = Field(default_factory=CompanyDetails, description="企业详细信息")
    news: NewsInfo = Field(default_factory=NewsInfo, description="新闻资讯")


class CompanyResponse(BaseModel):
    """企业信息处理响应模型"""
    status: str = Field(..., description="处理状态", pattern="^(success|error|processing)$")
    message: Optional[str] = Field(None, description="状态消息")
    data: Optional[CompanyData] = Field(None, description="企业数据")
    timestamp: datetime = Field(default_factory=now_utc, description="响应时间")


class ProgressiveCompanyRequest(BaseModel):
    """渐进式企业信息处理请求模型"""
    input_text: str = Field(..., description="用户输入的企业查询文本", max_length=500)
    disable_cache: bool = Field(False, description="是否禁用缓存（跳过命中与写入）")
    enable_network: bool = Field(True, description="是否启用联网搜索阶段")
    
    @field_validator('input_text', mode='before')
    def validate_input_text(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError('输入文本不能为空')
        return v.strip()


class ProgressiveStageData(BaseModel):
    """渐进式处理阶段数据模型"""
    stage: int = Field(..., description="当前处理阶段", ge=1, le=10)
    status: str = Field(..., description="阶段状态", pattern="^(processing|success|error|completed)$")
    message: str = Field(..., description="阶段消息")
    data: Dict[str, Any] = Field(default_factory=dict, description="阶段数据")
    timestamp: datetime = Field(default_factory=now_utc, description="阶段时间")


class UpdateCompanyRequest(BaseModel):
    """企业信息更新请求模型"""
    customer_id: int = Field(..., description="客户ID", gt=0)
    updates: Dict[str, Any] = Field(..., description="更新数据", min_length=1)
    
    @field_validator('updates')
    def validate_updates(cls, v):
        if not v:
            raise ValueError('更新数据不能为空')
        return v


class UpdateCompanyResponse(BaseModel):
    """企业信息更新响应模型"""
    status: str = Field(..., description="更新状态", pattern="^(success|error)$")
    message: str = Field(..., description="更新消息")
    data: Optional[Dict[str, Any]] = Field(None, description="更新后的数据")
    timestamp: datetime = Field(default_factory=now_utc, description="更新时间")


class ChainLeaderUpdateRequest(BaseModel):
    """链主企业信息更新请求模型"""
    company_name: str = Field(..., description="企业名称", min_length=1, max_length=200)
    updates: Dict[str, Any] = Field(..., description="更新数据", min_length=1)
    
    @field_validator('company_name', mode='before')
    def validate_company_name(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError('企业名称不能为空')
        return v.strip()
    
    @field_validator('updates')
    def validate_updates(cls, v):
        if not v:
            raise ValueError('更新数据不能为空')
        return v


class ChainLeaderUpdateResponse(BaseModel):
    """链主企业信息更新响应模型"""
    status: str = Field(..., description="更新状态", pattern="^(success|error)$")
    message: str = Field(..., description="更新消息")
    data: Optional[Dict[str, Any]] = Field(None, description="更新数据")
    timestamp: datetime = Field(default_factory=now_utc, description="更新时间")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(default="healthy", description="服务状态")
    timestamp: datetime = Field(default_factory=now_utc, description="检查时间")
    version: str = Field(default="1.0.0", description="API版本")
    services: Dict[str, str] = Field(default_factory=dict, description="各服务状态")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    status: str = Field(default="error", description="响应状态")
    message: str = Field(..., description="错误消息")
    error_code: Optional[str] = Field(None, description="错误代码")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=now_utc, description="错误时间")
