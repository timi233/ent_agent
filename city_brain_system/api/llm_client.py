from openai import OpenAI
import configparser
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_llm_client():
    """
    获取LLM客户端
    """
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini'))
    
    # 获取API配置，优先使用环境变量
    base_url = config.get('llm_api', 'base_url')
    api_key = os.getenv('DEEPSEEK_API_KEY') or config.get('llm_api', 'api_key')
    
    # 创建并返回客户端
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    return client

def generate_summary(content, model=None):
    """
    使用LLM生成摘要
    """
    # 读取配置文件获取默认模型
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini'))
    
    if model is None:
        model = config.get('llm_api', 'model')
    
    client = get_llm_client()
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个专业的信息整理助手，请将提供的企业信息整理成结构化的摘要。"},
            {"role": "user", "content": content}
        ],
        stream=False
    )
    
    return response.choices[0].message.content