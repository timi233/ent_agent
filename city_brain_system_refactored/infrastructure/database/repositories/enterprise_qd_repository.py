"""
enterprise_QD数据库的企业档案仓储
提供对青岛企业详细信息的访问
"""
import logging
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import mysql.connector
from mysql.connector import pooling

from infrastructure.database.models.enterprise_qd import EnterpriseQDProfile

logger = logging.getLogger(__name__)


class EnterpriseQDRepository:
    """enterprise_QD数据库的企业仓储"""

    def __init__(self):
        """初始化仓储，连接到enterprise_QD数据库"""
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "3306"))
        self.username = os.getenv("DB_USERNAME", "root")
        self.password = os.getenv("DB_PASSWORD", "1qaz2wsx")
        self.database = "enterprise_QD"  # 固定连接到enterprise_QD数据库
        self.charset = "utf8mb4"
        self._connection_pool = None

    def _create_connection_pool(self):
        """创建数据库连接池"""
        if self._connection_pool is None:
            try:
                pool_config = {
                    'pool_name': 'enterprise_qd_pool',
                    'pool_size': 5,
                    'pool_reset_session': True,
                    'host': self.host,
                    'port': self.port,
                    'user': self.username,
                    'password': self.password,
                    'database': self.database,
                    'charset': self.charset,
                    'autocommit': False,
                }
                self._connection_pool = pooling.MySQLConnectionPool(**pool_config)
                logger.info(f"enterprise_QD数据库连接池创建成功: {self.host}:{self.port}/{self.database}")
            except Exception as e:
                logger.error(f"创建enterprise_QD数据库连接池失败: {e}")
                raise
        return self._connection_pool

    @contextmanager
    def _get_connection(self):
        """获取数据库连接的上下文管理器"""
        connection = None
        try:
            pool = self._create_connection_pool()
            connection = pool.get_connection()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()

    def find_by_name(self, name: str) -> Optional[EnterpriseQDProfile]:
        """
        根据企业名称查找（支持模糊匹配）

        Args:
            name: 企业名称

        Returns:
            企业档案对象或None
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                # 首先尝试精确匹配
                query = """
                SELECT * FROM enterprise_profiles
                WHERE name = %s OR normalized_name = %s
                LIMIT 1
                """
                cursor.execute(query, (name, name))
                result = cursor.fetchone()

                # 如果精确匹配失败，尝试模糊匹配
                if not result:
                    query = """
                    SELECT * FROM enterprise_profiles
                    WHERE name LIKE %s OR normalized_name LIKE %s
                    ORDER BY is_complete DESC, confidence_score DESC
                    LIMIT 1
                    """
                    cursor.execute(query, (f"%{name}%", f"%{name}%"))
                    result = cursor.fetchone()

                cursor.close()

                if result:
                    return EnterpriseQDProfile.from_db_row(result)
                return None

        except Exception as e:
            logger.error(f"查询企业失败: {e}")
            return None

    def search_by_keyword(self, keyword: str, limit: int = 10) -> List[EnterpriseQDProfile]:
        """
        根据关键词搜索企业

        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制

        Returns:
            企业档案列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM enterprise_profiles
                WHERE name LIKE %s
                   OR normalized_name LIKE %s
                   OR address LIKE %s
                   OR industry LIKE %s
                ORDER BY is_complete DESC, confidence_score DESC
                LIMIT %s
                """
                search_pattern = f"%{keyword}%"
                cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern, limit))
                results = cursor.fetchall()
                cursor.close()

                return [EnterpriseQDProfile.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"搜索企业失败: {e}")
            return []

    def get_by_industry(self, industry: str, limit: int = 20) -> List[EnterpriseQDProfile]:
        """
        根据行业获取企业列表

        Args:
            industry: 行业名称
            limit: 返回结果数量限制

        Returns:
            企业档案列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM enterprise_profiles
                WHERE industry LIKE %s
                ORDER BY is_complete DESC, revenue_2023 DESC
                LIMIT %s
                """
                cursor.execute(query, (f"%{industry}%", limit))
                results = cursor.fetchall()
                cursor.close()

                return [EnterpriseQDProfile.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"按行业查询企业失败: {e}")
            return []

    def get_by_region(self, region: str, limit: int = 20) -> List[EnterpriseQDProfile]:
        """
        根据地区获取企业列表

        Args:
            region: 地区名称
            limit: 返回结果数量限制

        Returns:
            企业档案列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM enterprise_profiles
                WHERE region LIKE %s OR address LIKE %s
                ORDER BY is_complete DESC, revenue_2023 DESC
                LIMIT %s
                """
                search_pattern = f"%{region}%"
                cursor.execute(query, (search_pattern, search_pattern, limit))
                results = cursor.fetchall()
                cursor.close()

                return [EnterpriseQDProfile.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"按地区查询企业失败: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取企业数据统计信息

        Returns:
            统计信息字典
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT
                    COUNT(*) as total_count,
                    SUM(CASE WHEN is_complete = 1 THEN 1 ELSE 0 END) as complete_count,
                    SUM(CASE WHEN revenue_2023 IS NOT NULL THEN 1 ELSE 0 END) as has_revenue_count,
                    COUNT(DISTINCT industry) as industry_count,
                    COUNT(DISTINCT region) as region_count
                FROM enterprise_profiles
                """
                cursor.execute(query)
                result = cursor.fetchone()
                cursor.close()

                return result if result else {}

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}

    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                logger.info("enterprise_QD数据库连接测试成功")
                return True
        except Exception as e:
            logger.error(f"enterprise_QD数据库连接测试失败: {e}")
            return False
