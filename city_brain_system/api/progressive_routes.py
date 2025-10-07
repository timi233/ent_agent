from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from services.company_service import process_company_info
from database.queries import get_customer_by_name
from utils.text_extractor import extract_company_name
from utils.address_extractor import get_company_city
from utils.industry_extractor import get_company_industry
from utils.database_matcher import get_industry_brain_by_company, get_chain_leader_status
from utils.revenue_searcher import get_company_revenue_info
from utils.ranking_checker import get_company_ranking_status
from utils.news_searcher import get_company_business_news
from api.llm_client import generate_summary
from utils.logger import city_brain_logger
from pydantic import BaseModel
import json
import asyncio
import logging
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

class ProgressiveCompanyRequest(BaseModel):
    input_text: str

@router.post("/process-company-progressive")
async def process_company_progressive(request: ProgressiveCompanyRequest):
    """
    渐进式处理企业信息，分阶段返回数据
    """
    start_time = time.time()
    logger.info(f"开始渐进式处理企业信息: {request.input_text}")
    city_brain_logger.log_api_request("/process-company-progressive", request.input_text, {"input_text": request.input_text}, "开始处理")
    
    async def generate_progressive_response():
        try:
            # 阶段1: 提取企业名称和基础信息
            yield json.dumps({
                "stage": 1,
                "status": "processing",
                "message": "正在提取企业名称...",
                "data": {}
            }, ensure_ascii=False) + "\n"
            
            extraction_result = extract_company_name(request.input_text)
            if not extraction_result:
                city_brain_logger.log_error("企业名称提取失败", f"输入文本: {request.input_text}")
                yield json.dumps({
                    "stage": 1,
                    "status": "error",
                    "message": "无法提取企业名称",
                    "data": {}
                }, ensure_ascii=False) + "\n"
                return
            
            company_name = extraction_result['name']
            is_complete = extraction_result['is_complete']
            logger.info(f"提取到企业名称: {company_name}, 是否完整: {is_complete}")
            city_brain_logger.log_progressive_stage(company_name, 1, "企业名称提取", f"名称: {company_name}, 完整性: {is_complete}")
            
            # 阶段2: 查询本地数据库
            yield json.dumps({
                "stage": 2,
                "status": "processing",
                "message": "正在查询本地数据库...",
                "data": {"company_name": company_name}
            }, ensure_ascii=False) + "\n"
            
            # 先用提取的名称查询
            local_data = get_customer_by_name(company_name)
            
            # 如果没找到，尝试用不同的名称变体查询
            if not local_data:
                # 尝试添加常见的企业后缀
                possible_names = [
                    f"{company_name}股份有限公司",
                    f"{company_name}有限公司",
                    f"{company_name}集团",
                    f"{company_name}公司"
                ]
                
                for possible_name in possible_names:
                    local_data = get_customer_by_name(possible_name)
                    if local_data:
                        company_name = possible_name  # 更新为找到的完整名称
                        logger.info(f"找到匹配的企业: {company_name}")
                        break
            
            if not local_data:
                city_brain_logger.log_database_query("企业查询", "QD_customer", f"企业名称: {company_name}", 0)
                city_brain_logger.log_error("企业信息未找到", f"查询的企业名称: {company_name}", company_name)
                yield json.dumps({
                    "stage": 2,
                    "status": "error",
                    "message": "未找到企业信息",
                    "data": {}
                }, ensure_ascii=False) + "\n"
                return
            
            city_brain_logger.log_database_query("企业查询", "QD_customer", f"企业名称: {company_name}", 1)
            
            # 阶段3: 返回基础本地数据
            basic_info = {
                "name": local_data.get('customer_name', ''),
                "region": local_data.get('district_name', ''),
                "address": local_data.get('address', ''),
                "industry": local_data.get('industry_name', ''),
                "data_source": local_data.get('data_source', '')
            }
            
            yield json.dumps({
                "stage": 3,
                "status": "success",
                "message": "基础信息加载完成",
                "data": {
                    "details": basic_info,
                    "industry_brain": "查询中...",
                    "chain_status": "查询中...",
                    "revenue_info": "搜索中...",
                    "company_status": "分析中...",
                    "news": {"summary": "加载中...", "references": []}
                }
            }, ensure_ascii=False) + "\n"
            
            logger.info(f"基础信息加载完成: {company_name}")
            city_brain_logger.log_progressive_stage(company_name, 3, "基础信息加载", f"地区: {basic_info['region']}, 行业: {basic_info['industry']}")
            
            # 阶段4: 补充地区和行业信息
            yield json.dumps({
                "stage": 4,
                "status": "processing",
                "message": "正在补充地区和行业信息...",
                "data": {}
            }, ensure_ascii=False) + "\n"
            
            enhanced_data = local_data.copy()
            
            # 补充地区信息 - 修复链主企业表中错误的莱西市地区信息
            current_district = enhanced_data.get('district_name')
            source_table = enhanced_data.get('source_table')
            
            if (source_table == 'chain_leader' and current_district == '莱西市') or not current_district:
                city = get_company_city(enhanced_data, company_name)
                if city and city != '莱西市':  # 确保不是错误的莱西市
                    enhanced_data['district_name'] = city
                    basic_info['region'] = city
                    if current_district == '莱西市':
                        logger.info(f"为企业 {company_name} 修正所属地区: {current_district} -> {city}")
                    else:
                        logger.info(f"为企业 {company_name} 补充所属地区: {city}")
            
            # 补充行业信息
            if not enhanced_data.get('industry_name'):
                industry = get_company_industry(company_name, enhanced_data.get('address', ''))
                if industry:
                    enhanced_data['industry_name'] = industry
                    basic_info['industry'] = industry
            
            # 阶段5: 产业大脑和产业链信息
            yield json.dumps({
                "stage": 5,
                "status": "processing",
                "message": "正在查询产业大脑和产业链信息...",
                "data": {"details": basic_info}
            }, ensure_ascii=False) + "\n"
            
            region = enhanced_data.get('district_name', '')
            industry_name = enhanced_data.get('industry_name', '')
            
            # 获取产业大脑信息
            brain_name = get_industry_brain_by_company(company_name, region, industry_name)
            if not brain_name:
                brain_name = f"{region}暂无相应产业大脑"
            
            # 获取产业链状态
            chain_status = get_chain_leader_status(company_name, region, industry_name)
            
            yield json.dumps({
                "stage": 5,
                "status": "success",
                "message": "产业信息查询完成",
                "data": {
                    "details": basic_info,
                    "industry_brain": brain_name,
                    "chain_status": chain_status,
                    "revenue_info": "搜索中...",
                    "company_status": "分析中...",
                    "news": {"summary": "加载中...", "references": []}
                }
            }, ensure_ascii=False) + "\n"
            
            logger.info(f"产业信息查询完成: 产业大脑={brain_name}, 产业链状态={chain_status}")
            city_brain_logger.log_progressive_stage(company_name, 5, "产业信息查询", f"产业大脑: {brain_name}, 产业链状态: {chain_status}")
            
            # 阶段6: 营收信息搜索和LLM分析
            yield json.dumps({
                "stage": 6,
                "status": "processing",
                "message": "正在搜索营收信息并进行智能分析...",
                "data": {}
            }, ensure_ascii=False) + "\n"
            
            try:
                search_start_time = time.time()
                raw_revenue_info = get_company_revenue_info(company_name)
                search_duration = time.time() - search_start_time
                city_brain_logger.log_web_search(company_name, "营收信息", f"{company_name} 营收", len(str(raw_revenue_info)), search_duration)
                
                # 使用LLM对营收信息进行总结
                revenue_prompt = f"""
请对以下企业营收信息进行标准化总结：

企业名称：{company_name}
原始营收信息：{raw_revenue_info}

请严格按照以下格式输出：

近三年营收为 [年份][金额]元 [年份][金额]元 [年份][金额]元，综合年增长率为[数字]%。

要求：
1. 提取最近三年的营收数据，按时间顺序排列
2. 金额保留到亿元，如"298.1亿"
3. 计算三年的综合年增长率（复合增长率）
4. 如果数据不足三年，用现有数据
5. 严格按照格式，不要添加其他内容

示例：近三年营收为 2021年298.1亿元 2022年327.2亿元 2023年339.37亿元，综合年增长率为6.8%。
"""
                
                llm_start_time = time.time()
                revenue_analysis = generate_summary(revenue_prompt)
                llm_duration = time.time() - llm_start_time
                city_brain_logger.log_llm_analysis(company_name, "营收分析", len(revenue_prompt), len(revenue_analysis), llm_duration)
                logger.info(f"营收信息LLM分析完成: {company_name}")
                
            except Exception as e:
                logger.error(f"营收信息获取失败: {e}")
                city_brain_logger.log_error("营收信息获取失败", str(e), company_name, "营收搜索阶段")
                revenue_analysis = "暂无营收数据"
            
            # 阶段7: 企业地位分析
            yield json.dumps({
                "stage": 7,
                "status": "processing",
                "message": "正在分析企业地位...",
                "data": {}
            }, ensure_ascii=False) + "\n"
            
            try:
                ranking_start_time = time.time()
                company_status = get_company_ranking_status(company_name, industry_name)
                ranking_duration = time.time() - ranking_start_time
                city_brain_logger.log_company_query(company_name, "企业地位分析", company_status, ranking_duration)
                logger.info(f"企业地位分析完成: {company_status}")
            except Exception as e:
                logger.error(f"企业地位分析失败: {e}")
                city_brain_logger.log_error("企业地位分析失败", str(e), company_name, "企业地位分析阶段")
                company_status = "暂无排名信息"
            
            # 阶段8: 企业新闻搜索和LLM分析
            yield json.dumps({
                "stage": 8,
                "status": "processing",
                "message": "正在搜索最新商业资讯并进行智能分析...",
                "data": {
                    "details": basic_info,
                    "industry_brain": brain_name,
                    "chain_status": chain_status,
                    "revenue_info": revenue_analysis,
                    "company_status": company_status,
                    "news": {"summary": "分析中...", "references": []}
                }
            }, ensure_ascii=False) + "\n"
            
            try:
                news_start_time = time.time()
                raw_news_result = get_company_business_news(company_name)
                raw_news_content = raw_news_result.get('content', '暂无最新商业资讯')
                news_search_duration = time.time() - news_start_time
                city_brain_logger.log_web_search(company_name, "商业资讯", f"{company_name} 商业新闻", len(raw_news_content), news_search_duration)
                
                # 使用LLM对新闻信息进行总结
                news_prompt = f"""
# 角色
你是一个专业的企业资讯分析师，能够精准分析企业商业动态，并以中立客观、新闻式的专业语气为用户提供企业资讯总结。

## 任务
基于以下企业商业资讯，提供结构化的资讯总结：

企业名称：{company_name}
原始资讯内容：{raw_news_content}

## 输出要求
请严格按照以下格式输出，每条资讯总结控制在30-50字：

1. [资讯总结]【引用编号】
2. [资讯总结]【引用编号】  
3. [资讯总结]【引用编号】

## 技能要求
1. 提取最重要的3条商业资讯，按重要性排序
2. 每条总结应简洁明了，突出核心信息
3. 保持中立客观的新闻式语气
4. 必须保留原始的引用编号【1】【2】【3】等
5. 如果资讯不足3条，则按实际数量输出
6. 禁止添加额外的分析或评论

## 示例格式
1. 公司2024年获山东省轻工业联合会科技进步奖一等奖，技术创新能力获得认可【1】
2. 近三日累计获融资买入0.85亿元，市场资金关注度较高【2】
3. 发布2025年半年度报告，业绩表现将于说明会详细披露【3】
"""
                
                news_llm_start_time = time.time()
                news_analysis = generate_summary(news_prompt)
                news_llm_duration = time.time() - news_llm_start_time
                city_brain_logger.log_llm_analysis(company_name, "商业资讯分析", len(news_prompt), len(news_analysis), news_llm_duration)
                
                news_data = {
                    "summary": news_analysis,
                    "references": raw_news_result.get('sources', [])
                }
                logger.info(f"新闻信息LLM分析完成: {company_name}")
                
            except Exception as e:
                logger.error(f"新闻信息获取失败: {e}")
                city_brain_logger.log_error("新闻信息获取失败", str(e), company_name, "商业资讯搜索阶段")
                news_data = {"summary": "暂无最新商业资讯", "references": []}
            
            # 阶段9: 最终LLM综合分析
            yield json.dumps({
                "stage": 9,
                "status": "processing",
                "message": "正在生成综合分析报告...",
                "data": {}
            }, ensure_ascii=False) + "\n"
            
            # 生成最终的综合分析
            final_analysis_prompt = f"""
作为专业企业分析师，请基于以下信息生成简洁的企业综合评估：

企业名称：{company_name}
所在地区：{basic_info.get('region', '')}
所属行业：{basic_info.get('industry', '')}
产业大脑：{brain_name}
产业链状态：{chain_status}
营收分析：{revenue_analysis}
企业地位：{company_status}
商业资讯：{news_analysis}

请生成一份150字以内的综合评估，包含：
1. 企业核心优势
2. 市场地位评价
3. 发展前景判断

保持专业、客观。
"""
            
            try:
                final_llm_start_time = time.time()
                comprehensive_analysis = generate_summary(final_analysis_prompt)
                final_llm_duration = time.time() - final_llm_start_time
                city_brain_logger.log_llm_analysis(company_name, "综合分析报告", len(final_analysis_prompt), len(comprehensive_analysis), final_llm_duration)
                logger.info(f"综合分析报告生成完成: {company_name}")
            except Exception as e:
                logger.error(f"综合分析生成失败: {e}")
                city_brain_logger.log_error("综合分析生成失败", str(e), company_name, "综合分析阶段")
                comprehensive_analysis = f"{company_name}是一家位于{basic_info.get('region', '')}的{basic_info.get('industry', '')}企业，具有一定的市场地位。"
            
            # 阶段10: 完成
            final_result = {
                "stage": 10,
                "status": "completed",
                "message": "企业信息分析完成",
                "data": {
                    "company_name": company_name,
                    "summary": comprehensive_analysis,
                    "details": {
                        "name": basic_info.get('name', ''),
                        "region": basic_info.get('region', ''),
                        "address": basic_info.get('address', ''),
                        "industry": basic_info.get('industry', ''),
                        "industry_brain": brain_name,
                        "chain_status": chain_status,
                        "revenue_info": revenue_analysis,
                        "company_status": company_status,
                        "data_source": basic_info.get('data_source', '')
                    },
                    "news": news_data
                }
            }
            
            yield json.dumps(final_result, ensure_ascii=False) + "\n"
            
            total_duration = time.time() - start_time
            logger.info(f"企业信息渐进式处理完成: {company_name}")
            city_brain_logger.log_company_query(company_name, "渐进式完整处理", "成功完成", total_duration)
            city_brain_logger.log_api_request("/process-company-progressive", company_name, {"total_stages": 10}, f"成功完成，总耗时: {total_duration:.2f}秒")
            
        except Exception as e:
            logger.error(f"渐进式处理过程中出现错误: {e}")
            city_brain_logger.log_error("渐进式处理系统错误", str(e), request.input_text, "系统级错误")
            yield json.dumps({
                "stage": -1,
                "status": "error",
                "message": f"处理过程中出现错误: {str(e)}",
                "data": {}
            }, ensure_ascii=False) + "\n"
    
    return StreamingResponse(
        generate_progressive_response(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )