import mysql.connector
import configparser
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_db_connection():
    """
    获取数据库连接
    """
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini'))
    
    # 获取数据库配置
    db_config = {
        'host': config.get('database', 'host'),
        'user': config.get('database', 'username'),
        'password': config.get('database', 'password'),
        'database': config.get('database', 'database')
    }
    
    # 创建并返回数据库连接
    connection = mysql.connector.connect(**db_config)
    return connection