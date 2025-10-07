"""
数据增强服务 - 处理企业数据的补充和优化

负责：
- 企业地区信息优化
- 企业行业信息补充
- 产业大脑和链主企业信息补充
- 营收和企业地位信息获取
- 数据库同步更新
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from infrastructure.database.standalone_queries import (
    update_customer_info,
    update_customer_industry_info,
    update_customer_brain_info,
    update_customer_chain_leader_info
)
from infrastructure.utils.address_processor import get_company_city
from infrastructure.utils.text_processor import get_company_industry
from infrastructure.external import get_company_revenue_info, get_company_ranking_status
from infrastructure.database.standalone_queries import (
    get_industry_brain_by_company,
    get_chain_leader_status
)


class DataEnhancementService:
    """数据增强服务类"""
    
    def __init__(self):
        """初始化数据增强服务"""
        pass
    
    def enhance_location_info(self, data):
        """
        优化企业所在地区信息
        优先从地址提取，其次联网搜索
        修复链主企业表中错误的莱西市地区信息
        
        Args:
            data (dict): 企业数据
            
        Returns:
            dict: 增强后的企业数据
        """
        enhanced_data = data.copy()
        company_name = enhanced_data.get('customer_name')
        current_district = enhanced_data.get('district_name')
        source_table = enhanced_data.get('source_table')
        
        # 修复地区信息 - 如果来源是链主企业表且地区是莱西市，需要重新获取正确地区
        if (source_table == 'chain_leader' and current_district == '莱西市') or not current_district:
            # 重新获取正确的地区信息
            city = get_company_city(enhanced_data, company_name)
            if city and city != '莱西市':  # 确保不是错误的莱西市
                enhanced_data['district_name'] = city
                if current_district == '莱西市':
                    print(f"为企业 {company_name} 修正所属地区: {current_district} -> {city}")
                else:
                    print(f"为企业 {company_name} 补充所属地区: {city}")
            elif not current_district:
                # 如果完全没有地区信息，尝试获取
                if city:
                    enhanced_data['district_name'] = city
                    print(f"为企业 {company_name} 补充所属地区: {city}")
        
        return enhanced_data
    
    def enhance_industry_info(self, data):
        """
        优化企业行业信息
        当数据库中没有行业信息时，通过联网搜索获取
        
        Args:
            data (dict): 企业数据
            
        Returns:
            dict: 增强后的企业数据
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
    
    def enhance_brain_and_chain_info(self, data):
        """
        基于真实数据库数据补充产业大脑和链主企业信息
        
        Args:
            data (dict): 企业数据
            
        Returns:
            dict: 增强后的企业数据
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
    
    def enhance_revenue_and_status_info(self, data):
        """
        补充企业营收信息和企业地位
        
        Args:
            data (dict): 企业数据
            
        Returns:
            dict: 增强后的企业数据
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
    
    def sync_database_updates(self, enhanced_data, local_data):
        """
        同步数据库更新
        
        Args:
            enhanced_data (dict): 增强后的企业数据
            local_data (dict): 原始本地数据
        """
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
    
    def enhance_all_data(self, data):
        """
        对企业数据进行全面增强
        
        Args:
            data (dict): 原始企业数据
            
        Returns:
            dict: 全面增强后的企业数据
        """
        try:
            # 第一阶段：优化基础信息
            enhanced_data = self.enhance_location_info(data)
            enhanced_data = self.enhance_industry_info(enhanced_data)
            enhanced_data = self.enhance_brain_and_chain_info(enhanced_data)
            
            # 第二阶段：获取网络数据（营收、地位、新闻）
            enhanced_data = self.enhance_revenue_and_status_info(enhanced_data)
            
            return enhanced_data
        except Exception as e:
            print(f"数据增强过程中出错: {e}")
            return data  # 如果增强失败，返回原始数据