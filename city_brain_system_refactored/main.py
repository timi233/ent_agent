"""
城市大脑企业信息处理系统 - FastAPI应用主文件

这是系统的入口文件，负责启动FastAPI应用并配置所有路由
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from infrastructure.utils.datetime_utils import now_utc

# 加载环境变量
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from api import api_router
from config.simple_settings import load_settings

# 配置日志
logger = logging.getLogger(__name__)

# 全局设置
settings = load_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    在应用启动和关闭时执行相应的操作
    """
    # 启动时的操作
    logger.info("🚀 城市大脑企业信息处理系统正在启动...")

    try:
        # 检查数据库连接
        from infrastructure.database.connection import test_connection
        db_test_result = test_connection()
        if db_test_result:
            logger.info("✅ 数据库连接测试通过")
        else:
            logger.warning("⚠️  数据库连接测试失败，但服务仍将继续启动")
    except Exception as e:
        logger.warning(f"⚠️  数据库连接测试异常: {str(e)}")

    try:
        # 检查外部服务
        from infrastructure.external.service_manager import ServiceManager
        service_manager = ServiceManager()
        health_status = service_manager.get_all_service_health()
        healthy_services = sum(1 for status in health_status.values() if status.get("status") == "healthy")
        total_services = len(health_status)
        logger.info(f"✅ 外部服务检查完成: {healthy_services}/{total_services} 个服务正常")
    except Exception as e:
        logger.warning(f"⚠️  外部服务检查异常: {str(e)}")

    logger.info("✅ 应用启动完成，准备接收请求")

    yield  # 应用运行期间

    # 关闭时的操作
    logger.info("🛑 应用正在关闭...")

    try:
        # 关闭数据库连接池
        from infrastructure.database.connection import close_all_connections
        close_all_connections()
        logger.info("✅ 数据库连接池已关闭")
    except Exception as e:
        logger.warning(f"⚠️  关闭数据库连接池时出错: {str(e)}")

    logger.info("✅ 应用已完全关闭")


# 创建FastAPI应用实例
app = FastAPI(
    title="城市大脑企业信息处理系统",
    description="基于AI的企业信息搜索、分析和增强服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "服务器内部错误",
            "error_code": "INTERNAL_ERROR",
            "timestamp": now_utc().isoformat()
        }
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404错误处理"""
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "请求的接口不存在",
            "error_code": "NOT_FOUND",
            "timestamp": now_utc().isoformat()
        }
    )


@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    """405错误处理"""
    return JSONResponse(
        status_code=405,
        content={
            "status": "error",
            "message": "请求方法不被允许",
            "error_code": "METHOD_NOT_ALLOWED",
            "timestamp": now_utc().isoformat()
        }
    )


# 请求中间件
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """为每个请求添加请求ID"""
    import time
    request_id = f"{int(time.time())}-{hash(request.client.host if request.client else 'unknown') % 10000}"

    # 将请求ID添加到请求状态中
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


# 根路径
@app.get("/")
async def root():
    """根路径 - 系统信息"""
    return {
        "name": "城市大脑企业信息处理系统",
        "version": "1.0.0",
        "description": "基于AI的企业信息搜索、分析和增强服务",
        "status": "running",
        "timestamp": now_utc().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/api/v1/health",
            "api_v1": "/api/v1"
        }
    }


# 包含API路由
app.include_router(api_router, prefix="/api")


# 启动函数
def main():
    """应用启动函数"""
    logger.info("正在启动城市大脑企业信息处理系统...")

    # 获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", os.getenv("PORT", 8000)))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")

    logger.info(f"配置信息: HOST={host}, PORT={port}, RELOAD={reload}, LOG_LEVEL={log_level}")

    # 启动服务
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    )


if __name__ == "__main__":
    main()
