"""
博查AI搜索客户端
提供网络搜索功能，支持错误处理、重试机制和配置管理
"""
import requests
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import json

# 尝试导入配置，优先使用 settings（会从 .env 加载密钥），失败再回退到 simple_settings，最后默认
try:
    from config.settings import get_settings
    _cfg = get_settings()
    DEFAULT_BASE_URL = _cfg.bocha_api.base_url
    DEFAULT_API_KEY = _cfg.bocha_api.api_key
except Exception:
    try:
        from config.simple_settings import get_simple_config
        _cfg = get_simple_config()
        DEFAULT_BASE_URL = _cfg.bocha_api.base_url
        DEFAULT_API_KEY = _cfg.bocha_api.api_key
    except Exception:
        DEFAULT_BASE_URL = 'https://api.bochaai.com/v1/web-search'
        DEFAULT_API_KEY = ''

logger = logging.getLogger(__name__)


class SearchTimeRange(Enum):
    """搜索时间范围枚举"""
    ALL = "all"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


@dataclass
class SearchRequest:
    """搜索请求参数"""
    query: str
    summary: bool = True
    count: int = 10
    freshness: SearchTimeRange = SearchTimeRange.ALL
    include_images: bool = False
    include_videos: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'query': self.query,
            'summary': self.summary,
            'count': self.count,
            'freshness': self.freshness.value,
            'include_images': self.include_images,
            'include_videos': self.include_videos
        }


@dataclass
class SearchResult:
    """搜索结果"""
    success: bool
    data: Dict[str, Any]
    response_time: float = 0.0
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    
    @classmethod
    def success_result(cls, data: Dict[str, Any], response_time: float = 0.0) -> 'SearchResult':
        """创建成功结果"""
        return cls(success=True, data=data, response_time=response_time)
    
    @classmethod
    def error_result(cls, error_message: str, status_code: Optional[int] = None, response_time: float = 0.0) -> 'SearchResult':
        """创建错误结果"""
        return cls(
            success=False,
            data={},
            error_message=error_message,
            status_code=status_code,
            response_time=response_time
        )


class BochaAPIError(Exception):
    """博查AI API异常"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class BochaAIClient:
    """博查AI搜索客户端"""
    
    def __init__(self,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 timeout: int = 30,
                 max_retries: int = 3,
                 retry_delay: float = 1.0):
        """
        初始化博查AI客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_delay: 重试延迟时间（秒）
        """
        self.api_key = api_key or DEFAULT_API_KEY
        self.base_url = base_url or DEFAULT_BASE_URL
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # 验证配置
        if not self.api_key:
            logger.warning("博查AI API密钥未配置，可能导致请求失败")
        
        # 设置请求会话
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CityBrain/1.0'
        })
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })
    
    def search(self,
               query: str,
               summary: bool = True,
               count: int = 10,
               freshness: SearchTimeRange = SearchTimeRange.ALL,
               include_images: bool = False,
               include_videos: bool = False) -> SearchResult:
        """
        执行网络搜索
        
        Args:
            query: 搜索查询
            summary: 是否生成摘要
            count: 返回结果数量
            freshness: 时间范围
            include_images: 是否包含图片
            include_videos: 是否包含视频
            
        Returns:
            搜索结果
        """
        request = SearchRequest(
            query=query,
            summary=summary,
            count=count,
            freshness=freshness,
            include_images=include_images,
            include_videos=include_videos
        )
        
        return self.search_with_request(request)
    
    def search_with_request(self, request: SearchRequest) -> SearchResult:
        """
        使用请求对象执行搜索
        
        Args:
            request: 搜索请求对象
            
        Returns:
            搜索结果
        """
        start_time = time.time()
        
        try:
            logger.info(f"开始博查AI搜索: 查询='{request.query}', 数量={request.count}")
            
            # 执行带重试的请求
            response_data = self._make_request_with_retry(request.to_dict())
            
            response_time = time.time() - start_time
            logger.info(f"博查AI搜索完成: 耗时={response_time:.2f}秒")
            
            return SearchResult.success_result(response_data, response_time)
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"博查AI搜索失败: {str(e)}"
            logger.error(f"{error_msg}, 耗时={response_time:.2f}秒")
            return SearchResult.error_result(error_msg, response_time=response_time)
    
    def search_enterprise_info(self, enterprise_name: str, additional_keywords: Optional[List[str]] = None) -> SearchResult:
        """
        搜索企业信息
        
        Args:
            enterprise_name: 企业名称
            additional_keywords: 额外关键词
            
        Returns:
            搜索结果
        """
        # 构建搜索查询
        query_parts = [f'"{enterprise_name}"']
        
        if additional_keywords:
            query_parts.extend(additional_keywords)
        
        query = ' '.join(query_parts)
        
        return self.search(
            query=query,
            summary=True,
            count=5,
            freshness=SearchTimeRange.YEAR
        )
    
    def search_industry_info(self, industry_name: str, region: Optional[str] = None) -> SearchResult:
        """
        搜索行业信息
        
        Args:
            industry_name: 行业名称
            region: 地区名称
            
        Returns:
            搜索结果
        """
        query_parts = [industry_name, "行业"]
        
        if region:
            query_parts.append(region)
        
        query = ' '.join(query_parts)
        
        return self.search(
            query=query,
            summary=True,
            count=8,
            freshness=SearchTimeRange.YEAR
        )
    
    def search_address_info(self, address_query: str) -> SearchResult:
        """
        搜索地址信息
        
        Args:
            address_query: 地址查询
            
        Returns:
            搜索结果
        """
        return self.search(
            query=f"{address_query} 地址 位置",
            summary=False,
            count=3,
            freshness=SearchTimeRange.ALL
        )
    
    def _make_request_with_retry(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行带重试的HTTP请求
        
        Args:
            payload: 请求负载
            
        Returns:
            响应数据
            
        Raises:
            BochaAPIError: API请求失败
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    delay = self.retry_delay * (2 ** (attempt - 1))  # 指数退避
                    logger.info(f"重试博查AI请求 (第{attempt}次), 延迟{delay:.1f}秒")
                    time.sleep(delay)
                
                response = self.session.post(
                    self.base_url,
                    json=payload,
                    timeout=self.timeout
                )
                
                # 检查HTTP状态码
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise BochaAPIError("API密钥无效或已过期", response.status_code, response.text)
                elif response.status_code == 429:
                    raise BochaAPIError("请求频率过高，请稍后重试", response.status_code, response.text)
                elif response.status_code >= 500:
                    raise BochaAPIError(f"服务器错误: {response.status_code}", response.status_code, response.text)
                else:
                    raise BochaAPIError(f"请求失败: {response.status_code}", response.status_code, response.text)
                    
            except requests.exceptions.Timeout as e:
                last_exception = BochaAPIError(f"请求超时: {e}")
                logger.warning(f"博查AI请求超时 (第{attempt + 1}次尝试): {e}")
            except requests.exceptions.ConnectionError as e:
                last_exception = BochaAPIError(f"连接错误: {e}")
                logger.warning(f"博查AI连接错误 (第{attempt + 1}次尝试): {e}")
            except requests.exceptions.RequestException as e:
                last_exception = BochaAPIError(f"请求异常: {e}")
                logger.warning(f"博查AI请求异常 (第{attempt + 1}次尝试): {e}")
            except json.JSONDecodeError as e:
                last_exception = BochaAPIError(f"响应解析失败: {e}")
                logger.error(f"博查AI响应解析失败: {e}")
                break  # JSON解析错误不需要重试
            except BochaAPIError as e:
                if e.status_code in [401, 403]:  # 认证错误不需要重试
                    raise e
                last_exception = e
                logger.warning(f"博查AI API错误 (第{attempt + 1}次尝试): {e}")
        
        # 所有重试都失败了
        if last_exception:
            raise last_exception
        else:
            raise BochaAPIError("未知错误")
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            服务是否可用
        """
        try:
            # 使用简单查询进行健康检查
            result = self.search("test", count=1)
            return result.success
        except Exception as e:
            logger.error(f"博查AI API健康检查失败: {e}")
            return False
    
    def get_client_info(self) -> Dict[str, Any]:
        """
        获取客户端信息
        
        Returns:
            客户端配置信息
        """
        return {
            'base_url': self.base_url,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'has_api_key': bool(self.api_key)
        }
    
    def close(self):
        """关闭客户端会话"""
        if hasattr(self, 'session'):
            self.session.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


# 全局客户端实例（单例模式）
_global_client: Optional[BochaAIClient] = None


def get_bocha_client(api_key: Optional[str] = None,
                     base_url: Optional[str] = None,
                     **kwargs) -> BochaAIClient:
    """
    获取博查AI客户端实例（单例模式）
    
    Args:
        api_key: API密钥
        base_url: API基础URL
        **kwargs: 其他客户端参数
        
    Returns:
        博查AI客户端实例
    """
    global _global_client
    
    if _global_client is None:
        _global_client = BochaAIClient(api_key=api_key, base_url=base_url, **kwargs)
    
    return _global_client


# 向后兼容的函数
def search_web(query: str, count: int = 10, summary: bool = True) -> Dict[str, Any]:
    """
    向后兼容的网络搜索函数
    
    Args:
        query: 搜索查询
        count: 结果数量
        summary: 是否生成摘要
        
    Returns:
        搜索结果字典
        
    Raises:
        Exception: 搜索失败
    """
    try:
        client = get_bocha_client()
        result = client.search(query=query, count=count, summary=summary)
        
        if result.success:
            return result.data
        else:
            raise Exception(result.error_message or "搜索失败")
            
    except Exception as e:
        logger.error(f"网络搜索失败: {e}")
        raise Exception(f"博查AI API请求失败: {str(e)}")


def search_enterprise(enterprise_name: str) -> Dict[str, Any]:
    """
    向后兼容的企业搜索函数
    
    Args:
        enterprise_name: 企业名称
        
    Returns:
        搜索结果字典
        
    Raises:
        Exception: 搜索失败
    """
    try:
        client = get_bocha_client()
        result = client.search_enterprise_info(enterprise_name)
        
        if result.success:
            return result.data
        else:
            raise Exception(result.error_message or "企业搜索失败")
            
    except Exception as e:
        logger.error(f"企业搜索失败: {e}")
        raise Exception(f"博查AI API请求失败: {str(e)}")


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    with BochaAIClient() as client:
        logger.info(f"客户端信息: {client.get_client_info()}")
        
        # 测试搜索功能
        result = client.search("Python编程", count=3)
        print(f"搜索结果: 成功={result.success}")
        
        if result.success:
            logger.info(f"结果数量: {len(result.data.get('results', []))}")
        else:
            logger.error(f"错误信息: {result.error_message}")
