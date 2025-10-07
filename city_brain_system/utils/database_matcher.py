"""
基于真实数据库的产业大脑和链主企业匹配工具
"""
from database.connection import get_db_connection

def get_industry_brain_by_company(company_name, region, industry_name):
    """
    根据企业信息获取对应的产业大脑
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 首先根据行业名称获取行业ID
        cursor.execute("SELECT industry_id FROM QD_industry WHERE industry_name = %s", (industry_name,))
        industry_result = cursor.fetchone()
        
        if not industry_result:
            return None
            
        industry_id = industry_result[0]
        
        # 根据地区获取区域ID
        cursor.execute("SELECT area_id FROM QD_area WHERE city_name = %s", (region,))
        area_results = cursor.fetchall()
        
        if not area_results:
            return None
        
        # 查找该行业对应的产业大脑
        cursor.execute("""
            SELECT ib.brain_name, ib.area_id, a.district_name
            FROM QD_industry_brain ib
            JOIN QD_brain_industry_rel bir ON ib.brain_id = bir.brain_id
            JOIN QD_area a ON ib.area_id = a.area_id
            WHERE bir.industry_id = %s
        """, (industry_id,))
        
        brain_results = cursor.fetchall()
        
        if brain_results:
            # 优先返回同地区的产业大脑，如果没有则返回第一个
            for brain_name, brain_area_id, district_name in brain_results:
                return brain_name
            
        return None
        
    except Exception as e:
        print(f"查询产业大脑时出错: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_chain_leader_status(company_name, region, industry_name):
    """
    根据企业信息获取产业链状态
    优先检查是否为链主企业，使用数据库中的真实行业信息
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 首先检查是否为链主企业（使用精确匹配和模糊匹配）
        cursor.execute("""
            SELECT ecl.enterprise_name, i.industry_name, a.district_name
            FROM QD_enterprise_chain_leader ecl
            JOIN QD_industry i ON ecl.industry_id = i.industry_id
            JOIN QD_area a ON ecl.area_id = a.area_id
            WHERE ecl.enterprise_name = %s
        """, (company_name,))
        
        chain_result = cursor.fetchone()
        
        if chain_result:
            enterprise_name, chain_industry, district = chain_result
            return f"{chain_industry}，链主"
        
        # 如果精确匹配没找到，尝试模糊匹配（去掉常见后缀）
        base_name = company_name
        suffixes_to_remove = ['股份有限公司', '有限公司', '集团有限公司', '控股有限公司', '股份公司', '集团', '公司']
        
        for suffix in suffixes_to_remove:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                break
        
        # 使用基础名称进行模糊匹配
        cursor.execute("""
            SELECT ecl.enterprise_name, i.industry_name, a.district_name
            FROM QD_enterprise_chain_leader ecl
            JOIN QD_industry i ON ecl.industry_id = i.industry_id
            JOIN QD_area a ON ecl.area_id = a.area_id
            WHERE ecl.enterprise_name LIKE %s
            ORDER BY 
                CASE 
                    WHEN ecl.enterprise_name = %s THEN 1
                    WHEN ecl.enterprise_name LIKE %s THEN 2
                    ELSE 3
                END
            LIMIT 1
        """, (f"%{base_name}%", company_name, f"{base_name}%"))
        
        chain_result = cursor.fetchone()
        
        if chain_result:
            enterprise_name, chain_industry, district = chain_result
            return f"{chain_industry}，链主"
        
        # 如果不是链主，检查是否属于某个产业链的成员企业
        if industry_name:
            cursor.execute("SELECT industry_id FROM QD_industry WHERE industry_name = %s", (industry_name,))
            industry_result = cursor.fetchone()
            
            if industry_result:
                industry_id = industry_result[0]
                
                # 检查该行业是否有链主企业
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM QD_enterprise_chain_leader 
                    WHERE industry_id = %s
                """, (industry_id,))
                
                chain_count = cursor.fetchone()[0]
                
                if chain_count > 0:
                    return f"{industry_name}，成员企业"
        
        return "暂未归类"
        
    except Exception as e:
        print(f"查询产业链状态时出错: {e}")
        return "暂未归类"
    finally:
        cursor.close()
        conn.close()

def update_customer_industry_info(customer_id, industry_name):
    """
    更新客户的行业信息
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 获取行业ID
        cursor.execute("SELECT industry_id FROM QD_industry WHERE industry_name = %s", (industry_name,))
        industry_result = cursor.fetchone()
        
        if industry_result:
            industry_id = industry_result[0]
            
            # 更新客户的行业ID
            cursor.execute("""
                UPDATE QD_customer 
                SET industry_id = %s 
                WHERE customer_id = %s
            """, (industry_id, customer_id))
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"更新客户行业信息时出错: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
    
    return False

def update_customer_brain_info(customer_id, company_name, industry_name):
    """
    更新客户的产业大脑信息
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 获取行业ID
        cursor.execute("SELECT industry_id FROM QD_industry WHERE industry_name = %s", (industry_name,))
        industry_result = cursor.fetchone()
        
        if not industry_result:
            return False
            
        industry_id = industry_result[0]
        
        # 查找对应的产业大脑ID
        cursor.execute("""
            SELECT ib.brain_id
            FROM QD_industry_brain ib
            JOIN QD_brain_industry_rel bir ON ib.brain_id = bir.brain_id
            WHERE bir.industry_id = %s
            LIMIT 1
        """, (industry_id,))
        
        brain_result = cursor.fetchone()
        
        if brain_result:
            brain_id = brain_result[0]
            
            # 更新客户的产业大脑ID
            cursor.execute("""
                UPDATE QD_customer 
                SET brain_id = %s 
                WHERE customer_id = %s
            """, (brain_id, customer_id))
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"更新客户产业大脑信息时出错: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
    
    return False

def update_customer_chain_leader_info(customer_id, company_name):
    """
    更新客户的链主企业信息
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查是否为链主企业
        cursor.execute("""
            SELECT enterprise_id
            FROM QD_enterprise_chain_leader
            WHERE enterprise_name = %s
        """, (company_name,))
        
        chain_result = cursor.fetchone()
        
        if chain_result:
            chain_leader_id = chain_result[0]
            
            # 更新客户的链主企业ID
            cursor.execute("""
                UPDATE QD_customer 
                SET chain_leader_id = %s 
                WHERE customer_id = %s
            """, (chain_leader_id, customer_id))
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"更新客户链主企业信息时出错: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
    
    return False