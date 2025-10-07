"""
AS和IPG商机仓储
提供对feishu_crm数据库中商机数据的访问
"""
import logging
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import mysql.connector
from mysql.connector import pooling

from infrastructure.database.models.opportunities import ASOpportunity, IPGClient

logger = logging.getLogger(__name__)


class OpportunitiesRepository:
    """商机数据仓储（AS和IPG系统）"""

    def __init__(self):
        """初始化仓储，连接到feishu_crm数据库"""
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "3306"))
        self.username = os.getenv("DB_USERNAME", "root")
        self.password = os.getenv("DB_PASSWORD", "1qaz2wsx")
        self.database = "feishu_crm"  # 固定连接到feishu_crm数据库
        self.charset = "utf8mb4"
        self._connection_pool = None

    def _create_connection_pool(self):
        """创建数据库连接池"""
        if self._connection_pool is None:
            try:
                pool_config = {
                    'pool_name': 'opportunities_pool',
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
                logger.info(f"商机数据库连接池创建成功: {self.host}:{self.port}/{self.database}")
            except Exception as e:
                logger.error(f"创建商机数据库连接池失败: {e}")
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

    # ==================== AS商机相关方法 ====================

    def find_as_opportunities_by_customer(self, customer_name: str, limit: int = 20) -> List[ASOpportunity]:
        """
        根据客户名称查找AS商机（支持模糊匹配）

        Args:
            customer_name: 客户名称
            limit: 返回结果数量限制

        Returns:
            AS商机列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                # 优先精确匹配
                query = """
                SELECT * FROM as_opportunities
                WHERE customer_name = %s
                ORDER BY create_time DESC
                LIMIT %s
                """
                cursor.execute(query, (customer_name, limit))
                results = cursor.fetchall()

                # 如果精确匹配无结果，尝试模糊匹配
                if not results:
                    query = """
                    SELECT * FROM as_opportunities
                    WHERE customer_name LIKE %s
                    ORDER BY create_time DESC
                    LIMIT %s
                    """
                    cursor.execute(query, (f"%{customer_name}%", limit))
                    results = cursor.fetchall()

                cursor.close()
                return [ASOpportunity.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"查询AS商机失败: {e}")
            return []

    def search_as_opportunities(self, keyword: str, limit: int = 20) -> List[ASOpportunity]:
        """
        搜索AS商机（支持客户名称、产品名称、行业、合作伙伴）

        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制

        Returns:
            AS商机列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM as_opportunities
                WHERE customer_name LIKE %s
                   OR product_name LIKE %s
                   OR industry LIKE %s
                   OR partner_name LIKE %s
                   OR area LIKE %s
                ORDER BY create_time DESC
                LIMIT %s
                """
                search_pattern = f"%{keyword}%"
                cursor.execute(query, (search_pattern, search_pattern, search_pattern,
                                      search_pattern, search_pattern, limit))
                results = cursor.fetchall()
                cursor.close()

                return [ASOpportunity.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"搜索AS商机失败: {e}")
            return []

    def get_as_opportunities_by_partner(self, partner_name: str, limit: int = 20) -> List[ASOpportunity]:
        """
        根据合作伙伴获取AS商机列表

        Args:
            partner_name: 合作伙伴名称
            limit: 返回结果数量限制

        Returns:
            AS商机列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM as_opportunities
                WHERE partner_name LIKE %s
                ORDER BY create_time DESC
                LIMIT %s
                """
                cursor.execute(query, (f"%{partner_name}%", limit))
                results = cursor.fetchall()
                cursor.close()

                return [ASOpportunity.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"按合作伙伴查询AS商机失败: {e}")
            return []

    def get_as_opportunities_by_area(self, area: str, limit: int = 20) -> List[ASOpportunity]:
        """
        根据地区获取AS商机列表

        Args:
            area: 地区名称
            limit: 返回结果数量限制

        Returns:
            AS商机列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM as_opportunities
                WHERE area LIKE %s
                ORDER BY create_time DESC
                LIMIT %s
                """
                cursor.execute(query, (f"%{area}%", limit))
                results = cursor.fetchall()
                cursor.close()

                return [ASOpportunity.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"按地区查询AS商机失败: {e}")
            return []

    # ==================== IPG商机相关方法 ====================

    def find_ipg_clients_by_name(self, client_name: str, limit: int = 20) -> List[IPGClient]:
        """
        根据客户名称查找IPG商机（支持模糊匹配）

        Args:
            client_name: 客户名称
            limit: 返回结果数量限制

        Returns:
            IPG商机列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                # 优先精确匹配
                query = """
                SELECT * FROM ipg_clients
                WHERE client_name = %s AND (is_deleted = 0 OR is_deleted IS NULL)
                ORDER BY create_time DESC
                LIMIT %s
                """
                cursor.execute(query, (client_name, limit))
                results = cursor.fetchall()

                # 如果精确匹配无结果，尝试模糊匹配
                if not results:
                    query = """
                    SELECT * FROM ipg_clients
                    WHERE client_name LIKE %s AND (is_deleted = 0 OR is_deleted IS NULL)
                    ORDER BY create_time DESC
                    LIMIT %s
                    """
                    cursor.execute(query, (f"%{client_name}%", limit))
                    results = cursor.fetchall()

                cursor.close()
                return [IPGClient.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"查询IPG商机失败: {e}")
            return []

    def search_ipg_clients(self, keyword: str, limit: int = 20) -> List[IPGClient]:
        """
        搜索IPG商机（支持客户名称、产品、行业、代理商）

        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制

        Returns:
            IPG商机列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM ipg_clients
                WHERE (client_name LIKE %s
                   OR sell_product LIKE %s
                   OR trade LIKE %s
                   OR reseller_name LIKE %s
                   OR location_province LIKE %s)
                AND (is_deleted = 0 OR is_deleted IS NULL)
                ORDER BY create_time DESC
                LIMIT %s
                """
                search_pattern = f"%{keyword}%"
                cursor.execute(query, (search_pattern, search_pattern, search_pattern,
                                      search_pattern, search_pattern, limit))
                results = cursor.fetchall()
                cursor.close()

                return [IPGClient.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"搜索IPG商机失败: {e}")
            return []

    def get_ipg_clients_by_reseller(self, reseller_name: str, limit: int = 20) -> List[IPGClient]:
        """
        根据代理商获取IPG商机列表

        Args:
            reseller_name: 代理商名称
            limit: 返回结果数量限制

        Returns:
            IPG商机列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM ipg_clients
                WHERE reseller_name LIKE %s AND (is_deleted = 0 OR is_deleted IS NULL)
                ORDER BY create_time DESC
                LIMIT %s
                """
                cursor.execute(query, (f"%{reseller_name}%", limit))
                results = cursor.fetchall()
                cursor.close()

                return [IPGClient.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"按代理商查询IPG商机失败: {e}")
            return []

    def get_ipg_clients_by_province(self, province: str, limit: int = 20) -> List[IPGClient]:
        """
        根据省份获取IPG商机列表

        Args:
            province: 省份名称
            limit: 返回结果数量限制

        Returns:
            IPG商机列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM ipg_clients
                WHERE location_province LIKE %s AND (is_deleted = 0 OR is_deleted IS NULL)
                ORDER BY create_time DESC
                LIMIT %s
                """
                cursor.execute(query, (f"%{province}%", limit))
                results = cursor.fetchall()
                cursor.close()

                return [IPGClient.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"按省份查询IPG商机失败: {e}")
            return []

    # ==================== 统计方法 ====================

    def get_as_statistics(self) -> Dict[str, Any]:
        """
        获取AS商机统计信息

        Returns:
            统计信息字典
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT
                    COUNT(*) as total_count,
                    COUNT(DISTINCT customer_name) as unique_customers,
                    COUNT(DISTINCT partner_name) as partner_count,
                    COUNT(DISTINCT area) as area_count,
                    SUM(budget) as total_budget,
                    AVG(budget) as avg_budget
                FROM as_opportunities
                """
                cursor.execute(query)
                result = cursor.fetchone()
                cursor.close()

                # 转换Decimal为float
                if result:
                    if result.get('total_budget'):
                        result['total_budget'] = float(result['total_budget'])
                    if result.get('avg_budget'):
                        result['avg_budget'] = float(result['avg_budget'])

                return result if result else {}

        except Exception as e:
            logger.error(f"获取AS商机统计信息失败: {e}")
            return {}

    def get_ipg_statistics(self) -> Dict[str, Any]:
        """
        获取IPG商机统计信息

        Returns:
            统计信息字典
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT
                    COUNT(*) as total_count,
                    COUNT(DISTINCT client_name) as unique_clients,
                    COUNT(DISTINCT reseller_name) as reseller_count,
                    COUNT(DISTINCT location_province) as province_count,
                    SUM(agent_num) as total_agents,
                    AVG(agent_num) as avg_agents
                FROM ipg_clients
                WHERE is_deleted = 0 OR is_deleted IS NULL
                """
                cursor.execute(query)
                result = cursor.fetchone()
                cursor.close()

                return result if result else {}

        except Exception as e:
            logger.error(f"获取IPG商机统计信息失败: {e}")
            return {}

    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                logger.info("商机数据库连接测试成功")
                return True
        except Exception as e:
            logger.error(f"商机数据库连接测试失败: {e}")
            return False
