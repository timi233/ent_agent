"""
测试EnterpriseService
展示依赖注入带来的可测试性提升
"""
import pytest
from unittest.mock import Mock, patch
from domain.services.enterprise_service import EnterpriseService
from domain.models.enterprise import (
    EnterpriseComprehensiveInfo,
    EnterpriseBasicInfo,
    DataSource
)


class TestEnterpriseService:
    """测试EnterpriseService（依赖注入版本）"""

    @pytest.fixture
    def enterprise_service(
        self,
        mock_search_service,
        mock_data_enhancement_service,
        mock_analysis_service,
        mock_customer_repository
    ):
        """创建EnterpriseService实例（注入Mock依赖）"""
        return EnterpriseService(
            search_service=mock_search_service,
            data_enhancement_service=mock_data_enhancement_service,
            analysis_service=mock_analysis_service,
            customer_repository=mock_customer_repository
        )

    def test_service_initialization(self, enterprise_service):
        """测试服务初始化"""
        assert enterprise_service.search_service is not None
        assert enterprise_service.customer_repository is not None

    def test_process_company_info_v2_with_local_data(
        self,
        enterprise_service,
        mock_search_service,
        mock_customer_repository,
        sample_customer
    ):
        """测试使用本地数据处理（可以Mock依赖）"""
        # Mock: 名称提取成功
        mock_search_service.extract_company_name_from_input.return_value = {
            'status': 'success',
            'name': '青岛啤酒'
        }

        # Mock: 本地数据库有数据
        mock_customer_repository.find_by_name.return_value = sample_customer

        # Mock: 新闻服务返回空
        enterprise_service.analysis_service.get_company_news.return_value = None

        # 执行
        result = enterprise_service.process_company_info_v2("查询青岛啤酒")

        # 验证
        assert isinstance(result, EnterpriseComprehensiveInfo)
        assert result.company_name == "青岛啤酒股份有限公司"
        assert result.data_source == DataSource.LOCAL_DB
        assert result.basic_info.industry == "食品饮料制造"

        # 验证依赖调用
        mock_search_service.extract_company_name_from_input.assert_called_once_with("查询青岛啤酒")
        mock_customer_repository.find_by_name.assert_called_once_with("青岛啤酒")

    def test_process_company_info_v2_without_local_data(
        self,
        enterprise_service,
        mock_search_service,
        mock_customer_repository
    ):
        """测试无本地数据的情况"""
        # Mock: 名称提取成功
        mock_search_service.extract_company_name_from_input.return_value = {
            'status': 'success',
            'name': '未知企业'
        }

        # Mock: 本地数据库无数据
        mock_customer_repository.find_by_name.return_value = None

        # Mock: 搜索服务返回数据
        mock_search_service.search_company_info.return_value = {
            'status': 'error'
        }

        # Mock: 新闻服务
        enterprise_service.analysis_service.get_company_news.return_value = None

        # 执行
        result = enterprise_service.process_company_info_v2("未知企业")

        # 验证
        assert isinstance(result, EnterpriseComprehensiveInfo)
        assert result.data_source == DataSource.SEARCH_ENGINE
        assert result.confidence_score < 0.9  # 搜索数据可信度低

    def test_process_company_info_v2_empty_input(self, enterprise_service):
        """测试空输入"""
        with pytest.raises(ValueError, match="用户输入不能为空"):
            enterprise_service.process_company_info_v2("")

    def test_process_company_info_v2_name_extraction_failure(
        self,
        enterprise_service,
        mock_search_service
    ):
        """测试名称提取失败"""
        # Mock: 名称提取失败
        mock_search_service.extract_company_name_from_input.return_value = {
            'status': 'error',
            'message': '提取失败'
        }

        # 执行并验证异常
        with pytest.raises(RuntimeError, match="企业名称提取失败"):
            enterprise_service.process_company_info_v2("无效输入")

    def test_build_from_local_data(self, enterprise_service, sample_customer):
        """测试从本地数据构建"""
        # Mock新闻服务
        enterprise_service.analysis_service.get_company_news.return_value = {
            'summary': '测试新闻',
            'references': []
        }

        result = enterprise_service._build_from_local_data(sample_customer)

        assert isinstance(result, EnterpriseComprehensiveInfo)
        assert result.company_name == sample_customer.customer_name
        assert result.basic_info.industry == sample_customer.industry_name
        assert result.is_chain_leader() is True  # 有chain_leader_id

    def test_dependency_injection_benefits(self):
        """演示依赖注入的优势"""
        # 可以轻松创建不同配置的服务实例
        mock_repo = Mock()
        mock_search = Mock()

        service = EnterpriseService(
            search_service=mock_search,
            data_enhancement_service=Mock(),
            analysis_service=Mock(),
            customer_repository=mock_repo
        )

        # 可以验证依赖的具体调用
        mock_repo.find_by_name.return_value = None
        mock_search.extract_company_name_from_input.return_value = {
            'status': 'success',
            'name': 'test'
        }
        mock_search.search_company_info.return_value = {'status': 'error'}
        service.analysis_service.get_company_news.return_value = None

        result = service.process_company_info_v2("test input")

        # 验证Mock被正确调用
        assert mock_search.extract_company_name_from_input.called
        assert mock_repo.find_by_name.called


@pytest.mark.unit
class TestEnterpriseServiceIntegration:
    """集成测试标记示例"""

    def test_example_marked_as_unit(self):
        """这是一个单元测试"""
        assert True
