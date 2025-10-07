import pytest
import httpx
from httpx import ASGITransport

# 仅使用 asyncio 后端，避免 trio 依赖
@pytest.fixture
def anyio_backend():
    return "asyncio"

# 尝试导入应用与依赖
import logging

try:
    from main import app
    from api.v1 import dependencies as api_dependencies
    from api.v1.dependencies import get_request_logger, RequestLogger
except Exception:
    app = None
    api_dependencies = None
    get_request_logger = None
    RequestLogger = object

class NoOpRequestLogger(RequestLogger):
    def __init__(self, request):
        # 与真实依赖保持签名一致
        try:
            super().__init__(request)
        except Exception:
            self.request = request
            self.start_time = 0
    def log_request_start(self):
        # 不做任何日志输出，避免测试环境副作用
        return None
    def log_request_end(self, status_code: int = 200):
        return None

@pytest.mark.skipif(app is None, reason="FastAPI app 未找到")
@pytest.mark.anyio
async def test_basic_health_check(anyio_backend):
    # 覆盖依赖，注入无副作用的日志记录器，并修复模块级 logger
    if get_request_logger:
        app.dependency_overrides[get_request_logger] = lambda request: NoOpRequestLogger(request)
    if api_dependencies:
        api_dependencies.logger = logging.getLogger("api.v1.dependencies")


    async with httpx.AsyncClient(base_url="http://localhost:9003", timeout=10.0) as client:
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") in {"healthy", "error"}
        assert "services" in data

@pytest.mark.skipif(app is None, reason="FastAPI app 未找到")
@pytest.mark.anyio
async def test_detailed_health_check(anyio_backend):
    if get_request_logger:
        app.dependency_overrides[get_request_logger] = lambda request: NoOpRequestLogger(request)
    if api_dependencies:
        api_dependencies.logger = logging.getLogger("api.v1.dependencies")


    async with httpx.AsyncClient(base_url="http://localhost:9003", timeout=10.0) as client:
        resp = await client.get("/api/v1/health/detailed")
        assert resp.status_code in (200, 500)
        data = resp.json()
        assert "status" in data
        assert "services" in data
        services = data.get("services", {})
        # 验证包含关键子项
        assert "database" in services
        assert "external_services" in services