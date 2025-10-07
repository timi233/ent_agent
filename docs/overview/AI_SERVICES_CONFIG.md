# AI服务配置方案

## 📋 概述

本文档详细描述了城市大脑企业信息处理系统中AI服务的配置方案，包括博查AI搜索和DeepSeek大语言模型的集成配置。

## 🔍 博查AI搜索配置

### 环境配置
```python
# config/ai_config.py
from pydantic import BaseSettings

class BochaAIConfig(BaseSettings):
    api_key: str
    base_url: str = "https://api.bochaai.com/v1"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1
    
    # 搜索参数配置
    default_count: int = 10
    default_freshness: str = "year"  # year, month, week, day
    enable_summary: bool = True
    
    class Config:
        env_prefix = "BOCHAAI_"
```

### 搜索服务基础类
```python
# services/search_service.py
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from config.ai_config import BochaAIConfig
from utils.cache import cache_manager
from utils.logger import get_logger

logger = get_logger(__name__)

class BochaAISearchService:
    def __init__(self, config: BochaAIConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "CityBrain/2.0"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def search_enterprise_basic_info(self, enterprise_name: str) -> Dict[str, Any]:
        """搜索企业基础信息"""
        cache_key = f"enterprise_basic_search:{enterprise_name}"
        cached_result = await cache_manager.get(cache_key)
        
        if cached_result:
            logger.info(f"Cache hit for enterprise basic search: {enterprise_name}")
            return cached_result
        
        # 构建搜索查询
        query = self._build_basic_info_query(enterprise_name)
        
        try:
            result = await self._perform_search(query, search_type="basic_info")
            
            # 缓存结果24小时
            await cache_manager.set(cache_key, result, expire=86400)
            logger.info(f"Successfully searched basic info for: {enterprise_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error searching basic info for {enterprise_name}: {str(e)}")
            raise
    
    def _build_basic_info_query(self, enterprise_name: str) -> str:
        """构建基础信息搜索查询"""
        return f"{enterprise_name} 企业信息 注册资本 成立时间 法定代表人 经营范围 联系方式 地址"
    
    async def _perform_search(self, query: str, search_type: str = "general") -> Dict[str, Any]:
        """执行搜索请求"""
        payload = {
            "query": query,
            "summary": self.config.enable_summary,
            "freshness": self.config.default_freshness,
            "count": self.config.default_count,
            "search_type": search_type
        }
        
        for attempt in range(self.config.max_retries):
            try:
                async with self.session.post(
                    f"{self.config.base_url}/web-search",
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._process_search_result(result, search_type)
                    elif response.status == 429:  # Rate limit
                        wait_time = self.config.retry_delay * (2 ** attempt)
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        error_text = await response.text()
                        logger.error(f"BochaAI API error {response.status}: {error_text}")
                        if attempt == self.config.max_retries - 1:
                            raise Exception(f"搜索API调用失败: {response.status}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Search timeout, attempt {attempt + 1}")
                if attempt == self.config.max_retries - 1:
                    raise Exception("搜索请求超时")
                await asyncio.sleep(self.config.retry_delay)
                
            except Exception as e:
                logger.error(f"Search request error: {str(e)}")
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(self.config.retry_delay)
    
    def _process_search_result(self, raw_result: Dict[str, Any], search_type: str) -> Dict[str, Any]:
        """处理搜索结果"""
        return {
            "search_type": search_type,
            "timestamp": datetime.now().isoformat(),
            "raw_data": raw_result,
            "processed_data": self._extract_info_by_type(raw_result, search_type)
        }
    
    def _extract_info_by_type(self, raw_result: Dict[str, Any], search_type: str) -> Dict[str, Any]:
        """根据搜索类型提取信息"""
        return {
            "web_results": raw_result.get("web", []),
            "summary": raw_result.get("summary", ""),
            "extracted": True
        }
```

## 🧠 DeepSeek大语言模型配置

### 模型配置
```python
# config/llm_config.py
from pydantic import BaseSettings

class DeepSeekConfig(BaseSettings):
    api_key: str
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    timeout: int = 60
    max_retries: int = 3
    
    # 模型参数
    temperature: float = 0.1
    max_tokens: int = 2000
    top_p: float = 0.95
    
    class Config:
        env_prefix = "DEEPSEEK_"
```

### LLM服务基础类
```python
# services/llm_service.py
import asyncio
import aiohttp
import json
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from config.llm_config import DeepSeekConfig
from utils.cache import cache_manager
from utils.logger import get_logger

logger = get_logger(__name__)

class DeepSeekLLMService:
    def __init__(self, config: DeepSeekConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def extract_enterprise_name(self, text: str) -> Optional[str]:
        """从文本中提取企业名称"""
        cache_key = f"extract_name:{hash(text)}"
        cached_result = await cache_manager.get(cache_key)
        
        if cached_result:
            return cached_result
        
        system_prompt = """
        你是一个企业名称提取专家。请从用户输入的文本中提取企业名称。
        
        提取规则：
        1. 企业名称通常包含"有限公司"、"股份有限公司"、"集团"、"企业"等后缀
        2. 优先提取完整的企业全称
        3. 如果有多个企业名称，选择最主要的一个
        4. 如果没有找到明确的企业名称，返回"未找到"
        5. 只返回企业名称，不要添加任何解释
        """
        
        try:
            response = await self._call_llm(
                system_prompt=system_prompt,
                user_prompt=text,
                temperature=0.1,
                max_tokens=100
            )
            
            enterprise_name = response.strip()
            if enterprise_name and enterprise_name != "未找到":
                # 缓存结果1小时
                await cache_manager.set(cache_key, enterprise_name, expire=3600)
                logger.info(f"Extracted enterprise name: {enterprise_name}")
                return enterprise_name
            else:
                await cache_manager.set(cache_key, None, expire=3600)
                return None
                
        except Exception as e:
            logger.error(f"Error extracting enterprise name: {str(e)}")
            return None
    
    async def _call_llm(self, 
                       system_prompt: str, 
                       user_prompt: str, 
                       temperature: float = None,
                       max_tokens: int = None) -> str:
        """调用大语言模型"""
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "top_p": self.config.top_p
        }
        
        for attempt in range(self.config.max_retries):
            try:
                async with self.session.post(
                    f"{self.config.base_url}/chat/completions",
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    elif response.status == 429:  # Rate limit
                        wait_time = 2 ** attempt
                        logger.warning(f"LLM rate limited, waiting {wait_time}s before retry {attempt + 1}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        error_text = await response.text()
                        logger.error(f"DeepSeek API error {response.status}: {error_text}")
                        if attempt == self.config.max_retries - 1:
                            raise Exception(f"LLM API调用失败: {response.status}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"LLM request timeout, attempt {attempt + 1}")
                if attempt == self.config.max_retries - 1:
                    raise Exception("LLM请求超时")
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"LLM request error: {str(e)}")
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(1)
```

## 🔧 缓存管理配置

### Redis缓存配置
```python
# utils/cache.py
import redis.asyncio as redis
import json
import pickle
from typing import Any, Optional, Union
from datetime import datetime, timedelta
from config.cache_config import CacheConfig

class CacheManager:
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_client = None
    
    async def connect(self):
        """连接Redis"""
        self.redis_client = redis.Redis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            password=self.config.redis_password,
            db=self.config.redis_db,
            decode_responses=False,
            max_connections=self.config.max_connections
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            value = await self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存值"""
        try:
            serialized_value = pickle.dumps(value)
            await self.redis_client.setex(key, expire, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False

# 全局缓存管理器实例
cache_manager = CacheManager(CacheConfig())
```

## 📝 配置文件示例

### 环境变量配置 (.env)
```bash
# 博查AI配置
BOCHAAI_API_KEY=your_bochaai_api_key_here
BOCHAAI_BASE_URL=https://api.bochaai.com/v1
BOCHAAI_TIMEOUT=30
BOCHAAI_MAX_RETRIES=3

# DeepSeek配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TIMEOUT=60
DEEPSEEK_MAX_RETRIES=3
DEEPSEEK_TEMPERATURE=0.1
DEEPSEEK_MAX_TOKENS=2000

# Redis缓存配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_MAX_CONNECTIONS=20

# 数据库配置
DATABASE_URL=mysql+asyncio://user:password@localhost:3306/city_brain_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
```

### Docker Compose配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: city_brain_db
      MYSQL_USER: city_brain_user
      MYSQL_PASSWORD: city_brain_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      
  city_brain_backend:
    build: .
    ports:
      - "9003:9003"
    environment:
      - DATABASE_URL=mysql+asyncio://city_brain_user:city_brain_password@mysql:3306/city_brain_db
      - REDIS_HOST=redis
    depends_on:
      - redis
      - mysql
    volumes:
      - ./logs:/app/logs

volumes:
  redis_data:
  mysql_data:
```

---

*文档版本：v1.0*
*更新时间：2025年9月26日*