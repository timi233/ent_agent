"""
基础仓储类
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from database.connection import get_db_connection


class BaseRepository(ABC):
    """基础仓储抽象类"""
    
    def __init__(self):
        self._connection = None
        self._cursor = None
    
    def _get_connection(self):
        """获取数据库连接"""
        if not self._connection:
            self._connection = get_db_connection()
        return self._connection
    
    def _get_cursor(self, dictionary=True):
        """获取数据库游标"""
        if not self._cursor:
            connection = self._get_connection()
            self._cursor = connection.cursor(dictionary=dictionary)
        return self._cursor
    
    def _execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行查询并返回结果"""
        cursor = self._get_cursor()
        cursor.execute(query, params or ())
        return cursor.fetchall()
    
    def _execute_single_query(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """执行查询并返回单个结果"""
        cursor = self._get_cursor()
        cursor.execute(query, params or ())
        return cursor.fetchone()
    
    def _execute_update(self, query: str, params: tuple = None) -> bool:
        """执行更新操作"""
        cursor = self._get_cursor(dictionary=False)
        connection = self._get_connection()
        
        try:
            cursor.execute(query, params or ())
            connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            connection.rollback()
            raise e
    
    def _execute_insert(self, query: str, params: tuple = None) -> int:
        """执行插入操作并返回插入的ID"""
        cursor = self._get_cursor(dictionary=False)
        connection = self._get_connection()
        
        try:
            cursor.execute(query, params or ())
            connection.commit()
            return cursor.lastrowid
        except Exception as e:
            connection.rollback()
            raise e
    
    def close(self):
        """关闭数据库连接"""
        if self._cursor:
            self._cursor.close()
            self._cursor = None
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()