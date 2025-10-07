"""
工单数据仓储
提供对Task_sync_new数据库中工单数据的访问
"""
import logging
import os
from typing import List, Dict, Any
from contextlib import contextmanager
import mysql.connector
from mysql.connector import pooling

from infrastructure.database.models.work_orders import WorkOrder

logger = logging.getLogger(__name__)


class WorkOrderRepository:
    """工单服务记录仓储"""

    def __init__(self):
        """初始化仓储，连接到Task_sync_new数据库"""
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "3306"))
        self.username = os.getenv("DB_USERNAME", "root")
        self.password = os.getenv("DB_PASSWORD", "1qaz2wsx")
        self.database = "Task_sync_new"  # 固定连接到Task_sync_new数据库
        self.charset = "utf8mb4"
        self._connection_pool = None

    def _create_connection_pool(self):
        """创建数据库连接池"""
        if self._connection_pool is None:
            try:
                pool_config = {
                    'pool_name': 'work_order_pool',
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
                logger.info(f"工单数据库连接池创建成功: {self.host}:{self.port}/{self.database}")
            except Exception as e:
                logger.error(f"创建工单数据库连接池失败: {e}")
                raise
        return self._connection_pool

    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        pool = self._create_connection_pool()
        connection = pool.get_connection()
        try:
            yield connection
        finally:
            connection.close()

    def search_by_company_name(self, company_name: str, limit: int = 20) -> List[WorkOrder]:
        """
        根据客户公司名称搜索工单

        Args:
            company_name: 客户公司名称（支持模糊匹配）
            limit: 返回结果数量限制

        Returns:
            工单列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                query = """
                SELECT
                    record_id, source_id, application_no, application_link, status,
                    priority, workflow_name, customer_company, customer_contact,
                    customer_phone_secondary, work_content, work_mode, work_type,
                    engineer_identity, has_channel, channel_name, channel_contact,
                    channel_phone_secondary, initiator_department, initiated_at,
                    initiator_primary_id, initiator_primary_name, initiator_primary_email,
                    completed_at, service_start_date, service_start_datetime,
                    service_start_period, service_end_date, service_end_datetime,
                    service_end_period, after_sales_engineer_primary_id,
                    after_sales_engineer_primary_name, after_sales_engineer_primary_email,
                    fetched_at, created_at, updated_at
                FROM task_service_records
                WHERE customer_company LIKE %s
                ORDER BY service_start_date DESC
                LIMIT %s
                """

                cursor.execute(query, (f"%{company_name}%", limit))
                rows = cursor.fetchall()
                cursor.close()

                return [WorkOrder.from_db_row(row) for row in rows]

        except Exception as e:
            logger.error(f"根据公司名称搜索工单失败: {e}")
            raise

    def get_by_application_no(self, application_no: str) -> WorkOrder:
        """
        根据申请单号获取工单

        Args:
            application_no: 申请单号

        Returns:
            工单对象，如果不存在则返回None
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                query = """
                SELECT
                    record_id, source_id, application_no, application_link, status,
                    priority, workflow_name, customer_company, customer_contact,
                    customer_phone_secondary, work_content, work_mode, work_type,
                    engineer_identity, has_channel, channel_name, channel_contact,
                    channel_phone_secondary, initiator_department, initiated_at,
                    initiator_primary_id, initiator_primary_name, initiator_primary_email,
                    completed_at, service_start_date, service_start_datetime,
                    service_start_period, service_end_date, service_end_datetime,
                    service_end_period, after_sales_engineer_primary_id,
                    after_sales_engineer_primary_name, after_sales_engineer_primary_email,
                    fetched_at, created_at, updated_at
                FROM task_service_records
                WHERE application_no = %s
                """

                cursor.execute(query, (application_no,))
                row = cursor.fetchone()
                cursor.close()

                return WorkOrder.from_db_row(row) if row else None

        except Exception as e:
            logger.error(f"根据申请单号获取工单失败: {e}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取工单统计信息

        Returns:
            包含统计信息的字典
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # 总工单数
                cursor.execute("SELECT COUNT(*) FROM task_service_records")
                total_count = cursor.fetchone()[0]

                # 按状态统计
                cursor.execute("""
                    SELECT status, COUNT(*) as count
                    FROM task_service_records
                    GROUP BY status
                """)
                status_stats = {row[0]: row[1] for row in cursor.fetchall()}

                # 按工单类型统计
                cursor.execute("""
                    SELECT work_type, COUNT(*) as count
                    FROM task_service_records
                    WHERE work_type IS NOT NULL
                    GROUP BY work_type
                """)
                type_stats = {row[0]: row[1] for row in cursor.fetchall()}

                # 独立客户数
                cursor.execute("""
                    SELECT COUNT(DISTINCT customer_company)
                    FROM task_service_records
                    WHERE customer_company IS NOT NULL
                """)
                unique_customers = cursor.fetchone()[0]

                cursor.close()

                return {
                    'total_count': total_count,
                    'unique_customers': unique_customers,
                    'status_distribution': status_stats,
                    'type_distribution': type_stats
                }

        except Exception as e:
            logger.error(f"获取工单统计失败: {e}")
            raise

    def test_connection(self) -> bool:
        """
        测试数据库连接

        Returns:
            连接成功返回True，否则返回False
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                return True
        except Exception as e:
            logger.error(f"工单数据库连接测试失败: {e}")
            return False
