"""
地址解析工具
用于从企业地址中提取城市信息
"""

import re

def extract_city_from_address(address):
    """
    从企业地址中提取市级城市名称
    
    Args:
        address (str): 企业地址
        
    Returns:
        str: 提取的城市名称，如果提取失败返回None
    """
    if not address or not isinstance(address, str):
        return None
    
    # 常见的市级城市模式
    city_patterns = [
        # 直辖市模式：北京市、上海市、天津市、重庆市
        r'(北京市|上海市|天津市|重庆市)',
        # 地级市模式：XX市（避免重复匹配）
        r'([^省自治区市]{2,6}市)',
        # 特殊行政区
        r'(香港|澳门)',
    ]
    
    for pattern in city_patterns:
        match = re.search(pattern, address)
        if match:
            city = match.group(1)
            # 过滤掉一些常见的非城市词汇
            exclude_words = ['公司', '集团', '有限', '股份', '企业', '商贸', '科技', '发展']
            if not any(word in city for word in exclude_words):
                return city
    
    return None

def search_company_address(company_name):
    """
    根据企业名称联网搜索获取完整地址信息
    
    Args:
        company_name (str): 企业名称
        
    Returns:
        str: 搜索到的企业地址，如果搜索失败返回None
    """
    if not company_name:
        return None
    
    try:
        from api.bocha_client import search_web
        
        # 搜索企业地址信息 - 使用更精确的搜索词
        search_queries = [
            f"{company_name} 注册地址",
            f"{company_name} 公司地址", 
            f"{company_name} 总部地址",
            f"{company_name} 办公地址"
        ]
        
        for search_query in search_queries:
            search_result = search_web(search_query)
            
            if search_result and search_result.get('code') == 200:
                data = search_result.get('data', {})
                if isinstance(data, dict):
                    content = data.get('content', '') or data.get('text', '') or str(data)
                    
                    # 优先查找最新的地址信息（地址变更公告等）
                    priority_patterns = [
                        # 最高优先级：地址变更公告
                        rf'(?:地址变更|新办公地址|总部新|迁至).*?([^。\n]*(?:市|区|县)[^。\n]*(?:街道|路|号|大厦|中心|园区)[^。\n]*)',
                        # 高优先级：当前地址、现地址
                        rf'(?:当前地址|现地址|现办公地址)[:：]\s*([^。\n]+(?:市|区|县|镇|街道|路|号)[^。\n]*)',
                    ]
                    
                    # 先尝试优先级模式
                    for pattern in priority_patterns:
                        match = re.search(pattern, content)
                        if match:
                            address = match.group(1).strip()
                            if len(address) > 5 and ('市' in address or '区' in address or '县' in address):
                                print(f"搜索到企业最新地址: {company_name} -> {address}")
                                return address
                    
                    # 如果没有找到最新地址，再使用常规模式
                    address_patterns = [
                        # 最精确：企业名称 + 地址关键词 + 具体地址
                        rf'{re.escape(company_name)}.*?(?:注册地址|公司地址|总部地址|办公地址|地址)[:：]\s*([^。\n]+(?:市|区|县|镇|街道|路|号)[^。\n]*)',
                        # 次精确：地址关键词 + 具体地址
                        r'(?:注册地址|公司地址|总部地址|办公地址|地址)[:：]\s*([^。\n]+(?:市|区|县|镇|街道|路|号)[^。\n]*)',
                        # 一般：位于、坐落于等 + 地址
                        r'(?:位于|坐落于|设在)[:：]?\s*([^。\n]+(?:市|区|县|镇|街道|路|号)[^。\n]*)',
                        # 最后：企业名称附近的地址信息
                        rf'{re.escape(company_name)}[^。\n]*?([^。\n]*(?:省|市|区|县)[^。\n]*(?:街道|路|号|大厦|中心|园区)[^。\n]*)',
                    ]
                    
                    for pattern in address_patterns:
                        match = re.search(pattern, content)
                        if match:
                            address = match.group(1).strip()
                            # 过滤掉明显不是地址的内容和过期信息
                            if (len(address) > 5 and 
                                ('市' in address or '区' in address or '县' in address) and
                                not any(word in address for word in ['吊销', '注销', '已迁出', '原地址'])):
                                print(f"搜索到企业地址: {company_name} -> {address}")
                                return address
        
        return None
        
    except Exception as e:
        print(f"搜索企业地址失败: {e}")
        return None

def search_city_by_company_name(company_name, update_database=True):
    """
    根据企业名称联网搜索获取城市信息
    先搜索企业地址，再从地址中提取城市
    
    Args:
        company_name (str): 企业名称
        update_database (bool): 是否将搜索到的地址更新到数据库
        
    Returns:
        str: 搜索到的城市名称，如果搜索失败返回None
    """
    if not company_name:
        return None
    
    # 先搜索企业完整地址
    address = search_company_address(company_name)
    if address:
        # 从搜索到的地址中提取城市
        city = extract_city_from_address(address)
        if city:
            print(f"从搜索地址提取城市: {address} -> {city}")
            
            # 如果启用数据库更新，将新地址保存到数据库
            if update_database:
                try:
                    from .address_updater import update_customer_address_info
                    success = update_customer_address_info(company_name, address, city)
                    if success:
                        print(f"✅ 地址已更新到数据库: {company_name} -> {city}")
                    else:
                        print(f"⚠️ 地址更新到数据库失败: {company_name}")
                except Exception as update_error:
                    print(f"⚠️ 数据库更新异常: {update_error}")
            
            return city
    
    return None

def get_company_city(company_data, company_name):
    """
    获取企业所在城市信息
    优先从地址提取，其次联网搜索
    
    Args:
        company_data (dict): 企业数据
        company_name (str): 企业名称
        
    Returns:
        str: 城市名称或None
    """
    # 1. 优先从企业地址提取城市
    address = company_data.get('address')
    if address:
        city = extract_city_from_address(address)
        if city:
            print(f"从地址提取城市: {address} -> {city}")
            return city
    
    # 2. 如果地址不存在或提取失败，联网搜索
    if company_name:
        city = search_city_by_company_name(company_name)
        if city:
            print(f"联网搜索获取城市: {company_name} -> {city}")
            return city
    
    return None