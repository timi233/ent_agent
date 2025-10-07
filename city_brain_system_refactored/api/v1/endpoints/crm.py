"""
CRM商机数据相关的API端点
"""
import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from api.v1.schemas.crm import (
    OpportunityListResponse,
    OpportunityDetailResponse,
    OpportunitySearchRequest,
    StatusListResponse,
    CRMHealthResponse
)
from infrastructure.database.repositories.crm_repository import CRMOpportunityRepository
from infrastructure.database.crm_connection import get_crm_connection
from infrastructure.utils.datetime_utils import now_utc

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crm", tags=["CRM商机数据"])


@router.get("/health", response_model=CRMHealthResponse)
async def check_crm_health():
    """
    检查CRM数据库连接健康状态
    """
    try:
        crm_conn = get_crm_connection()
        is_healthy = crm_conn.test_connection()
        
        if is_healthy:
            return CRMHealthResponse(
                status="healthy",
                database=crm_conn.settings.database,
                host=f"{crm_conn.settings.host}:{crm_conn.settings.port}",
                message="CRM数据库连接正常",
                timestamp=now_utc()
            )
        else:
            return CRMHealthResponse(
                status="unhealthy",
                database=crm_conn.settings.database,
                host=f"{crm_conn.settings.host}:{crm_conn.settings.port}",
                message="CRM数据库连接失败",
                timestamp=now_utc()
            )
    except Exception as e:
        logger.error(f"CRM健康检查失败: {e}")
        return CRMHealthResponse(
            status="error",
            database="unknown",
            host="unknown",
            message=f"健康检查异常: {str(e)}",
            timestamp=now_utc()
        )


@router.get("/opportunities", response_model=OpportunityListResponse)
async def search_opportunities(
    company_name: Optional[str] = Query(None, description="企业名称（模糊匹配）"),
    status: Optional[str] = Query(None, description="项目状态过滤"),
    page: int = Query(1, ge=1, description="页码（从1开始）"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小（1-100）")
):
    """
    搜索商机数据
    
    根据企业名称搜索相关的商机信息，支持分页和状态过滤
    """
    try:
        logger.info(f"搜索商机数据: company_name={company_name}, status={status}, page={page}, page_size={page_size}")
        
        repository = CRMOpportunityRepository()
        result = repository.search_opportunities_by_company_name(
            company_name=company_name,
            status_filter=status,
            page=page,
            page_size=page_size
        )
        
        return OpportunityListResponse(**result)
        
    except Exception as e:
        logger.error(f"搜索商机数据失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"搜索商机数据失败: {str(e)}"
        )


@router.get("/opportunities/{opportunity_id}", response_model=OpportunityDetailResponse)
async def get_opportunity_detail(
    opportunity_id: str = Path(..., description="商机ID")
):
    """
    获取商机详情
    
    根据商机ID获取详细信息，包括原始数据
    """
    try:
        logger.info(f"获取商机详情: opportunity_id={opportunity_id}")
        
        repository = CRMOpportunityRepository()
        opportunity = repository.get_opportunity_by_id(opportunity_id)
        
        if not opportunity:
            raise HTTPException(
                status_code=404,
                detail=f"未找到ID为 {opportunity_id} 的商机"
            )
        
        return OpportunityDetailResponse(**opportunity)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取商机详情失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取商机详情失败: {str(e)}"
        )


@router.get("/statuses", response_model=StatusListResponse)
async def get_available_statuses():
    """
    获取所有可用的项目状态
    
    返回CRM系统中所有可用的项目状态列表，用于前端筛选
    """
    try:
        logger.info("获取CRM项目状态列表")
        
        repository = CRMOpportunityRepository()
        statuses = repository.get_available_statuses()
        
        return StatusListResponse(statuses=statuses)
        
    except Exception as e:
        logger.error(f"获取项目状态列表失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取项目状态列表失败: {str(e)}"
        )


@router.post("/opportunities/search", response_model=OpportunityListResponse)
async def search_opportunities_post(request: OpportunitySearchRequest):
    """
    搜索商机数据（POST方式）
    
    通过POST请求体搜索商机数据，支持更复杂的搜索条件
    """
    try:
        logger.info(f"POST搜索商机数据: {request.dict()}")
        
        repository = CRMOpportunityRepository()
        result = repository.search_opportunities_by_company_name(
            company_name=request.company_name,
            status_filter=request.status,
            page=request.page,
            page_size=request.page_size
        )
        
        return OpportunityListResponse(**result)
        
    except Exception as e:
        logger.error(f"POST搜索商机数据失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"搜索商机数据失败: {str(e)}"
        )