"""
基础仓储类
重构自原有的 database/repositories/base_repository.py，增强错误处理和连接管理
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Union
from contextlib import contextmanager
import logging

from ..connection import DatabaseManager

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """基础仓储抽象类"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        初始化仓储
        
        Args:
            db_manager: 数据库管理器实例，如果为None则使用默认实例
        """
        self._db_manager = db_manager or DatabaseManager()
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接的上下文管理器"""
        connection = None
        try:
            connection = self._db_manager.get_connection()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if connection:
                self._db_manager.return_connection(connection)
    
    def _execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        执行查询并返回结果列表
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        with self._get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                logger.debug(f"查询执行成功，返回 {len(results)} 条记录")
                return results
            finally:
                cursor.close()
    
    def _execute_single_query(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        执行查询并返回单个结果
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            单个查询结果或None
        """
        with self._get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                result = cursor.fetchone()
                logger.debug(f"单条查询执行成功，结果: {'存在' if result else '不存在'}")
                return result
            finally:
                cursor.close()
    
    def _execute_update(self, query: str, params: tuple = None) -> bool:
        """
        执行更新操作
        
        Args:
            query: SQL更新语句
            params: 更新参数
            
        Returns:
            是否更新成功（影响行数 > 0）
        """
        with self._get_connection() as connection:
            cursor = connection.cursor(dictionary=False)
            try:
                cursor.execute(query, params or ())
                connection.commit()
                affected_rows = cursor.rowcount
                logger.debug(f"更新操作完成，影响行数: {affected_rows}")
                return affected_rows > 0
            except Exception as e:
                connection.rollback()
                logger.error(f"更新操作失败: {e}")
                raise
            finally:
                cursor.close()
    
    def _execute_insert(self, query: str, params: tuple = None) -> int:
        """
        执行插入操作并返回插入的ID
        
        Args:
            query: SQL插入语句
            params: 插入参数
            
        Returns:
            插入记录的ID
        """
        with self._get_connection() as connection:
            cursor = connection.cursor(dictionary=False)
            try:
                cursor.execute(query, params or ())
                connection.commit()
                insert_id = cursor.lastrowid
                logger.debug(f"插入操作完成，新记录ID: {insert_id}")
                return insert_id
            except Exception as e:
                connection.rollback()
                logger.error(f"插入操作失败: {e}")
                raise
            finally:
                cursor.close()
    
    def _execute_batch_insert(self, query: str, params_list: List[tuple]) -> int:
        """
        执行批量插入操作
        
        Args:
            query: SQL插入语句
            params_list: 参数列表
            
        Returns:
            插入的记录数量
        """
        if not params_list:
            return 0
            
        with self._get_connection() as connection:
            cursor = connection.cursor(dictionary=False)
            try:
                cursor.executemany(query, params_list)
                connection.commit()
                affected_rows = cursor.rowcount
                logger.debug(f"批量插入操作完成，插入记录数: {affected_rows}")
                return affected_rows
            except Exception as e:
                connection.rollback()
                logger.error(f"批量插入操作失败: {e}")
                raise
            finally:
                cursor.close()
    
    def _execute_transaction(self, operations: List[Dict[str, Any]]) -> bool:
        """
        执行事务操作
        
        Args:
            operations: 操作列表，每个操作包含 'query' 和 'params'
            
        Returns:
            事务是否执行成功
        """
        with self._get_connection() as connection:
            cursor = connection.cursor(dictionary=False)
            try:
                for operation in operations:
                    query = operation['query']
                    params = operation.get('params', ())
                    cursor.execute(query, params)
                
                connection.commit()
                logger.debug(f"事务执行成功，包含 {len(operations)} 个操作")
                return True
            except Exception as e:
                connection.rollback()
                logger.error(f"事务执行失败: {e}")
                raise
            finally:
                cursor.close()
    
    def _count_records(self, table: str, where_clause: str = "", params: tuple = None) -> int:
        """
        统计记录数量
        
        Args:
            table: 表名
            where_clause: WHERE子句（不包含WHERE关键字）
            params: 查询参数
            
        Returns:
            记录数量
        """
        query = f"SELECT COUNT(*) as count FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        result = self._execute_single_query(query, params)
        return result['count'] if result else 0
    
    def _exists(self, table: str, where_clause: str, params: tuple = None) -> bool:
        """
        检查记录是否存在
        
        Args:
            table: 表名
            where_clause: WHERE子句（不包含WHERE关键字）
            params: 查询参数
            
        Returns:
            记录是否存在
        """
        return self._count_records(table, where_clause, params) > 0