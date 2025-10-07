#!/bin/bash
# 城市大脑系统快速启动脚本

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== 城市大脑企业信息处理系统快速启动 ===${NC}"

# 停止可能正在运行的服务
echo "正在停止可能正在运行的服务..."
pkill -f "vite" 2>/dev/null
pkill -f "uvicorn.*9003" 2>/dev/null
sleep 2

# 启动后端服务
echo "正在启动后端服务..."
cd /home/server/code/city_brain_system

# 检查并创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖（如果需要）
source venv/bin/activate
if [ ! -f "venv/installed" ]; then
    echo "安装后端依赖..."
    pip install -r requirements.txt > install.log 2>&1
    touch venv/installed
fi

nohup uvicorn main:app --host 0.0.0.0 --port 9003 > backend.log 2>&1 &
BACKEND_PID=$!
deactivate
sleep 3

# 启动前端服务
echo "正在启动前端服务..."
cd /home/server/code/city_brain_frontend

# 检查并安装前端依赖
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install > install.log 2>&1
fi

nohup npm run start > frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 8

echo "=== 启动完成 ==="
echo "前端服务 PID: $FRONTEND_PID"
echo "后端服务 PID: $BACKEND_PID"
echo ""
echo "访问地址:"
echo "  前端界面: http://localhost:9002"
echo "  后端API文档: http://localhost:9003/docs"
echo "  后端健康检查: http://localhost:9003/api/v1/health"
echo ""
echo "日志文件:"
echo "  前端日志: /home/server/code/city_brain_frontend/frontend.log"
echo "  后端日志: /home/server/code/city_brain_system/backend.log"
echo ""
echo -e "${YELLOW}提示: 使用 ./stop.sh 停止服务${NC}"