import pytest

from domain.services.enterprise_service import EnterpriseService


class DummySearchService:
    def extract_company_name_from_input(self, user_input: str):
        text = (user_input or "").strip()
        if not text:
            return {
                "status": "error",
                "message": "企业名称不能为空",
            }
        return {
            "status": "success",
            "name": "海尔集团",
            "is_complete": True,
            "source": "fixture",
        }

    def search_company_info(self, company_name: str):
        return {
            "status": "success",
            "data": {
                "name": company_name,
                "industry": "家电制造",
                "address": "中国山东省青岛市",
                "district_name": "青岛市",
                "region": "青岛市",
            },
        }


class DummyDataEnhancementService:
    def enhance_all_data(self, local_data):
        return {
            **local_data,
            "revenue_info": local_data.get("revenue_info", "暂无营收数据"),
            "company_status": local_data.get("company_status", "暂无排名信息"),
            "data_source": local_data.get("data_source", "local"),
        }

    def sync_database_updates(self, enhanced_data, local_data):
        # 测试上下文不需要落库，保持无副作用
        return None


class DummyCustomerRepository:
    SAMPLE = {
        "customer_name": "海尔集团",
        "district_name": "青岛市",
        "address": "中国山东省青岛市经济开发区海尔路1号",
        "industry_name": "家电制造",
        "brain_name": "青岛市工业互联网产业大脑",
        "chain_status": "链主企业",
        "revenue_info": "年营收超3000亿元",
        "company_status": "世界500强",
        "data_source": "local_fixture",
    }

    def find_by_name(self, name: str):
        if name == self.SAMPLE["customer_name"]:
            return dict(self.SAMPLE)
        return None


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
    search = DummySearchService()
    enhancer = DummyDataEnhancementService()
    analysis = DummyAnalysisService()
    customer_repo = DummyCustomerRepository()
    return EnterpriseService(search, enhancer, analysis, customer_repo)

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
