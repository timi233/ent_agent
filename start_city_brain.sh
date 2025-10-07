#!/bin/bash
# 城市大脑企业信息处理系统一键启动脚本

# 设置变量
FRONTEND_DIR="/home/server/code/city_brain_frontend"
BACKEND_DIR="/home/server/code/city_brain_system"
FRONTEND_PORT=9002
BACKEND_PORT=9003

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_step "检查系统依赖..."
    
    local missing_deps=()
    
    if ! command -v node &> /dev/null; then
        missing_deps+=("Node.js")
    fi
    
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi
    
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("Python3")
    fi
    
    if ! command -v pip &> /dev/null; then
        missing_deps+=("pip")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "缺少以下依赖: ${missing_deps[*]}"
        print_info "请先安装这些依赖再运行脚本"
        exit 1
    fi
    
    print_info "所有依赖检查通过"
}

# 检查目录是否存在
check_directories() {
    print_step "检查项目目录..."
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "前端项目目录不存在: $FRONTEND_DIR"
        exit 1
    fi
    
    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "后端项目目录不存在: $BACKEND_DIR"
        exit 1
    fi
    
    print_info "项目目录检查通过"
}

# 检查端口是否被占用
check_ports() {
    print_step "检查端口占用情况..."
    
    local frontend_pid=$(lsof -ti:$FRONTEND_PORT)
    local backend_pid=$(lsof -ti:$BACKEND_PORT)
    
    if [ ! -z "$frontend_pid" ]; then
        print_warning "端口 $FRONTEND_PORT 已被占用 (PID: $frontend_pid)"
        read -p "是否终止该进程? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill -9 $frontend_pid
            print_info "已终止占用端口 $FRONTEND_PORT 的进程"
        else
            print_error "端口 $FRONTEND_PORT 被占用，无法启动前端服务"
            exit 1
        fi
    fi
    
    if [ ! -z "$backend_pid" ]; then
        print_warning "端口 $BACKEND_PORT 已被占用 (PID: $backend_pid)"
        read -p "是否终止该进程? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill -9 $backend_pid
            print_info "已终止占用端口 $BACKEND_PORT 的进程"
        else
            print_error "端口 $BACKEND_PORT 被占用，无法启动后端服务"
            exit 1
        fi
    fi
    
    print_info "端口检查完成"
}

# 安装前端依赖
install_frontend_deps() {
    print_step "安装前端依赖..."
    
    cd $FRONTEND_DIR
    
    # 检查node_modules是否存在
    if [ ! -d "node_modules" ]; then
        print_info "正在安装前端依赖..."
        if ! npm install; then
            print_error "前端依赖安装失败"
            exit 1
        fi
        print_info "前端依赖安装完成"
    else
        print_info "前端依赖已存在，跳过安装"
    fi
}

# 安装后端依赖
install_backend_deps() {
    print_step "安装后端依赖..."
    
    cd $BACKEND_DIR
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        print_info "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    print_info "激活虚拟环境并安装依赖..."
    source venv/bin/activate
    
    if ! pip install -r requirements.txt; then
        print_error "后端依赖安装失败"
        deactivate
        exit 1
    fi
    
    print_info "后端依赖安装完成"
    deactivate
}

# 启动后端服务
start_backend() {
    print_step "启动后端服务..."
    
    cd $BACKEND_DIR
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 启动后端服务
    nohup uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT > backend.log 2>&1 &
    local backend_pid=$!
    
    # 等待服务启动
    sleep 5
    
    # 检查服务是否启动成功
    if curl -s http://localhost:$BACKEND_PORT/api/v1/health > /dev/null; then
        echo $backend_pid > backend.pid
        print_info "后端服务启动成功 (PID: $backend_pid)"
    else
        print_error "后端服务启动失败"
        deactivate
        exit 1
    fi
    
    deactivate
}

# 启动前端服务
start_frontend() {
    print_step "启动前端服务..."
    
    cd $FRONTEND_DIR
    
    # 启动前端开发服务器
    nohup npm run start > frontend.log 2>&1 &
    local frontend_pid=$!
    
    # 等待服务启动
    sleep 10
    
    echo $frontend_pid > frontend.pid
    print_info "前端服务启动成功 (PID: $frontend_pid)"
}

# 显示服务状态
show_status() {
    print_step "检查服务状态..."
    
    local frontend_status="未运行"
    local backend_status="未运行"
    
    if [ -f "$FRONTEND_DIR/frontend.pid" ]; then
        local frontend_pid=$(cat $FRONTEND_DIR/frontend.pid)
        if ps -p $frontend_pid > /dev/null; then
            frontend_status="运行中 (PID: $frontend_pid)"
        else
            frontend_status="已停止 (PID文件存在但进程不存在)"
        fi
    fi
    
    if [ -f "$BACKEND_DIR/backend.pid" ]; then
        local backend_pid=$(cat $BACKEND_DIR/backend.pid)
        if ps -p $backend_pid > /dev/null; then
            backend_status="运行中 (PID: $backend_pid)"
        else
            backend_status="已停止 (PID文件存在但进程不存在)"
        fi
    fi
    
    echo "前端服务: $frontend_status"
    echo "后端服务: $backend_status"
    
    if [[ $frontend_status == *"运行中"* ]] && [[ $backend_status == *"运行中"* ]]; then
        print_info "系统启动完成！"
        print_info "访问地址:"
        print_info "  前端界面: http://localhost:$FRONTEND_PORT"
        print_info "  后端API文档: http://localhost:$BACKEND_PORT/docs"
        print_info "  后端健康检查: http://localhost:$BACKEND_PORT/api/v1/health"
    fi
}

# 停止所有服务
stop_services() {
    print_step "停止所有服务..."
    
    # 停止前端服务
    if [ -f "$FRONTEND_DIR/frontend.pid" ]; then
        local frontend_pid=$(cat $FRONTEND_DIR/frontend.pid)
        if ps -p $frontend_pid > /dev/null; then
            kill $frontend_pid
            print_info "已停止前端服务 (PID: $frontend_pid)"
        fi
        rm -f $FRONTEND_DIR/frontend.pid
    fi
    
    # 停止后端服务
    if [ -f "$BACKEND_DIR/backend.pid" ]; then
        local backend_pid=$(cat $BACKEND_DIR/backend.pid)
        if ps -p $backend_pid > /dev/null; then
            # 先停用虚拟环境再杀死进程
            cd $BACKEND_DIR
            if [ -d "venv" ]; then
                source venv/bin/activate
                kill $backend_pid
                deactivate
            else
                kill $backend_pid
            fi
            print_info "已停止后端服务 (PID: $backend_pid)"
        fi
        rm -f $BACKEND_DIR/backend.pid
    fi
    
    # 强制清理可能残留的进程
    pkill -f "vite" 2>/dev/null
    pkill -f "uvicorn.*$BACKEND_PORT" 2>/dev/null
    
    print_info "所有服务已停止"
}

# 显示使用帮助
show_help() {
    echo "城市大脑企业信息处理系统一键启动脚本"
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  start     启动所有服务（默认）"
    echo "  stop      停止所有服务"
    echo "  status    显示服务状态"
    echo "  restart   重启所有服务"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0          # 启动所有服务"
    echo "  $0 start    # 启动所有服务"
    echo "  $0 stop     # 停止所有服务"
    echo "  $0 status   # 显示服务状态"
}

# 主函数
main() {
    case "$1" in
        "start"|"")
            print_info "开始启动城市大脑企业信息处理系统..."
            check_dependencies
            check_directories
            check_ports
            install_frontend_deps
            install_backend_deps
            start_backend
            start_frontend
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "status")
            show_status
            ;;
        "restart")
            stop_services
            sleep 2
            exec $0 start
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"