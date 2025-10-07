"""
产业大脑和链主企业匹配工具
"""

def get_industry_brain_by_region_and_industry(region, industry):
    """
    根据地区和行业获取产业大脑信息
    """
    # 产业大脑映射表 - 按地区和行业分类
    brain_mapping = {
        '青岛市': {
            '食品饮料制造业': '青岛食品饮料产业大脑',
            '汽车制造业': '青岛汽车产业大脑',
            '海洋装备制造业': '青岛海洋装备产业大脑',
            '纺织服装业': '青岛纺织服装产业大脑',
            '化工业': '青岛化工产业大脑',
            '电子信息制造业': '青岛电子信息产业大脑',
            '机械制造业': '青岛机械制造产业大脑'
        },
        '济南市': {
            '软件和信息技术服务业': '济南软件信息产业大脑',
            '汽车制造业': '济南汽车产业大脑',
            '机械制造业': '济南机械制造产业大脑',
            '生物医药业': '济南生物医药产业大脑',
            '新材料产业': '济南新材料产业大脑'
        },
        '烟台市': {
            '食品饮料制造业': '烟台食品饮料产业大脑',
            '海洋装备制造业': '烟台海洋装备产业大脑',
            '化工业': '烟台化工产业大脑',
            '黄金产业': '烟台黄金产业大脑'
        },
        '潍坊市': {
            '化工业': '潍坊化工产业大脑',
            '农业机械制造业': '潍坊农机产业大脑',
            '纺织服装业': '潍坊纺织服装产业大脑'
        },
        '临沂市': {
            '物流业': '临沂物流产业大脑',
            '建材业': '临沂建材产业大脑',
            '食品加工业': '临沂食品加工产业大脑'
        }
    }
    
    # 行业相似度映射 - 用于匹配相近行业
    industry_similarity = {
        '食品饮料制造业': ['食品加工业', '农产品加工业', '饮料制造业'],
        '汽车制造业': ['汽车零部件制造业', '新能源汽车制造业', '交通运输设备制造业'],
        '机械制造业': ['农业机械制造业', '工程机械制造业', '通用设备制造业'],
        '化工业': ['石油化工业', '精细化工业', '化学原料制造业'],
        '纺织服装业': ['纺织业', '服装制造业', '家纺制造业'],
        '电子信息制造业': ['软件和信息技术服务业', '通信设备制造业', '计算机制造业']
    }
    
    if not region or not industry:
        return None
    
    # 1. 直接匹配：地区 + 行业
    region_brains = brain_mapping.get(region, {})
    if industry in region_brains:
        return region_brains[industry]
    
    # 2. 相近行业匹配
    for brain_industry, similar_industries in industry_similarity.items():
        if industry in similar_industries and brain_industry in region_brains:
            return region_brains[brain_industry]
    
    # 3. 反向匹配：当前行业的相似行业
    for similar_industry in industry_similarity.get(industry, []):
        if similar_industry in region_brains:
            return region_brains[similar_industry]
    
    return None

def get_chain_leader_by_region_and_industry(region, industry):
    """
    根据地区和行业获取链主企业信息
    """
    # 链主企业映射表 - 按地区和产业链分类
    chain_leader_mapping = {
        '青岛市': {
            '食品饮料制造业': '青岛啤酒股份有限公司',
            '汽车制造业': '一汽解放青岛汽车有限公司',
            '海洋装备制造业': '中车青岛四方机车车辆股份有限公司',
            '纺织服装业': '青岛即发集团控股有限公司',
            '化工业': '青岛海湾化学有限公司',
            '电子信息制造业': '海信集团有限公司',
            '机械制造业': '青岛重工股份有限公司'
        },
        '济南市': {
            '软件和信息技术服务业': '浪潮集团有限公司',
            '汽车制造业': '中国重汽集团有限公司',
            '机械制造业': '济南二机床集团有限公司',
            '生物医药业': '齐鲁制药集团有限公司',
            '新材料产业': '山东南山铝业股份有限公司'
        },
        '烟台市': {
            '食品饮料制造业': '烟台张裕集团有限公司',
            '海洋装备制造业': '中集来福士海洋工程有限公司',
            '化工业': '万华化学集团股份有限公司',
            '黄金产业': '山东黄金集团有限公司'
        },
        '潍坊市': {
            '化工业': '潍柴动力股份有限公司',
            '农业机械制造业': '雷沃重工股份有限公司',
            '纺织服装业': '山东如意科技集团有限公司'
        },
        '临沂市': {
            '物流业': '临沂商城集团有限公司',
            '建材业': '山东兰陵集团有限公司',
            '食品加工业': '金锣集团有限公司'
        }
    }
    
    # 产业链相似度映射
    industry_chain_similarity = {
        '食品饮料制造业': ['食品加工业', '农产品加工业', '饮料制造业', '酒类制造业'],
        '汽车制造业': ['汽车零部件制造业', '新能源汽车制造业', '交通运输设备制造业'],
        '机械制造业': ['农业机械制造业', '工程机械制造业', '通用设备制造业', '专用设备制造业'],
        '化工业': ['石油化工业', '精细化工业', '化学原料制造业'],
        '纺织服装业': ['纺织业', '服装制造业', '家纺制造业'],
        '电子信息制造业': ['软件和信息技术服务业', '通信设备制造业', '计算机制造业']
    }
    
    if not region or not industry:
        return None
    
    # 1. 直接匹配：地区 + 行业
    region_chains = chain_leader_mapping.get(region, {})
    if industry in region_chains:
        return region_chains[industry]
    
    # 2. 产业链相似度匹配
    for chain_industry, similar_industries in industry_chain_similarity.items():
        if industry in similar_industries and chain_industry in region_chains:
            return region_chains[chain_industry]
    
    # 3. 反向匹配：当前行业的相似产业链
    for similar_industry in industry_chain_similarity.get(industry, []):
        if similar_industry in region_chains:
            return region_chains[similar_industry]
    
    return None

def enhance_brain_and_chain_info(company_data):
    """
    为企业数据补充产业大脑和链主企业信息
    """
    region = company_data.get('district_name')
    industry = company_data.get('industry_name')
    
    # 获取产业大脑信息
    brain_name = get_industry_brain_by_region_and_industry(region, industry)
    if brain_name:
        company_data['brain_name'] = brain_name
        print(f"为企业补充产业大脑信息: {brain_name}")
    else:
        company_data['brain_name'] = f"{region}暂无相应产业大脑" if region else "暂无相应产业大脑"
        print(f"未找到匹配的产业大脑: {region} - {industry}")
    
    # 获取链主企业信息
    chain_leader = get_chain_leader_by_region_and_industry(region, industry)
    if chain_leader:
        company_data['chain_leader_name'] = chain_leader
        print(f"为企业补充链主企业信息: {chain_leader}")
    else:
        company_data['chain_leader_name'] = f"{region}暂无相应产业链主企业" if region else "暂无相应产业链主企业"
        print(f"未找到匹配的链主企业: {region} - {industry}")
    
    return company_data