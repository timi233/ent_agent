"""
产业大脑数据模型
对应数据库表：QD_industry_brain
"""
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class IndustryBrain:
    """产业大脑数据模型"""
    
    def __init__(self, **kwargs):
        """
        初始化产业大脑模型
        
        Args:
            **kwargs: 产业大脑数据字段
        """
        # 主键
        self.brain_id: Optional[int] = kwargs.get('brain_id')
        
        # 基本信息
        self.brain_name: str = kwargs.get('brain_name', '')
        self.area_id: Optional[int] = kwargs.get('area_id')
        self.build_year: Optional[int] = kwargs.get('build_year')
        self.brain_remark: Optional[str] = kwargs.get('brain_remark', '')
        
        # 元数据
        self.created_at: Optional[str] = kwargs.get('created_at')
        self.updated_at: Optional[str] = kwargs.get('updated_at')
        
        # 关联数据（非数据库字段）
        self.area_info: Optional[Dict[str, Any]] = kwargs.get('area_info')
        self.related_industries: list = kwargs.get('related_industries', [])
        self.customer_count: int = kwargs.get('customer_count', 0)
        self.enterprise_count: int = kwargs.get('enterprise_count', 0)
        
        # 数据验证
        self._validate_data()
    
    def _validate_data(self):
        """验证数据完整性"""
        try:
            # 验证必填字段
            if not self.brain_name or not self.brain_name.strip():
                logger.warning("产业大脑名称不能为空")
                self.brain_name = "未知产业大脑"
            
            # 验证建设年份
            if self.build_year is not None:
                current_year = 2025
                if self.build_year < 2000 or self.build_year > current_year:
                    logger.warning(f"产业大脑建设年份异常: {self.build_year}")
                    self.build_year = None
            
            # 清理文本字段
            self.brain_name = self.brain_name.strip()
            if self.brain_remark:
                self.brain_remark = self.brain_remark.strip()
            
        except Exception as e:
            logger.error(f"产业大脑数据验证失败: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式（包含所有字段）
        
        Returns:
            包含所有字段的字典
        """
        return {
            'brain_id': self.brain_id,
            'brain_name': self.brain_name,
            'area_id': self.area_id,
            'build_year': self.build_year,
            'brain_remark': self.brain_remark,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'area_info': self.area_info,
            'related_industries': self.related_industries,
            'customer_count': self.customer_count,
            'enterprise_count': self.enterprise_count
        }
    
    def to_db_dict(self) -> Dict[str, Any]:
        """
        转换为数据库格式（仅包含数据库字段）
        
        Returns:
            数据库字段字典
        """
        db_dict = {}
        
        # 只包含数据库表中的字段
        if self.brain_id is not None:
            db_dict['brain_id'] = self.brain_id
        if self.brain_name:
            db_dict['brain_name'] = self.brain_name
        if self.area_id is not None:
            db_dict['area_id'] = self.area_id
        if self.build_year is not None:
            db_dict['build_year'] = self.build_year
        if self.brain_remark:
            db_dict['brain_remark'] = self.brain_remark
        
        return db_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IndustryBrain':
        """
        从字典创建产业大脑对象
        
        Args:
            data: 产业大脑数据字典
            
        Returns:
            产业大脑对象
        """
        return cls(**data)
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'IndustryBrain':
        """
        从数据库行创建产业大脑对象
        
        Args:
            row: 数据库行数据
            
        Returns:
            产业大脑对象
        """
        return cls(**row)
    
    def update_from_dict(self, data: Dict[str, Any]):
        """
        从字典更新产业大脑信息
        
        Args:
            data: 更新数据字典
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # 重新验证数据
        self._validate_data()
    
    def add_area_info(self, area_info: Dict[str, Any]):
        """
        添加地区信息
        
        Args:
            area_info: 地区信息字典
        """
        self.area_info = area_info
    
    def add_related_industry(self, industry_info: Dict[str, Any]):
        """
        添加关联行业信息
        
        Args:
            industry_info: 行业信息字典
        """
        if industry_info not in self.related_industries:
            self.related_industries.append(industry_info)
    
    def set_statistics(self, customer_count: int = 0, enterprise_count: int = 0):
        """
        设置统计信息
        
        Args:
            customer_count: 关联客户数量
            enterprise_count: 关联企业数量
        """
        self.customer_count = customer_count
        self.enterprise_count = enterprise_count
    
    def get_display_name(self) -> str:
        """
        获取显示名称
        
        Returns:
            格式化的显示名称
        """
        if self.build_year:
            return f"{self.brain_name}({self.build_year}年)"
        return self.brain_name
    
    def is_valid(self) -> bool:
        """
        检查产业大脑数据是否有效
        
        Returns:
            数据是否有效
        """
        return bool(self.brain_name and self.brain_name.strip())
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"IndustryBrain(id={self.brain_id}, name='{self.brain_name}', build_year={self.build_year})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"IndustryBrain(brain_id={self.brain_id}, brain_name='{self.brain_name}', "
                f"area_id={self.area_id}, build_year={self.build_year})")
    
    def __eq__(self, other) -> bool:
        """相等比较"""
        if not isinstance(other, IndustryBrain):
            return False
        return (self.brain_id == other.brain_id and 
                self.brain_name == other.brain_name)
    
    def __hash__(self) -> int:
        """哈希值"""
        return hash((self.brain_id, self.brain_name))