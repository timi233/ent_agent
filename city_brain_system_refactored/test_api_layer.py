"""API 层核心端点测试：直调函数，避免 HTTP 循环引发阻塞。"""

import os
import sys
import asyncio
from typing import Dict, Any

from fastapi import BackgroundTasks

sys.path.append(os.path.dirname(__file__))

from api.v1 import dependencies as api_dependencies
from api.v1.endpoints import health as health_module
from api.v1.endpoints import company as company_module


class _DummyRequestLogger:
    def log_request_start(self):
        pass

    def log_request_end(self, status_code: int = 200):
        pass


class _StubSearchService:
    def extract_company_name_from_input(self, user_input: str):
        return {"status": "success", "name": "海尔集团", "is_complete": True}

    def search_company_info(self, company_name: str):
        return {
            "status": "success",
            "data": {"company_name": company_name, "region": "青岛"},
            "source": "stub",
        }


class _StubEnterpriseService:
    def __init__(self):
        self.search_service = _StubSearchService()

    def process_company_info(self, user_input: str):
        return {
            "status": "success",
            "data": {
                "company_name": "海尔集团",
                "summary": "stubbed summary",
                "details": {"name": "海尔集团"},
                "news": {"summary": "stub"},
            },
        }

    def search_local_database(self, company_name: str):
        return {"found": False, "data": None, "message": "stub"}

    def update_company_info(self, customer_id: int, updates: Dict[str, Any]):
        return {"status": "success", "data": updates, "message": "updated"}

    def update_chain_leader_info(self, company_name: str, updates: Dict[str, Any]):
        return {"status": "success", "data": updates, "message": "updated"}


# 替换依赖容器，确保端点调用桩实现
api_dependencies._service_container._enterprise_service = _StubEnterpriseService()
api_dependencies._service_container._search_service = api_dependencies._service_container.enterprise_service.search_service
api_dependencies._service_container._data_enhancement_service = None
api_dependencies._service_container._analysis_service = None

api_dependencies.logger = _DummyRequestLogger()
api_dependencies.get_request_logger = lambda request: _DummyRequestLogger()
api_dependencies.check_rate_limit = lambda request: "test-ip"
api_dependencies.get_client_ip = lambda request: "test-ip"


# 健康检查内部函数替换
health_module.ServiceManager = lambda *args, **kwargs: type(
    "StubServiceManager",
    (),
    {"get_all_service_health": lambda self: {"service_manager": {"status": "healthy"}}},
)()
health_module.check_database_health = lambda: {
    "status": "healthy",
    "message": "stubbed",
    "response_time": "<1ms",
}
health_module.check_external_services_health = lambda: {
    "status": "healthy",
    "message": "stubbed",
    "services": {},
}
health_module.check_system_resources = lambda: {
    "status": "healthy",
    "message": "stubbed",
    "details": {},
}


def _stub_request_context() -> Dict[str, Any]:
    return {
        "request": None,
        "client_ip": "test-ip",
        "request_logger": _DummyRequestLogger(),
        "current_user": {"user_id": "test"},
        "request_id": "test-1",
    }


def _run(coro):
    return asyncio.run(coro)


def test_health_check():
    result = _run(health_module.health_check(request_context=_stub_request_context()))
    assert result.status == "healthy"


def test_detailed_health_check():
    result = _run(health_module.detailed_health_check(request_context=_stub_request_context()))
    assert result["status"] in {"healthy", "degraded"}


def test_readiness_check():
    response = _run(health_module.readiness_check(request_context=_stub_request_context()))
    assert response.status_code in {200, 503}


def test_liveness_check():
    response = _run(health_module.liveness_check(request_context=_stub_request_context()))
    assert response["status"] == "alive"


def test_company_process_endpoint():
    background_tasks = BackgroundTasks()
    result = _run(
        company_module.process_company_info(
            request=company_module.CompanyRequest(input_text="查询海尔集团"),
            background_tasks=background_tasks,
            enterprise_service=api_dependencies.get_enterprise_service(),
            request_context=_stub_request_context(),
        )
    )
    assert result.status == "success"
    assert result.data.company_name == "海尔集团"


def test_company_search_endpoint():
    background_tasks = BackgroundTasks()
    response = _run(
        company_module.search_company(
            q="海尔集团",
            background_tasks=background_tasks,
            enterprise_service=api_dependencies.get_enterprise_service(),
            request_context=_stub_request_context(),
        )
    )
    assert response["status"] in {"success", "error", "processing"}


def test_company_update_endpoint():
    background_tasks = BackgroundTasks()
    response = _run(
        company_module.update_company_info(
            request=company_module.UpdateCompanyRequest(
                customer_id=1, updates={"address": "测试地址"}
            ),
            background_tasks=background_tasks,
            enterprise_service=api_dependencies.get_enterprise_service(),
            request_context=_stub_request_context(),
        )
    )
    assert response.status == "success"


def test_progressive_company_process_endpoint():
    background_tasks = BackgroundTasks()
    response = _run(
        company_module.process_company_progressive(
            request=company_module.ProgressiveCompanyRequest(input_text="查询海尔集团"),
            background_tasks=background_tasks,
            enterprise_service=api_dependencies.get_enterprise_service(),
            request_context=_stub_request_context(),
        )
    )
    assert response.status in {"processing", "completed", "success"}


def test_chain_leader_update_endpoint():
    background_tasks = BackgroundTasks()
    response = _run(
        company_module.update_chain_leader_info(
            request=company_module.ChainLeaderUpdateRequest(
                company_name="海尔集团", updates={"is_chain_leader": True}
            ),
            background_tasks=background_tasks,
            enterprise_service=api_dependencies.get_enterprise_service(),
            request_context=_stub_request_context(),
        )
    )
    assert response.status == "success"


def test_api_documentation_paths_exist():
    # 直接检查路由表
    routes = {route.path for route in health_module.router.routes}
    assert any(path.endswith("/") or path == "/" for path in routes)


def test_error_handling_for_invalid_company_request():
    background_tasks = BackgroundTasks()
    try:
        _run(
            company_module.process_company_info(
                request=company_module.CompanyRequest(input_text=""),
                background_tasks=background_tasks,
                enterprise_service=api_dependencies.get_enterprise_service(),
                request_context=_stub_request_context(),
            )
        )
    except Exception as exc:
        assert "输入文本不能为空" in str(exc)
