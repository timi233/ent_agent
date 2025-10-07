import re

def extract_company_name(text):
    """
    从文本中提取公司名称
    优先提取完整的公司名称，如果只能提取到简称则标记为不完整
    """
    # 匹配完整的公司名称（带有公司后缀）
    complete_patterns = [
        r'([\u4e00-\u9fa5]{2,20}(?:股份有限公司|有限责任公司|有限公司|股份公司|集团有限公司|集团股份有限公司|集团公司|公司|集团|企业|厂|店|中心|协会|学会))',
        r'((?:阿里巴巴|腾讯|百度|京东|华为|小米|美团|滴滴|字节跳动)[\u4e00-\u9fa5]{0,10}(?:股份有限公司|有限责任公司|有限公司|股份公司|集团有限公司|集团股份有限公司|集团公司|公司|集团))'
    ]
    
    # 先尝试匹配完整的公司名称
    for pattern in complete_patterns:
        match = re.search(pattern, text)
        if match:
            return {
                'name': match.group(1),
                'is_complete': True
            }
    
    # 如果没有找到完整名称，尝试匹配简称或品牌名
    incomplete_patterns = [
        # 知名品牌名称（不带后缀，被认为是不完整的）
        r'(青岛啤酒|茅台|五粮液|中国平安|招商银行|工商银行|建设银行|中国银行|农业银行|中国石油|中国石化|中国移动|中国联通|中国电信|格力电器|美的集团|海尔智家|比亚迪|长城汽车|吉利汽车|万科|恒大|碧桂园|中国建筑|中国中铁|中国铁建)',
        # 通用中文企业名称（2-10个汉字，不带公司后缀）
        r'([\u4e00-\u9fa5]{2,10})'
    ]
    
    for pattern in incomplete_patterns:
        match = re.search(pattern, text)
        if match:
            company_name = match.group(1)
            # 如果是通用模式匹配的，需要进一步验证
            if pattern == r'([\u4e00-\u9fa5]{2,10})':
                # 排除一些明显不是公司名称的词汇
                exclude_words = ['查询', '信息', '请问', '什么', '怎么', '哪里', '为什么', '如何', '谢谢', '你好', '公司', '企业', '集团']
                if company_name not in exclude_words:
                    return {
                        'name': company_name,
                        'is_complete': False
                    }
            else:
                return {
                    'name': company_name,
                    'is_complete': False
                }
    
    # 如果没有匹配到，返回None
    return None

def is_complete_company_name(company_name):
    """
    判断公司名称是否完整（是否包含公司后缀）
    """
    complete_suffixes = ['股份有限公司', '有限责任公司', '有限公司', '股份公司', '集团有限公司', '集团股份有限公司', '集团公司', '公司', '集团', '企业', '厂', '店', '中心', '协会', '学会']
    
    for suffix in complete_suffixes:
        if company_name.endswith(suffix):
            return True
    
    return False

def extract_company_info_from_search_results(search_results):
    """
    从搜索结果中提取公司信息
    """
    # 这是一个简化的实现
    # 实际应用中需要解析搜索结果并提取有用信息
    company_info = {
        'name': '',
        'description': '',
        'website': '',
        'industry': ''
    }
    
    if search_results and 'data' in search_results and 'webPages' in search_results['data']:
        web_pages = search_results['data']['webPages']
        if 'value' in web_pages and len(web_pages['value']) > 0:
            first_result = web_pages['value'][0]
            company_info['name'] = first_result.get('name', '')
            company_info['description'] = first_result.get('snippet', '')
            company_info['website'] = first_result.get('url', '')
    
    return company_info