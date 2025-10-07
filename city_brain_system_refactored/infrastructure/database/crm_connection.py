"""
CRM数据库连接管理模块
"""
import logging
from typing import Optional, Dict, Any, List
import pymysql
from pymysql.cursors import DictCursor
from config.settings import get_settings

logger = logging.getLogger(__name__)


class CRMDatabaseConnection:
    """CRM数据库连接管理器"""
    
    def __init__(self):
        self.settings = get_settings().crm_database
        self._connection: Optional[pymysql.Connection] = None
    
    def get_connection(self) -> pymysql.Connection:
        """获取数据库连接"""
        if self._connection is None or not self._connection.open:
            try:
                self._connection = pymysql.connect(
                    host=self.settings.host,
                    port=self.settings.port,
                    user=self.settings.username,
                    password=self.settings.password,
                    database=self.settings.database,
                    charset=self.settings.charset,
                    cursorclass=DictCursor,
                    autocommit=True,
                    connect_timeout=self.settings.pool_timeout
                )
                logger.info(f"CRM数据库连接成功: {self.settings.host}:{self.settings.port}/{self.settings.database}")
            except Exception as e:
                logger.error(f"CRM数据库连接失败: {e}")
                raise
        
        return self._connection
    
    def close_connection(self):
        """关闭数据库连接"""
        if self._connection and self._connection.open:
            self._connection.close()
            self._connection = None
            logger.info("CRM数据库连接已关闭")
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"CRM数据库连接测试失败: {e}")
            return False
    
    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """执行查询并返回结果"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, params or {})
                results = cursor.fetchall()
                logger.debug(f"CRM查询执行成功，返回 {len(results)} 条记录")
                return results
        except Exception as e:
            logger.error(f"CRM查询执行失败: {e}")
            raise
    
    def execute_count_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> int:
        """执行计数查询"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, params or {})
                result = cursor.fetchone()
                return result.get('count', 0) if result else 0
        except Exception as e:
            logger.error(f"CRM计数查询执行失败: {e}")
            raise


# 全局CRM连接实例
_crm_connection: Optional[CRMDatabaseConnection] = None


def get_crm_connection() -> CRMDatabaseConnection:
    """获取CRM数据库连接实例"""
    global _crm_connection
    if _crm_connection is None:
        _crm_connection = CRMDatabaseConnection()
    return _crm_connection


def close_crm_connection():
    """关闭CRM数据库连接"""
    global _crm_connection
    if _crm_connection:
        _crm_connection.close_connection()
        _crm_connection = None