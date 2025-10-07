"""
公司查询结果缓存仓储
表: QD_company_cache
- cache_id INT AUTO_INCREMENT PRIMARY KEY
- company_name VARCHAR(255) UNIQUE
- payload TEXT (JSON字符串, 存 final_result)
- cached_at DATETIME
- expires_at DATETIME
"""
import logging
from typing import Optional, Dict, Any
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)

class CompanyCacheRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        self._ensure_table()

    def _ensure_table(self):
        # 建表（如不存在）
        query = """
        CREATE TABLE IF NOT EXISTS QD_company_cache (
            cache_id INT AUTO_INCREMENT PRIMARY KEY,
            company_name VARCHAR(255) NOT NULL UNIQUE,
            payload TEXT NOT NULL,
            cached_at DATETIME NOT NULL,
            expires_at DATETIME NOT NULL
        ) CHARACTER SET utf8mb4
        """
        try:
            self._execute_update(query)
        except Exception as e:
            logger.error(f"创建缓存表失败: {e}")

    def get_valid_cache(self, company_name: str) -> Optional[Dict[str, Any]]:
        """查询未过期的缓存记录"""
        query = """
        SELECT company_name, payload, cached_at, expires_at
        FROM QD_company_cache
        WHERE company_name = %s AND expires_at > NOW()
        LIMIT 1
        """
        return self._execute_single_query(query, (company_name,))

    def upsert_cache(self, company_name: str, payload_json: str, ttl_days: int = 90) -> bool:
        """写入或更新缓存，设置过期时间为当前时间+ttl_days"""
        query = """
        INSERT INTO QD_company_cache (company_name, payload, cached_at, expires_at)
        VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL %s DAY))
        ON DUPLICATE KEY UPDATE
            payload = VALUES(payload),
            cached_at = VALUES(cached_at),
            expires_at = VALUES(expires_at)
        """
        try:
            return self._execute_update(query, (company_name, payload_json, ttl_days))
        except Exception as e:
            logger.error(f"写入缓存失败: {e}")
            return False

    def purge_cache(self, company_name: str) -> bool:
        """按标准化公司名删除缓存记录"""
        query = """
        DELETE FROM QD_company_cache
        WHERE company_name = %s
        """
        try:
            return self._execute_update(query, (company_name,))
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False