"""
健康检查API端点
提供系统健康状态检查功能
"""

import sys
import os
from datetime import datetime, timezone
import logging
import time
from typing import Dict, Any



from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from infrastructure.utils.datetime_utils import now_utc

from api.v1.schemas.company import HealthResponse
from api.v1.dependencies import get_container, get_request_context
from infrastructure.external.service_manager import ServiceManager
from infrastructure.database.connection import get_database_connection

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


def check_database_health() -> Dict[str, Any]:
    """检查数据库健康状态"""
    try:
        # 尝试获取数据库连接管理器
        db_connection = get_database_connection()
        if db_connection:
            # 使用正确的方法执行查询测试
            result = db_connection.execute_query("SELECT 1")
            if result is not None:
                return {
                    "status": "healthy",
                    "message": "数据库连接正常",
                    "response_time": "<100ms"
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": "数据库查询返回空结果",
                    "response_time": "error"
                }
        else:
            return {
                "status": "unhealthy",
                "message": "无法获取数据库连接",
                "response_time": "timeout"
            }
    except Exception as e:
        logger.error(f"数据库健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"数据库检查异常: {str(e)}",
            "response_time": "error"
        }


def check_external_services_health() -> Dict[str, Any]:
    """检查外部服务健康状态"""
    try:
        service_manager = ServiceManager()
        health_status = service_manager.get_all_service_health()

        # 检查是否有任何服务不健康
        unhealthy_services = [
            service for service, status in health_status.items()
            if status.get("status") != "healthy"
        ]

        if unhealthy_services:
            return {
                "status": "degraded",
                "message": f"部分外部服务异常: {', '.join(unhealthy_services)}",
                "services": health_status
            }
        else:
            return {
                "status": "healthy",
                "message": "所有外部服务正常",
                "services": health_status
            }

    except Exception as e:
        logger.error(f"外部服务健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"外部服务检查异常: {str(e)}",
            "services": {}
        }


def check_system_resources() -> Dict[str, Any]:
    """检查系统资源使用情况"""
    try:
        import psutil

        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)

        # 内存使用率
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100

        # 判断资源状态
        if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
            status = "unhealthy"
            message = "系统资源使用率过高"
        elif cpu_percent > 70 or memory_percent > 70 or disk_percent > 70:
            status = "degraded"
            message = "系统资源使用率较高"
        else:
            status = "healthy"
            message = "系统资源使用正常"

        return {
            "status": status,
            "message": message,
            "details": {
                "cpu_usage": f"{cpu_percent:.1f}%",
                "memory_usage": f"{memory_percent:.1f}%",
                "disk_usage": f"{disk_percent:.1f}%"
            }
        }

    except ImportError:
        logger.warning("psutil模块未安装，跳过系统资源检查")
        return {
            "status": "unknown",
            "message": "无法检查系统资源（缺少psutil模块）",
            "details": {}
        }
    except Exception as e:
        logger.error(f"系统资源检查失败: {str(e)}")
        return {
            "status": "error",
            "message": f"系统资源检查异常: {str(e)}",
            "details": {}
        }


@router.get("", response_model=HealthResponse)
@router.get("/", response_model=HealthResponse)
async def health_check(
    request_context: Dict[str, Any] = Depends(get_request_context)
):
    """
    基础健康检查

    返回服务的基本健康状态
    """
    request_id = request_context["request_id"]

    try:
        logger.info(f"[{request_id}] 执行基础健康检查")

        current_time = now_utc()
        health_data = HealthResponse(
            status="healthy",
            timestamp=current_time,
            version="1.0.0",
            services={
                "api": "healthy",
                "timestamp": current_time.isoformat()
            }
        )

        logger.info(f"[{request_id}] 基础健康检查完成: 正常")
        return health_data

    except Exception as e:
        logger.error(f"[{request_id}] 基础健康检查异常: {str(e)}")

        return HealthResponse(
            status="error",
            timestamp=now_utc(),
            version="1.0.0",
            services={
                "api": "error",
                "error": str(e)
            }
        )


@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health_check(
    request_context: Dict[str, Any] = Depends(get_request_context)
):
    """
    详细健康检查

    返回包括数据库、外部服务和系统资源的详细健康状态
    """
    request_id = request_context["request_id"]
    start_time = time.time()

    try:
        logger.info(f"[{request_id}] 执行详细健康检查")

        # 并行检查各个组件
        db_health = check_database_health()
        external_health = check_external_services_health()
        system_health = check_system_resources()

        # 综合判断整体状态
        all_statuses = [
            db_health["status"],
            external_health["status"],
            system_health["status"]
        ]

        if "unhealthy" in all_statuses:
            overall_status = "unhealthy"
        elif "degraded" in all_statuses or "error" in all_statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        response_time = round((time.time() - start_time) * 1000, 2)
        current_time = now_utc()

        detailed_health = {
            "status": overall_status,
            "timestamp": current_time.isoformat(),
            "version": "1.0.0",
            "response_time_ms": response_time,
            "services": {
                "api": "healthy",
                "database": db_health,
                "external_services": external_health,
                "system_resources": system_health
            }
        }

        logger.info(f"[{request_id}] 详细健康检查完成: {overall_status} ({response_time}ms)")
        return detailed_health

    except Exception as e:
        logger.error(f"[{request_id}] 详细健康检查异常: {str(e)}", exc_info=True)

        return {
            "status": "error",
            "timestamp": now_utc().isoformat(),
            "version": "1.0.0",
            "response_time_ms": round((time.time() - start_time) * 1000, 2),
            "error": str(e),
            "services": {
                "api": "error",
                "error_details": str(e)
            }
        }


@router.get("/ready", response_model=Dict[str, Any])
async def readiness_check(
    request_context: Dict[str, Any] = Depends(get_request_context)
):
    """
    就绪检查

    检查服务是否已准备好接收流量（用于Kubernetes就绪探针）
    """
    request_id = request_context["request_id"]

    try:
        logger.info(f"[{request_id}] 执行就绪检查")

        # 检查数据库连接
        db_health = check_database_health()

        # 检查关键外部服务
        external_health = check_external_services_health()

        # 判断是否就绪
        if (db_health["status"] == "healthy" and
            external_health["status"] in ["healthy", "degraded"]):
            ready_status = True
            status_code = 200
        else:
            ready_status = False
            status_code = 503  # Service Unavailable

        readiness_data = {
            "ready": ready_status,
            "status": "ready" if ready_status else "not_ready",
            "timestamp": now_utc().isoformat(),
            "checks": {
                "database": db_health,
                "external_services": external_health
            }
        }

        logger.info(f"[{request_id}] 就绪检查完成: {'就绪' if ready_status else '未就绪'}")

        return JSONResponse(
            content=readiness_data,
            status_code=status_code
        )

    except Exception as e:
        logger.error(f"[{request_id}] 就绪检查异常: {str(e)}")

        return JSONResponse(
            content={
                "ready": False,
                "status": "error",
                "timestamp": now_utc().isoformat(),
                "error": str(e)
            },
            status_code=503
        )


@router.get("/live", response_model=Dict[str, Any])
async def liveness_check(
    request_context: Dict[str, Any] = Depends(get_request_context)
):
    """
    存活检查

    检查服务是否存活（用于Kubernetes存活探针）
    """
    request_id = request_context["request_id"]

    try:
        logger.info(f"[{request_id}] 执行存活检查")

        # 简单的存活检查 - 只要能响应请求就说明服务存活
        liveness_data = {
            "alive": True,
            "status": "alive",
            "timestamp": now_utc().isoformat(),
            "uptime": "unknown"  # 可以扩展为实际的服务运行时间
        }

        logger.info(f"[{request_id}] 存活检查完成: 存活")
        return liveness_data

    except Exception as e:
        logger.error(f"[{request_id}] 存活检查异常: {str(e)}")

        # 即使检查异常，也要返回500错误表示服务不存活
        return JSONResponse(
            content={
                "alive": False,
                "status": "error",
                "timestamp": now_utc().isoformat(),
                "error": str(e)
            },
            status_code=500
        )
