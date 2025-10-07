"""
CRM_sync_new数据API端点 - 访问CRM_sync_new数据库的客户和商机数据
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import logging

from infrastructure.database.repositories.crm_sync_repository import CRMSyncRepository

logger = logging.getLogger(__name__)

router = APIRouter()

# 全局仓储实例
_crm_sync_repo = None


def get_crm_sync_repo() -> CRMSyncRepository:
    """获取CRM Sync仓储实例"""
    global _crm_sync_repo
    if _crm_sync_repo is None:
        _crm_sync_repo = CRMSyncRepository()
    return _crm_sync_repo


# ==================== 客户相关端点 ====================

@router.get("/customers/search", summary="搜索CRM客户")
async def search_customers(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, ge=1, le=100, description="返回结果数量")
) -> Dict[str, Any]:
    """
    搜索CRM客户（支持名称、行业、地址关键词）
    """
    try:
        repo = get_crm_sync_repo()
        results = repo.search_customers(keyword, limit)

        return {
            "status": "success",
            "count": len(results),
            "data": [r.to_dict() for r in results]
        }
    except Exception as e:
        logger.error(f"搜索客户失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/customers/by-name/{name}", summary="根据名称查询客户")
async def get_customer_by_name(name: str) -> Dict[str, Any]:
    """
    根据客户名称查询详细信息
    """
    try:
        repo = get_crm_sync_repo()
        result = repo.find_customer_by_name(name)

        if not result:
            raise HTTPException(status_code=404, detail=f"未找到客户: {name}")

        return {
            "status": "success",
            "data": result.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询客户失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/customers/by-industry/{industry}", summary="根据行业查询客户")
async def get_customers_by_industry(
    industry: str,
    limit: int = Query(20, ge=1, le=100, description="返回结果数量")
) -> Dict[str, Any]:
    """
    根据行业查询客户列表
    """
    try:
        repo = get_crm_sync_repo()
        results = repo.get_customers_by_industry(industry, limit)

        return {
            "status": "success",
            "industry": industry,
            "count": len(results),
            "data": [r.to_dict() for r in results]
        }
    except Exception as e:
        logger.error(f"按行业查询客户失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/customers/by-owner/{owner_name}", summary="根据负责人查询客户")
async def get_customers_by_owner(
    owner_name: str,
    limit: int = Query(20, ge=1, le=100, description="返回结果数量")
) -> Dict[str, Any]:
    """
    根据负责人查询客户列表
    """
    try:
        repo = get_crm_sync_repo()
        results = repo.get_customers_by_owner(owner_name, limit)

        return {
            "status": "success",
            "owner_name": owner_name,
            "count": len(results),
            "data": [r.to_dict() for r in results]
        }
    except Exception as e:
        logger.error(f"按负责人查询客户失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


# ==================== 商机相关端点 ====================

@router.get("/opportunities/search", summary="搜索商机")
async def search_opportunities(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, ge=1, le=100, description="返回结果数量")
) -> Dict[str, Any]:
    """
    搜索商机（支持名称、客户、产品、描述关键词）
    """
    try:
        repo = get_crm_sync_repo()
        results = repo.search_opportunities(keyword, limit)

        return {
            "status": "success",
            "count": len(results),
            "data": [r.to_dict() for r in results]
        }
    except Exception as e:
        logger.error(f"搜索商机失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/opportunities/{opportunity_id}", summary="根据ID查询商机")
async def get_opportunity_by_id(opportunity_id: int) -> Dict[str, Any]:
    """
    根据商机ID查询详细信息
    """
    try:
        repo = get_crm_sync_repo()
        result = repo.find_opportunity_by_id(opportunity_id)

        if not result:
            raise HTTPException(status_code=404, detail=f"未找到商机: {opportunity_id}")

        return {
            "status": "success",
            "data": result.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询商机失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/opportunities/by-customer/{customer_name}", summary="根据客户查询商机")
async def get_opportunities_by_customer(
    customer_name: str,
    limit: int = Query(20, ge=1, le=100, description="返回结果数量")
) -> Dict[str, Any]:
    """
    根据客户名称查询商机列表
    """
    try:
        repo = get_crm_sync_repo()
        results = repo.get_opportunities_by_customer(customer_name, limit)

        return {
            "status": "success",
            "customer_name": customer_name,
            "count": len(results),
            "data": [r.to_dict() for r in results]
        }
    except Exception as e:
        logger.error(f"按客户查询商机失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/opportunities/by-product/{product}", summary="根据产品查询商机")
async def get_opportunities_by_product(
    product: str,
    limit: int = Query(20, ge=1, le=100, description="返回结果数量")
) -> Dict[str, Any]:
    """
    根据产品查询商机列表
    """
    try:
        repo = get_crm_sync_repo()
        results = repo.get_opportunities_by_product(product, limit)

        return {
            "status": "success",
            "product": product,
            "count": len(results),
            "data": [r.to_dict() for r in results]
        }
    except Exception as e:
        logger.error(f"按产品查询商机失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/opportunities/by-status/{status}", summary="根据状态查询商机")
async def get_opportunities_by_status(
    status: str,
    limit: int = Query(20, ge=1, le=100, description="返回结果数量")
) -> Dict[str, Any]:
    """
    根据状态查询商机列表
    """
    try:
        repo = get_crm_sync_repo()
        results = repo.get_opportunities_by_status(status, limit)

        return {
            "status": "success",
            "opportunity_status": status,
            "count": len(results),
            "data": [r.to_dict() for r in results]
        }
    except Exception as e:
        logger.error(f"按状态查询商机失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


# ==================== 统计端点 ====================

@router.get("/statistics", summary="获取CRM统计信息")
async def get_crm_statistics() -> Dict[str, Any]:
    """
    获取CRM数据库的统计信息（客户和商机）
    """
    try:
        repo = get_crm_sync_repo()
        customer_stats = repo.get_customer_statistics()
        opportunity_stats = repo.get_opportunity_statistics()

        return {
            "status": "success",
            "database": "CRM_sync_new",
            "statistics": {
                "customers": customer_stats,
                "opportunities": opportunity_stats
            }
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")
