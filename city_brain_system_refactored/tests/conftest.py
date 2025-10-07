"""
Pytest配置和共享fixtures
"""
import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from unittest.mock import Mock
from domain.models.enterprise import (
    EnterpriseBasicInfo,
    EnterpriseNewsInfo,
    EnterpriseComprehensiveInfo,
    DataSource
)
from infrastructure.database.models.customer import Customer


@pytest.fixture
def mock_customer_repository():
    """Mock的CustomerRepository"""
    return Mock()


@pytest.fixture
def mock_search_service():
    """Mock的SearchService"""
    return Mock()


@pytest.fixture
def mock_data_enhancement_service():
    """Mock的DataEnhancementService"""
    return Mock()


@pytest.fixture
def mock_analysis_service():
    """Mock的AnalysisService"""
    return Mock()


@pytest.fixture
def sample_customer():
    """示例Customer对象"""
    return Customer(
        customer_id=1,
        customer_name="青岛啤酒股份有限公司",
        industry_name="食品饮料制造",
        address="山东省青岛市市北区登州路56号",
        district_name="市北区",
        brain_name="青岛市食品饮料产业大脑",
        chain_leader_id=1,
        chain_leader_name="青岛啤酒股份有限公司",
        data_source="local_db"
    )


@pytest.fixture
def sample_basic_info():
    """示例EnterpriseBasicInfo"""
    return EnterpriseBasicInfo(
        name="青岛啤酒股份有限公司",
        normalized_name="青岛啤酒",
        industry="食品饮料制造",
        address="山东省青岛市市北区登州路56号",
        district="市北区"
    )


@pytest.fixture
def sample_news_info():
    """示例EnterpriseNewsInfo"""
    return EnterpriseNewsInfo(
        summary="青岛啤酒发布2024年Q3财报",
        references=[{"title": "财报", "url": "https://example.com"}],
        source="test"
    )


@pytest.fixture
def sample_comprehensive_info(sample_basic_info, sample_news_info):
    """示例EnterpriseComprehensiveInfo"""
    return EnterpriseComprehensiveInfo(
        basic_info=sample_basic_info,
        revenue_info="年营收超300亿元",
        ranking_status="中国啤酒行业TOP3",
        industry_brain="青岛市食品饮料产业大脑",
        chain_status="食品饮料产业链链主企业",
        news_info=sample_news_info,
        data_source=DataSource.LOCAL_DB,
        confidence_score=0.95
    )
