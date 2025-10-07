"""
客户Repository接口（领域层定义）
遵循依赖倒置原则：Domain层定义接口，Infrastructure层实现
"""
from abc import ABC, abstractmethod
from typing import Optional, Any


class ICustomerRepository(ABC):
    """客户仓储接口"""

    @abstractmethod
    def find_by_name(self, customer_name: str) -> Optional[Any]:
        """
        根据客户名称查找客户信息

        Args:
            customer_name: 客户名称

        Returns:
            客户信息对象（Customer），未找到返回None
        """
        pass

    @abstractmethod
    def find_by_id(self, customer_id: int) -> Optional[Any]:
        """
        根据ID查找客户信息

        Args:
            customer_id: 客户ID

        Returns:
            客户信息对象（Customer），未找到返回None
        """
        pass
