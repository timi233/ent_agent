"""
CRM商机数据仓库模块
"""
import logging
from typing import List, Dict, Any, Optional
from infrastructure.database.crm_connection import get_crm_connection

logger = logging.getLogger(__name__)


class CRMOpportunityRepository:
    """CRM商机数据仓库"""
    
    def __init__(self):
        self.crm_conn = get_crm_connection()
    
    def search_opportunities_by_company_name(
        self,
        company_name: str,
        status_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        根据企业名称搜索商机数据
        
        Args:
            company_name: 企业名称（模糊匹配）
            status_filter: 项目状态过滤（可选）
            page: 页码（从1开始）
            page_size: 每页大小
            
        Returns:
            包含商机列表和分页信息的字典
        """
        try:
            # 构建查询条件
            where_conditions = []
            params = {}
            
            # 企业名称模糊匹配
            if company_name:
                where_conditions.append(
                    'JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."客户名称"[0].text\')) LIKE %(company_name)s'
                )
                params['company_name'] = f'%{company_name}%'
            
            # 项目状态过滤
            if status_filter:
                where_conditions.append(
                    'JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."项目状态"\')) = %(status_filter)s'
                )
                params['status_filter'] = status_filter
            
            where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
            
            # 计算偏移量
            offset = (page - 1) * page_size
            
            # 查询总数
            count_sql = f"""
            SELECT COUNT(*) as count
            FROM Task_Feishu_Table_records
            WHERE {where_clause}
            """
            
            total_count = self.crm_conn.execute_count_query(count_sql, params)
            
            # 查询数据
            data_sql = f"""
            SELECT
                id,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."机会名称"[0].text\')) AS opportunity_name,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."客户名称"[0].text\')) AS customer_name,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."项目状态"\')) AS status,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."产品"\')) AS product,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."商机描述"\')) AS description,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."商机创建人".name\')) AS owner_name,
                FROM_UNIXTIME(JSON_EXTRACT(record_data, \'$."商机创建时间"\')/1000) AS created_time,
                FROM_UNIXTIME(JSON_EXTRACT(record_data, \'$."预计交易日期"\')/1000) AS expected_deal_date,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."#预计合同额（万元）"\')) AS expected_amount_wan,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."合同管理-商机名称"[0].text\')) AS contract_opportunity_name,
                updated_at
            FROM Task_Feishu_Table_records
            WHERE {where_clause}
            ORDER BY updated_at DESC
            LIMIT %(limit)s OFFSET %(offset)s
            """
            
            params.update({
                'limit': page_size,
                'offset': offset
            })
            
            opportunities = self.crm_conn.execute_query(data_sql, params)
            
            # 计算分页信息
            total_pages = (total_count + page_size - 1) // page_size
            
            return {
                'opportunities': opportunities,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }
            
        except Exception as e:
            logger.error(f"搜索CRM商机数据失败: {e}")
            raise
    
    def get_opportunity_by_id(self, opportunity_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取单个商机详情
        
        Args:
            opportunity_id: 商机ID
            
        Returns:
            商机详情字典或None
        """
        try:
            sql = """
            SELECT
                id,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."机会名称"[0].text\')) AS opportunity_name,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."客户名称"[0].text\')) AS customer_name,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."项目状态"\')) AS status,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."产品"\')) AS product,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."商机描述"\')) AS description,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."商机创建人".name\')) AS owner_name,
                FROM_UNIXTIME(JSON_EXTRACT(record_data, \'$."商机创建时间"\')/1000) AS created_time,
                FROM_UNIXTIME(JSON_EXTRACT(record_data, \'$."预计交易日期"\')/1000) AS expected_deal_date,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."#预计合同额（万元）"\')) AS expected_amount_wan,
                JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."合同管理-商机名称"[0].text\')) AS contract_opportunity_name,
                record_data,
                created_at,
                updated_at
            FROM Task_Feishu_Table_records
            WHERE id = %(opportunity_id)s
            """
            
            results = self.crm_conn.execute_query(sql, {'opportunity_id': opportunity_id})
            return results[0] if results else None
            
        except Exception as e:
            logger.error(f"获取CRM商机详情失败: {e}")
            raise
    
    def get_available_statuses(self) -> List[str]:
        """
        获取所有可用的项目状态
        
        Returns:
            状态列表
        """
        try:
            sql = """
            SELECT DISTINCT JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."项目状态"\')) AS status
            FROM Task_Feishu_Table_records
            WHERE JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."项目状态"\')) IS NOT NULL
            AND JSON_UNQUOTE(JSON_EXTRACT(record_data, \'$."项目状态"\')) != ''
            ORDER BY status
            """
            
            results = self.crm_conn.execute_query(sql)
            return [row['status'] for row in results if row['status']]
            
        except Exception as e:
            logger.error(f"获取CRM项目状态列表失败: {e}")
            raise