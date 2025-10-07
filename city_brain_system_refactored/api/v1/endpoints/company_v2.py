"""
企业相关API端点 V2版本
使用重构后的EnterpriseServiceRefactored
提供更清晰的职责分离和更好的可维护性
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from api.v1.schemas.company import (
    CompanyRequest,
    CompanyResponse,
    ErrorResponse
)
from api.v1.dependencies import (
    get_enterprise_service_refactored,
    get_request_context
)
from domain.services.enterprise_service_refactored import EnterpriseServiceRefactored
from infrastructure.utils.datetime_utils import now_utc

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v2/company", tags=["company-v2"])


@router.post("/process", response_model=CompanyResponse)
async def process_company_v2(
    request: CompanyRequest,
    service: EnterpriseServiceRefactored = Depends(get_enterprise_service_refactored),
    context: dict = Depends(get_request_context)
):
    """
    处理企业信息（V2版本 - 使用重构后的服务）

    **改进点**:
    - 使用处理器模式，职责更清晰
    - 更好的错误处理和日志记录
    - 更易于测试和维护

    **流程**:
    1. 企业信息处理器：提取和清洗企业名称
    2. 数据增强器：补充和优化企业数据
    3. 企业分析器：生成综合分析报告
    """
    try:
        request_id = context.get('request_id', 'unknown')
        client_ip = context.get('client_ip', 'unknown')

        logger.info(
            f"[{request_id}] V2企业信息处理请求: {request.input_text}, "
            f"client_ip={client_ip}"
        )

        # 调用重构后的服务
        result = service.process_company_info(request.input_text)

        # 记录请求日志
        context.get('request_logger').log_request_end(
            status_code=200 if result.get('status') == 'success' else 400
        )

        if result.get('status') == 'error':
            logger.warning(
                f"[{request_id}] V2企业信息处理失败: {result.get('message')}"
            )
            return JSONResponse(
                status_code=400,
                content=jsonable_encoder({
                    "status": "error",
                    "message": result.get('message', '处理失败'),
                    "timestamp": now_utc(),
                    "request_id": request_id
                })
            )

        logger.info(
            f"[{request_id}] V2企业信息处理成功: "
            f"{result.get('data', {}).get('company_name', 'unknown')}"
        )

        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "status": "success",
                "data": result.get('data', {}),
                "source": result.get('source', 'unknown'),
                "timestamp": now_utc(),
                "request_id": request_id,
                "version": "v2"
            })
        )

    except Exception as e:
        logger.error(
            f"[{context.get('request_id', 'unknown')}] V2企业信息处理异常: {e}",
            exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder({
                "status": "error",
                "message": "服务器内部错误",
                "timestamp": now_utc(),
                "request_id": context.get('request_id', 'unknown')
            })
        )


@router.post("/basic-info", response_model=CompanyResponse)
async def get_basic_info_v2(
    request: CompanyRequest,
    service: EnterpriseServiceRefactored = Depends(get_enterprise_service_refactored),
    context: dict = Depends(get_request_context)
):
    """
    获取企业基础信息（V2版本）

    只返回基础信息（名称、地址、行业、地区），不包含分析报告
    适用于需要快速获取基本信息的场景
    """
    try:
        request_id = context.get('request_id', 'unknown')
        logger.info(f"[{request_id}] V2获取企业基础信息: {request.input_text}")

        result = service.get_company_basic_info(request.input_text)

        context.get('request_logger').log_request_end(
            status_code=200 if result.get('status') == 'success' else 400
        )

        if result.get('status') == 'error':
            return JSONResponse(
                status_code=400,
                content=jsonable_encoder({
                    "status": "error",
                    "message": result.get('message', '获取失败'),
                    "timestamp": now_utc(),
                    "request_id": request_id
                })
            )

        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "status": "success",
                "data": result.get('data', {}),
                "timestamp": now_utc(),
                "request_id": request_id,
                "version": "v2"
            })
        )

    except Exception as e:
        logger.error(
            f"[{context.get('request_id', 'unknown')}] V2获取基础信息异常: {e}",
            exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder({
                "status": "error",
                "message": "服务器内部错误",
                "timestamp": now_utc(),
                "request_id": context.get('request_id', 'unknown')
            })
        )


@router.get("/search/{company_name}")
async def search_company_v2(
    company_name: str,
    service: EnterpriseServiceRefactored = Depends(get_enterprise_service_refactored),
    context: dict = Depends(get_request_context)
):
    """
    搜索本地数据库中的企业（V2版本）

    Returns:
        - found: bool - 是否找到
        - data: dict - 企业数据（如果找到）
        - message: str - 消息
    """
    try:
        request_id = context.get('request_id', 'unknown')
        logger.info(f"[{request_id}] V2搜索企业: {company_name}")

        result = service.search_local_database(company_name)

        context.get('request_logger').log_request_end(200)

        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "status": "success",
                "found": result.get('found', False),
                "data": result.get('data'),
                "message": result.get('message', ''),
                "timestamp": now_utc(),
                "request_id": request_id,
                "version": "v2"
            })
        )

    except Exception as e:
        logger.error(
            f"[{context.get('request_id', 'unknown')}] V2搜索企业异常: {e}",
            exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder({
                "status": "error",
                "message": "服务器内部错误",
                "timestamp": now_utc(),
                "request_id": context.get('request_id', 'unknown')
            })
        )


@router.get("/health")
async def health_check_v2():
    """
    V2服务健康检查

    Returns:
        - status: str - 服务状态
        - version: str - API版本
        - features: list - 可用功能列表
    """
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "status": "healthy",
            "version": "v2",
            "timestamp": now_utc(),
            "features": [
                "enterprise_processor",
                "enterprise_enhancer",
                "enterprise_analyzer",
                "refactored_architecture"
            ],
            "architecture": "Clean Architecture with Processor Pattern"
        })
    )
