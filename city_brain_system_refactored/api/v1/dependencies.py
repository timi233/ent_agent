"""
API依赖注入模块
使用dependency-injector管理服务依赖关系（重构版）
提供通用的依赖项和中间件
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import time
import logging
from dependency_injector import containers, providers

from domain.services.enterprise_service import EnterpriseService
from domain.services.enterprise_service_refactored import EnterpriseServiceRefactored
from domain.services.data_enhancement_service import DataEnhancementService
from domain.services.analysis_service import AnalysisService
from domain.services.search_service import SearchService
from infrastructure.database.repositories.customer_repository import CustomerRepository

# 配置日志
logger = logging.getLogger(__name__)

# 安全认证（可选）
security = HTTPBearer(auto_error=False)


class Container(containers.DeclarativeContainer):
    """
    依赖注入容器
    使用dependency-injector管理所有服务依赖
    """

    # 配置
    config = providers.Configuration()

    # Repository层（工厂模式）
    customer_repository = providers.Factory(CustomerRepository)

    # 领域服务层 - 基础服务（单例）
    search_service = providers.Singleton(SearchService)
    data_enhancement_service = providers.Singleton(DataEnhancementService)
    analysis_service = providers.Singleton(AnalysisService)

    # 领域服务层 - 企业服务（工厂模式，每次请求创建新实例）
    enterprise_service = providers.Factory(
        EnterpriseService,
        search_service=search_service,
        data_enhancement_service=data_enhancement_service,
        analysis_service=analysis_service,
        customer_repository=customer_repository
    )

    # 领域服务层 - 重构后的企业服务（工厂模式）
    enterprise_service_refactored = providers.Factory(
        EnterpriseServiceRefactored,
        search_service=search_service,
        data_enhancement_service=data_enhancement_service,
        analysis_service=analysis_service,
        customer_repository=customer_repository
    )


# 全局容器实例
_container = Container()


def get_container() -> Container:
    """获取依赖注入容器"""
    return _container


def get_enterprise_service() -> EnterpriseService:
    """获取企业服务依赖（FastAPI Depends用）"""
    return _container.enterprise_service()


def get_enterprise_service_refactored() -> EnterpriseServiceRefactored:
    """获取重构后的企业服务依赖（FastAPI Depends用）"""
    return _container.enterprise_service_refactored()


def get_data_enhancement_service() -> DataEnhancementService:
    """获取数据增强服务依赖"""
    return _container.data_enhancement_service()


def get_analysis_service() -> AnalysisService:
    """获取分析服务依赖"""
    return _container.analysis_service()


def get_search_service() -> SearchService:
    """获取搜索服务依赖"""
    return _container.search_service()


def get_customer_repository() -> CustomerRepository:
    """获取客户Repository依赖"""
    return _container.customer_repository()


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    获取当前用户（可选的认证中间件）
    目前返回匿名用户，后续可以扩展为真实的用户认证
    """
    # 这里可以实现JWT token验证或其他认证逻辑
    # 目前返回匿名用户
    return {"user_id": "anonymous", "username": "anonymous"}


class RequestLogger:
    """请求日志记录器"""
    
    def __init__(self, request: Request):
        self.request = request
        self.start_time = time.time()
    
    def log_request_start(self):
        """记录请求开始"""
        logger.info(f"API请求开始: {self.request.method} {self.request.url}")
    
    def log_request_end(self, status_code: int = 200):
        """记录请求结束"""
        duration = time.time() - self.start_time
        logger.info(f"API请求完成: {self.request.method} {self.request.url} - {status_code} - {duration:.3f}s")


def get_request_logger(request: Request) -> RequestLogger:
    """获取请求日志记录器依赖"""
    request_logger = RequestLogger(request)
    request_logger.log_request_start()
    return request_logger


def validate_request_size(request: Request):
    """验证请求大小"""
    content_length = request.headers.get("content-length")
    if content_length:
        content_length = int(content_length)
        max_size = 10 * 1024 * 1024  # 10MB
        if content_length > max_size:
            raise HTTPException(
                status_code=413,
                detail="请求体过大，最大支持10MB"
            )


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    # 检查代理头
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # 返回直接连接的IP
    return request.client.host if request.client else "unknown"


class RateLimiter:
    """简单的速率限制器"""
    
    def __init__(self):
        self.requests = {}
        self.max_requests = 100  # 每分钟最大请求数
        self.window_size = 60    # 时间窗口（秒）
    
    def is_allowed(self, client_ip: str) -> bool:
        """检查是否允许请求"""
        current_time = time.time()
        
        # 清理过期记录
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < self.window_size
            ]
        else:
            self.requests[client_ip] = []
        
        # 检查请求数量
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        
        # 记录当前请求
        self.requests[client_ip].append(current_time)
        return True


# 全局速率限制器实例
_rate_limiter = RateLimiter()


def check_rate_limit(request: Request):
    """检查速率限制依赖"""
    client_ip = get_client_ip(request)
    
    if not _rate_limiter.is_allowed(client_ip):
        logger.warning(f"速率限制触发: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="请求过于频繁，请稍后再试"
        )
    
    return client_ip


def get_request_context(
    request: Request,
    client_ip: str = Depends(check_rate_limit),
    request_logger: RequestLogger = Depends(get_request_logger),
    current_user: dict = Depends(get_current_user)
):
    """获取请求上下文信息"""
    return {
        "request": request,
        "client_ip": client_ip,
        "request_logger": request_logger,
        "current_user": current_user,
        "request_id": f"{int(time.time())}-{hash(client_ip) % 10000}"
    }
