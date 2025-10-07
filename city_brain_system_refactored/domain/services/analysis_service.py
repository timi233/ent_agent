"""
分析服务 - 处理LLM分析和报告生成

负责：
- 企业综合分析报告生成
- 企业新闻资讯获取
- LLM调用和备用分析
- 分析结果格式化
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from infrastructure.external import generate_summary, get_company_business_news


class AnalysisService:
    """分析服务类"""
    
    def __init__(self):
        """初始化分析服务"""
        pass
    
    def get_company_news(self, company_name):
        """
        获取企业新闻资讯
        
        Args:
            company_name (str): 企业名称
            
        Returns:
            dict: 新闻数据，包含摘要和来源
        """
        try:
            news_result = get_company_business_news(company_name)
            return {
                "summary": news_result.get('content', '暂无最新商业资讯'),
                "references": news_result.get('sources', [])
            }
        except Exception as e:
            print(f"获取企业新闻失败: {e}")
            return {
                "summary": "暂无最新商业资讯",
                "references": []
            }
    
    def generate_comprehensive_company_analysis(self, enhanced_data, news_data):
        """
        使用LLM对企业信息进行综合分析和智能总结
        
        Args:
            enhanced_data (dict): 增强后的企业数据
            news_data (dict): 企业新闻数据
            
        Returns:
            str: 综合分析报告
        """
        # 构建详细的分析提示词
        analysis_prompt = self._build_analysis_prompt(enhanced_data, news_data)
        
        try:
            # 调用LLM生成综合分析
            from infrastructure.external.llm_client import LLMClient
            llm = LLMClient()
            analysis_result = llm.simple_chat(analysis_prompt).content
            return analysis_result
        except Exception as e:
            print(f"生成企业分析报告失败: {e}")
            # 如果LLM调用失败，返回基础的结构化信息
            return self.generate_fallback_analysis(enhanced_data, news_data)
    
    def _build_analysis_prompt(self, enhanced_data, news_data):
        """
        构建分析提示词
        
        Args:
            enhanced_data (dict): 增强后的企业数据
            news_data (dict): 企业新闻数据
            
        Returns:
            str: 分析提示词
        """
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
        return analysis_prompt
    
    def generate_fallback_analysis(self, enhanced_data, news_data):
        """
        当LLM调用失败时的备用分析方法
        
        Args:
            enhanced_data (dict): 增强后的企业数据
            news_data (dict): 企业新闻数据
            
        Returns:
            str: 备用分析报告
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
    
    def format_analysis_result(self, enhanced_data, news_data, llm_analysis):
        """
        格式化分析结果
        
        Args:
            enhanced_data (dict): 增强后的企业数据
            news_data (dict): 企业新闻数据
            llm_analysis (str): LLM分析结果
            
        Returns:
            dict: 格式化的完整结果
        """
        result = {
            "status": "success",
            "data": {
                "company_name": enhanced_data.get('customer_name', ''),
                "summary": llm_analysis,
                "details": {
                    "name": enhanced_data.get('customer_name', ''),
                    "region": enhanced_data.get('district_name', ''),
                    "address": enhanced_data.get('address', ''),
                    "industry": enhanced_data.get('industry_name', ''),
                    "industry_brain": enhanced_data.get('brain_name', ''),
                    "chain_status": enhanced_data.get('chain_status', ''),
                    "revenue_info": enhanced_data.get('revenue_info', '暂无营收数据'),
                    "company_status": enhanced_data.get('company_status', '暂无排名信息'),
                    "data_source": enhanced_data.get('data_source', '')
                },
                "news": news_data
            }
        }
        
        return result