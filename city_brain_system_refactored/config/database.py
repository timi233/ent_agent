"""
数据库配置和连接管理
"""
from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging

from .settings import get_settings

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """数据库配置管理类"""
    
    def __init__(self):
        self.settings = get_settings().database
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
    
    def get_database_url(self) -> str:
        """构建数据库连接URL"""
        return (
            f"mysql+pymysql://{self.settings.username}:{self.settings.password}"
            f"@{self.settings.host}:{self.settings.port}/{self.settings.database}"
            f"?charset={self.settings.charset}"
        )
    
    def create_engine(self) -> Engine:
        """创建数据库引擎"""
        if self._engine is None:
            database_url = self.get_database_url()
            
            self._engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=self.settings.pool_size,
                max_overflow=self.settings.max_overflow,
                pool_timeout=self.settings.pool_timeout,
                pool_recycle=self.settings.pool_recycle,
                echo=get_settings().app.debug,  # 在调试模式下显示SQL
                echo_pool=get_settings().app.debug,
            )
            
            logger.info(f"数据库引擎创建成功: {self.settings.host}:{self.settings.port}/{self.settings.database}")
        
        return self._engine
    
    def get_session_factory(self) -> sessionmaker:
        """获取会话工厂"""
        if self._session_factory is None:
            engine = self.create_engine()
            self._session_factory = sessionmaker(
                bind=engine,
                autocommit=False,
                autoflush=False
            )
        
        return self._session_factory
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        session_factory = self.get_session_factory()
        return session_factory()
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            engine = self.create_engine()
            with engine.connect() as connection:
                connection.execute("SELECT 1")
            logger.info("数据库连接测试成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    
    def close_all_connections(self):
        """关闭所有数据库连接"""
        if self._engine:
            self._engine.dispose()
            logger.info("数据库连接已关闭")


# 全局数据库配置实例
db_config = DatabaseConfig()


def get_database_config() -> DatabaseConfig:
    """获取数据库配置实例"""
    return db_config


def get_db_session() -> Session:
    """获取数据库会话（用于依赖注入）"""
    return db_config.get_session()


def test_database_connection() -> bool:
    """测试数据库连接"""
    return db_config.test_connection()