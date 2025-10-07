"""
简化的数据库连接管理模块
不依赖复杂的ORM，使用基础的mysql.connector
"""
import logging
import os
from typing import Optional, Dict, Any
from contextlib import contextmanager

# 尝试导入mysql.connector
try:
    import mysql.connector
    from mysql.connector import pooling
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    logging.warning("mysql-connector-python未安装，数据库功能不可用")

# 导入配置
try:
    from config.simple_settings import get_settings
except ImportError:
    # 简单的配置类作为后备 - 从环境变量读取
    class SimpleSettings:
        def __init__(self):
            self.database = type('obj', (object,), {
                'host': os.getenv("DB_HOST", "localhost"),
                'port': int(os.getenv("DB_PORT", "3306")),
                'username': os.getenv("DB_USERNAME", "root"),
                'password': os.getenv("DB_PASSWORD", "1qaz2wsx"),
                'database': os.getenv("DB_DATABASE", "City_Brain_DB"),
                'charset': os.getenv("DB_CHARSET", "utf8mb4"),
                'pool_size': int(os.getenv("DB_POOL_SIZE", "10"))
            })()
    
    def get_settings():
        return SimpleSettings()

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """数据库连接管理类"""
    
    def __init__(self):
        self.settings = get_settings().database
        self._connection_pool: Optional[pooling.MySQLConnectionPool] = None
    
    def _create_connection_pool(self):
        """创建数据库连接池"""
        if not MYSQL_AVAILABLE:
            raise RuntimeError("mysql-connector-python未安装")
            
        if self._connection_pool is None:
            try:
                pool_config = {
                    'pool_name': 'city_brain_pool',
                    'pool_size': self.settings.pool_size,
                    'pool_reset_session': True,
                    'host': self.settings.host,
                    'port': self.settings.port,
                    'user': self.settings.username,
                    'password': self.settings.password,
                    'database': self.settings.database,
                    'charset': self.settings.charset,
                    'autocommit': False,
                    'time_zone': '+08:00'
                }
                
                self._connection_pool = pooling.MySQLConnectionPool(**pool_config)
                logger.info(f"数据库连接池创建成功: {self.settings.host}:{self.settings.port}/{self.settings.database}")
                
            except Exception as e:
                logger.error(f"创建数据库连接池失败: {e}")
                raise
        
        return self._connection_pool
    
    def get_connection(self):
        """获取数据库连接"""
        if not MYSQL_AVAILABLE:
            raise RuntimeError("mysql-connector-python未安装")
            
        try:
            pool = self._create_connection_pool()
            connection = pool.get_connection()
            return connection
        except Exception as e:
            logger.error(f"获取数据库连接失败: {e}")
            raise
    
    @contextmanager
    def get_connection_context(self):
        """获取数据库连接上下文管理器"""
        if not MYSQL_AVAILABLE:
            logger.warning("数据库连接不可用，返回模拟连接")
            yield None
            return
            
        connection = None
        try:
            connection = self.get_connection()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        if not MYSQL_AVAILABLE:
            logger.warning("mysql-connector-python未安装，跳过数据库连接测试")
            return False
            
        try:
            with self.get_connection_context() as connection:
                if connection:
                    cursor = connection.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    cursor.close()
            logger.info("数据库连接测试成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False


# 全局数据库连接实例
db_connection = DatabaseConnection()


def get_database_connection() -> DatabaseConnection:
    """获取数据库连接管理器"""
    return db_connection


def test_database_connection() -> bool:
    """测试数据库连接"""
    return db_connection.test_connection()
