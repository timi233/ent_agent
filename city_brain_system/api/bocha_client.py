import requests
import configparser
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def search_web(query, summary=True, count=10):
    """
    使用博查API进行网络搜索
    """
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini'))
    
    # 获取API配置
    base_url = config.get('bocha_api', 'base_url')
    # 优先使用环境变量中的API密钥
    api_key = os.getenv('BOCHA_API_KEY') or config.get('bocha_api', 'api_key')
    
    # 设置请求头
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 设置请求体
    payload = {
        'query': query,
        'summary': summary,
        'count': count
    }
    
    # 发送请求
    response = requests.post(base_url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"博查API请求失败: {response.status_code} - {response.text}")