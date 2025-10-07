from database.queries import get_customer_by_name, update_customer_info, insert_customer
from api.bocha_client import search_web
from api.llm_client import generate_summary
from utils.text_extractor import extract_company_name, extract_company_info_from_search_results
from utils.address_extractor import get_company_city
from utils.industry_extractor import get_company_industry
from utils.database_matcher import (
    get_industry_brain_by_company, 
    get_chain_leader_status,
    update_customer_industry_info,
    update_customer_brain_info,
    update_customer_chain_leader_info
)
from utils.revenue_searcher import get_company_revenue_info
from utils.ranking_checker import get_company_ranking_status
from utils.news_searcher import get_company_business_news
import re

def process_company_info(user_input):
    """
    处理用户输入的企业信息
    """
    # 1. 提取公司名称
    extraction_result = extract_company_name(user_input)
    
    if not extraction_result:
        # 如果本地无法提取公司名称，尝试通过网络搜索推断
        complete_name = infer_company_name_from_search(user_input)
        if not complete_name:
            return {
                "status": "error",
                "message": "无法从输入中提取公司名称，请提供更明确的公司信息"
            }
        company_name = complete_name
        is_complete = True  # 从搜索中获取的应该是完整名称
    else:
        company_name = extraction_result['name']
        is_complete = extraction_result['is_complete']
        
        # 如果提取到的名称不完整，尝试通过搜索获取完整名称
        if not is_complete:
            complete_name = infer_complete_company_name_from_search(company_name)
            if complete_name:
                company_name = complete_name
                is_complete = True
    
    # 2. 查询本地数据库（先用完整名称查询，如果没有再用简称查询）
    local_data = get_customer_by_name(company_name)
    if not local_data and is_complete:
        # 如果完整名称没找到，尝试用简称查询
        original_name = extraction_result['name'] if extraction_result else None
        if original_name and original_name != company_name:
            local_data = get_customer_by_name(original_name)
    
    if local_data:
        # 存在本地数据
        return process_with_local_data(local_data)
    else:
        # 不存在本地数据
        return process_without_local_data(company_name)

def process_with_local_data(local_data):
    """
    处理存在本地数据的情况
    """
    # 优化所在地区信息
    enhanced_data = enhance_location_info(local_data)
    
    # 优化行业信息
    enhanced_data = enhance_industry_info(enhanced_data)
    
    # 补充产业大脑和链主企业信息
    enhanced_data = enhance_brain_and_chain_info(enhanced_data)
    
    # 补充营收信息和企业地位
    enhanced_data = enhance_revenue_and_status_info(enhanced_data)
    
    # 获取企业新闻
    company_name = enhanced_data.get('customer_name', '')
    try:
        news_result = get_company_business_news(company_name)
        news_data = {
            "summary": news_result.get('content', '暂无最新商业资讯'),
            "references": news_result.get('sources', [])
        }
    except Exception as e:
        print(f"获取企业新闻失败: {e}")
        news_data = {
            "summary": "暂无最新商业资讯",
            "references": []
        }
    
    # 检查是否有数据更新，如果有则同步到数据库
    updates = {}
    sync_messages = []
    
    if enhanced_data.get('district_name') and enhanced_data['district_name'] != local_data.get('district_name'):
        updates['district_name'] = enhanced_data['district_name']
        sync_messages.append(f"已同步所在地区到数据库: {enhanced_data['district_name']}")
    
    if enhanced_data.get('industry_name') and enhanced_data['industry_name'] != local_data.get('industry_name'):
        updates['industry_name'] = enhanced_data['industry_name']
        sync_messages.append(f"已同步所属行业到数据库: {enhanced_data['industry_name']}")
    
    if updates:
        try:
            update_customer_info(enhanced_data['customer_id'], updates)
            for message in sync_messages:
                print(message)
        except Exception as e:
            print(f"数据库同步失败: {e}")
    
    # 使用LLM对所有收集到的信息进行智能总结和分析
    llm_analysis = generate_comprehensive_company_analysis(enhanced_data, news_data)
    
    result = {
        "status": "success",
        "data": {
            "company_name": enhanced_data.get('customer_name', ''),
            "analysis": llm_analysis,
            "raw_details": {
                "企业名称": enhanced_data.get('customer_name', ''),
                "所在地区": enhanced_data.get('district_name', ''),
                "企业地址": enhanced_data.get('address', ''),
                "所属行业": enhanced_data.get('industry_name', ''),
                "产业大脑": enhanced_data.get('brain_name', ''),
                "产业链状态": enhanced_data.get('chain_status', ''),
                "近三年营收情况": enhanced_data.get('revenue_info', '暂无营收数据'),
                "企业地位": enhanced_data.get('company_status', '暂无排名信息'),
                "数据来源": enhanced_data.get('data_source', '')
            },
            "news": news_data
        }
    }
    
    # 添加同步消息
    if sync_messages:
        result["sync_messages"] = sync_messages
    
    return result

def enhance_location_info(data):
    """
    优化企业所在地区信息
    优先从地址提取，其次联网搜索
    """
    enhanced_data = data.copy()
    
    # 如果district_name为空，尝试提取城市信息
    if not enhanced_data.get('district_name'):
        company_name = enhanced_data.get('customer_name')
        city = get_company_city(enhanced_data, company_name)
        
        if city:
            enhanced_data['district_name'] = city
            print(f"为企业 {company_name} 补充所在地区: {city}")
    
    return enhanced_data

def enhance_industry_info(data):
    """
    优化企业行业信息
    当数据库中没有行业信息时，通过联网搜索获取
    """
    enhanced_data = data.copy()
    
    # 如果industry_name为空，尝试获取行业信息
    if not enhanced_data.get('industry_name'):
        company_name = enhanced_data.get('customer_name')
        address = enhanced_data.get('address', '')
        
        industry = get_company_industry(company_name, address)
        if industry:
            enhanced_data['industry_name'] = industry
            print(f"为企业 {company_name} 补充所属行业: {industry}")
    
    return enhanced_data

def enhance_brain_and_chain_info(data):
    """
    基于真实数据库数据补充产业大脑和链主企业信息
    """
    enhanced_data = data.copy()
    company_name = enhanced_data.get('customer_name', '')
    region = enhanced_data.get('district_name', '')
    industry_name = enhanced_data.get('industry_name', '')
    customer_id = enhanced_data.get('customer_id')
    
    # 获取产业大脑信息
    if industry_name and not enhanced_data.get('brain_name'):
        brain_name = get_industry_brain_by_company(company_name, region, industry_name)
        if brain_name:
            enhanced_data['brain_name'] = brain_name
            print(f"为企业补充产业大脑信息: {brain_name}")
            
            # 同步到数据库
            if customer_id:
                update_customer_brain_info(customer_id, company_name, industry_name)
        else:
            enhanced_data['brain_name'] = f"{region}暂无相应产业大脑"
    
    # 获取产业链状态信息
    if industry_name:
        chain_status = get_chain_leader_status(company_name, region, industry_name)
        enhanced_data['chain_status'] = chain_status
        print(f"为企业补充产业链状态: {chain_status}")
        
        # 如果是链主企业，设置链主企业名称为自己
        if "链主" in chain_status:
            enhanced_data['chain_leader_name'] = company_name
            
            # 同步到数据库
            if customer_id:
                update_customer_chain_leader_info(customer_id, company_name)
        else:
            # 查找该产业链的链主企业
            # 这里可以进一步扩展，查找同行业的链主企业
            enhanced_data['chain_leader_name'] = "暂无"
    
    return enhanced_data

def enhance_revenue_and_status_info(data):
    """
    补充企业营收信息和企业地位
    """
    enhanced_data = data.copy()
    company_name = enhanced_data.get('customer_name', '')
    industry_name = enhanced_data.get('industry_name', '')
    
    if company_name:
        # 获取营收信息
        try:
            revenue_info = get_company_revenue_info(company_name)
            enhanced_data['revenue_info'] = revenue_info
            print(f"为企业 {company_name} 补充营收信息")
        except Exception as e:
            print(f"获取营收信息失败: {e}")
            enhanced_data['revenue_info'] = "暂无营收数据"
        
        # 获取企业地位
        try:
            company_status = get_company_ranking_status(company_name, industry_name)
            enhanced_data['company_status'] = company_status
            print(f"为企业 {company_name} 补充企业地位: {company_status}")
        except Exception as e:
            print(f"获取企业地位失败: {e}")
            enhanced_data['company_status'] = "暂无排名信息"
    
    return enhanced_data

def process_without_local_data(company_name):
    """
    处理不存在本地数据的情况
    """
    # 联网搜索公司信息
    search_query = f"{company_name} 公司信息"
    search_results = search_web(search_query)
    
    # 提取搜索结果中的信息
    company_info = extract_company_info_from_search_results(search_results)
    
    # 生成摘要
    summary = generate_summary(str(company_info))
    
    # 保存到数据库（简化实现）
    # customer_data = {
    #     'customer_name': company_name,
    #     'data_source': 'web_search',
    #     'address': company_info.get('description', ''),
    #     'tag_result': 1,
    #     'industry_id': None,
    #     'brain_id': None,
    #     'chain_leader_id': None
    # }
    # customer_id = insert_customer(customer_data)
    
    return {
        "status": "success",
        "data": company_info,
        "summary": summary,
        "source": "web_search"
    }

def check_missing_fields(data):
    """
    检查数据中缺失的字段
    """
    required_fields = ['customer_name', 'industry_name', 'brain_name', 'chain_leader_name', 'district_name']
    missing = []
    
    for field in required_fields:
        if not data.get(field):
            missing.append(field)
    
    return missing

def generate_comprehensive_company_analysis(enhanced_data, news_data):
    """
    使用LLM对企业信息进行综合分析和智能总结
    """
    # 构建详细的分析提示词
    analysis_prompt = f"""
作为一名专业的企业分析师，请基于以下收集到的企业信息，为用户提供一份专业、全面的企业分析报告。

## 企业基础信息
- 企业名称：{enhanced_data.get('customer_name', '未知')}
- 所在地区：{enhanced_data.get('district_name', '未知')}
- 企业地址：{enhanced_data.get('address', '未知')}
- 所属行业：{enhanced_data.get('industry_name', '未知')}

## 产业生态信息
- 产业大脑：{enhanced_data.get('brain_name', '未知')}
- 产业链状态：{enhanced_data.get('chain_status', '未知')}

## 经营状况与市场地位
- 近三年营收情况：{enhanced_data.get('revenue_info', '暂无营收数据')}
- 企业地位：{enhanced_data.get('company_status', '暂无排名信息')}

## 最新商业动态
{news_data.get('summary', '暂无最新商业资讯')}

## 数据来源
{enhanced_data.get('data_source', '未知')}

---

请按照以下结构提供专业分析：

### 🏢 企业概况
[简要介绍企业的基本情况、主营业务和市场定位]

### 📍 区域优势分析
[分析企业所在地区的产业环境和区位优势]

### 🏭 产业链地位
[分析企业在产业链中的地位和作用，包括产业大脑关联性]

### 💰 经营实力评估
[基于营收情况和市场地位，评估企业的经营实力]

### 📈 发展前景展望
[结合最新商业动态，分析企业的发展趋势和前景]

### 💡 投资价值建议
[从投资角度给出专业建议和风险提示]

请确保分析客观、专业，避免过度夸大或贬低。如果某些信息不足，请如实说明并基于现有信息进行合理推断。
"""
    
    try:
        # 调用LLM生成综合分析
        analysis_result = generate_summary(analysis_prompt)
        return analysis_result
    except Exception as e:
        print(f"生成企业分析报告失败: {e}")
        # 如果LLM调用失败，返回基础的结构化信息
        return generate_fallback_analysis(enhanced_data, news_data)

def generate_fallback_analysis(enhanced_data, news_data):
    """
    当LLM调用失败时的备用分析方法
    """
    company_name = enhanced_data.get('customer_name', '未知企业')
    industry = enhanced_data.get('industry_name', '未知行业')
    region = enhanced_data.get('district_name', '未知地区')
    chain_status = enhanced_data.get('chain_status', '未知')
    
    fallback_analysis = f"""
### 🏢 企业概况
{company_name}是一家位于{region}的{industry}企业。

### 📍 区域优势分析
企业位于{region}，具有一定的区域优势。

### 🏭 产业链地位
根据数据显示，该企业在产业链中的状态为：{chain_status}。

### 💰 经营实力评估
企业营收情况：{enhanced_data.get('revenue_info', '暂无相关数据')}
市场地位：{enhanced_data.get('company_status', '暂无排名信息')}

### 📈 发展前景展望
{news_data.get('summary', '暂无最新商业资讯')}

### 💡 投资价值建议
建议关注该企业的后续发展动态，进行更深入的尽职调查。
"""
    
    return fallback_analysis

def merge_data(local_data, web_data):
    """
    合并本地数据和网络数据
    """
    merged = local_data.copy()
    
    # 用网络数据补充缺失的信息
    if not merged.get('industry_name') and web_data.get('industry'):
        merged['industry_name'] = web_data['industry']
    
    if not merged.get('address') and web_data.get('description'):
        merged['address'] = web_data['description']
    
    return merged

def infer_company_name_from_search(user_input):
    """
    通过网络搜索推断公司名称（当完全无法提取时使用）
    """
    try:
        # 尝试通过搜索用户输入来推断公司名称
        search_results = search_web(user_input)
        
        if search_results and 'data' in search_results and 'webPages' in search_results['data']:
            web_pages = search_results['data']['webPages']
            if 'value' in web_pages and len(web_pages['value']) > 0:
                # 检查前几个搜索结果，看是否能提取公司名称
                for result in web_pages['value'][:3]:  # 检查前3个结果
                    title = result.get('name', '')
                    snippet = result.get('snippet', '')
                    
                    # 尝试从标题中提取公司名称
                    title_extraction = extract_company_name(title)
                    if title_extraction and title_extraction['is_complete']:
                        return title_extraction['name']
                    
                    # 尝试从摘要中提取公司名称
                    snippet_extraction = extract_company_name(snippet)
                    if snippet_extraction and snippet_extraction['is_complete']:
                        return snippet_extraction['name']
        
        return None
    except Exception as e:
        print(f"通过搜索推断公司名称时出错: {e}")
        return None

def infer_complete_company_name_from_search(incomplete_name):
    """
    通过网络搜索获取完整的公司名称（当提取到不完整名称时使用）
    """
    try:
        # 搜索不完整的公司名称，尝试找到完整名称
        search_query = f"{incomplete_name} 公司 官网"
        search_results = search_web(search_query)
        
        if search_results and 'data' in search_results and 'webPages' in search_results['data']:
            web_pages = search_results['data']['webPages']
            if 'value' in web_pages and len(web_pages['value']) > 0:
                # 检查前几个搜索结果，寻找完整的公司名称
                for result in web_pages['value'][:5]:  # 检查前5个结果
                    title = result.get('name', '')
                    snippet = result.get('snippet', '')
                    url = result.get('url', '')
                    
                    # 优先从官网标题中提取
                    if '官网' in title or 'www.' in url:
                        title_extraction = extract_company_name(title)
                        if title_extraction and title_extraction['is_complete']:
                            # 验证是否包含原始名称
                            if incomplete_name in title_extraction['name']:
                                return title_extraction['name']
                    
                    # 从摘要中提取
                    snippet_extraction = extract_company_name(snippet)
                    if snippet_extraction and snippet_extraction['is_complete']:
                        # 验证是否包含原始名称
                        if incomplete_name in snippet_extraction['name']:
                            return snippet_extraction['name']
        
        return None
    except Exception as e:
        print(f"通过搜索获取完整公司名称时出错: {e}")
        return None