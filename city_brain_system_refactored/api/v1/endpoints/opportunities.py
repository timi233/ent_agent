"""
商机API端点 - AS和IPG系统 + Enterprise_QD企业档案
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from infrastructure.database.repositories.opportunities_repository import OpportunitiesRepository
from infrastructure.database.repositories.enterprise_qd_repository import EnterpriseQDRepository
from infrastructure.database.repositories.work_order_repository import WorkOrderRepository

logger = logging.getLogger(__name__)

router = APIRouter()

# 初始化仓储
opportunities_repo = OpportunitiesRepository()
enterprise_qd_repo = EnterpriseQDRepository()
work_order_repo = WorkOrderRepository()


# ==================== AS商机端点 ====================

@router.get("/as/search")
async def search_as_opportunities(
    customer_name: Optional[str] = Query(None, description="客户名称（精确或模糊匹配）"),
    keyword: Optional[str] = Query(None, description="关键词搜索（客户、产品、行业、合作伙伴、地区）"),
    partner: Optional[str] = Query(None, description="合作伙伴名称"),
    area: Optional[str] = Query(None, description="地区"),
    limit: int = Query(20, ge=1, le=100, description="返回结果数量限制")
):
    """
    搜索AS系统商机

    - **customer_name**: 根据客户名称查询（优先使用）
    - **keyword**: 关键词搜索
    - **partner**: 按合作伙伴筛选
    - **area**: 按地区筛选
    - **limit**: 返回结果数量（1-100）
    """
    try:
        # 优先级：customer_name > partner > area > keyword
        if customer_name:
            opportunities = opportunities_repo.find_as_opportunities_by_customer(customer_name, limit)
        elif partner:
            opportunities = opportunities_repo.get_as_opportunities_by_partner(partner, limit)
        elif area:
            opportunities = opportunities_repo.get_as_opportunities_by_area(area, limit)
        elif keyword:
            opportunities = opportunities_repo.search_as_opportunities(keyword, limit)
        else:
            raise HTTPException(status_code=400, detail="请提供至少一个搜索条件")

        return {
            "success": True,
            "count": len(opportunities),
            "data": [opp.to_dict() for opp in opportunities]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索AS商机失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/as/statistics")
async def get_as_statistics():
    """
    获取AS系统商机统计信息

    返回总数、独立客户数、合作伙伴数、地区数、总预算等
    """
    try:
        stats = opportunities_repo.get_as_statistics()

        return {
            "success": True,
            "data": stats
        }

    except Exception as e:
        logger.error(f"获取AS商机统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


# ==================== IPG商机端点 ====================

@router.get("/ipg/search")
async def search_ipg_clients(
    client_name: Optional[str] = Query(None, description="客户名称（精确或模糊匹配）"),
    keyword: Optional[str] = Query(None, description="关键词搜索（客户、产品、行业、代理商、省份）"),
    reseller: Optional[str] = Query(None, description="代理商名称"),
    province: Optional[str] = Query(None, description="省份"),
    limit: int = Query(20, ge=1, le=100, description="返回结果数量限制")
):
    """
    搜索IPG系统商机

    - **client_name**: 根据客户名称查询（优先使用）
    - **keyword**: 关键词搜索
    - **reseller**: 按代理商筛选
    - **province**: 按省份筛选
    - **limit**: 返回结果数量（1-100）
    """
    try:
        # 优先级：client_name > reseller > province > keyword
        if client_name:
            clients = opportunities_repo.find_ipg_clients_by_name(client_name, limit)
        elif reseller:
            clients = opportunities_repo.get_ipg_clients_by_reseller(reseller, limit)
        elif province:
            clients = opportunities_repo.get_ipg_clients_by_province(province, limit)
        elif keyword:
            clients = opportunities_repo.search_ipg_clients(keyword, limit)
        else:
            raise HTTPException(status_code=400, detail="请提供至少一个搜索条件")

        return {
            "success": True,
            "count": len(clients),
            "data": [client.to_dict() for client in clients]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索IPG商机失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/ipg/statistics")
async def get_ipg_statistics():
    """
    获取IPG系统商机统计信息

    返回总数、独立客户数、代理商数、省份数、总点数等
    """
    try:
        stats = opportunities_repo.get_ipg_statistics()

        return {
            "success": True,
            "data": stats
        }

    except Exception as e:
        logger.error(f"获取IPG商机统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


# ==================== 综合查询端点 ====================

@router.get("/search")
async def search_all_opportunities(
    company_name: str = Query(..., description="企业名称"),
    limit_per_source: int = Query(10, ge=1, le=50, description="每个数据源返回结果数量")
):
    """
    跨AS、IPG、Enterprise_QD和工单综合查询企业信息

    根据企业名称同时查询AS、IPG、Enterprise_QD和工单四个数据源

    - **company_name**: 企业名称（必填）
    - **limit_per_source**: 每个数据源返回的结果数量（1-50）
    """
    try:
        # 查询AS系统
        as_opportunities = opportunities_repo.find_as_opportunities_by_customer(
            company_name, limit_per_source
        )

        # 查询IPG系统
        ipg_clients = opportunities_repo.find_ipg_clients_by_name(
            company_name, limit_per_source
        )

        # 查询Enterprise_QD企业档案
        qd_enterprises = enterprise_qd_repo.search_by_keyword(
            company_name, limit_per_source
        )

        # 查询工单
        work_orders = work_order_repo.search_by_company_name(
            company_name, limit_per_source
        )

        return {
            "success": True,
            "company_name": company_name,
            "summary": {
                "as_count": len(as_opportunities),
                "ipg_count": len(ipg_clients),
                "qd_count": len(qd_enterprises),
                "work_order_count": len(work_orders),
                "total_count": len(as_opportunities) + len(ipg_clients) + len(qd_enterprises) + len(work_orders)
            },
            "data": {
                "as_opportunities": [opp.to_dict() for opp in as_opportunities],
                "ipg_clients": [client.to_dict() for client in ipg_clients],
                "qd_enterprises": [ent.to_dict() for ent in qd_enterprises],
                "work_orders": [order.to_dict() for order in work_orders]
            }
        }

    except Exception as e:
        logger.error(f"综合查询商机失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/statistics")
async def get_all_statistics():
    """
    获取AS和IPG系统的综合统计信息
    """
    try:
        as_stats = opportunities_repo.get_as_statistics()
        ipg_stats = opportunities_repo.get_ipg_statistics()

        return {
            "success": True,
            "data": {
                "as": as_stats,
                "ipg": ipg_stats,
                "total_opportunities": (
                    as_stats.get('total_count', 0) + ipg_stats.get('total_count', 0)
                )
            }
        }

    except Exception as e:
        logger.error(f"获取综合统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    健康检查端点
    """
    try:
        is_healthy = opportunities_repo.test_connection()

        return {
            "success": is_healthy,
            "service": "opportunities",
            "database": "feishu_crm",
            "status": "healthy" if is_healthy else "unhealthy"
        }

    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "success": False,
            "service": "opportunities",
            "database": "feishu_crm",
            "status": "unhealthy",
            "error": str(e)
        }
