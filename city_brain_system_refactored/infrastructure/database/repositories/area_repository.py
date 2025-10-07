"""
地区仓储类
处理地区相关的数据访问操作
"""
from typing import Optional, Dict, Any, List
import logging

from .base_repository import BaseRepository
from ..models.area import Area

logger = logging.getLogger(__name__)


class AreaRepository(BaseRepository):
    """地区数据访问仓储类"""
    
    def __init__(self, connection_manager=None):
        super().__init__(connection_manager)
        self.table_name = "QD_area"
    
    def find_by_id(self, area_id: int) -> Optional[Area]:
        """根据地区ID查询地区信息"""
        try:
            query = """
            SELECT area_id, city_name, district_name, district_code
            FROM QD_area
            WHERE area_id = %s
            """
            result = self._execute_single_query(query, (area_id,))
            return self._create_area_from_result(result) if result else None
        except Exception as e:
            logger.error(f"查询地区失败: {area_id}, 错误: {e}")
            return None
    
    def find_by_name(self, city_name: str, district_name: str = None) -> Optional[Area]:
        """根据城市和区县名称查询地区信息"""
        if district_name:
            query = """
            SELECT area_id, city_name, district_name, district_code
            FROM QD_area
            WHERE city_name = %s AND district_name = %s
            """
            result = self._execute_single_query(query, (city_name, district_name))
        else:
            query = """
            SELECT area_id, city_name, district_name, district_code
            FROM QD_area
            WHERE city_name = %s
            LIMIT 1
            """
            result = self._execute_single_query(query, (city_name,))
        
        return self._create_area_from_result(result) if result else None
    
    def find_by_city(self, city_name: str) -> List[Area]:
        """根据城市名称查询所有区县"""
        query = """
        SELECT area_id, city_name, district_name, district_code
        FROM QD_area
        WHERE city_name = %s
        ORDER BY district_name
        """
        results = self._execute_query(query, (city_name,))
        return [self._create_area_from_result(row) for row in results]
    
    def search_by_keyword(self, keyword: str) -> List[Area]:
        """根据关键词搜索地区"""
        query = """
        SELECT area_id, city_name, district_name, district_code
        FROM QD_area
        WHERE city_name LIKE %s OR district_name LIKE %s
        ORDER BY city_name, district_name
        """
        keyword_pattern = f"%{keyword}%"
        results = self._execute_query(query, (keyword_pattern, keyword_pattern))
        return [self._create_area_from_result(row) for row in results]
    
    def get_all_cities(self) -> List[str]:
        """获取所有城市名称"""
        query = "SELECT DISTINCT city_name FROM QD_area ORDER BY city_name"
        results = self._execute_query(query)
        return [row['city_name'] for row in results if row['city_name']]
    
    def get_all(self) -> List[Area]:
        """获取所有地区"""
        query = """
        SELECT area_id, city_name, district_name, district_code
        FROM QD_area
        ORDER BY city_name, district_name
        """
        results = self._execute_query(query)
        return [self._create_area_from_result(row) for row in results]
    
    def create(self, area: Area) -> bool:
        """创建新地区"""
        query = """
        INSERT INTO QD_area (city_name, district_name, district_code)
        VALUES (%s, %s, %s)
        """
        params = (area.city_name, area.district_name, area.district_code)
        return self._execute_update(query, params)
    
    def update(self, area: Area) -> bool:
        """更新地区信息"""
        query = """
        UPDATE QD_area SET
            city_name = %s,
            district_name = %s,
            district_code = %s
        WHERE area_id = %s
        """
        params = (area.city_name, area.district_name, area.district_code, area.area_id)
        return self._execute_update(query, params)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取地区统计信息"""
        stats = {}
        
        # 总地区数
        total_query = "SELECT COUNT(*) as total FROM QD_area"
        total_result = self._execute_single_query(total_query)
        stats['total_areas'] = total_result['total'] if total_result else 0
        
        # 按城市分组统计
        city_query = """
        SELECT city_name, COUNT(*) as district_count
        FROM QD_area
        GROUP BY city_name
        ORDER BY district_count DESC
        """
        city_results = self._execute_query(city_query)
        stats['by_city'] = {row['city_name']: row['district_count'] for row in city_results}
        
        return stats
    
    def _create_area_from_result(self, result: Dict[str, Any]) -> Area:
        """从查询结果创建Area对象"""
        if not result:
            return None
        
        return Area(
            area_id=result.get('area_id'),
            city_name=result.get('city_name'),
            district_name=result.get('district_name'),
            district_code=result.get('district_code')
        )