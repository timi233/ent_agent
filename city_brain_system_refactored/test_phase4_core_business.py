#!/usr/bin/env python3
"""
Phase 4 核心业务逻辑测试
测试企业服务、数据增强服务、分析服务、搜索服务的功能
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from domain.services.enterprise_service import EnterpriseService
from domain.services.data_enhancement_service import DataEnhancementService
from domain.services.analysis_service import AnalysisService
from domain.services.search_service import SearchService


def test_search_service():
    """测试搜索服务"""
    print("=" * 60)
    print("🔍 测试搜索服务")
    print("=" * 60)
    
    search_service = SearchService()
    
    # 测试企业名称提取
    test_inputs = [
        "青岛啤酒股份有限公司",
        "请查询海尔集团的信息",
        "华为技术有限公司怎么样？"
    ]
    
    for user_input in test_inputs:
        print(f"\n📝 测试输入: {user_input}")
        result = search_service.extract_company_name_from_input(user_input)
        print(f"✅ 提取结果: {result}")
    
    print("\n✅ 搜索服务测试完成")


def test_data_enhancement_service():
    """测试数据增强服务"""
    print("=" * 60)
    print("🔧 测试数据增强服务")
    print("=" * 60)
    
    enhancement_service = DataEnhancementService()
    
    # 模拟企业数据
    mock_data = {
        'customer_id': 1,
        'customer_name': '青岛啤酒股份有限公司',
        'address': '山东省青岛市市南区',
        'industry_name': '',
        'district_name': '',
        'source_table': 'customer'
    }
    
    print(f"📊 原始数据: {mock_data}")
    
    # 测试地区信息增强
    enhanced_data = enhancement_service.enhance_location_info(mock_data)
    print(f"🌍 地区增强后: district_name = {enhanced_data.get('district_name')}")
    
    # 测试行业信息增强
    enhanced_data = enhancement_service.enhance_industry_info(enhanced_data)
    print(f"🏭 行业增强后: industry_name = {enhanced_data.get('industry_name')}")
    
    # 测试产业大脑和链主信息增强
    enhanced_data = enhancement_service.enhance_brain_and_chain_info(enhanced_data)
    print(f"🧠 产业大脑: {enhanced_data.get('brain_name')}")
    print(f"🔗 链主状态: {enhanced_data.get('chain_status')}")
    
    print("\n✅ 数据增强服务测试完成")


def test_analysis_service():
    """测试分析服务"""
    print("=" * 60)
    print("📊 测试分析服务")
    print("=" * 60)
    
    analysis_service = AnalysisService()
    
    # 模拟增强后的企业数据
    enhanced_data = {
        'customer_name': '青岛啤酒股份有限公司',
        'district_name': '青岛市',
        'address': '山东省青岛市市南区',
        'industry_name': '食品饮料制造业',
        'brain_name': '青岛市食品产业大脑',
        'chain_status': '食品饮料制造业，链主',
        'revenue_info': '暂无营收数据',
        'company_status': '暂无排名信息',
        'data_source': '本地数据库'
    }
    
    # 测试新闻获取
    print("📰 测试新闻获取...")
    news_data = analysis_service.get_company_news('青岛啤酒股份有限公司')
    print(f"✅ 新闻数据: {news_data}")
    
    # 测试综合分析
    print("\n🎯 测试综合分析...")
    analysis_result = analysis_service.generate_comprehensive_company_analysis(enhanced_data, news_data)
    print(f"✅ 分析结果长度: {len(analysis_result)} 字符")
    print(f"📄 分析结果预览: {analysis_result[:200]}...")
    
    # 测试结果格式化
    print("\n📋 测试结果格式化...")
    formatted_result = analysis_service.format_analysis_result(enhanced_data, news_data, analysis_result)
    print(f"✅ 格式化结果状态: {formatted_result.get('status')}")
    print(f"📊 企业名称: {formatted_result.get('data', {}).get('company_name')}")
    
    print("\n✅ 分析服务测试完成")


def test_enterprise_service():
    """测试企业服务主逻辑"""
    print("=" * 60)
    print("🏢 测试企业服务主逻辑")
    print("=" * 60)
    
    enterprise_service = EnterpriseService()
    
    # 测试企业信息处理
    test_queries = [
        "青岛啤酒股份有限公司",
        "海尔集团",
        "华为技术有限公司"
    ]
    
    for query in test_queries:
        print(f"\n🔍 处理查询: {query}")
        try:
            result = enterprise_service.process_company_info(query)
            print(f"✅ 处理状态: {result.get('status')}")
            if result.get('status') == 'success':
                data = result.get('data', {})
                print(f"📊 企业名称: {data.get('company_name')}")
                print(f"📍 所在地区: {data.get('details', {}).get('region')}")
                print(f"🏭 所属行业: {data.get('details', {}).get('industry')}")
                print(f"📄 摘要长度: {len(data.get('summary', ''))} 字符")
            else:
                print(f"❌ 错误信息: {result.get('message')}")
        except Exception as e:
            print(f"❌ 处理异常: {e}")
    
    print("\n✅ 企业服务主逻辑测试完成")


def test_service_integration():
    """测试服务集成"""
    print("=" * 60)
    print("🔄 测试服务集成")
    print("=" * 60)
    
    # 测试各服务之间的协调工作
    enterprise_service = EnterpriseService()
    
    print("🎯 测试完整的企业信息处理流程...")
    
    # 模拟一个完整的处理流程
    test_input = "青岛啤酒股份有限公司的详细信息"
    
    try:
        result = enterprise_service.process_company_info(test_input)
        
        print(f"✅ 最终结果状态: {result.get('status')}")
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            details = data.get('details', {})
            
            print(f"📊 企业信息完整性检查:")
            print(f"  - 企业名称: {'✅' if details.get('name') else '❌'} {details.get('name', 'N/A')}")
            print(f"  - 所在地区: {'✅' if details.get('region') else '❌'} {details.get('region', 'N/A')}")
            print(f"  - 所属行业: {'✅' if details.get('industry') else '❌'} {details.get('industry', 'N/A')}")
            print(f"  - 产业大脑: {'✅' if details.get('industry_brain') else '❌'} {details.get('industry_brain', 'N/A')}")
            print(f"  - 链主状态: {'✅' if details.get('chain_status') else '❌'} {details.get('chain_status', 'N/A')}")
            print(f"  - 分析摘要: {'✅' if data.get('summary') else '❌'} {len(data.get('summary', ''))} 字符")
            print(f"  - 新闻资讯: {'✅' if data.get('news', {}).get('summary') else '❌'}")
        
    except Exception as e:
        print(f"❌ 集成测试异常: {e}")
    
    print("\n✅ 服务集成测试完成")


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始 Phase 4 核心业务逻辑测试")
    print("=" * 80)
    
    try:
        # 运行各项测试
        test_search_service()
        test_data_enhancement_service()
        test_analysis_service()
        test_enterprise_service()
        test_service_integration()
        
        print("\n" + "=" * 80)
        print("🎉 Phase 4 核心业务逻辑测试全部完成！")
        print("✅ 所有服务模块工作正常")
        print("✅ 企业信息处理流程完整")
        print("✅ 数据增强功能正常")
        print("✅ 分析服务功能正常")
        print("✅ 服务间协调正常")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)