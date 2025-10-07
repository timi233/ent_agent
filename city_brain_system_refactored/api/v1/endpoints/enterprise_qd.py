"""
enterprise_QD数据源的API端点
提供对青岛企业详细信息的访问
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging

from infrastructure.database.repositories.enterprise_qd_repository import EnterpriseQDRepository

logger = logging.getLogger(__name__)

router = APIRouter()

# 全局仓储实例
_enterprise_qd_repo = None


def get_enterprise_qd_repo() -> EnterpriseQDRepository:
    """获取enterprise_QD仓储实例"""
    global _enterprise_qd_repo
    if _enterprise_qd_repo is None:
        _enterprise_qd_repo = EnterpriseQDRepository()
    return _enterprise_qd_repo


@router.get("/search", summary="搜索企业")
async def search_enterprises(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, ge=1, le=100, description="返回结果数量")
) -> Dict[str, Any]:
    """
    搜索企业（支持名称、地址、行业关键词）
    """
    try:
        repo = get_enterprise_qd_repo()
        results = repo.search_by_keyword(keyword, limit)

        return {
            "status": "success",
            "count": len(results),
            "data": [r.to_dict() for r in results]
        }
    except Exception as e:
        logger.error(f"搜索企业失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/by-name/{name}", summary="根据名称查询企业")
async def get_enterprise_by_name(name: str) -> Dict[str, Any]:
    """
    根据企业名称查询详细信息
    """
    try:
        repo = get_enterprise_qd_repo()
        result = repo.find_by_name(name)

        if not result:
            raise HTTPException(status_code=404, detail=f"未找到企业: {name}")

        return {
            "status": "success",
            "data": result.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询企业失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/by-industry/{industry}", summary="根据行业查询企业")
async def get_enterprises_by_industry(
    industry: str,
    limit: int = Query(20, ge=1, le=100, description="返回结果数量")
) -> Dict[str, Any]:
    """
    根据行业查询企业列表
    """
    try:
        repo = get_enterprise_qd_repo()
        results = repo.get_by_industry(industry, limit)

        return {
            "status": "success",
            "industry": industry,
            "count": len(results),
            "data": [r.to_dict() for r in results]
        }
    except Exception as e:
        logger.error(f"按行业查询企业失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/by-region/{region}", summary="根据地区查询企业")
async def get_enterprises_by_region(
    region: str,
    limit: int = Query(20, ge=1, le=100, description="返回结果数量")
) -> Dict[str, Any]:
    """
    根据地区查询企业列表
    """
    try:
        repo = get_enterprise_qd_repo()
        results = repo.get_by_region(region, limit)

        return {
            "status": "success",
            "region": region,
            "count": len(results),
            "data": [r.to_dict() for r in results]
        }
    except Exception as e:
        logger.error(f"按地区查询企业失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/statistics", summary="获取统计信息")
async def get_statistics() -> Dict[str, Any]:
    """
    获取enterprise_QD数据库的统计信息
    """
    try:
        repo = get_enterprise_qd_repo()
        stats = repo.get_statistics()

        return {
            "status": "success",
            "database": "enterprise_QD",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")
