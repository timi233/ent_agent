"""
企业领域模型
定义企业相关的核心业务实体和值对象

设计原则：
- 使用dataclass提供类型安全
- 业务逻辑封装在模型内
- 不依赖数据库或外部框架
- 提供验证和转换方法
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DataSource(Enum):
    """数据来源枚举"""
    LOCAL_DB = "local_db"
    SEARCH_ENGINE = "search_engine"
    EXTERNAL_API = "external_api"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class EnterpriseBasicInfo:
    """
    企业基础信息（值对象）
    包含企业的核心识别信息
    """
    name: str
    normalized_name: str
    industry: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None

    def __post_init__(self):
        """数据验证"""
        if not self.name or not self.name.strip():
            raise ValueError("企业名称不能为空")

        if not self.normalized_name or not self.normalized_name.strip():
            raise ValueError("标准化名称不能为空")

        # 清理字符串
        self.name = self.name.strip()
        self.normalized_name = self.normalized_name.strip()
        if self.industry:
            self.industry = self.industry.strip()
        if self.address:
            self.address = self.address.strip()
        if self.district:
            self.district = self.district.strip()

    def is_complete(self) -> bool:
        """检查基础信息是否完整"""
        return all([
            self.name,
            self.industry,
            self.address,
            self.district
        ])

    def completeness_score(self) -> float:
        """
        计算信息完整度分数
        Returns:
            0.0 - 1.0 的分数
        """
        fields = [self.name, self.industry, self.address, self.district]
        filled = sum(1 for f in fields if f)
        return filled / len(fields)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "normalized_name": self.normalized_name,
            "industry": self.industry,
            "address": self.address,
            "district": self.district
        }


@dataclass
class EnterpriseNewsInfo:
    """
    企业新闻信息（值对象）
    包含企业的最新新闻和动态
    """
    summary: str
    references: List[Dict[str, str]] = field(default_factory=list)
    last_updated: Optional[datetime] = None
    source: str = "unknown"

    def __post_init__(self):
        """数据验证"""
        if self.summary:
            self.summary = self.summary.strip()

        if self.last_updated is None:
            self.last_updated = datetime.now()

    def has_news(self) -> bool:
        """是否有新闻信息"""
        return bool(self.summary and self.summary.strip())

    def reference_count(self) -> int:
        """新闻引用数量"""
        return len(self.references)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "summary": self.summary,
            "references": self.references,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "source": self.source
        }


@dataclass
class EnterpriseComprehensiveInfo:
    """
    企业综合信息（聚合根）
    整合企业的所有相关信息

    这是领域驱动设计中的聚合根（Aggregate Root）
    负责维护企业信息的一致性
    """
    basic_info: EnterpriseBasicInfo
    revenue_info: Optional[str] = None
    ranking_status: Optional[str] = None
    industry_brain: Optional[str] = None
    chain_status: Optional[str] = None
    news_info: Optional[EnterpriseNewsInfo] = None
    data_source: DataSource = DataSource.UNKNOWN
    confidence_score: float = 0.0  # 信息可信度评分 0-1

    def __post_init__(self):
        """数据验证和初始化"""
        if not isinstance(self.basic_info, EnterpriseBasicInfo):
            raise TypeError("basic_info必须是EnterpriseBasicInfo类型")

        # 清理字符串字段
        if self.revenue_info:
            self.revenue_info = self.revenue_info.strip()
        if self.ranking_status:
            self.ranking_status = self.ranking_status.strip()
        if self.industry_brain:
            self.industry_brain = self.industry_brain.strip()
        if self.chain_status:
            self.chain_status = self.chain_status.strip()

        # 验证置信度评分
        if not 0 <= self.confidence_score <= 1:
            raise ValueError("confidence_score必须在0-1之间")

    @property
    def company_name(self) -> str:
        """企业名称（快捷访问）"""
        return self.basic_info.name

    def has_revenue_info(self) -> bool:
        """是否有营收信息"""
        return bool(self.revenue_info and self.revenue_info.strip())

    def has_ranking_info(self) -> bool:
        """是否有排名信息"""
        return bool(self.ranking_status and self.ranking_status.strip())

    def is_chain_leader(self) -> bool:
        """是否为产业链链主"""
        return bool(self.chain_status and "链主" in self.chain_status)

    def has_industry_brain(self) -> bool:
        """是否关联产业大脑"""
        return bool(self.industry_brain and self.industry_brain.strip())

    def overall_completeness(self) -> float:
        """
        计算整体信息完整度
        Returns:
            0.0 - 1.0 的分数
        """
        scores = []

        # 基础信息完整度（权重40%）
        scores.append(self.basic_info.completeness_score() * 0.4)

        # 营收信息（权重20%）
        scores.append(0.2 if self.has_revenue_info() else 0)

        # 排名信息（权重15%）
        scores.append(0.15 if self.has_ranking_info() else 0)

        # 产业大脑（权重15%）
        scores.append(0.15 if self.has_industry_brain() else 0)

        # 新闻信息（权重10%）
        if self.news_info and self.news_info.has_news():
            scores.append(0.1)
        else:
            scores.append(0)

        return sum(scores)

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典（用于API响应）
        """
        return {
            "company_name": self.basic_info.name,
            "details": {
                "name": self.basic_info.name,
                "normalized_name": self.basic_info.normalized_name,
                "industry": self.basic_info.industry,
                "address": self.basic_info.address,
                "district_name": self.basic_info.district,
                "revenue_info": self.revenue_info or "暂无营收数据",
                "company_status": self.ranking_status or "暂无排名信息",
                "industry_brain": self.industry_brain or "",
                "chain_status": self.chain_status or "",
                "data_source": self.data_source.value,
                "confidence_score": self.confidence_score,
                "completeness": self.overall_completeness()
            },
            "news": {
                "summary": self.news_info.summary if self.news_info else "",
                "references": self.news_info.references if self.news_info else [],
                "last_updated": self.news_info.last_updated.isoformat() if self.news_info and self.news_info.last_updated else None
            } if self.news_info else {
                "summary": "",
                "references": [],
                "last_updated": None
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnterpriseComprehensiveInfo':
        """
        从字典创建实例
        适配现有的Dict返回格式
        """
        # 提取基础信息
        details = data.get('details', {})
        basic_info = EnterpriseBasicInfo(
            name=data.get('company_name', '') or details.get('name', ''),
            normalized_name=details.get('normalized_name', '') or data.get('company_name', ''),
            industry=details.get('industry'),
            address=details.get('address'),
            district=details.get('district_name')
        )

        # 提取新闻信息
        news_data = data.get('news', {})
        news_info = None
        if news_data and news_data.get('summary'):
            news_info = EnterpriseNewsInfo(
                summary=news_data.get('summary', ''),
                references=news_data.get('references', []),
                last_updated=datetime.fromisoformat(news_data['last_updated']) if news_data.get('last_updated') else None
            )

        # 解析数据来源
        source_str = details.get('data_source', 'unknown')
        try:
            data_source = DataSource(source_str)
        except ValueError:
            data_source = DataSource.UNKNOWN

        return cls(
            basic_info=basic_info,
            revenue_info=details.get('revenue_info'),
            ranking_status=details.get('company_status'),
            industry_brain=details.get('industry_brain'),
            chain_status=details.get('chain_status'),
            news_info=news_info,
            data_source=data_source,
            confidence_score=details.get('confidence_score', 0.0)
        )

    def __str__(self) -> str:
        """字符串表示"""
        return f"EnterpriseComprehensiveInfo(name={self.company_name}, industry={self.basic_info.industry}, completeness={self.overall_completeness():.1%})"

    def __repr__(self) -> str:
        """详细表示"""
        return f"EnterpriseComprehensiveInfo(basic_info={self.basic_info}, data_source={self.data_source}, confidence={self.confidence_score})"
