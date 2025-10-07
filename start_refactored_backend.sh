#!/bin/bash

# 设置项目根目录和端口
PROJECT_DIR="/home/server/code/city_brain_system_refactored"
LOG_FILE="/home/server/code/backend_refactored.log"
PID_FILE="/home/server/code/backend_refactored.pid"
PORT=9003

# --- 强制杀死占用端口的旧进程 ---
echo "Checking for process on port $PORT..."
PID_TO_KILL=$(lsof -t -i:$PORT)

if [ -n "$PID_TO_KILL" ]; then
    echo "Found process with PID: $PID_TO_KILL on port $PORT. Terminating..."
    kill -9 "$PID_TO_KILL"
    sleep 2 # 等待端口释放
    echo "Process terminated."
else
    echo "No process found on port $PORT."
fi

# 进入项目目录
cd "$PROJECT_DIR" || exit

# 启动新服务
echo "Starting backend service..."
export APP_PORT=$PORT
nohup python3 main.py > "$LOG_FILE" 2>&1 &

# 保存新进程的PID
echo $! > "$PID_FILE"

sleep 7

# 检查服务状态
if ps -p $(cat "$PID_FILE") > /dev/null; then
    echo "Service started successfully with PID: $(cat "$PID_FILE")"
    echo "Checking health endpoint..."
    curl -sS http://localhost:${PORT}/api/v1/industry/brain-chain/health
else
    echo "Service failed to start. Check logs at $LOG_FILE"
fi