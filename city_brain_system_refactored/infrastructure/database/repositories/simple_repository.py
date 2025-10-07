"""
简化的仓储层基类
不依赖复杂的ORM，使用基础的数据库操作
"""
from typing import List, Dict, Any, Optional
import logging

try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from infrastructure.database.simple_connection import get_database_connection
except ImportError:
    print("警告: 无法导入数据库连接模块")
    def get_database_connection():
        return None

logger = logging.getLogger(__name__)


class SimpleRepository:
    """简化的仓储基类"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.db = get_database_connection()
    
    def find_by_id(self, id_value: Any, id_field: str = "id") -> Optional[Dict[str, Any]]:
        """根据ID查找记录"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE {id_field} = %s"
            with self.db.get_connection_context() as connection:
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
            with self.db.get_connection_context() as connection:
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
    
    def find_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """查找所有记录"""
        try:
            query = f"SELECT * FROM {self.table_name} LIMIT %s"
            with self.db.get_connection_context() as connection:
                if connection is None:
                    return []
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, (limit,))
                results = cursor.fetchall()
                cursor.close()
                return results
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
            return []
    
    def update_by_id(self, id_value: Any, data: Dict[str, Any], id_field: str = "id") -> bool:
        """根据ID更新记录"""
        try:
            if not data:
                return False
                
            set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE {id_field} = %s"
            values = list(data.values()) + [id_value]
            
            with self.db.get_connection_context() as connection:
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


class CustomerRepository(SimpleRepository):
    """客户仓储类"""
    
    def __init__(self):
        super().__init__("QD_customer")
    
    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据客户名称查找"""
        return super().find_by_name(name, "customer_name")
    
    def update_address(self, customer_id: int, address: str) -> bool:
        """更新客户地址"""
        return self.update_by_id(customer_id, {"address": address}, "customer_id")


class EnterpriseRepository(SimpleRepository):
    """企业仓储类"""
    
    def __init__(self):
        super().__init__("QD_enterprise_chain_leader")
    
    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据企业名称查找"""
        return super().find_by_name(name, "enterprise_name")
    
    def update_address(self, enterprise_id: int, address: str) -> bool:
        """更新企业地址"""
        return self.update_by_id(enterprise_id, {"address": address}, "enterprise_id")