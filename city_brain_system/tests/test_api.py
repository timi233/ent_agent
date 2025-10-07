import pytest
from main import app

def test_health_check():
    # 简单测试，验证模块导入是否正常
    assert app is not None

def test_app_title():
    # 验证应用标题
    assert app.title == "城市大脑企业信息处理系统"