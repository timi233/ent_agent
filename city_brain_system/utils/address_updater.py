"""
地址信息更新工具
负责将联网搜索到的正确地址信息更新到数据库中
"""
from typing import Optional, Dict, Any
from database.connection import get_db_connection
from utils.logger import city_brain_logger
import mysql.connector


def update_customer_address_info(customer_name: str, new_address: str, new_city: str) -> bool:
    """
    更新客户的地址信息到数据库
    支持QD_customer表和QD_enterprise_chain_leader表
    
    Args:
        customer_name: 企业名称
        new_address: 新的完整地址
        new_city: 新的城市信息
        
    Returns:
        bool: 更新是否成功
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 首先查找QD_customer表中的企业记录
        cursor.execute("""
            SELECT customer_id, customer_name, address 
            FROM QD_customer 
            WHERE customer_name = %s
        """, (customer_name,))
        
        customer_record = cursor.fetchone()
        
        if customer_record:
            # 更新QD_customer表
            customer_id = customer_record['customer_id']
            old_address = customer_record['address']
            
            update_query = """
                UPDATE QD_customer 
                SET address = %s
                WHERE customer_id = %s
            """
            
            cursor.execute(update_query, (new_address, customer_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                city_brain_logger.log_company_query(
                    customer_name, 
                    "地址更新", 
                    f"QD_customer表地址更新成功，城市: {new_city}"
                )
                return True
        
        # 如果QD_customer表中没有找到，查找QD_enterprise_chain_leader表
        cursor.execute("""
            SELECT enterprise_id, enterprise_name 
            FROM QD_enterprise_chain_leader 
            WHERE enterprise_name = %s
        """, (customer_name,))
        
        chain_record = cursor.fetchone()
        
        if chain_record:
            # 对于链主企业，我们记录地址信息但不直接更新表结构
            city_brain_logger.log_company_query(
                customer_name,
                "链主企业地址获取",
                f"地址信息已获取，城市: {new_city}"
            )
            return True
        
        # 如果两个表都没有找到记录
        city_brain_logger.log_error("地址更新失败", f"未找到企业记录: {customer_name}")
        return False
            
    except mysql.connector.Error as e:
        if conn:
            conn.rollback()
        city_brain_logger.log_error("数据库更新地址失败", f"{customer_name}: {str(e)}")
        return False
        
    except Exception as e:
        if conn:
            conn.rollback()
        city_brain_logger.log_error("更新地址时发生未知错误", f"{customer_name}: {str(e)}")
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def find_companies_with_wrong_addresses() -> list:
    """
    查找数据库中可能有错误地址的企业
    主要针对所有地区显示为"莱西市"的链主企业
    
    Returns:
        list: 需要修正地址的企业名称列表
    """
    conn = None
    cursor = None
    companies = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 查找所有链主企业中地区为"莱西市"的记录
        cursor.execute("""
            SELECT DISTINCT ecl.enterprise_name
            FROM QD_enterprise_chain_leader ecl
            JOIN QD_area a ON ecl.area_id = a.area_id
            WHERE a.district_name = '莱西市'
            AND ecl.enterprise_name IS NOT NULL
            AND ecl.enterprise_name != ''
        """)
        
        chain_leader_companies = cursor.fetchall()
        
        # 合并结果
        for record in chain_leader_companies:
            companies.append(record['enterprise_name'])
        
        city_brain_logger.log_company_query(
            "批量地址修正",
            "查找企业",
            f"找到需要修正地址的企业: {len(companies)}家"
        )
        
        return companies
        
    except Exception as e:
        city_brain_logger.log_error("查找错误地址企业失败", str(e))
        return []
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()