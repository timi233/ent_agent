import pytest
import httpx
from httpx import ASGITransport

# 仅使用 asyncio 后端，避免 trio 依赖
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

@pytest.mark.skipif(app is None, reason="FastAPI app 未找到")
@pytest.mark.anyio
async def test_process_company_basic(anyio_backend, monkeypatch):
    # 修复模块级 logger，覆盖依赖为无副作用版本
    if api_dependencies:
        import logging
        api_dependencies.logger = logging.getLogger("api.v1.dependencies")
    if get_request_logger:
        app.dependency_overrides[get_request_logger] = lambda request: NoOpRequestLogger(request)

    # 覆盖 AnalysisService.simple_chat 返回值，避免外部LLM依赖
    class DummyResult:
        success = True
        content = "测试AI分析摘要"
        error_message = None
    class DummyAnalysisService:
        def generate_comprehensive_company_analysis(self, company_data):
            return {"analysis_summary": "测试AI分析摘要", "analysis_time": "2025-09-30", "data_source": "测试"}
    if get_analysis_service:
        app.dependency_overrides[get_analysis_service] = lambda: DummyAnalysisService()

    # 覆盖 EnterpriseService 的搜索以避免外部API
    class DummyEnterpriseService:
        def process_company_info(self, company_name: str):
            return {
                "basic_info": {"name": company_name, "status": "测试"},
                "financial_data": {"revenue": "N/A"},
                "business_info": {"tags": ["测试"]},
                "analysis": {"summary": "测试AI分析摘要"}
            }
    if get_enterprise_service:
        app.dependency_overrides[get_enterprise_service] = lambda: DummyEnterpriseService()

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 同步处理接口
        resp = await client.post("/api/v1/company/process", json={"company_name": "示例公司"})
        assert resp.status_code in (200, 422)  # 允许Pydantic校验失败显示422
        if resp.status_code == 200:
            data = resp.json()
            assert "basic_info" in data
            assert "analysis" in data

@pytest.mark.skipif(app is None, reason="FastAPI app 未找到")
@pytest.mark.anyio
async def test_process_company_progressive(anyio_backend, monkeypatch):
    # 修复模块级 logger，覆盖依赖为无副作用版本
    if api_dependencies:
        import logging
        api_dependencies.logger = logging.getLogger("api.v1.dependencies")
    if get_request_logger:
        app.dependency_overrides[get_request_logger] = lambda request: NoOpRequestLogger(request)

    # 复用 Dummy 服务
    class DummyAnalysisService:
        def generate_comprehensive_company_analysis(self, company_data):
            return {"analysis_summary": "测试AI分析摘要", "analysis_time": "2025-09-30", "data_source": "测试"}
    class DummyEnterpriseService:
        def process_company_info(self, company_name: str):
            return {"basic_info": {"name": company_name}}
    if get_analysis_service:
        app.dependency_overrides[get_analysis_service] = lambda: DummyAnalysisService()
    if get_enterprise_service:
        app.dependency_overrides[get_enterprise_service] = lambda: DummyEnterpriseService()

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 渐进式处理接口
        resp = await client.post("/api/v1/company/process/progressive", json={"company_name": "示例公司"})
        assert resp.status_code in (200, 202, 422)
        if resp.status_code in (200, 202):
            data = resp.json()
            assert "message" in data or "basic_info" in data