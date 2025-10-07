#!/bin/bash
# 城市大脑前端应用部署脚本

# 设置变量
PROJECT_DIR="/home/server/code/city_brain_frontend"
BACKEND_DIR="/home/server/code/city_brain_system"
NODE_VERSION="16"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# 检查依赖
check_dependencies() {
    print_info "检查系统依赖..."
    
    if ! command -v node &> /dev/null; then
        print_error "未找到Node.js，请先安装Node.js"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "未找到npm，请先安装npm"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "未找到Python3，请先安装Python3"
        exit 1
    fi
    
    print_info "所有依赖检查通过"
}

# 安装前端依赖
install_frontend_deps() {
    print_info "安装前端依赖..."
    
    cd $PROJECT_DIR
    if ! npm install; then
        print_error "前端依赖安装失败"
        exit 1
    fi
    
    print_info "前端依赖安装完成"
}

# 启动后端服务
start_backend() {
    print_info "启动后端服务..."
    
    cd $BACKEND_DIR
    
    # 检查后端服务是否已在运行
    if pgrep -f "uvicorn main:app.*9001" > /dev/null; then
        print_warning "后端服务已在运行"
        return 0
    fi
    
    # 启动后端服务
    nohup uvicorn main:app --host 0.0.0.0 --port 9001 > backend.log 2>&1 &
    
    # 等待服务启动
    sleep 5
    
    # 检查服务是否启动成功
    if curl -s http://localhost:9001/api/v1/health > /dev/null; then
        print_info "后端服务启动成功"
    else
        print_error "后端服务启动失败"
        exit 1
    fi
}

# 构建前端应用
build_frontend() {
    print_info "构建前端应用..."
    
    cd $PROJECT_DIR
    if ! npm run build; then
        print_error "前端构建失败"
        exit 1
    fi
    
    print_info "前端构建完成"
}

# 启动前端开发服务器
start_frontend_dev() {
    print_info "启动前端开发服务器..."
    
    cd $PROJECT_DIR
    
    # 检查前端服务是否已在运行
    if pgrep -f "vite" > /dev/null; then
        print_warning "前端开发服务器已在运行"
        return 0
    fi
    
    # 启动前端开发服务器
    nohup npm run start > frontend.log 2>&1 &
    
    # 等待服务启动
    sleep 10
    
    print_info "前端开发服务器已启动，请访问 http://localhost:3000"
}

# 启动生产服务器
start_frontend_prod() {
    print_info "启动前端生产服务器..."
    
    # 这里可以使用nginx、apache或其他web服务器来提供静态文件
    # 作为示例，我们使用简单的Python HTTP服务器
    cd $PROJECT_DIR/dist
    
    # 检查服务是否已在运行
    if pgrep -f "python3.*http.server.*9000" > /dev/null; then
        print_warning "前端生产服务器已在运行"
        return 0
    fi
    
    # 启动简单的HTTP服务器
    nohup python3 -m http.server 9000 > prod_server.log 2>&1 &
    
    # 等待服务启动
    sleep 3
    
    print_info "前端生产服务器已启动，请访问 http://localhost:3000"
}

# 停止所有服务
stop_services() {
    print_info "停止所有服务..."
    
    # 停止前端开发服务器
    pkill -f "vite" 2>/dev/null
    
    # 停止前端生产服务器
    pkill -f "python3.*http.server.*9000" 2>/dev/null
    
    # 停止后端服务
    pkill -f "uvicorn main:app.*9001" 2>/dev/null
    
    print_info "所有服务已停止"
}

# 显示服务状态
show_status() {
    print_info "检查服务状态..."
    
    if pgrep -f "uvicorn main:app.*9001" > /dev/null; then
        echo "后端服务: ${GREEN}运行中${NC}"
    else
        echo "后端服务: ${RED}未运行${NC}"
    fi
    
    if pgrep -f "vite" > /dev/null; then
        echo "前端开发服务: ${GREEN}运行中${NC}"
    else
        echo "前端开发服务: ${RED}未运行${NC}"
    fi
    
    if pgrep -f "python3.*http.server.*9000" > /dev/null; then
        echo "前端生产服务: ${GREEN}运行中${NC}"
    else
        echo "前端生产服务: ${RED}未运行${NC}"
    fi
}

# 主函数
main() {
    case "$1" in
        "install")
            check_dependencies
            install_frontend_deps
            ;;
        "start-backend")
            start_backend
            ;;
        "start-frontend")
            start_frontend_dev
            ;;
        "build")
            build_frontend
            ;;
        "start-prod")
            build_frontend
            start_frontend_prod
            ;;
        "deploy")
            check_dependencies
            install_frontend_deps
            start_backend
            start_frontend_dev
            ;;
        "status")
            show_status
            ;;
        "stop")
            stop_services
            ;;
        *)
            echo "城市大脑前端应用部署脚本"
            echo "用法: $0 {install|start-backend|start-frontend|build|start-prod|deploy|status|stop}"
            echo ""
            echo "命令说明:"
            echo "  install        安装前端依赖"
            echo "  start-backend  启动后端服务"
            echo "  start-frontend 启动前端开发服务器"
            echo "  build          构建前端应用"
            echo "  start-prod     启动前端生产服务器"
            echo "  deploy         完整部署（安装依赖+启动服务）"
            echo "  status         显示服务状态"
            echo "  stop           停止所有服务"
            ;;
    esac
}

# 执行主函数
main "$@"