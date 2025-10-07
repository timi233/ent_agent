#!/bin/bash
# 城市大脑系统停止脚本

# 颜色定义
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== 停止城市大脑企业信息处理系统 ===${NC}"

# 停止前端服务
echo "正在停止前端服务..."
pkill -f "vite" 2>/dev/null

# 停止后端服务
echo "正在停止后端服务..."
cd /home/server/code/city_brain_system
if [ -d "venv" ]; then
    source venv/bin/activate
    pkill -f "uvicorn.*9003" 2>/dev/null
    deactivate
else
    pkill -f "uvicorn.*9003" 2>/dev/null
fi

# 等待进程结束
sleep 3

echo "=== 系统已停止 ==="
echo "您可以使用 ./quick_start.sh 重新启动系统"