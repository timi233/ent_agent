#!/usr/bin/env python3
# 完整系统测试

import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.company_service import process_company_info

def test_company_processing():
    """测试公司信息处理功能"""
    print("=== 完整系统测试 ===")
    
    # 测试用例1：包含公司名称的输入
    test_input1 = "我想了解阿里巴巴集团的相关信息"
    print(f"测试输入1: {test_input1}")
    result1 = process_company_info(test_input1)
    print(f"处理结果1: {result1}")
    print()
    
    # 测试用例2：查询本地数据库中存在的公司（如果有）
    test_input2 = "我想了解青岛海尔集团的相关信息"
    print(f"测试输入2: {test_input2}")
    result2 = process_company_info(test_input2)
    print(f"处理结果2: {result2}")
    print()
    
    # 测试用例3：不包含公司名称的输入
    test_input3 = "请告诉我一些企业信息"
    print(f"测试输入3: {test_input3}")
    result3 = process_company_info(test_input3)
    print(f"处理结果3: {result3}")
    print()

if __name__ == "__main__":
    test_company_processing()