"""
行业仓储类
新增的行业数据访问仓储类，提供行业和产业大脑相关的数据操作
"""
from typing import Optional, Dict, Any, List
import logging

from .base_repository import BaseRepository
from ..models.industry import Industry, IndustryBrain, create_industry, create_industry_brain

logger = logging.getLogger(__name__)


class IndustryRepository(BaseRepository):
    """行业数据访问仓储类"""
    
    def find_by_id(self, industry_id: int) -> Optional[Industry]:
        """
        根据行业ID查询行业信息
        
        Args:
            industry_id: 行业ID
            
        Returns:
            行业信息或None
        """
        query = """
        SELECT industry_id, industry_name, industry_type, industry_remark
        FROM QD_industry
        WHERE industry_id = %s
        """
        result = self._execute_single_query(query, (industry_id,))
        return create_industry(result) if result else None
    
    def find_by_name(self, industry_name: str) -> Optional[Industry]:
        """
        根据行业名称查询行业信息
        
        Args:
            industry_name: 行业名称
            
        Returns:
            行业信息或None
        """
        query = """
        SELECT industry_id, industry_name, industry_type, industry_remark
        FROM QD_industry
        WHERE industry_name = %s
        """
        result = self._execute_single_query(query, (industry_name,))
        return create_industry(result) if result else None
    
    def find_all(self) -> List[Industry]:
        """
        查询所有行业信息
        
        Returns:
            行业信息列表
        """
        query = """
        SELECT industry_id, industry_name, industry_type, industry_remark
        FROM QD_industry
        ORDER BY industry_name
        """
        results = self._execute_query(query)
        return [create_industry(result) for result in results]
    
    def find_by_type(self, industry_type: str) -> List[Industry]:
        """
        根据行业类型查询行业列表
        
        Args:
            industry_type: 行业类型
            
        Returns:
            行业信息列表
        """
        query = """
        SELECT industry_id, industry_name, industry_type, industry_remark
        FROM QD_industry
        WHERE industry_type = %s
        ORDER BY industry_name
        """
        results = self._execute_query(query, (industry_type,))
        return [create_industry(result) for result in results]


class IndustryBrainRepository(BaseRepository):
    """产业大脑数据访问仓储类"""
    
    def find_by_id(self, brain_id: int) -> Optional[IndustryBrain]:
        """
        根据产业大脑ID查询产业大脑信息
        
        Args:
            brain_id: 产业大脑ID
            
        Returns:
            产业大脑信息或None
        """
        query = """
        SELECT b.brain_id, b.brain_name, b.area_id, b.build_year, b.brain_remark,
               a.city_name, a.district_name
        FROM QD_industry_brain b
        LEFT JOIN QD_area a ON b.area_id = a.area_id
        WHERE b.brain_id = %s
        """
        result = self._execute_single_query(query, (brain_id,))
        return create_industry_brain(result) if result else None
    
    def find_by_name(self, brain_name: str) -> Optional[IndustryBrain]:
        """
        根据产业大脑名称查询产业大脑信息
        
        Args:
            brain_name: 产业大脑名称
            
        Returns:
            产业大脑信息或None
        """
        query = """
        SELECT b.brain_id, b.brain_name, b.area_id, b.build_year, b.brain_remark,
               a.city_name, a.district_name
        FROM QD_industry_brain b
        LEFT JOIN QD_area a ON b.area_id = a.area_id
        WHERE b.brain_name = %s
        """
        result = self._execute_single_query(query, (brain_name,))
        return create_industry_brain(result) if result else None
    
    def find_all(self) -> List[IndustryBrain]:
        """
        查询所有产业大脑信息
        
        Returns:
            产业大脑信息列表
        """
        query = """
        SELECT b.brain_id, b.brain_name, b.area_id, b.build_year, b.brain_remark,
               a.city_name, a.district_name
        FROM QD_industry_brain b
        LEFT JOIN QD_area a ON b.area_id = a.area_id
        ORDER BY b.brain_name
        """
        results = self._execute_query(query)
        return [create_industry_brain(result) for result in results]
    
    def find_by_area(self, area_id: int) -> List[IndustryBrain]:
        """
        根据地区ID查询产业大脑列表
        
        Args:
            area_id: 地区ID
            
        Returns:
            产业大脑信息列表
        """
        query = """
        SELECT b.brain_id, b.brain_name, b.area_id, b.build_year, b.brain_remark,
               a.city_name, a.district_name
        FROM QD_industry_brain b
        LEFT JOIN QD_area a ON b.area_id = a.area_id
        WHERE b.area_id = %s
        ORDER BY b.brain_name
        """
        results = self._execute_query(query, (area_id,))
        return [create_industry_brain(result) for result in results]
    
    def find_by_industry(self, industry_id: int) -> List[IndustryBrain]:
        """
        根据行业ID查询关联的产业大脑列表
        
        Args:
            industry_id: 行业ID
            
        Returns:
            产业大脑信息列表
        """
        query = """
        SELECT b.brain_id, b.brain_name, b.area_id, b.build_year, b.brain_remark,
               a.city_name, a.district_name
        FROM QD_industry_brain b
        LEFT JOIN QD_area a ON b.area_id = a.area_id
        INNER JOIN QD_brain_industry_rel r ON b.brain_id = r.brain_id
        WHERE r.industry_id = %s
        ORDER BY b.brain_name
        """
        results = self._execute_query(query, (industry_id,))
        return [create_industry_brain(result) for result in results]
    
    def find_industries_by_brain(self, brain_id: int) -> List[Industry]:
        """
        根据产业大脑ID查询关联的行业列表
        
        Args:
            brain_id: 产业大脑ID
            
        Returns:
            行业信息列表
        """
        query = """
        SELECT i.industry_id, i.industry_name, i.industry_type, i.industry_remark
        FROM QD_industry i
        INNER JOIN QD_brain_industry_rel r ON i.industry_id = r.industry_id
        WHERE r.brain_id = %s
        ORDER BY i.industry_name
        """
        results = self._execute_query(query, (brain_id,))
        return [create_industry(result) for result in results]


class AreaRepository(BaseRepository):
    """地区数据访问仓储类"""
    
    def find_by_id(self, area_id: int) -> Optional[Dict[str, Any]]:
        """
        根据地区ID查询地区信息
        
        Args:
            area_id: 地区ID
            
        Returns:
            地区信息字典或None
        """
        query = """
        SELECT area_id, city_name, district_name, district_code
        FROM QD_area
        WHERE area_id = %s
        """
        return self._execute_single_query(query, (area_id,))
    
    def find_by_district_name(self, district_name: str) -> Optional[Dict[str, Any]]:
        """
        根据区县名称查询地区信息
        
        Args:
            district_name: 区县名称
            
        Returns:
            地区信息字典或None
        """
        query = """
        SELECT area_id, city_name, district_name, district_code
        FROM QD_area
        WHERE district_name = %s
        """
        return self._execute_single_query(query, (district_name,))
    
    def find_all(self) -> List[Dict[str, Any]]:
        """
        查询所有地区信息
        
        Returns:
            地区信息列表
        """
        query = """
        SELECT area_id, city_name, district_name, district_code
        FROM QD_area
        ORDER BY city_name, district_name
        """
        return self._execute_query(query)