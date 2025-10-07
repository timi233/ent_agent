# 后端技术实现方案

## 📋 概述

本文档详细描述了城市大脑企业信息处理系统后端的技术实现方案，包括FastAPI应用架构、服务层设计、AI服务集成和数据处理流程。

## 🏗️ 应用架构设计

### 项目结构
```
city_brain_system/
├── main.py                 # 应用入口
├── config/
│   ├── __init__.py
│   ├── settings.py         # 配置管理
│   └── database.py         # 数据库配置
├── models/
│   ├── __init__.py
│   ├── enterprise.py       # 企业模型
│   ├── address.py          # 地址模型
│   ├── industry.py         # 行业模型
│   └── data_quality.py     # 数据质量模型
├── schemas/
│   ├── __init__.py
│   ├── enterprise.py       # 企业Schema
│   ├── address.py          # 地址Schema
│   └── common.py           # 通用Schema
├── repositories/
│   ├── __init__.py
│   ├── base.py             # 基础Repository
│   ├── enterprise.py       # 企业Repository
│   └── data_quality.py     # 数据质量Repository
├── services/
│   ├── __init__.py
│   ├── enterprise.py       # 企业服务
│   ├── ai_service.py       # AI服务
│   ├── address.py          # 地址服务
│   └── data_quality.py     # 数据质量服务
├── routers/
│   ├── __init__.py
│   ├── enterprises.py      # 企业路由
│   ├── addresses.py        # 地址路由
│   ├── ai_services.py      # AI服务路由
│   └── data_quality.py     # 数据质量路由
├── utils/
│   ├── __init__.py
│   ├── cache.py            # 缓存工具
│   ├── logger.py           # 日志工具
│   └── validators.py       # 验证工具
├── middleware/
│   ├── __init__.py
│   ├── auth.py             # 认证中间件
│   ├── cors.py             # CORS中间件
│   └── logging.py          # 日志中间件
└── tests/
    ├── __init__.py
    ├── test_enterprises.py  # 企业测试
    └── test_ai_services.py  # AI服务测试
```

## 🚀 FastAPI 应用配置

### 主应用入口 (main.py)
```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config.settings import settings
from config.database import init_database, close_database
from utils.cache import init_cache, close_cache
from utils.logger import setup_logging
from middleware.logging import LoggingMiddleware
from routers import enterprises, addresses, industries, data_quality, ai_services

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    setup_logging()
    await init_database()
    await init_cache()
    
    yield
    
    # 关闭时清理
    await close_database()
    await close_cache()

app = FastAPI(
    title="城市大脑企业信息处理系统",
    description="智能化企业信息查询和产业链分析平台",
    version="2.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(LoggingMiddleware)

# 路由注册
app.include_router(
    enterprises.router, 
    prefix="/api/v1/enterprises", 
    tags=["enterprises"]
)
app.include_router(
    addresses.router, 
    prefix="/api/v1/addresses", 
    tags=["addresses"]
)
app.include_router(
    industries.router, 
    prefix="/api/v1/industries", 
    tags=["industries"]
)
app.include_router(
    data_quality.router, 
    prefix="/api/v1/data-quality", 
    tags=["data-quality"]
)
app.include_router(
    ai_services.router, 
    prefix="/api/v1/ai", 
    tags=["ai-services"]
)

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "version": "2.0.0"}

@app.get("/ready")
async def readiness_check():
    """就绪检查端点"""
    # 检查数据库连接
    # 检查Redis连接
    # 检查外部API连接
    return {"status": "ready"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1
    )
```

### 配置管理 (config/settings.py)
```python
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "城市大脑企业信息处理系统"
    VERSION: str = "2.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 9003
    WORKERS: int = 4
    
    # 数据库配置
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10
    
    # AI服务配置
    BOCHAAI_API_KEY: str
    BOCHAAI_BASE_URL: str = "https://api.bochaai.com/v1"
    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    
    # 安全配置
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: Optional[str] = None
    LOG_ROTATION: str = "1 day"
    LOG_RETENTION: str = "30 days"
    
    # 缓存配置
    CACHE_TTL: int = 3600  # 1小时
    SEARCH_CACHE_TTL: int = 86400  # 24小时
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".xlsx", ".xls", ".csv"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

## 🗄️ 数据模型定义

### 企业模型 (models/enterprise.py)
```python
from sqlalchemy import Column, BigInteger, String, Enum, Decimal, Date, Text, Boolean, TIMESTAMP, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
import enum

class EnterpriseType(str, enum.Enum):
    CUSTOMER = "customer"
    CHAIN_LEADER = "chain_leader"
    SUPPLIER = "supplier"
    OTHER = "other"

class EnterpriseStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MERGED = "merged"
    DISSOLVED = "dissolved"

class DataSource(str, enum.Enum):
    MANUAL = "manual"
    WEB_SEARCH = "web_search"
    API = "api"
    IMPORT = "import"

class Enterprise(Base):
    __tablename__ = "enterprise"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="企业ID")
    name = Column(String(255), nullable=False, comment="企业名称")
    unified_social_credit_code = Column(String(32), unique=True, comment="统一社会信用代码")
    enterprise_type = Column(Enum(EnterpriseType), nullable=False, comment="企业类型")
    status = Column(Enum(EnterpriseStatus), default=EnterpriseStatus.ACTIVE, comment="企业状态")
    registration_capital = Column(Decimal(15, 2), comment="注册资本")
    establishment_date = Column(Date, comment="成立日期")
    business_scope = Column(Text, comment="经营范围")
    legal_representative = Column(String(100), comment="法定代表人")
    contact_phone = Column(String(50), comment="联系电话")
    contact_email = Column(String(100), comment="联系邮箱")
    website = Column(String(255), comment="官方网站")
    employee_count = Column(BigInteger, comment="员工数量")
    annual_revenue = Column(Decimal(15, 2), comment="年营收")
    data_source = Column(Enum(DataSource), nullable=False, default=DataSource.MANUAL, comment="数据来源")
    import_batch = Column(String(50), comment="导入批次")
    confidence_score = Column(Decimal(3, 2), default=1.00, comment="数据可信度")
    verified_at = Column(TIMESTAMP, comment="验证时间")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    addresses = relationship("EnterpriseAddress", back_populates="enterprise", cascade="all, delete-orphan")
    source_relationships = relationship("EnterpriseRelationship", foreign_keys="EnterpriseRelationship.source_enterprise_id")
    target_relationships = relationship("EnterpriseRelationship", foreign_keys="EnterpriseRelationship.target_enterprise_id")
    
    # 索引
    __table_args__ = (
        Index('idx_enterprise_name', 'name'),
        Index('idx_enterprise_type', 'enterprise_type'),
        Index('idx_enterprise_credit_code', 'unified_social_credit_code'),
        Index('idx_enterprise_status', 'status'),
        Index('idx_enterprise_batch', 'import_batch'),
        Index('idx_enterprise_name_type', 'name', 'enterprise_type'),
        {'comment': '统一企业信息表'}
    )
    
    def __repr__(self):
        return f"<Enterprise(id={self.id}, name='{self.name}', type='{self.enterprise_type}')>"
```

### 地址模型 (models/address.py)
```python
from sqlalchemy import Column, BigInteger, String, Enum, Decimal, Boolean, TIMESTAMP, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
import enum

class AddressType(str, enum.Enum):
    REGISTERED = "registered"
    OFFICE = "office"
    FACTORY = "factory"
    BRANCH = "branch"

class EnterpriseAddress(Base):
    __tablename__ = "enterprise_address"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="地址ID")
    enterprise_id = Column(BigInteger, ForeignKey("enterprise.id", ondelete="CASCADE"), nullable=False, comment="企业ID")
    address_type = Column(Enum(AddressType), nullable=False, comment="地址类型")
    province = Column(String(50), comment="省份")
    city = Column(String(50), comment="城市")
    district = Column(String(50), comment="区县")
    street = Column(String(100), comment="街道")
    detailed_address = Column(String(500), comment="详细地址")
    postal_code = Column(String(10), comment="邮政编码")
    longitude = Column(Decimal(10, 7), comment="经度")
    latitude = Column(Decimal(10, 7), comment="纬度")
    data_source = Column(Enum(DataSource), nullable=False, comment="数据来源")
    confidence_score = Column(Decimal(3, 2), default=1.00, comment="数据可信度")
    verified_at = Column(TIMESTAMP, comment="验证时间")
    is_primary = Column(Boolean, default=False, comment="是否主要地址")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    enterprise = relationship("Enterprise", back_populates="addresses")
    
    # 索引
    __table_args__ = (
        Index('idx_address_enterprise_type', 'enterprise_id', 'address_type'),
        Index('idx_address_location', 'province', 'city', 'district'),
        Index('idx_address_coordinates', 'longitude', 'latitude'),
        Index('idx_address_enterprise_primary', 'enterprise_id', 'is_primary'),
        {'comment': '企业地址信息表'}
    )
    
    def __repr__(self):
        return f"<EnterpriseAddress(id={self.id}, enterprise_id={self.enterprise_id}, type='{self.address_type}')>"
```

## 🔧 Repository 模式实现

### 基础 Repository (repositories/base.py)
```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Type, TypeVar, Generic
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc, asc
from config.database import Base
from utils.logger import get_logger

T = TypeVar('T', bound=Base)
logger = get_logger(__name__)

class BaseRepository(Generic[T], ABC):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
    
    async def create(self, obj_data: Dict[str, Any]) -> T:
        """创建记录"""
        try:
            db_obj = self.model(**obj_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info(f"Created {self.model.__name__} with id: {db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """根据ID获取记录"""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by id {id}: {str(e)}")
            raise
    
    async def get_all(self, skip: int = 0, limit: int = 100, **filters) -> List[T]:
        """获取所有记录"""
        try:
            query = self.db.query(self.model)
            
            # 应用过滤器
            if filters:
                query = self._apply_filters(query, filters)
            
            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model.__name__}: {str(e)}")
            raise
    
    async def update(self, id: int, obj_data: Dict[str, Any]) -> Optional[T]:
        """更新记录"""
        try:
            db_obj = await self.get_by_id(id)
            if db_obj:
                for field, value in obj_data.items():
                    if hasattr(db_obj, field):
                        setattr(db_obj, field, value)
                
                self.db.commit()
                self.db.refresh(db_obj)
                logger.info(f"Updated {self.model.__name__} with id: {id}")
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model.__name__} with id {id}: {str(e)}")
            raise
    
    async def delete(self, id: int) -> bool:
        """删除记录"""
        try:
            db_obj = await self.get_by_id(id)
            if db_obj:
                self.db.delete(db_obj)
                self.db.commit()
                logger.info(f"Deleted {self.model.__name__} with id: {id}")
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with id {id}: {str(e)}")
            raise
    
    async def count(self, **filters) -> int:
        """统计记录数量"""
        try:
            query = self.db.query(self.model)
            if filters:
                query = self._apply_filters(query, filters)
            return query.count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            raise
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """应用过滤器"""
        for field, value in filters.items():
            if hasattr(self.model, field):
                if isinstance(value, list):
                    query = query.filter(getattr(self.model, field).in_(value))
                elif isinstance(value, dict):
                    # 支持范围查询
                    if 'gte' in value:
                        query = query.filter(getattr(self.model, field) >= value['gte'])
                    if 'lte' in value:
                        query = query.filter(getattr(self.model, field) <= value['lte'])
                    if 'like' in value:
                        query = query.filter(getattr(self.model, field).like(f"%{value['like']}%"))
                else:
                    query = query.filter(getattr(self.model, field) == value)
        return query
```

### 企业 Repository (repositories/enterprise.py)
```python
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from .base import BaseRepository
from models.enterprise import Enterprise, EnterpriseType, EnterpriseStatus
from models.address import EnterpriseAddress
from utils.logger import get_logger

logger = get_logger(__name__)

class EnterpriseRepository(BaseRepository[Enterprise]):
    def __init__(self, db: Session):
        super().__init__(db, Enterprise)
    
    async def search_by_name(self, name: str, fuzzy: bool = True, limit: int = 50) -> List[Enterprise]:
        """根据名称搜索企业"""
        try:
            query = self.db.query(Enterprise)
            
            if fuzzy:
                # 模糊搜索
                query = query.filter(
                    or_(
                        Enterprise.name.contains(name),
                        Enterprise.business_scope.contains(name)
                    )
                )
            else:
                # 精确搜索
                query = query.filter(Enterprise.name == name)
            
            return query.limit(limit).all()
        except Exception as e:
            logger.error(f"Error searching enterprises by name '{name}': {str(e)}")
            raise
    
    async def get_with_addresses(self, enterprise_id: int) -> Optional[Enterprise]:
        """获取企业及其地址信息"""
        try:
            return self.db.query(Enterprise)\
                .options(joinedload(Enterprise.addresses))\
                .filter(Enterprise.id == enterprise_id)\
                .first()
        except Exception as e:
            logger.error(f"Error getting enterprise with addresses for id {enterprise_id}: {str(e)}")
            raise
    
    async def get_by_type(self, enterprise_type: EnterpriseType, limit: int = 100) -> List[Enterprise]:
        """根据企业类型获取企业列表"""
        try:
            return self.db.query(Enterprise)\
                .filter(Enterprise.enterprise_type == enterprise_type)\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error getting enterprises by type '{enterprise_type}': {str(e)}")
            raise
    
    async def get_chain_leaders_by_city(self, city: str) -> List[Enterprise]:
        """根据城市获取链主企业"""
        try:
            return self.db.query(Enterprise)\
                .join(EnterpriseAddress)\
                .filter(
                    and_(
                        Enterprise.enterprise_type == EnterpriseType.CHAIN_LEADER,
                        EnterpriseAddress.city == city
                    )
                )\
                .all()
        except Exception as e:
            logger.error(f"Error getting chain leaders by city '{city}': {str(e)}")
            raise
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取企业统计信息"""
        try:
            total_count = self.db.query(func.count(Enterprise.id)).scalar()
            
            type_stats = self.db.query(
                Enterprise.enterprise_type,
                func.count(Enterprise.id).label('count')
            ).group_by(Enterprise.enterprise_type).all()
            
            status_stats = self.db.query(
                Enterprise.status,
                func.count(Enterprise.id).label('count')
            ).group_by(Enterprise.status).all()
            
            return {
                'total_count': total_count,
                'by_type': {stat.enterprise_type: stat.count for stat in type_stats},
                'by_status': {stat.status: stat.count for stat in status_stats}
            }
        except Exception as e:
            logger.error(f"Error getting enterprise statistics: {str(e)}")
            raise
    
    async def check_duplicate_by_name(self, name: str, exclude_id: Optional[int] = None) -> Optional[Enterprise]:
        """检查重复企业名称"""
        try:
            query = self.db.query(Enterprise).filter(Enterprise.name == name)
            
            if exclude_id:
                query = query.filter(Enterprise.id != exclude_id)
            
            return query.first()
        except Exception as e:
            logger.error(f"Error checking duplicate enterprise name '{name}': {str(e)}")
            raise
    
    async def batch_update_data_source(self, enterprise_ids: List[int], data_source: str, batch_id: str) -> int:
        """批量更新数据来源"""
        try:
            updated_count = self.db.query(Enterprise)\
                .filter(Enterprise.id.in_(enterprise_ids))\
                .update({
                    'data_source': data_source,
                    'import_batch': batch_id
                }, synchronize_session=False)
            
            self.db.commit()
            logger.info(f"Batch updated {updated_count} enterprises with data_source: {data_source}")
            return updated_count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error batch updating enterprises: {str(e)}")
            raise
```

## 🤖 AI服务集成

### AI服务 (services/ai_service.py)
```python
import asyncio
import aiohttp
import json
import re
from typing import Dict, List, Optional, Any
from config.settings import settings
from utils.cache import cache_manager
from utils.logger import get_logger

logger = get_logger(__name__)

class AIService:
    def __init__(self):
        self.bochaai_api_key = settings.BOCHAAI_API_KEY
        self.deepseek_api_key = settings.DEEPSEEK_API_KEY
        self.bochaai_base_url = settings.BOCHAAI_BASE_URL
        self.deepseek_base_url = settings.DEEPSEEK_BASE_URL
        self.session = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def search_enterprise_info(self, enterprise_name: str) -> Dict[str, Any]:
        """联网搜索企业信息"""
        cache_key = f"enterprise_search:{enterprise_name}"
        cached_result = await cache_manager.get(cache_key)
        
        if cached_result:
            logger.info(f"Cache hit for enterprise search: {enterprise_name}")
            return cached_result
        
        search_query = f"{enterprise_name} 企业信息 营收 员工 地址 联系方式"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.bochaai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": search_query,
                "summary": True,
                "freshness": "year",
                "count": 10
            }
            
            async with self.session.post(
                f"{self.bochaai_base_url}/web-search",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # 缓存结果24小时
                    await cache_manager.set(cache_key, result, expire=settings.SEARCH_CACHE_TTL)
                    logger.info(f"Successfully searched enterprise info for: {enterprise_name}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"BochaAI API error {response.status}: {error_text}")
                    raise Exception(f"搜索API调用失败: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error searching enterprise info for {enterprise_name}: {str(e)}")
            raise
    
    async def extract_structured_info(self, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """使用LLM提取结构化信息"""
        system_prompt = """
        你是一个企业信息提取专家。请从搜索结果中提取以下结构化信息：
        
        1. 企业基本信息：
           - 企业全称
           - 统一社会信用代码
           - 注册资本
           - 成立时间
           - 法定代表人
           - 经营范围
        
        2. 经营信息：
           - 年营收
           - 员工数量
           - 主营业务
           - 行业分类
        
        3. 地址信息：
           - 注册地址
           - 办公地址
           - 省市区信息
        
        4. 联系信息：
           - 联系电话
           - 邮箱地址
           - 官方网站
        
        请以JSON格式返回，确保数据准确性。如果某些信息不确定或缺失，请标注为null。
        """
        
        user_prompt = f"搜索结果：{json.dumps(search_results, ensure_ascii=False)}"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            async with self.session.post(
                f"{self.deepseek_base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    ai_content = result['choices'][0]['message']['content']
                    
                    # 解析AI返回的JSON
                    structured_info = self._parse_ai_response(ai_content)
                    logger.info("Successfully extracted structured info from search results")
                    return structured_info
                else:
                    error_text = await response.text()
                    logger.error(f"DeepSeek API error {response.status}: {error_text}")
                    raise Exception(f"AI提取API调用失败: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error extracting structured info: {str(e)}")
            raise
    
    async def extract_enterprise_name(self, text: str) -> Optional[str]:
        """从文本中提取企业名称"""
        cache_key = f"extract_name:{hash(text)}"
        cached_result = await cache_manager.get(cache_key)
        
        if cached_result:
            return cached_result
        
        system_prompt = """
        你是一个企业名称提取专家。请从用户输入的文本中提取企业名称。
        
        规则：
        1. 如果找到明确的企业名称，请直接返回企业名称，不要添加任何其他内容
        2. 企业名称通常包含"有限公司"、"股份有限公司"、"集团"等后缀
        3. 如果没有找到企业名称，请返回"未找到"
        4. 只返回一个最可能的企业名称
        """
        
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.1,
                "max_tokens": 100
            }
            
            async with self.session.post(
                f"{self.deepseek_base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    ai_content = result['choices'][0]['message']['content'].strip()
                    
                    enterprise_name = ai_content if ai_content != "未找到" else None
                    
                    # 缓存结果1小时
                    await cache_manager.set(cache_key, enterprise_name, expire=3600)
                    
                    logger.info(f"Extracted enterprise name: {enterprise_name}")
                    return enterprise_name
                else:
                    error_text = await response.text()
                    logger.error(f"DeepSeek API error {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error extracting enterprise name: {str(e)}")
            return None
    
    async def generate_enterprise_summary(self, enterprise_data: Dict[str, Any]) -> str:
        """生成企业信息结构化总结"""
        system_prompt = """
        你是一个企业分析专家。请根据提供的企业信息生成一份结构化的企业总结报告。
        
        报告应包括：
        1. 企业基本概况（名称、类型、成立时间、注册资本等）
        2. 经营状况分析（营收规模、员工规模、主营业务等）
        3. 地理位置信息（注册地址、经营地址等）
        4. 产业链位置分析（所属行业、产业大脑关联等）
        5. 联系方式信息
        
        请使用专业、客观的语言，确保信息准确性。报告应该结构清晰，便于阅读。
        """
        
        user_prompt = f"企业信息：{json.dumps(enterprise_data, ensure_ascii=False)}"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1500
            }
            
            async with self.session.post(
                f"{self.deepseek_base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    summary = result['choices'][0]['message']['content']
                    logger.info("Successfully generated enterprise summary")
                    return summary
                else:
                    error_text = await response.text()
                    logger.error(f"DeepSeek API error {response.status}: {error_text}")
                    raise Exception(f"生成总结API调用失败: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error generating enterprise summary: {str(e)}")
            raise
    
    def _parse_ai_response(self, ai_content: str) -> Dict[str, Any]:
        """解析AI返回的JSON内容"""
        try:
            # 尝试直接解析JSON
            return json.loads(ai_content)
        except json.JSONDecodeError:
            # 如果解析失败，尝试提取JSON部分
            json_match = re.search(r'\{.*\}', ai_content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # 如果都失败了，返回原始内容
            logger.warning(f"Failed to parse AI response as JSON: {ai_content}")
            return {"raw_content": ai_content}

# 创建全局AI服务实例
ai_service = AIService()
```

---

*文档版本：v1.0*
*更新时间：2025年9月26日*