"""
外部服务管理器
统一管理和编排外部API服务
"""
import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

from infrastructure.utils.datetime_utils import now_utc
from .bocha_client import BochaAIClient, get_bocha_client
from .llm_client import LLMClient, get_llm_client

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """服务类型枚举"""
    SEARCH = "search"
    LLM = "llm"
    ANALYSIS = "analysis"


@dataclass
class ServiceResult:
    """服务调用结果"""
    service_type: ServiceType
    success: bool
    data: Any = None
    error_message: Optional[str] = None
    response_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success_result(cls, service_type: ServiceType, data: Any, response_time: float = 0.0, **metadata) -> 'ServiceResult':
        """创建成功结果"""
        return cls(
            service_type=service_type,
            success=True,
            data=data,
            response_time=response_time,
            metadata=metadata
        )
    
    @classmethod
    def error_result(cls, service_type: ServiceType, error_message: str, response_time: float = 0.0) -> 'ServiceResult':
        """创建错误结果"""
        return cls(
            service_type=service_type,
            success=False,
            error_message=error_message,
            response_time=response_time
        )


@dataclass
class EnterpriseSearchRequest:
    """企业搜索请求"""
    enterprise_name: str
    search_fields: List[str] = field(default_factory=lambda: ['address', 'industry', 'scale', 'revenue'])
    max_results: int = 5
    include_analysis: bool = True
    analysis_prompt: Optional[str] = None


@dataclass
class EnterpriseInfo:
    """企业信息结构"""
    name: str
    address: Optional[str] = None
    industry: Optional[str] = None
    scale: Optional[str] = None
    revenue: Optional[str] = None
    description: Optional[str] = None
    analysis: Optional[str] = None
    confidence_score: float = 0.0
    data_sources: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)


class ExternalServiceManager:
    """外部服务管理器"""
    
    def __init__(self,
                 bocha_client: Optional[BochaAIClient] = None,
                 llm_client: Optional[LLMClient] = None,
                 max_workers: int = 3,
                 default_timeout: int = 30):
        """
        初始化服务管理器
        
        Args:
            bocha_client: 博查AI客户端
            llm_client: LLM客户端
            max_workers: 最大并发工作线程数
            default_timeout: 默认超时时间
        """
        self.bocha_client = bocha_client or get_bocha_client()
        self.llm_client = llm_client or get_llm_client()
        self.max_workers = max_workers
        self.default_timeout = default_timeout
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        logger.info(f"外部服务管理器初始化完成: max_workers={max_workers}")
    
    def search_enterprise_info(self, request: EnterpriseSearchRequest) -> ServiceResult:
        """
        搜索企业信息
        
        Args:
            request: 搜索请求
            
        Returns:
            搜索结果
        """
        start_time = time.time()
        req_id = uuid.uuid4().hex
        
        try:
            logger.info(f"开始搜索企业信息: {request.enterprise_name}")
            
            # 构建搜索查询
            search_query = self._build_search_query(request.enterprise_name, request.search_fields)
            
            # 执行搜索
            search_result = self.bocha_client.search(
                query=search_query,
                count=request.max_results,
                summary=True
            )
            
            if not search_result.success:
                return ServiceResult.error_result(
                    ServiceType.SEARCH,
                    search_result.error_message or "搜索失败",
                    time.time() - start_time
                )
            
            # 解析搜索结果
            enterprise_info = self._parse_search_results(
                request.enterprise_name,
                search_result.data,
                request.search_fields
            )
            
            # 如果需要分析，调用LLM进行分析
            if request.include_analysis and enterprise_info.raw_data:
                analysis_result = self._analyze_enterprise_data(enterprise_info, request.analysis_prompt)
                if analysis_result.success:
                    enterprise_info.analysis = analysis_result.data
            
            response_time = time.time() - start_time
            logger.info(f"企业信息搜索完成: {request.enterprise_name}, 耗时={response_time:.2f}秒")
            
            return ServiceResult.success_result(
                ServiceType.SEARCH,
                enterprise_info,
                response_time,
                search_query=search_query,
                results_count=len(search_result.data.get('results', [])),
                request_id=req_id
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"企业信息搜索失败: {str(e)}"
            logger.exception(f"{error_msg}, 耗时={response_time:.2f}秒")
            return ServiceResult.error_result(ServiceType.SEARCH, error_msg, response_time)
    
    def batch_search_enterprises(self, enterprise_names: List[str], **search_options) -> Dict[str, ServiceResult]:
        """
        批量搜索企业信息
        
        Args:
            enterprise_names: 企业名称列表
            **search_options: 搜索选项
            
        Returns:
            搜索结果字典
        """
        logger.info(f"开始批量搜索企业信息: {len(enterprise_names)}家企业")
        
        results = {}
        futures = {}
        
        # 提交搜索任务
        for name in enterprise_names:
            request = EnterpriseSearchRequest(enterprise_name=name, **search_options)
            future = self.executor.submit(self.search_enterprise_info, request)
            futures[future] = name
        
        # 收集结果
        try:
            for future in as_completed(futures, timeout=self.default_timeout * len(enterprise_names)):
                name = futures[future]
                try:
                    result = future.result()
                    results[name] = result
                    logger.info(f"企业搜索完成: {name}, 成功={result.success}")
                except Exception as e:
                    logger.exception(f"企业搜索异常: {name}, 错误={e}")
                    results[name] = ServiceResult.error_result(ServiceType.SEARCH, str(e))
        except TimeoutError:
            logger.exception(f"批量搜索超时: 超时阈值={self.default_timeout}s * {len(enterprise_names)}")
            # 标记未完成的任务为超时
            for future, name in futures.items():
                if name not in results:
                    results[name] = ServiceResult.error_result(ServiceType.SEARCH, "批量搜索超时")
        
        logger.info(f"批量搜索完成: 成功={sum(1 for r in results.values() if r.success)}/{len(enterprise_names)}")
        return results
    
    def analyze_enterprise_data(self, enterprise_data: Dict[str, Any], analysis_type: str = "comprehensive") -> ServiceResult:
        """
        分析企业数据
        
        Args:
            enterprise_data: 企业数据
            analysis_type: 分析类型 (comprehensive, financial, industry, competitive)
            
        Returns:
            分析结果
        """
        start_time = time.time()
        req_id = uuid.uuid4().hex
        
        try:
            logger.info(f"开始企业数据分析: 类型={analysis_type}")
            
            # 根据分析类型选择提示词
            system_prompt = self._get_analysis_prompt(analysis_type)
            
            # 调用LLM分析（传入提示词）
            response = self.llm_client.analyze_enterprise_info(enterprise_data, system_prompt=system_prompt)
            
            if not response.success:
                return ServiceResult.error_result(
                    ServiceType.ANALYSIS,
                    response.error_message or "分析失败",
                    time.time() - start_time
                )
            
            response_time = time.time() - start_time
            logger.info(f"企业数据分析完成: 耗时={response_time:.2f}秒")
            
            return ServiceResult.success_result(
                ServiceType.ANALYSIS,
                response.content,
                response_time,
                analysis_type=analysis_type,
                token_usage=response.usage,
                request_id=req_id
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"企业数据分析失败: {str(e)}"
            logger.exception(f"{error_msg}, 耗时={response_time:.2f}秒")
            return ServiceResult.error_result(ServiceType.ANALYSIS, error_msg, response_time)
    
    def generate_industry_report(self, industry_name: str, region: str = "", enterprises: Optional[List[Dict[str, Any]]] = None) -> ServiceResult:
        """
        生成行业报告
        
        Args:
            industry_name: 行业名称
            region: 地区名称
            enterprises: 相关企业数据
            
        Returns:
            报告生成结果
        """
        start_time = time.time()
        req_id = uuid.uuid4().hex
        
        try:
            logger.info(f"开始生成行业报告: {industry_name} ({region})")
            
            # 准备数据
            report_data = {
                'industry': industry_name,
                'region': region,
                'enterprises': enterprises or []
            }
            
            # 调用LLM生成报告
            response = self.llm_client.generate_industry_report(industry_name, region, report_data)
            
            if not response.success:
                return ServiceResult.error_result(
                    ServiceType.LLM,
                    response.error_message or "报告生成失败",
                    time.time() - start_time
                )
            
            response_time = time.time() - start_time
            logger.info(f"行业报告生成完成: 耗时={response_time:.2f}秒")
            
            return ServiceResult.success_result(
                ServiceType.LLM,
                response.content,
                response_time,
                industry=industry_name,
                region=region,
                enterprises_count=len(enterprises) if enterprises else 0,
                token_usage=response.usage,
                request_id=req_id
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"行业报告生成失败: {str(e)}"
            logger.exception(f"{error_msg}, 耗时={response_time:.2f}秒")
            return ServiceResult.error_result(ServiceType.LLM, error_msg, response_time)
    
    def extract_enterprise_info_from_text(self, text: str, enterprise_name: str) -> ServiceResult:
        """
        从文本中提取企业信息
        
        Args:
            text: 源文本
            enterprise_name: 企业名称
            
        Returns:
            提取结果
        """
        start_time = time.time()
        req_id = uuid.uuid4().hex
        
        try:
            logger.info(f"开始从文本提取企业信息: {enterprise_name}")
            
            # 定义要提取的字段
            fields = ['企业名称', '注册地址', '经营地址', '所属行业', '企业规模', '年营收', '员工人数', '成立时间', '法定代表人', '经营范围']
            
            # 调用LLM提取信息
            response = self.llm_client.extract_structured_info(text, fields)
            
            if not response.success:
                return ServiceResult.error_result(
                    ServiceType.LLM,
                    response.error_message or "信息提取失败",
                    time.time() - start_time
                )
            
            # 解析提取结果
            try:
                import json
                extracted_data = json.loads(response.content)
            except json.JSONDecodeError:
                # 如果不是JSON格式，直接返回文本
                extracted_data = {'raw_text': response.content}
            
            response_time = time.time() - start_time
            logger.info(f"企业信息提取完成: 耗时={response_time:.2f}秒")
            
            return ServiceResult.success_result(
                ServiceType.LLM,
                extracted_data,
                response_time,
                enterprise_name=enterprise_name,
                fields_count=len(fields),
                token_usage=response.usage,
                request_id=req_id
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"企业信息提取失败: {str(e)}"
            logger.exception(f"{error_msg}, 耗时={response_time:.2f}秒")
            return ServiceResult.error_result(ServiceType.LLM, error_msg, response_time)
    
    def comprehensive_enterprise_research(self, enterprise_name: str, include_industry_analysis: bool = True) -> Dict[str, ServiceResult]:
        """
        综合企业调研
        
        Args:
            enterprise_name: 企业名称
            include_industry_analysis: 是否包含行业分析
            
        Returns:
            调研结果字典
        """
        logger.info(f"开始综合企业调研: {enterprise_name}")
        
        results = {}
        
        # 1. 搜索企业基础信息
        search_request = EnterpriseSearchRequest(
            enterprise_name=enterprise_name,
            search_fields=['address', 'industry', 'scale', 'revenue', 'business_scope'],
            include_analysis=True
        )
        results['basic_info'] = self.search_enterprise_info(search_request)
        
        # 2. 如果基础信息搜索成功，进行深度分析
        if results['basic_info'].success:
            enterprise_info = results['basic_info'].data
            
            # 企业竞争力分析
            if enterprise_info.raw_data:
                results['competitive_analysis'] = self.analyze_enterprise_data(
                    enterprise_info.raw_data,
                    'competitive'
                )
            
            # 行业分析（如果需要）
            if include_industry_analysis and enterprise_info.industry:
                results['industry_analysis'] = self.generate_industry_report(
                    enterprise_info.industry,
                    enterprises=[enterprise_info.raw_data] if enterprise_info.raw_data else None
                )
        
        # 统计结果
        success_count = sum(1 for result in results.values() if result.success)
        total_count = len(results)
        
        logger.info(f"综合企业调研完成: {enterprise_name}, 成功={success_count}/{total_count}")
        
        return results
    
    def _build_search_query(self, enterprise_name: str, search_fields: List[str]) -> str:
        """构建搜索查询"""
        base_query = f'"{enterprise_name}"'
        
        field_keywords = {
            'address': '地址 注册地址 办公地址',
            'industry': '行业 所属行业 主营业务',
            'scale': '规模 企业规模 员工人数',
            'revenue': '营收 年营收 营业收入 销售额',
            'business_scope': '经营范围 业务范围'
        }
        
        additional_terms = []
        for field in search_fields:
            if field in field_keywords:
                additional_terms.append(field_keywords[field])
        
        if additional_terms:
            query = f'{base_query} ({" OR ".join(additional_terms)})'
        else:
            query = base_query
        
        return query
    
    def _parse_search_results(self, enterprise_name: str, search_data: Dict[str, Any], search_fields: List[str]) -> EnterpriseInfo:
        """解析搜索结果"""
        enterprise_info = EnterpriseInfo(name=enterprise_name)
        
        results = search_data.get('results', [])
        if not results:
            return enterprise_info
        
        # 合并所有搜索结果的文本
        all_text = ""
        data_sources = []
        
        for result in results:
            if 'content' in result:
                all_text += result['content'] + "\n"
            if 'url' in result:
                data_sources.append(result['url'])
        
        enterprise_info.data_sources = data_sources
        enterprise_info.raw_data = search_data
        
        # 简单的信息提取（可以后续用LLM优化）
        text_lower = all_text.lower()
        
        # 提取地址信息
        if 'address' in search_fields:
            address_keywords = ['地址', '位于', '坐落于']
            for keyword in address_keywords:
                if keyword in all_text:
                    # 简单的地址提取逻辑
                    lines = all_text.split('\n')
                    for line in lines:
                        if keyword in line and len(line) < 200:
                            enterprise_info.address = line.strip()
                            break
        
        # 提取行业信息
        if 'industry' in search_fields:
            industry_keywords = ['行业', '从事', '主营']
            for keyword in industry_keywords:
                if keyword in all_text:
                    lines = all_text.split('\n')
                    for line in lines:
                        if keyword in line and len(line) < 100:
                            enterprise_info.industry = line.strip()
                            break
        
        # 设置置信度
        enterprise_info.confidence_score = min(1.0, len(results) * 0.2)
        
        return enterprise_info
    
    def _analyze_enterprise_data(self, enterprise_info: EnterpriseInfo, custom_prompt: Optional[str] = None) -> ServiceResult:
        """分析企业数据"""
        start_time = time.time()
        req_id = uuid.uuid4().hex
        try:
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = f"请分析企业 {enterprise_info.name} 的基本情况，包括业务特点、发展状况等"
            
            # 准备分析数据
            analysis_data = {
                'name': enterprise_info.name,
                'address': enterprise_info.address,
                'industry': enterprise_info.industry,
                'raw_search_data': enterprise_info.raw_data
            }
            
            # 传入提示词以提升分析质量
            response = self.llm_client.analyze_enterprise_info(analysis_data, system_prompt=prompt)
            
            if response.success:
                response_time = time.time() - start_time
                return ServiceResult.success_result(
                    ServiceType.ANALYSIS,
                    response.content,
                    response_time,
                    token_usage=getattr(response, "usage", None),
                    request_id=req_id
                )
            else:
                return ServiceResult.error_result(ServiceType.ANALYSIS, response.error_message or "分析失败", time.time() - start_time)
                
        except Exception as e:
            return ServiceResult.error_result(ServiceType.ANALYSIS, str(e), time.time() - start_time)
    
    def _get_analysis_prompt(self, analysis_type: str) -> str:
        """获取分析提示词"""
        prompts = {
            'comprehensive': """请对企业进行综合分析，包括：
1. 企业基本情况概述
2. 主营业务和产品服务
3. 市场地位和竞争优势
4. 发展规模和财务状况
5. 发展前景和风险评估""",
            
            'financial': """请重点分析企业的财务状况，包括：
1. 营收规模和增长趋势
2. 盈利能力分析
3. 资产负债情况
4. 现金流状况
5. 财务风险评估""",
            
            'industry': """请从行业角度分析企业，包括：
1. 所属行业发展现状
2. 企业在行业中的地位
3. 行业竞争格局分析
4. 行业发展趋势
5. 企业行业适应性""",
            
            'competitive': """请分析企业的竞争力，包括：
1. 核心竞争优势
2. 产品/服务差异化
3. 技术创新能力
4. 市场占有率
5. 竞争策略分析"""
        }
        
        return prompts.get(analysis_type, prompts['comprehensive'])
    
    def get_all_service_health(self) -> Dict[str, Any]:
        """获取所有服务的健康状态"""
        health_status = {}

        # 检查博查AI服务
        try:
            bocha_health = self.bocha_client.health_check() if hasattr(self, 'bocha_client') else False
            health_status['bocha_ai'] = {
                'status': 'healthy' if bocha_health else 'unhealthy',
                'last_check': now_utc().isoformat(),
                'details': self.bocha_client.get_client_info() if bocha_health else {}
            }
        except Exception as e:
            health_status['bocha_ai'] = {
                'status': 'unhealthy',
                'last_check': now_utc().isoformat(),
                'error': str(e)
            }

        # 检查LLM服务
        try:
            llm_health = self.llm_client.health_check() if hasattr(self, 'llm_client') else False
            health_status['deepseek_llm'] = {
                'status': 'healthy' if llm_health else 'unhealthy',
                'last_check': now_utc().isoformat(),
                'details': {'model': 'deepseek-chat'} if llm_health else {}
            }
        except Exception as e:
            health_status['deepseek_llm'] = {
                'status': 'unhealthy',
                'last_check': now_utc().isoformat(),
                'error': str(e)
            }

        # 检查服务管理器本身
        try:
            manager_health = len(health_status) > 0
            health_status['service_manager'] = {
                'status': 'healthy' if manager_health else 'unhealthy',
                'last_check': now_utc().isoformat(),
                'details': {
                    'max_workers': getattr(self, 'max_workers', 0),
                    'default_timeout': getattr(self, 'default_timeout', 0),
                    'services_count': len(health_status)
                }
            }
        except Exception as e:
            health_status['service_manager'] = {
                'status': 'unhealthy',
                'last_check': now_utc().isoformat(),
                'error': str(e)
            }

        return health_status

    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        status = {
            'bocha_client': {
                'available': False,
                'info': {}
            },
            'llm_client': {
                'available': False,
                'info': {}
            },
            'manager': {
                'max_workers': self.max_workers,
                'default_timeout': self.default_timeout
            }
        }
        
        # 检查博查AI客户端
        try:
            status['bocha_client']['available'] = self.bocha_client.health_check()
            status['bocha_client']['info'] = self.bocha_client.get_client_info()
        except Exception as e:
            logger.exception(f"博查AI客户端状态检查失败: {e}")
        
        # 检查LLM客户端
        try:
            status['llm_client']['available'] = self.llm_client.health_check()
            status['llm_client']['info'] = self.llm_client.get_client_info()
        except Exception as e:
            logger.exception(f"LLM客户端状态检查失败: {e}")
        
        return status
    
    def close(self):
        """关闭服务管理器"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
        
        if hasattr(self, 'bocha_client'):
            self.bocha_client.close()
        
        if hasattr(self, 'llm_client'):
            self.llm_client.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


# 全局服务管理器实例
_global_service_manager: Optional[ExternalServiceManager] = None

# 向后兼容的别名
ServiceManager = ExternalServiceManager


def get_service_manager(**kwargs) -> ExternalServiceManager:
    """
    获取服务管理器实例（单例模式）
    
    Args:
        **kwargs: 服务管理器参数
        
    Returns:
        服务管理器实例
    """
    global _global_service_manager
    
    if _global_service_manager is None:
        _global_service_manager = ExternalServiceManager(**kwargs)
    
    return _global_service_manager


# 向后兼容的便捷函数
def search_enterprise_comprehensive(enterprise_name: str) -> Dict[str, Any]:
    """
    向后兼容的企业综合搜索函数
    
    Args:
        enterprise_name: 企业名称
        
    Returns:
        搜索结果
    """
    try:
        manager = get_service_manager()
        results = manager.comprehensive_enterprise_research(enterprise_name)
        
        # 转换为向后兼容的格式
        output = {
            'enterprise_name': enterprise_name,
            'success': any(result.success for result in results.values()),
            'data': {},
            'error_messages': []
        }
        
        for key, result in results.items():
            if result.success:
                output['data'][key] = result.data
            else:
                output['error_messages'].append(f"{key}: {result.error_message}")
        
        return output
        
    except Exception as e:
        logger.exception(f"企业综合搜索失败: {e}")
        return {
            'enterprise_name': enterprise_name,
            'success': False,
            'data': {},
            'error_messages': [str(e)]
        }


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    with ExternalServiceManager() as manager:
        logger.info(f"服务状态: {manager.get_service_status()}")
        
        # 测试企业搜索
        request = EnterpriseSearchRequest(enterprise_name="海尔集团")
        result = manager.search_enterprise_info(request)
        logger.info(f"搜索结果: 成功={result.success}")
        
        if result.success:
            info = result.data
            logger.info(f"企业信息: 名称={info.name}, 地址={info.address}, 行业={info.industry}")
