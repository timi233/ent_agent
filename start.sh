#!/bin/bash
# 城市大脑系统日常启动脚本

# 颜色定义
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== 城市大脑企业信息处理系统启动 ===${NC}"

# 停止可能正在运行的服务
echo "正在停止可能正在运行的服务..."
pkill -f "vite" 2>/dev/null
pkill -f "uvicorn.*9003" 2>/dev/null
sleep 2

# 启动后端服务
echo "正在启动后端服务..."
cd /home/server/code/city_brain_system
nohup uvicorn main:app --host 0.0.0.0 --port 9003 > backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务 PID: $BACKEND_PID"
sleep 3

# 启动前端服务
echo "正在启动前端服务..."
cd /home/server/code/city_brain_frontend
# 使用Vite的host参数确保可以外部访问
nohup npm run start -- --host 0.0.0.0 > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端服务 PID: $FRONTEND_PID"
sleep 10

# 检查服务是否正常启动
if curl -s http://localhost:9003/api/v1/health > /dev/null; then
    echo "后端服务启动成功"
else
    echo "后端服务启动失败，请检查 backend.log"
fi

if curl -s http://localhost:9002 > /dev/null; then
    echo "前端服务启动成功"
else
    echo "前端服务启动失败，请检查 frontend.log"
fi

echo "=== 启动完成 ==="
echo "请稍等片刻，服务正在启动..."
echo ""
echo "访问地址:"
echo "  前端界面: http://localhost:9002"
echo "  后端API文档: http://localhost:9003/docs"
echo "  后端健康检查: http://localhost:9003/api/v1/health"