"""
独立的仓储层模块
完全避免相对导入，使用绝对路径
"""
import sys
import os
from typing import List, Dict, Any, Optional
import logging

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入数据库连接
try:
    from config.simple_settings import get_settings
    from infrastructure.database.simple_connection import get_database_connection
    DB_AVAILABLE = True
except ImportError as e:
    print(f"警告: 无法导入数据库模块: {e}")
    DB_AVAILABLE = False
    
    def get_database_connection():
        return None

logger = logging.getLogger(__name__)


class StandaloneRepository:
    """独立的仓储基类"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.db = get_database_connection() if DB_AVAILABLE else None
    
    def find_by_id(self, id_value: Any, id_field: str = "id") -> Optional[Dict[str, Any]]:
        """根据ID查找记录"""
        if not self.db:
            print("警告: 数据库连接不可用")
            return None
            
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
        if not self.db:
            print("警告: 数据库连接不可用")
            return None
            
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
    
    def update_by_id(self, id_value: Any, data: Dict[str, Any], id_field: str = "id") -> bool:
        """根据ID更新记录"""
        if not self.db:
            print("警告: 数据库连接不可用")
            return False
            
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


class StandaloneCustomerRepository(StandaloneRepository):
    """独立的客户仓储类"""
    
    def __init__(self):
        super().__init__("QD_customer")
    
    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据客户名称查找"""
        return super().find_by_name(name, "customer_name")
    
    def update_address(self, customer_id: int, address: str) -> bool:
        """更新客户地址"""
        return self.update_by_id(customer_id, {"address": address}, "customer_id")


class StandaloneEnterpriseRepository(StandaloneRepository):
    """独立的企业仓储类"""
    
    def __init__(self):
        super().__init__("QD_enterprise_chain_leader")
    
    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据企业名称查找"""
        return super().find_by_name(name, "enterprise_name")
    
    def update_address(self, enterprise_id: int, address: str) -> bool:
        """更新企业地址"""
        return self.update_by_id(enterprise_id, {"address": address}, "enterprise_id")