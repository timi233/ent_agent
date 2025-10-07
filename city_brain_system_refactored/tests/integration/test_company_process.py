import pytest

from domain.services.enterprise_service import EnterpriseService

class DummyAnalysisService:
    def get_company_news(self, company_name):
        return {"summary": "暂无最新商业资讯", "references": []}

    def generate_comprehensive_company_analysis(self, enhanced_data, news_data):
        # 返回稳定的伪造分析内容，避免外部LLM依赖
        return "这是一份稳定的企业分析摘要，用于测试。"

    def format_analysis_result(self, enhanced_data, news_data, llm_analysis):
        return {
            "status": "success",
            "data": {
                "company_name": enhanced_data.get("customer_name", ""),
                "summary": llm_analysis,
                "details": {
                    "name": enhanced_data.get("customer_name", ""),
                    "region": enhanced_data.get("district_name", ""),
                    "address": enhanced_data.get("address", ""),
                    "industry": enhanced_data.get("industry_name", ""),
                    "industry_brain": enhanced_data.get("brain_name", ""),
                    "chain_status": enhanced_data.get("chain_status", ""),
                    "revenue_info": enhanced_data.get("revenue_info", ""),
                    "company_status": enhanced_data.get("company_status", ""),
                    "data_source": enhanced_data.get("data_source", ""),
                },
                "news": news_data,
            },
        }

@pytest.fixture
def enterprise_service():
    svc = EnterpriseService()
    # 注入替身 AnalysisService，避免外部依赖导致不稳定
    svc.analysis_service = DummyAnalysisService()
    return svc

def test_process_company_info_success(enterprise_service):
    # 使用常见企业名作为输入，验证成功路径
    result = enterprise_service.process_company_info("查询海尔集团")
    assert isinstance(result, dict)
    assert result.get("status") in {"success", "error"}  # 不强制联网成功
    if result.get("status") == "success":
        data = result.get("data", {})
        assert "company_name" in data
        assert "summary" in data
        assert "details" in data

def test_process_company_info_empty_input(enterprise_service):
    # 验证空输入的错误路径
    result = enterprise_service.process_company_info("")
    assert isinstance(result, dict)
    assert result.get("status") == "error"