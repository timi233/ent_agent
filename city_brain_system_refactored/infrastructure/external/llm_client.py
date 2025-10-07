"""
大语言模型客户端
支持DeepSeek API，提供文本生成、总结和分析功能
"""
import requests
import time
import logging
import json
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum

# 尝试导入配置，优先使用 settings（会从 .env 加载密钥），失败再回退到 simple_settings，最后默认
try:
    from config.settings import get_settings
    _cfg = get_settings()
    DEFAULT_BASE_URL = _cfg.llm_api.base_url
    DEFAULT_API_KEY = _cfg.llm_api.api_key
    DEFAULT_MODEL = _cfg.llm_api.model
except Exception:
    try:
        from config.simple_settings import get_simple_config
        _cfg = get_simple_config()
        DEFAULT_BASE_URL = _cfg.llm_api.base_url
        DEFAULT_API_KEY = _cfg.llm_api.api_key
        DEFAULT_MODEL = _cfg.llm_api.model
    except Exception:
        DEFAULT_BASE_URL = 'https://api.deepseek.com'
        DEFAULT_API_KEY = ''
        DEFAULT_MODEL = 'deepseek-chat'

logger = logging.getLogger(__name__)


class MessageRole(Enum):
    """消息角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ChatMessage:
    """聊天消息"""
    role: MessageRole
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {
            'role': self.role.value,
            'content': self.content
        }
    
    @classmethod
    def system(cls, content: str) -> 'ChatMessage':
        """创建系统消息"""
        return cls(MessageRole.SYSTEM, content)
    
    @classmethod
    def user(cls, content: str) -> 'ChatMessage':
        """创建用户消息"""
        return cls(MessageRole.USER, content)
    
    @classmethod
    def assistant(cls, content: str) -> 'ChatMessage':
        """创建助手消息"""
        return cls(MessageRole.ASSISTANT, content)


@dataclass
class ChatRequest:
    """聊天请求参数"""
    messages: List[ChatMessage]
    model: str = DEFAULT_MODEL
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stream: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = {
            'model': self.model,
            'messages': [msg.to_dict() for msg in self.messages],
            'temperature': self.temperature,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'stream': self.stream
        }
        
        if self.max_tokens is not None:
            data['max_tokens'] = self.max_tokens
            
        return data


@dataclass
class ChatResponse:
    """聊天响应"""
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: Optional[str] = None
    response_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, response_data: Dict[str, Any], response_time: float = 0.0) -> 'ChatResponse':
        """从API响应创建聊天响应"""
        try:
            choices = response_data.get('choices', [])
            if not choices:
                return cls.error_response("API响应中没有选择项")
            
            choice = choices[0]
            message = choice.get('message', {})
            content = message.get('content', '')
            
            return cls(
                content=content,
                model=response_data.get('model', ''),
                usage=response_data.get('usage', {}),
                finish_reason=choice.get('finish_reason'),
                response_time=response_time,
                success=True
            )
        except Exception as e:
            logger.error(f"解析API响应失败: {e}")
            return cls.error_response(f"响应解析失败: {str(e)}")
    
    @classmethod
    def error_response(cls, error_message: str) -> 'ChatResponse':
        """创建错误响应"""
        return cls(
            content="",
            model="",
            success=False,
            error_message=error_message
        )


class LLMAPIError(Exception):
    """LLM API异常"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class LLMClient:
    """大语言模型客户端"""
    
    def __init__(self,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 model: Optional[str] = None,
                 timeout: int = 60,
                 max_retries: int = 3,
                 retry_delay: float = 1.0):
        """
        初始化LLM客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 默认模型名称
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_delay: 重试延迟时间（秒）
        """
        self.api_key = api_key or DEFAULT_API_KEY
        self.base_url = base_url or DEFAULT_BASE_URL
        self.model = model or DEFAULT_MODEL
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # 验证配置
        if not self.api_key:
            logger.warning("LLM API密钥未配置，可能导致请求失败")
        
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
    
    def chat(self,
             messages: List[ChatMessage],
             model: Optional[str] = None,
             temperature: float = 0.7,
             max_tokens: Optional[int] = None,
             **kwargs) -> ChatResponse:
        """
        执行聊天对话
        
        Args:
            messages: 消息列表（支持 ChatMessage、dict 或 str）
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            聊天响应
        """
        # 兼容多种消息输入类型，统一转为 ChatMessage
        normalized_messages: List[ChatMessage] = []
        for msg in messages or []:
            try:
                if isinstance(msg, ChatMessage):
                    normalized_messages.append(msg)
                elif isinstance(msg, dict):
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    # 容错：role大小写与非法值兜底为user
                    role_val = str(role).lower()
                    if role_val not in {"system", "user", "assistant"}:
                        role_val = "user"
                    if role_val == "system":
                        normalized_messages.append(ChatMessage.system(content))
                    elif role_val == "assistant":
                        normalized_messages.append(ChatMessage.assistant(content))
                    else:
                        normalized_messages.append(ChatMessage.user(content))
                elif isinstance(msg, str):
                    # 直接将字符串作为用户消息
                    normalized_messages.append(ChatMessage.user(msg))
                else:
                    # 跳过未知类型，避免崩溃
                    logging.getLogger(__name__).warning(f"不支持的消息类型，已跳过: {type(msg)}")
            except Exception as _e:
                logging.getLogger(__name__).warning(f"消息规范化失败，已跳过: {msg}")
        
        request = ChatRequest(
            messages=normalized_messages,
            model=model or self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return self.chat_with_request(request)
    
    def chat_with_request(self, request: ChatRequest) -> ChatResponse:
        """
        使用请求对象执行聊天
        
        Args:
            request: 聊天请求对象
            
        Returns:
            聊天响应
        """
        start_time = time.time()
        
        try:
            logger.info(f"开始LLM请求: 模型={request.model}, 消息数={len(request.messages)}")
            
            # 执行带重试的请求
            response_data = self._make_request_with_retry('/v1/chat/completions', request.to_dict())
            
            response_time = time.time() - start_time
            result = ChatResponse.from_api_response(response_data, response_time)
            
            logger.info(f"LLM请求完成: 耗时={response_time:.2f}秒, 成功={result.success}")
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"LLM请求失败: {str(e)}"
            logger.error(f"{error_msg}, 耗时={response_time:.2f}秒")
            return ChatResponse.error_response(error_msg)
    
    def simple_chat(self, user_message: str, system_message: Optional[str] = None, **kwargs) -> ChatResponse:
        """
        简单聊天接口
        
        Args:
            user_message: 用户消息
            system_message: 系统消息（可选）
            **kwargs: 其他参数
            
        Returns:
            聊天响应
        """
        start_time = time.time()
        
        try:
            # 构建简单的请求数据
            request_data = {
                "model": kwargs.get("model", self.model),
                "messages": []
            }
            
            if system_message:
                request_data["messages"].append({
                    "role": "system",
                    "content": system_message
                })
            
            request_data["messages"].append({
                "role": "user",
                "content": user_message
            })
            
            # 添加可选参数
            if "temperature" in kwargs:
                request_data["temperature"] = kwargs["temperature"]
            if "max_tokens" in kwargs:
                request_data["max_tokens"] = kwargs["max_tokens"]
            
            logger.info(f"开始简单LLM请求: 模型={request_data['model']}, 消息数={len(request_data['messages'])}")
            
            # 直接执行HTTP请求
            response_data = self._make_request_with_retry('/v1/chat/completions', request_data)
            
            response_time = time.time() - start_time
            result = ChatResponse.from_api_response(response_data, response_time)
            
            logger.info(f"简单LLM请求完成: 耗时={response_time:.2f}秒, 成功={result.success}")
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"简单LLM请求失败: {str(e)}"
            logger.error(f"{error_msg}, 耗时={response_time:.2f}秒")
            return ChatResponse.error_response(error_msg)
    
    def summarize_text(self, text: str, max_length: int = 200) -> ChatResponse:
        """
        文本总结
        
        Args:
            text: 要总结的文本
            max_length: 最大总结长度
            
        Returns:
            总结结果
        """
        system_message = f"""你是一个专业的文本总结助手。请将用户提供的文本总结为不超过{max_length}字的简洁摘要。
要求：
1. 保留关键信息和要点
2. 语言简洁明了
3. 逻辑清晰
4. 不要添加原文中没有的信息"""
        
        return self.simple_chat(
            user_message=f"请总结以下文本：\n\n{text}",
            system_message=system_message,
            temperature=0.3,
            max_tokens=max_length * 2
        )
    
    def analyze_enterprise_info(self, enterprise_data: Dict[str, Any]) -> ChatResponse:
        """
        分析企业信息
        
        Args:
            enterprise_data: 企业数据
            
        Returns:
            分析结果
        """
        system_message = """你是一个专业的企业分析师。请根据提供的企业信息，生成结构化的企业分析报告。
报告应包括：
1. 企业基本信息概述
2. 行业地位分析
3. 发展规模评估
4. 关键特点总结
5. 发展前景展望

请用专业、客观的语言进行分析，确保信息准确性。"""
        
        enterprise_text = json.dumps(enterprise_data, ensure_ascii=False, indent=2)
        
        return self.simple_chat(
            user_message=f"请分析以下企业信息：\n\n{enterprise_text}",
            system_message=system_message,
            temperature=0.5,
            max_tokens=1500
        )
    
    def generate_industry_report(self, industry_name: str, region: str = "", data: Optional[Dict[str, Any]] = None) -> ChatResponse:
        """
        生成行业报告
        
        Args:
            industry_name: 行业名称
            region: 地区名称
            data: 相关数据
            
        Returns:
            行业报告
        """
        system_message = """你是一个专业的行业分析师。请根据提供的信息，生成专业的行业分析报告。
报告应包括：
1. 行业概况
2. 发展现状
3. 市场规模
4. 主要企业
5. 发展趋势
6. 政策环境
7. 发展建议

请确保分析客观、专业，数据准确。"""
        
        region_text = f"在{region}地区的" if region else ""
        data_text = f"\n\n相关数据：\n{json.dumps(data, ensure_ascii=False, indent=2)}" if data else ""
        
        user_message = f"请分析{region_text}{industry_name}行业情况{data_text}"
        
        return self.simple_chat(
            user_message=user_message,
            system_message=system_message,
            temperature=0.6,
            max_tokens=2000
        )
    
    def extract_structured_info(self, text: str, fields: List[str]) -> ChatResponse:
        """
        从文本中提取结构化信息
        
        Args:
            text: 源文本
            fields: 要提取的字段列表
            
        Returns:
            结构化信息
        """
        fields_text = "、".join(fields)
        system_message = f"""你是一个信息提取专家。请从用户提供的文本中提取以下字段的信息：{fields_text}

请以JSON格式返回结果，格式如下：
{{
    "field1": "提取的值或null",
    "field2": "提取的值或null",
    ...
}}

如果某个字段在文本中找不到相关信息，请设置为null。"""
        
        return self.simple_chat(
            user_message=f"请从以下文本中提取信息：\n\n{text}",
            system_message=system_message,
            temperature=0.1,
            max_tokens=1000
        )
    
    def _make_request_with_retry(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行带重试的HTTP请求
        
        Args:
            endpoint: API端点
            payload: 请求负载
            
        Returns:
            响应数据
            
        Raises:
            LLMAPIError: API请求失败
        """
        url = f"{self.base_url.rstrip('/')}{endpoint}"
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    delay = self.retry_delay * (2 ** (attempt - 1))  # 指数退避
                    logger.info(f"重试LLM请求 (第{attempt}次), 延迟{delay:.1f}秒")
                    time.sleep(delay)
                
                response = self.session.post(
                    url,
                    json=payload,
                    timeout=self.timeout
                )
                
                # 检查HTTP状态码
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise LLMAPIError("API密钥无效或已过期", response.status_code, response.text)
                elif response.status_code == 429:
                    raise LLMAPIError("请求频率过高，请稍后重试", response.status_code, response.text)
                elif response.status_code >= 500:
                    raise LLMAPIError(f"服务器错误: {response.status_code}", response.status_code, response.text)
                else:
                    raise LLMAPIError(f"请求失败: {response.status_code}", response.status_code, response.text)
                    
            except requests.exceptions.Timeout as e:
                last_exception = LLMAPIError(f"请求超时: {e}")
                logger.warning(f"LLM请求超时 (第{attempt + 1}次尝试): {e}")
            except requests.exceptions.ConnectionError as e:
                last_exception = LLMAPIError(f"连接错误: {e}")
                logger.warning(f"LLM连接错误 (第{attempt + 1}次尝试): {e}")
            except requests.exceptions.RequestException as e:
                last_exception = LLMAPIError(f"请求异常: {e}")
                logger.warning(f"LLM请求异常 (第{attempt + 1}次尝试): {e}")
            except json.JSONDecodeError as e:
                last_exception = LLMAPIError(f"响应解析失败: {e}")
                logger.error(f"LLM响应解析失败: {e}")
                break  # JSON解析错误不需要重试
            except LLMAPIError as e:
                if e.status_code in [401, 403]:  # 认证错误不需要重试
                    raise e
                last_exception = e
                logger.warning(f"LLM API错误 (第{attempt + 1}次尝试): {e}")
        
        # 所有重试都失败了
        if last_exception:
            raise last_exception
        else:
            raise LLMAPIError("未知错误")
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            服务是否可用
        """
        try:
            response = self.simple_chat("Hello", max_tokens=10)
            return response.success
        except Exception as e:
            logger.error(f"LLM API健康检查失败: {e}")
            return False
    
    def get_client_info(self) -> Dict[str, Any]:
        """
        获取客户端信息
        
        Returns:
            客户端配置信息
        """
        return {
            'base_url': self.base_url,
            'model': self.model,
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
_global_client: Optional[LLMClient] = None


def get_llm_client(api_key: Optional[str] = None,
                   base_url: Optional[str] = None,
                   model: Optional[str] = None,
                   **kwargs) -> LLMClient:
    """
    获取LLM客户端实例（单例模式）
    
    Args:
        api_key: API密钥
        base_url: API基础URL
        model: 模型名称
        **kwargs: 其他客户端参数
        
    Returns:
        LLM客户端实例
    """
    global _global_client
    
    if _global_client is None:
        _global_client = LLMClient(api_key=api_key, base_url=base_url, model=model, **kwargs)
    
    return _global_client


# 向后兼容的函数
def generate_summary(text: str, max_length: int = 200) -> str:
    """
    向后兼容的文本总结函数
    
    Args:
        text: 要总结的文本
        max_length: 最大长度
        
    Returns:
        总结文本
        
    Raises:
        Exception: 总结失败
    """
    try:
        client = get_llm_client()
        response = client.summarize_text(text, max_length)
        
        if response.success:
            return response.content
        else:
            raise Exception(response.error_message or "总结失败")
            
    except Exception as e:
        logger.error(f"文本总结失败: {e}")
        raise Exception(f"LLM API请求失败: {str(e)}")


def analyze_text(text: str, prompt: str = "") -> str:
    """
    向后兼容的文本分析函数
    
    Args:
        text: 要分析的文本
        prompt: 分析提示
        
    Returns:
        分析结果
        
    Raises:
        Exception: 分析失败
    """
    try:
        client = get_llm_client()
        
        if prompt:
            user_message = f"{prompt}\n\n{text}"
        else:
            user_message = f"请分析以下文本：\n\n{text}"
        
        response = client.simple_chat(user_message)
        
        if response.success:
            return response.content
        else:
            raise Exception(response.error_message or "分析失败")
            
    except Exception as e:
        logger.error(f"文本分析失败: {e}")
        raise Exception(f"LLM API请求失败: {str(e)}")


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    with LLMClient() as client:
        logger.info(f"客户端信息: {client.get_client_info()}")
        
        # 测试简单聊天
        response = client.simple_chat("你好，请介绍一下你自己")
        logger.info(f"聊天结果: 成功={response.success}")
        
        if response.success:
            logger.info("回复: " + (response.content[:100] + "..." if len(response.content) > 100 else response.content))
        else:
            logger.error(f"错误信息: {response.error_message}")
