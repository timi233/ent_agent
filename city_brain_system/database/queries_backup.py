from database.connection import get_db_connection

def get_customer_by_name(customer_name):
    """
    根据企业名称查询客户信息，支持精确匹配和模糊匹配
    同时搜索QD_customer表和QD_enterprise_chain_leader表
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # 首先在QD_customer表中尝试精确匹配
    customer_query = """
    SELECT c.*, 
           i.industry_name,
           b.brain_name,
           e.enterprise_name as chain_leader_name,
           a.district_name,
           'customer' as source_table
    FROM QD_customer c
    LEFT JOIN QD_industry i ON c.industry_id = i.industry_id
    LEFT JOIN QD_industry_brain b ON c.brain_id = b.brain_id
    LEFT JOIN QD_enterprise_chain_leader e ON c.chain_leader_id = e.enterprise_id
    LEFT JOIN QD_area a ON b.area_id = a.area_id
    WHERE c.customer_name = %s
    """
    
    cursor.execute(customer_query, (customer_name,))
    result = cursor.fetchone()
    
    # 如果在customer表中没找到，搜索链主企业表
    if not result:
        chain_leader_query = """
        SELECT e.enterprise_id as customer_id,
               e.enterprise_name as customer_name,
               NULL as data_source,
               NULL as address,
               1 as tag_result,
               e.industry_id,
               NULL as brain_id,
               e.enterprise_id as chain_leader_id,
               i.industry_name,
               NULL as brain_name,
               e.enterprise_name as chain_leader_name,
               a.district_name,
               'chain_leader' as source_table
        FROM QD_enterprise_chain_leader e
        LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
        LEFT JOIN QD_area a ON e.area_id = a.area_id
        WHERE e.enterprise_name = %s
        """
        
        cursor.execute(chain_leader_query, (customer_name,))
        result = cursor.fetchone()
    
    # 如果精确匹配都没有结果，尝试模糊匹配
    if not result:
        # 移除常见的企业后缀进行模糊匹配
        base_name = customer_name
        suffixes_to_remove = ['股份有限公司', '有限公司', '集团有限公司', '控股有限公司', '股份公司', '集团', '公司']
        
        for suffix in suffixes_to_remove:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                break
        
        # 先在customer表中模糊匹配
        customer_fuzzy_query = """
        SELECT c.*, 
               i.industry_name,
               b.brain_name,
               e.enterprise_name as chain_leader_name,
               a.district_name,
               'customer' as source_table
        FROM QD_customer c
        LEFT JOIN QD_industry i ON c.industry_id = i.industry_id
        LEFT JOIN QD_industry_brain b ON c.brain_id = b.brain_id
        LEFT JOIN QD_enterprise_chain_leader e ON c.chain_leader_id = e.enterprise_id
        LEFT JOIN QD_area a ON b.area_id = a.area_id
        WHERE c.customer_name LIKE %s
        ORDER BY 
            CASE 
                WHEN c.customer_name = %s THEN 1
                WHEN c.customer_name LIKE %s THEN 2
                ELSE 3
            END
        LIMIT 1
        """
        
        like_pattern = f"%{base_name}%"
        exact_pattern = customer_name
        starts_with_pattern = f"{base_name}%"
        
        cursor.execute(customer_fuzzy_query, (like_pattern, exact_pattern, starts_with_pattern))
        result = cursor.fetchone()
        
        # 如果customer表中模糊匹配也没找到，在链主企业表中模糊匹配
        if not result:
            chain_leader_fuzzy_query = """
            SELECT e.enterprise_id as customer_id,
                   e.enterprise_name as customer_name,
                   NULL as data_source,
                   NULL as address,
                   1 as tag_result,
                   e.industry_id,
                   NULL as brain_id,
                   e.enterprise_id as chain_leader_id,
                   i.industry_name,
                   NULL as brain_name,
                   e.enterprise_name as chain_leader_name,
                   a.district_name,
                   'chain_leader' as source_table
            FROM QD_enterprise_chain_leader e
            LEFT JOIN QD_industry i ON e.industry_id = i.industry_id
            LEFT JOIN QD_area a ON e.area_id = a.area_id
            WHERE e.enterprise_name LIKE %s
            ORDER BY 
                CASE 
                    WHEN e.enterprise_name = %s THEN 1
                    WHEN e.enterprise_name LIKE %s THEN 2
                    ELSE 3
                END
            LIMIT 1
            """
            
            cursor.execute(chain_leader_fuzzy_query, (like_pattern, exact_pattern, starts_with_pattern))
            result = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return result

def update_customer_info(customer_id, updates):
    """
    更新客户信息
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # 构建动态更新语句
    set_clauses = []
    values = []
    
    # 只处理QD_customer表中实际存在的字段
    allowed_fields = {
        'address': 'address',
        'customer_name': 'customer_name',
        'data_source': 'data_source'
        # district_name不在QD_customer表中，通过JOIN获取，暂时跳过
        # industry_id, brain_id, chain_leader_id需要通过名称查找ID，暂时简化处理
    }
    
    for field, value in updates.items():
        if field in allowed_fields:
            db_field = allowed_fields[field]
            set_clauses.append(f"{db_field} = %s")
            values.append(value)
        else:
            print(f"跳过字段 {field}，需要复杂的ID映射逻辑")
    
    if not set_clauses:
        cursor.close()
        connection.close()
        return True  # 没有需要更新的字段，返回成功
    
    values.append(customer_id)
    query = f"UPDATE QD_customer SET {', '.join(set_clauses)} WHERE customer_id = %s"
    
    try:
        cursor.execute(query, values)
        connection.commit()
        success = cursor.rowcount > 0
        print(f"更新客户信息成功: customer_id={customer_id}, 更新字段={list(updates.keys())}")
    except Exception as e:
        print(f"更新客户信息失败: {e}")
        connection.rollback()
        success = False
    finally:
        cursor.close()
        connection.close()
    
    return success

def insert_customer(customer_data):
    """
    插入新的客户信息
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    
    query = """
    INSERT INTO QD_customer 
    (customer_name, data_source, address, tag_result, industry_id, brain_id, chain_leader_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    cursor.execute(query, (
        customer_data['customer_name'],
        customer_data['data_source'],
        customer_data['address'],
        customer_data['tag_result'],
        customer_data['industry_id'],
        customer_data['brain_id'],
        customer_data['chain_leader_id']
    ))
    
    connection.commit()
    customer_id = cursor.lastrowid
    
    cursor.close()
    connection.close()
    
    return customer_id

def get_customer_by_id(customer_id):
    """
    根据客户ID查询客户信息
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
    SELECT c.*, 
           i.industry_name,
           b.brain_name,
           e.enterprise_name as chain_leader_name,
           a.district_name
    FROM QD_customer c
    LEFT JOIN QD_industry i ON c.industry_id = i.industry_id
    LEFT JOIN QD_industry_brain b ON c.brain_id = b.brain_id
    LEFT JOIN QD_enterprise_chain_leader e ON c.chain_leader_id = e.enterprise_id
    LEFT JOIN QD_area a ON b.area_id = a.area_id
    WHERE c.customer_id = %s
    """
    
    cursor.execute(query, (customer_id,))
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return result