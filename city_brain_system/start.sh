#!/bin/bash
# 启动城市大脑企业信息处理系统

# 检查是否安装了必要的依赖
if ! command -v python3 &> /dev/null
then
    echo "错误: 未找到Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    echo "激活虚拟环境并安装依赖..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 启动服务器
echo "启动服务器..."
uvicorn main:app --host 0.0.0.0 --port 9003 --reload