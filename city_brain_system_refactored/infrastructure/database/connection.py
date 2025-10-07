"""
数据库连接管理模块
重构自原有的 database/connection.py，使用现代化的连接管理方式
"""
import mysql.connector
from mysql.connector import pooling
from typing import Optional, Dict, Any
import logging
from contextlib import contextmanager

from config.settings import get_settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """数据库连接管理类"""
    
    def __init__(self):
        self.settings = get_settings().database
        self._connection_pool: Optional[pooling.MySQLConnectionPool] = None
    
    def _create_connection_pool(self) -> pooling.MySQLConnectionPool:
        """创建数据库连接池"""
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
    
    def get_connection(self) -> mysql.connector.MySQLConnection:
        """获取数据库连接"""
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
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
        """执行查询语句"""
        with self.get_connection_context() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
            finally:
                cursor.close()
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """执行更新语句"""
        with self.get_connection_context() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(query, params)
                connection.commit()
                return cursor.rowcount
            except Exception as e:
                connection.rollback()
                raise
            finally:
                cursor.close()
    
    def execute_insert(self, query: str, params: Optional[tuple] = None) -> int:
        """执行插入语句，返回插入的ID"""
        with self.get_connection_context() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(query, params)
                connection.commit()
                return cursor.lastrowid
            except Exception as e:
                connection.rollback()
                raise
            finally:
                cursor.close()
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.get_connection_context() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
            logger.info("数据库连接测试成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    
    def close_pool(self):
        """关闭连接池"""
        if self._connection_pool:
            # MySQL连接池没有直接的关闭方法，但可以通过设置为None来释放
            self._connection_pool = None
            logger.info("数据库连接池已关闭")


# 全局数据库连接实例
db_connection = DatabaseConnection()


class DatabaseManager:
    """向后兼容的数据库管理器"""

    def __init__(self, connection: Optional[DatabaseConnection] = None):
        self._connection = connection or db_connection

    def get_connection(self):
        """获取数据库连接"""
        return self._connection.get_connection()

    def return_connection(self, connection) -> None:
        """释放数据库连接"""
        if connection and getattr(connection, "is_connected", lambda: False)():
            connection.close()


def get_db_connection() -> mysql.connector.MySQLConnection:
    """获取数据库连接（保持向后兼容）"""
    return db_connection.get_connection()


def get_database_connection() -> DatabaseConnection:
    """获取数据库连接管理器"""
    return db_connection


def test_database_connection() -> bool:
    """测试数据库连接"""
    return db_connection.test_connection()


def test_connection() -> bool:
    """测试数据库连接（简化函数名）"""
    return db_connection.test_connection()


def close_all_connections():
    """关闭所有数据库连接"""
    db_connection.close_pool()
