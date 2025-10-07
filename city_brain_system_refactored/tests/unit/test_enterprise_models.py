"""
测试企业领域模型
"""
import pytest
from datetime import datetime
from domain.models.enterprise import (
    EnterpriseBasicInfo,
    EnterpriseNewsInfo,
    EnterpriseComprehensiveInfo,
    DataSource
)


class TestEnterpriseBasicInfo:
    """测试EnterpriseBasicInfo"""

    def test_create_basic_info(self):
        """测试创建基础信息"""
        info = EnterpriseBasicInfo(
            name="测试企业",
            normalized_name="测试企业",
            industry="信息技术",
            address="测试地址",
            district="测试区"
        )

        assert info.name == "测试企业"
        assert info.industry == "信息技术"
        assert info.is_complete() is True

    def test_empty_name_raises_error(self):
        """测试空名称抛出异常"""
        with pytest.raises(ValueError, match="企业名称不能为空"):
            EnterpriseBasicInfo(name="", normalized_name="test")

    def test_completeness_score(self):
        """测试完整度计算"""
        # 完全填充
        complete = EnterpriseBasicInfo(
            name="企业",
            normalized_name="企业",
            industry="行业",
            address="地址",
            district="区域"
        )
        assert complete.completeness_score() == 1.0

        # 部分填充
        partial = EnterpriseBasicInfo(
            name="企业",
            normalized_name="企业",
            industry=None,
            address=None,
            district=None
        )
        assert partial.completeness_score() == 0.25  # 只有name字段

    def test_to_dict(self):
        """测试转换为字典"""
        info = EnterpriseBasicInfo(
            name="测试",
            normalized_name="测试",
            industry="IT"
        )
        result = info.to_dict()

        assert isinstance(result, dict)
        assert result["name"] == "测试"
        assert result["industry"] == "IT"


class TestEnterpriseNewsInfo:
    """测试EnterpriseNewsInfo"""

    def test_create_news_info(self):
        """测试创建新闻信息"""
        news = EnterpriseNewsInfo(
            summary="测试新闻",
            references=[{"title": "新闻1", "url": "http://test.com"}],
            source="test_source"
        )

        assert news.summary == "测试新闻"
        assert news.reference_count() == 1
        assert news.has_news() is True

    def test_empty_news(self):
        """测试空新闻"""
        news = EnterpriseNewsInfo(summary="")
        assert news.has_news() is False

    def test_auto_timestamp(self):
        """测试自动时间戳"""
        news = EnterpriseNewsInfo(summary="test")
        assert isinstance(news.last_updated, datetime)


class TestEnterpriseComprehensiveInfo:
    """测试EnterpriseComprehensiveInfo"""

    def test_create_comprehensive_info(self, sample_basic_info, sample_news_info):
        """测试创建综合信息"""
        info = EnterpriseComprehensiveInfo(
            basic_info=sample_basic_info,
            revenue_info="营收",
            ranking_status="排名",
            industry_brain="产业大脑",
            chain_status="链主企业",
            news_info=sample_news_info,
            data_source=DataSource.LOCAL_DB,
            confidence_score=0.9
        )

        assert info.company_name == "青岛啤酒股份有限公司"
        assert info.has_revenue_info() is True
        assert info.is_chain_leader() is True
        assert info.has_industry_brain() is True

    def test_overall_completeness(self, sample_comprehensive_info):
        """测试整体完整度"""
        score = sample_comprehensive_info.overall_completeness()
        assert 0 <= score <= 1
        assert score > 0.9  # 样本数据应该很完整

    def test_to_dict_format(self, sample_comprehensive_info):
        """测试字典格式"""
        result = sample_comprehensive_info.to_dict()

        assert "company_name" in result
        assert "details" in result
        assert "news" in result
        assert result["details"]["completeness"] > 0.9

    def test_from_dict(self, sample_comprehensive_info):
        """测试从字典创建"""
        data = sample_comprehensive_info.to_dict()
        reconstructed = EnterpriseComprehensiveInfo.from_dict(data)

        assert reconstructed.company_name == sample_comprehensive_info.company_name
        assert reconstructed.basic_info.industry == sample_comprehensive_info.basic_info.industry

    def test_invalid_confidence_score(self, sample_basic_info):
        """测试无效的可信度分数"""
        with pytest.raises(ValueError, match="confidence_score必须在0-1之间"):
            EnterpriseComprehensiveInfo(
                basic_info=sample_basic_info,
                confidence_score=1.5
            )
