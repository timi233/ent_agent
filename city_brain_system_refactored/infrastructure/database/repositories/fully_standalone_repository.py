"""
完全独立的仓储层模块
不依赖任何其他模块，直接实现数据库操作
"""
import logging
import os
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

# 尝试导入mysql.connector
try:
    import mysql.connector
    from mysql.connector import pooling
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    logging.warning("mysql-connector-python未安装，数据库功能不可用")

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """简单的数据库配置类"""
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "3306"))
        self.username = os.getenv("DB_USERNAME", "City_Brain_user_mysql")
        self.password = os.getenv("DB_PASSWORD", "CityBrain@2024")
        self.database = os.getenv("DB_DATABASE", "City_Brain_DB")
        self.charset = os.getenv("DB_CHARSET", "utf8mb4")
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "10"))


class FullyStandaloneRepository:
    """完全独立的仓储基类"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.config = DatabaseConfig()
        self._connection_pool = None
    
    def _create_connection_pool(self):
        """创建数据库连接池"""
        if not MYSQL_AVAILABLE:
            return None
            
        if self._connection_pool is None:
            try:
                pool_config = {
                    'pool_name': f'{self.table_name}_pool',
                    'pool_size': self.config.pool_size,
                    'pool_reset_session': True,
                    'host': self.config.host,
                    'port': self.config.port,
                    'user': self.config.username,
                    'password': self.config.password,
                    'database': self.config.database,
                    'charset': self.config.charset,
                    'autocommit': False,
                    'time_zone': '+08:00'
                }
                
                self._connection_pool = pooling.MySQLConnectionPool(**pool_config)
                logger.info(f"数据库连接池创建成功: {self.config.host}:{self.config.port}/{self.config.database}")
                
            except Exception as e:
                logger.error(f"创建数据库连接池失败: {e}")
                return None
        
        return self._connection_pool
    
    @contextmanager
    def get_connection_context(self):
        """获取数据库连接上下文管理器"""
        if not MYSQL_AVAILABLE:
            logger.warning("数据库连接不可用，返回模拟连接")
            yield None
            return
            
        connection = None
        try:
            pool = self._create_connection_pool()
            if pool:
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
    
    def find_by_id(self, id_value: Any, id_field: str = "id") -> Optional[Dict[str, Any]]:
        """根据ID查找记录"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE {id_field} = %s"
            with self.get_connection_context() as connection:
                if connection is None:
                    return None
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, (id_value,))
                result = cursor.fetchone()
                cursor.close()
                return result
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return None
    
    def find_by_name(self, name: str, name_field: str = "name") -> Optional[Dict[str, Any]]:
        """根据名称查找记录"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE {name_field} = %s"
            with self.get_connection_context() as connection:
                if connection is None:
                    return None
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, (name,))
                result = cursor.fetchone()
                cursor.close()
                return result
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return None
    
    def update_by_id(self, id_value: Any, data: Dict[str, Any], id_field: str = "id") -> bool:
        """根据ID更新记录"""
        try:
            if not data:
                return False
                
            set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE {id_field} = %s"
            values = list(data.values()) + [id_value]
            
            with self.get_connection_context() as connection:
                if connection is None:
                    return False
                cursor = connection.cursor()
                cursor.execute(query, values)
                connection.commit()
                affected_rows = cursor.rowcount
                cursor.close()
                return affected_rows > 0
        except Exception as e:
            logger.error(f"更新记录失败: {e}")
            return False


class FullyStandaloneCustomerRepository(FullyStandaloneRepository):
    """完全独立的客户仓储类"""
    
    def __init__(self):
        super().__init__("QD_customer")
    
    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据客户名称查找"""
        return super().find_by_name(name, "customer_name")
    
    def update_address(self, customer_id: int, address: str) -> bool:
        """更新客户地址"""
        return self.update_by_id(customer_id, {"address": address}, "customer_id")


class FullyStandaloneEnterpriseRepository(FullyStandaloneRepository):
    """完全独立的企业仓储类"""
    
    def __init__(self):
        super().__init__("QD_enterprise_chain_leader")
    
    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据企业名称查找"""
        return super().find_by_name(name, "enterprise_name")
    
    def update_address(self, enterprise_id: int, address: str) -> bool:
        """更新企业地址"""
        return self.update_by_id(enterprise_id, {"address": address}, "enterprise_id")
