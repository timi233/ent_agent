#!/usr/bin/env python3
# 模块导入测试

def test_imports():
    """测试所有模块是否能正常导入"""
    print("=== 测试模块导入 ===")
    
    try:
        from api.bocha_client import search_web
        print("✓ bocha_client 模块导入成功")
    except Exception as e:
        print(f"✗ bocha_client 模块导入失败: {e}")
    
    try:
        from api.llm_client import generate_summary
        print("✓ llm_client 模块导入成功")
    except Exception as e:
        print(f"✗ llm_client 模块导入失败: {e}")
    
    try:
        from database.connection import get_db_connection
        print("✓ database.connection 模块导入成功")
    except Exception as e:
        print(f"✗ database.connection 模块导入失败: {e}")
    
    try:
        from database.queries import get_customer_by_name
        print("✓ database.queries 模块导入成功")
    except Exception as e:
        print(f"✗ database.queries 模块导入失败: {e}")
    
    try:
        from services.company_service import process_company_info
        print("✓ services.company_service 模块导入成功")
    except Exception as e:
        print(f"✗ services.company_service 模块导入失败: {e}")
    
    try:
        from utils.text_extractor import extract_company_name
        print("✓ utils.text_extractor 模块导入成功")
    except Exception as e:
        print(f"✗ utils.text_extractor 模块导入失败: {e}")
    
    print("=== 模块导入测试完成 ===")

if __name__ == "__main__":
    test_imports()