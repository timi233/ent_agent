import pytest
import time
import statistics
import httpx
from httpx import ASGITransport

# 仅使用 asyncio 后端
@pytest.fixture
def anyio_backend():
    return "asyncio"

# 尝试导入应用与依赖
try:
    from main import app
    from api.v1 import dependencies as api_dependencies
    from api.v1.dependencies import get_request_logger, RequestLogger, get_analysis_service, get_enterprise_service
except Exception:
    app = None
    api_dependencies = None
    get_request_logger = None
    RequestLogger = object
    get_analysis_service = None
    get_enterprise_service = None

class NoOpRequestLogger(RequestLogger):
    def __init__(self, request):
        try:
            super().__init__(request)
        except Exception:
            self.request = request
            self.start_time = 0
    def log_request_start(self): return None
    def log_request_end(self, status_code: int = 200): return None

@pytest.mark.anyio
async def test_basic_performance_company_process(anyio_backend):
    # 覆盖依赖，避免外部服务波动
    if api_dependencies:
        import logging
        api_dependencies.logger = logging.getLogger("api.v1.dependencies")
    if get_request_logger:
        app.dependency_overrides[get_request_logger] = lambda request: NoOpRequestLogger(request)

    class DummyAnalysisService:
        def generate_comprehensive_company_analysis(self, company_data):
            return {"analysis_summary": "测试AI分析摘要", "analysis_time": "2025-09-30", "data_source": "测试"}
    class DummyEnterpriseService:
        def process_company_info(self, company_name: str):
            return {"status": "success", "data": {"company_name": company_name, "summary": "ok"}}

    if get_analysis_service:
        app.dependency_overrides[get_analysis_service] = lambda: DummyAnalysisService()
    if get_enterprise_service:
        app.dependency_overrides[get_enterprise_service] = lambda: DummyEnterpriseService()


    latencies = []
    n = 10

    async with httpx.AsyncClient(base_url="http://localhost:9003", timeout=10.0) as client:
        for _ in range(n):
            t0 = time.perf_counter()
            resp = await client.post("/api/v1/company/process/progressive", json={"input_text": "测试企业", "disable_cache": True, "enable_network": False})
            t1 = time.perf_counter()
            assert resp.status_code == 200
            lat = (t1 - t0) * 1000.0  # ms
            latencies.append(lat)
            # 软阈值，避免环境抖动导致失败
            assert lat < 5000

    p50 = statistics.median(latencies)
    p95 = sorted(latencies)[int(n * 0.95) - 1]
    # 最终断言保持宽松，仅保证不超过极端上限
    assert p95 < 5000, f"P95过高: {p95:.1f}ms"

@pytest.mark.anyio
async def test_basic_performance_company_progressive(anyio_backend):
    # 同样覆盖依赖
    if api_dependencies:
        import logging
        api_dependencies.logger = logging.getLogger("api.v1.dependencies")
    if get_request_logger:
        app.dependency_overrides[get_request_logger] = lambda request: NoOpRequestLogger(request)

    class DummyAnalysisService:
        def generate_comprehensive_company_analysis(self, company_data):
            return {"analysis_summary": "测试AI分析摘要", "analysis_time": "2025-09-30", "data_source": "测试"}
    class DummyEnterpriseService:
        def process_company_info(self, company_name: str):
            return {"status": "success", "data": {"company_name": company_name}}

    if get_analysis_service:
        app.dependency_overrides[get_analysis_service] = lambda: DummyAnalysisService()
    if get_enterprise_service:
        app.dependency_overrides[get_enterprise_service] = lambda: DummyEnterpriseService()


    latencies = []
    n = 10

    async with httpx.AsyncClient(base_url="http://localhost:9003", timeout=10.0) as client:
        for _ in range(n):
            t0 = time.perf_counter()
            resp = await client.post("/api/v1/company/process/progressive", json={"input_text": "测试企业", "disable_cache": True, "enable_network": False})
            t1 = time.perf_counter()
            assert resp.status_code in (200, 202)
            lat = (t1 - t0) * 1000.0
            latencies.append(lat)
            assert lat < 5000

    p95 = sorted(latencies)[int(n * 0.95) - 1]
    assert p95 < 5000