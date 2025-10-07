import re
from api.bocha_client import search_web

def extract_industry_from_search(company_name):
    """
    通过联网搜索获取企业的行业信息
    """
    try:
        # 构建搜索查询
        search_query = f"{company_name} 行业 主营业务"
        
        # 执行搜索
        search_results = search_web(search_query)
        
        if not search_results or 'results' not in search_results:
            return None
            
        # 从搜索结果中提取行业信息
        industry_info = parse_industry_from_results(search_results['results'], company_name)
        
        return industry_info
        
    except Exception as e:
        print(f"搜索行业信息时出错: {e}")
        return None

def parse_industry_from_results(results, company_name):
    """
    从搜索结果中解析行业信息
    """
    # 常见行业关键词模式
    industry_patterns = [
        # 制造业相关
        r'(啤酒|饮料|食品|制造|生产|加工)(?:业|行业|企业|公司)',
        r'(汽车|机械|电子|化工|纺织|钢铁|有色金属)(?:业|行业|制造)',
        
        # 服务业相关
        r'(金融|银行|保险|证券|投资)(?:业|行业|服务)',
        r'(房地产|建筑|工程|装修)(?:业|行业|开发)',
        r'(零售|批发|贸易|商业|电商)(?:业|行业)',
        r'(物流|运输|快递|仓储)(?:业|行业|服务)',
        r'(教育|培训|咨询|医疗|健康)(?:业|行业|服务)',
        r'(旅游|酒店|餐饮|娱乐)(?:业|行业|服务)',
        
        # 科技相关
        r'(软件|互联网|科技|IT|通信|电信)(?:业|行业|服务)',
        r'(人工智能|大数据|云计算|区块链)(?:业|行业|技术)',
        
        # 能源相关
        r'(石油|天然气|煤炭|电力|新能源|太阳能|风能)(?:业|行业)',
        
        # 农业相关
        r'(农业|种植|养殖|渔业|林业)(?:业|行业)',
        
        # 通用行业描述
        r'主要从事\s*([^。，,\s]{2,10}?)(?:业务|行业|生产|经营)',
        r'(?:属于|隶属于|归属)\s*([^。，,\s]{2,10}?)(?:行业|领域)',
        r'([^。，,\s]{2,10}?)(?:行业|领域)(?:的|中的)(?:龙头|领军|知名|著名)企业',
    ]
    
    # 行业标准化映射
    industry_mapping = {
        '啤酒': '食品饮料制造业',
        '饮料': '食品饮料制造业', 
        '食品': '食品饮料制造业',
        '汽车': '汽车制造业',
        '机械': '机械制造业',
        '电子': '电子信息制造业',
        '化工': '化学工业',
        '纺织': '纺织业',
        '钢铁': '钢铁工业',
        '金融': '金融业',
        '银行': '金融业',
        '保险': '保险业',
        '房地产': '房地产业',
        '建筑': '建筑业',
        '零售': '零售业',
        '批发': '批发业',
        '物流': '物流业',
        '教育': '教育业',
        '医疗': '医疗健康业',
        '旅游': '旅游业',
        '软件': '软件和信息技术服务业',
        '互联网': '互联网和相关服务业',
        '通信': '电信、广播电视和卫星传输服务业',
        '石油': '石油和天然气开采业',
        '电力': '电力、热力、燃气及水生产和供应业',
        '农业': '农、林、牧、渔业',
    }
    
    for result in results[:5]:  # 只检查前5个结果
        content = result.get('content', '') + ' ' + result.get('title', '')
        
        for pattern in industry_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                for match in matches:
                    # 清理匹配结果
                    industry = match.strip()
                    
                    # 标准化行业名称
                    for key, standard_name in industry_mapping.items():
                        if key in industry:
                            return standard_name
                    
                    # 如果没有找到标准映射，返回原始匹配
                    if len(industry) >= 2 and len(industry) <= 15:
                        # 确保行业名称以"业"结尾
                        if not industry.endswith('业'):
                            industry += '业'
                        return industry
    
    # 特殊处理：根据公司名称推断行业
    if '啤酒' in company_name:
        return '食品饮料制造业'
    elif '银行' in company_name:
        return '金融业'
    elif '保险' in company_name:
        return '保险业'
    elif '科技' in company_name or '技术' in company_name:
        return '软件和信息技术服务业'
    elif '地产' in company_name or '置业' in company_name:
        return '房地产业'
    elif '汽车' in company_name:
        return '汽车制造业'
    
    return None

def get_company_industry(company_name, address=None):
    """
    获取企业行业信息的主函数
    """
    # 首先尝试从公司名称直接推断
    if '啤酒' in company_name:
        return '食品饮料制造业'
    
    # 如果无法直接推断，进行联网搜索
    industry = extract_industry_from_search(company_name)
    
    if industry:
        print(f"通过联网搜索获取行业信息: {industry}")
        return industry
    
    return None