"""
CRM_sync_new数据库的客户和商机仓储
提供对飞书CRM同步数据的访问
"""
import logging
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import mysql.connector
from mysql.connector import pooling

from infrastructure.database.models.crm import CRMCustomer, CRMOpportunity

logger = logging.getLogger(__name__)


class CRMSyncRepository:
    """CRM_sync_new数据库的客户和商机仓储"""

    def __init__(self):
        """初始化仓储，连接到CRM_sync_new数据库"""
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "3306"))
        self.username = os.getenv("DB_USERNAME", "root")
        self.password = os.getenv("DB_PASSWORD", "1qaz2wsx")
        self.database = "CRM_sync_new"  # 固定连接到CRM_sync_new数据库
        self.charset = "utf8mb4"
        self._connection_pool = None

    def _create_connection_pool(self):
        """创建数据库连接池"""
        if self._connection_pool is None:
            try:
                pool_config = {
                    'pool_name': 'crm_sync_pool',
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
                logger.info(f"CRM_sync_new数据库连接池创建成功: {self.host}:{self.port}/{self.database}")
            except Exception as e:
                logger.error(f"创建CRM_sync_new数据库连接池失败: {e}")
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

    # ==================== 客户相关方法 ====================

    def find_customer_by_name(self, name: str) -> Optional[CRMCustomer]:
        """
        根据客户名称查找（支持模糊匹配）

        Args:
            name: 客户名称

        Returns:
            客户对象或None
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                # 首先尝试精确匹配
                query = """
                SELECT * FROM customers
                WHERE name = %s AND (is_deleted = 0 OR is_deleted IS NULL)
                LIMIT 1
                """
                cursor.execute(query, (name,))
                result = cursor.fetchone()

                # 如果精确匹配失败，尝试模糊匹配
                if not result:
                    query = """
                    SELECT * FROM customers
                    WHERE name LIKE %s AND (is_deleted = 0 OR is_deleted IS NULL)
                    ORDER BY last_seen_at DESC
                    LIMIT 1
                    """
                    cursor.execute(query, (f"%{name}%",))
                    result = cursor.fetchone()

                cursor.close()

                if result:
                    return CRMCustomer.from_db_row(result)
                return None

        except Exception as e:
            logger.error(f"查询客户失败: {e}")
            return None

    def search_customers(self, keyword: str, limit: int = 10) -> List[CRMCustomer]:
        """
        根据关键词搜索客户

        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制

        Returns:
            客户列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM customers
                WHERE (name LIKE %s
                   OR industry LIKE %s
                   OR contact_name LIKE %s
                   OR phone LIKE %s)
                AND (is_deleted = 0 OR is_deleted IS NULL)
                ORDER BY last_seen_at DESC
                LIMIT %s
                """
                search_pattern = f"%{keyword}%"
                cursor.execute(query, (search_pattern, search_pattern, search_pattern,
                                      search_pattern, limit))
                results = cursor.fetchall()
                cursor.close()

                return [CRMCustomer.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"搜索客户失败: {e}")
            return []

    def get_customers_by_industry(self, industry: str, limit: int = 20) -> List[CRMCustomer]:
        """
        根据行业获取客户列表

        Args:
            industry: 行业名称
            limit: 返回结果数量限制

        Returns:
            客户列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM customers
                WHERE industry LIKE %s
                AND (is_deleted = 0 OR is_deleted IS NULL)
                ORDER BY last_seen_at DESC
                LIMIT %s
                """
                cursor.execute(query, (f"%{industry}%", limit))
                results = cursor.fetchall()
                cursor.close()

                return [CRMCustomer.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"按行业查询客户失败: {e}")
            return []

    def get_customers_by_owner(self, owner_name: str, limit: int = 20) -> List[CRMCustomer]:
        """
        根据负责人获取客户列表

        Args:
            owner_name: 负责人姓名
            limit: 返回结果数量限制

        Returns:
            客户列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM customers
                WHERE owner_name LIKE %s
                AND (is_deleted = 0 OR is_deleted IS NULL)
                ORDER BY last_seen_at DESC
                LIMIT %s
                """
                cursor.execute(query, (f"%{owner_name}%", limit))
                results = cursor.fetchall()
                cursor.close()

                return [CRMCustomer.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"按负责人查询客户失败: {e}")
            return []

    # ==================== 商机相关方法 ====================

    def find_opportunity_by_id(self, opportunity_id: int) -> Optional[CRMOpportunity]:
        """
        根据ID查找商机

        Args:
            opportunity_id: 商机ID

        Returns:
            商机对象或None
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM opportunities
                WHERE id = %s AND (is_deleted = 0 OR is_deleted IS NULL)
                LIMIT 1
                """
                cursor.execute(query, (opportunity_id,))
                result = cursor.fetchone()
                cursor.close()

                if result:
                    return CRMOpportunity.from_db_row(result)
                return None

        except Exception as e:
            logger.error(f"查询商机失败: {e}")
            return None

    def search_opportunities(self, keyword: str, limit: int = 10) -> List[CRMOpportunity]:
        """
        根据关键词搜索商机

        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制

        Returns:
            商机列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM opportunities
                WHERE (name LIKE %s
                   OR customer_name LIKE %s
                   OR product LIKE %s
                   OR description LIKE %s)
                AND (is_deleted = 0 OR is_deleted IS NULL)
                ORDER BY last_seen_at DESC
                LIMIT %s
                """
                search_pattern = f"%{keyword}%"
                cursor.execute(query, (search_pattern, search_pattern, search_pattern,
                                      search_pattern, limit))
                results = cursor.fetchall()
                cursor.close()

                return [CRMOpportunity.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"搜索商机失败: {e}")
            return []

    def get_opportunities_by_customer(self, customer_name: str, limit: int = 20) -> List[CRMOpportunity]:
        """
        根据客户名称获取商机列表

        Args:
            customer_name: 客户名称
            limit: 返回结果数量限制

        Returns:
            商机列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM opportunities
                WHERE customer_name LIKE %s
                AND (is_deleted = 0 OR is_deleted IS NULL)
                ORDER BY last_seen_at DESC
                LIMIT %s
                """
                cursor.execute(query, (f"%{customer_name}%", limit))
                results = cursor.fetchall()
                cursor.close()

                return [CRMOpportunity.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"按客户查询商机失败: {e}")
            return []

    def get_opportunities_by_product(self, product: str, limit: int = 20) -> List[CRMOpportunity]:
        """
        根据产品获取商机列表

        Args:
            product: 产品名称
            limit: 返回结果数量限制

        Returns:
            商机列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM opportunities
                WHERE product LIKE %s
                AND (is_deleted = 0 OR is_deleted IS NULL)
                ORDER BY last_seen_at DESC
                LIMIT %s
                """
                cursor.execute(query, (f"%{product}%", limit))
                results = cursor.fetchall()
                cursor.close()

                return [CRMOpportunity.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"按产品查询商机失败: {e}")
            return []

    def get_opportunities_by_status(self, status: str, limit: int = 20) -> List[CRMOpportunity]:
        """
        根据状态获取商机列表

        Args:
            status: 商机状态
            limit: 返回结果数量限制

        Returns:
            商机列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT * FROM opportunities
                WHERE status LIKE %s
                AND (is_deleted = 0 OR is_deleted IS NULL)
                ORDER BY last_seen_at DESC
                LIMIT %s
                """
                cursor.execute(query, (f"%{status}%", limit))
                results = cursor.fetchall()
                cursor.close()

                return [CRMOpportunity.from_db_row(row) for row in results]

        except Exception as e:
            logger.error(f"按状态查询商机失败: {e}")
            return []

    # ==================== 统计方法 ====================

    def get_customer_statistics(self) -> Dict[str, Any]:
        """
        获取客户统计信息

        Returns:
            统计信息字典
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT
                    COUNT(*) as total_count,
                    COUNT(DISTINCT industry) as industry_count,
                    COUNT(DISTINCT owner_name) as owner_count,
                    COUNT(DISTINCT company_size) as company_size_count
                FROM customers
                WHERE is_deleted = 0 OR is_deleted IS NULL
                """
                cursor.execute(query)
                result = cursor.fetchone()
                cursor.close()

                return result if result else {}

        except Exception as e:
            logger.error(f"获取客户统计信息失败: {e}")
            return {}

    def get_opportunity_statistics(self) -> Dict[str, Any]:
        """
        获取商机统计信息

        Returns:
            统计信息字典
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                query = """
                SELECT
                    COUNT(*) as total_count,
                    COUNT(DISTINCT product) as product_count,
                    COUNT(DISTINCT status) as status_count,
                    SUM(expected_amount) as total_expected_amount,
                    COUNT(CASE WHEN has_contract = 1 THEN 1 END) as has_contract_count
                FROM opportunities
                WHERE is_deleted = 0 OR is_deleted IS NULL
                """
                cursor.execute(query)
                result = cursor.fetchone()
                cursor.close()

                # 转换Decimal为float便于JSON序列化
                if result:
                    if result.get('total_expected_amount'):
                        result['total_expected_amount'] = float(result['total_expected_amount'])

                return result if result else {}

        except Exception as e:
            logger.error(f"获取商机统计信息失败: {e}")
            return {}

    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                logger.info("CRM_sync_new数据库连接测试成功")
                return True
        except Exception as e:
            logger.error(f"CRM_sync_new数据库连接测试失败: {e}")
            return False
