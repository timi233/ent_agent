#!/bin/bash
# 城市大脑系统MySQL数据库一键安装配置脚本
# 使用方法: sudo bash setup_mysql.sh

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 数据库配置
DB_NAME="City_Brain_DB"
DB_USER="City_Brain_user_mysql"
DB_PASSWORD="CityBrain@2024"  # 建议修改为更安全的密码
DB_HOST="localhost"
DB_PORT="3306"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}城市大脑系统 MySQL 数据库一键安装${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请使用 sudo 运行此脚本${NC}"
    echo "使用方法: sudo bash $0"
    exit 1
fi

# 0. 修复软件源问题（如果是Ubuntu 24.10 oracular）
echo -e "\n${YELLOW}[0/8] 检查并修复软件源配置...${NC}"
if grep -q "oracular" /etc/os-release 2>/dev/null; then
    echo -e "${YELLOW}检测到Ubuntu 24.10 (Oracular)，临时切换到官方源...${NC}"

    # 备份当前源列表
    cp /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list.d/ubuntu.sources.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

    # 使用官方源或noble（24.04）源作为替代
    cat > /etc/apt/sources.list.d/ubuntu-temp.sources <<EOF
Types: deb
URIs: http://archive.ubuntu.com/ubuntu/
Suites: noble noble-updates noble-backports
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg

Types: deb
URIs: http://security.ubuntu.com/ubuntu/
Suites: noble-security
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
EOF

    echo -e "${GREEN}✓ 已切换到Ubuntu 24.04 (Noble)源${NC}"
fi

# 1. 更新软件包列表
echo -e "\n${YELLOW}[1/8] 更新软件包列表...${NC}"
apt update 2>&1 | grep -v "^Ign:" | head -20 || true

# 2. 安装MySQL服务器
echo -e "\n${YELLOW}[2/8] 安装MySQL服务器...${NC}"
echo -e "${YELLOW}提示: 安装过程可能需要几分钟，请耐心等待...${NC}"

# 设���非交互式安装
export DEBIAN_FRONTEND=noninteractive

# 预配置MySQL（避免交互式提示）
echo "mysql-server mysql-server/root_password password " | debconf-set-selections
echo "mysql-server mysql-server/root_password_again password " | debconf-set-selections

# 安装MySQL
apt install -y mysql-server 2>&1 | tail -20

# 3. 启动MySQL服务
echo -e "\n${YELLOW}[3/8] 启动MySQL服务...${NC}"
systemctl start mysql || true
systemctl enable mysql || true

# 等待MySQL完全启动
echo -e "${YELLOW}等待MySQL服务完全启动...${NC}"
for i in {1..30}; do
    if mysqladmin ping -h localhost --silent 2>/dev/null; then
        echo -e "${GREEN}✓ MySQL服务已就绪${NC}"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# 4. 检查MySQL服务状态
echo -e "\n${YELLOW}[4/8] 检查MySQL服务状态...${NC}"
if systemctl is-active --quiet mysql; then
    echo -e "${GREEN}✓ MySQL服务运行正常${NC}"
    mysql --version
else
    echo -e "${YELLOW}⚠ MySQL服务状态异常，尝试启动...${NC}"
    systemctl restart mysql
    sleep 3
    if systemctl is-active --quiet mysql; then
        echo -e "${GREEN}✓ MySQL服务已成功启动${NC}"
    else
        echo -e "${RED}✗ MySQL服务启动失败${NC}"
        echo -e "${YELLOW}尝试查看日志:${NC}"
        journalctl -u mysql -n 50 --no-pager
        exit 1
    fi
fi

# 5. 创建数据库和用户
echo -e "\n${YELLOW}[5/8] 创建数据库和用户...${NC}"

# 使用sudo方式连接MySQL（Ubuntu默认配置）
mysql <<-EOSQL 2>&1 | grep -v "mysql: "
    -- 创建数据库
    CREATE DATABASE IF NOT EXISTS ${DB_NAME}
        DEFAULT CHARACTER SET utf8mb4
        COLLATE utf8mb4_unicode_ci;

    -- 创建用户
    CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
    CREATE USER IF NOT EXISTS '${DB_USER}'@'%' IDENTIFIED BY '${DB_PASSWORD}';

    -- 授予权限
    GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
    GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'%';

    -- 刷新权限
    FLUSH PRIVILEGES;

    -- 显示创建的数据库
    SELECT CONCAT('✓ 数据库 ', SCHEMA_NAME, ' 创建成功') AS status
    FROM information_schema.SCHEMATA
    WHERE SCHEMA_NAME = '${DB_NAME}';
EOSQL

echo -e "${GREEN}✓ 数据库和用户创建成功${NC}"
echo -e "  数据库名: ${DB_NAME}"
echo -e "  用户名: ${DB_USER}"
echo -e "  密码: ${DB_PASSWORD}"

# 6. 导入数据库结构和初始数据
echo -e "\n${YELLOW}[6/8] 导入数据库结构和初始数据...${NC}"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SQL_FILE="${SCRIPT_DIR}/init_database.sql"

if [ -f "$SQL_FILE" ]; then
    echo -e "${YELLOW}导入SQL文件: $SQL_FILE${NC}"
    mysql ${DB_NAME} < "$SQL_FILE" 2>&1 | grep -v "mysql: " | head -20
    echo -e "${GREEN}✓ 数据库结构和初始数据导入成功${NC}"
else
    echo -e "${RED}✗ 找不到SQL文件: $SQL_FILE${NC}"
    echo -e "${YELLOW}请确保 init_database.sql 文件存在${NC}"
    exit 1
fi

# 7. 验证数据导入
echo -e "\n${YELLOW}[7/8] 验证数据导入...${NC}"

mysql ${DB_NAME} <<-EOSQL
    SELECT
        '地区表' AS 表名, COUNT(*) AS 记录数 FROM QD_area
    UNION ALL
    SELECT '行业表', COUNT(*) FROM QD_industry
    UNION ALL
    SELECT '产业大脑表', COUNT(*) FROM QD_industry_brain
    UNION ALL
    SELECT '链主企业表', COUNT(*) FROM QD_enterprise_chain_leader
    UNION ALL
    SELECT '客户企业表', COUNT(*) FROM QD_customer
    UNION ALL
    SELECT '产业大脑关联表', COUNT(*) FROM QD_brain_industry_rel
    UNION ALL
    SELECT '缓存表', COUNT(*) FROM company_cache;
EOSQL

# 8. 更新项目配置文件
echo -e "\n${YELLOW}[8/8] 更新项目配置文件...${NC}"

PROJECT_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"

# 更新 city_brain_system_refactored/.env
ENV_FILE_REFACTORED="${PROJECT_ROOT}/city_brain_system_refactored/.env"
if [ -f "$ENV_FILE_REFACTORED" ]; then
    # 备份原文件
    cp "$ENV_FILE_REFACTORED" "${ENV_FILE_REFACTORED}.backup.$(date +%Y%m%d_%H%M%S)"

    # 更新数据库配置
    sed -i "s/^DB_HOST=.*/DB_HOST=${DB_HOST}/" "$ENV_FILE_REFACTORED"
    sed -i "s/^DB_PORT=.*/DB_PORT=${DB_PORT}/" "$ENV_FILE_REFACTORED"
    sed -i "s/^DB_USERNAME=.*/DB_USERNAME=${DB_USER}/" "$ENV_FILE_REFACTORED"
    sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD=${DB_PASSWORD}/" "$ENV_FILE_REFACTORED"
    sed -i "s/^DB_DATABASE=.*/DB_DATABASE=${DB_NAME}/" "$ENV_FILE_REFACTORED"

    echo -e "${GREEN}✓ 已更新: ${ENV_FILE_REFACTORED}${NC}"
else
    echo -e "${YELLOW}⚠ 配置文件不存在: ${ENV_FILE_REFACTORED}${NC}"
fi

# 更新 city_brain_system/.env
ENV_FILE_LEGACY="${PROJECT_ROOT}/city_brain_system/.env"
if [ -f "$ENV_FILE_LEGACY" ]; then
    # 备份原文件
    cp "$ENV_FILE_LEGACY" "${ENV_FILE_LEGACY}.backup.$(date +%Y%m%d_%H%M%S)"

    # 更新数据库配置
    sed -i "s/^DB_HOST=.*/DB_HOST=${DB_HOST}/" "$ENV_FILE_LEGACY"
    sed -i "s/^DB_PORT=.*/DB_PORT=${DB_PORT}/" "$ENV_FILE_LEGACY"
    sed -i "s/^DB_USERNAME=.*/DB_USERNAME=${DB_USER}/" "$ENV_FILE_LEGACY"
    sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD=${DB_PASSWORD}/" "$ENV_FILE_LEGACY"
    sed -i "s/^DB_DATABASE=.*/DB_DATABASE=${DB_NAME}/" "$ENV_FILE_LEGACY"

    echo -e "${GREEN}✓ 已更新: ${ENV_FILE_LEGACY}${NC}"
else
    echo -e "${YELLOW}⚠ 配置文件不存在: ${ENV_FILE_LEGACY}${NC}"
fi

# 9. 配置MySQL允许远程连接（可选）
echo -e "\n${YELLOW}配置MySQL允许远程连接（可选）...${NC}"
MYSQL_CONF="/etc/mysql/mysql.conf.d/mysqld.cnf"
if [ -f "$MYSQL_CONF" ]; then
    # 备份配置文件
    cp "$MYSQL_CONF" "${MYSQL_CONF}.backup.$(date +%Y%m%d_%H%M%S)"

    # 注释掉 bind-address
    sed -i 's/^bind-address/#bind-address/' "$MYSQL_CONF" 2>/dev/null || true

    # 重启MySQL服务
    systemctl restart mysql
    sleep 2
    echo -e "${GREEN}✓ MySQL已配置为允许远程连接${NC}"
else
    echo -e "${YELLOW}⚠ MySQL配置文件不存在，跳过远程连接配置${NC}"
fi

# 10. 测试数据库连接
echo -e "\n${YELLOW}测试数据库连接...${NC}"

# 测试连接
if mysql -u ${DB_USER} -p${DB_PASSWORD} ${DB_NAME} -e "SELECT 1" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ 数据库连接测试成功！${NC}"

    # 显示一条示例数据
    echo -e "\n${YELLOW}示例数据:${NC}"
    mysql -u ${DB_USER} -p${DB_PASSWORD} ${DB_NAME} -e "SELECT customer_name AS 企业名称, address AS 地址 FROM QD_customer LIMIT 3;" 2>/dev/null
else
    echo -e "${RED}✗ 数据库连接测试失败${NC}"
fi

# 恢复软件源配置（如果修改过）
if [ -f "/etc/apt/sources.list.d/ubuntu-temp.sources" ]; then
    echo -e "\n${YELLOW}恢复软件源配置...${NC}"
    rm -f /etc/apt/sources.list.d/ubuntu-temp.sources
    echo -e "${GREEN}✓ 已恢复原始软件源配置${NC}"
fi

# 完成
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✓ MySQL数据库安装配置完成！${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n数据库信息:"
echo -e "  主机: ${DB_HOST}"
echo -e "  端口: ${DB_PORT}"
echo -e "  数据库: ${DB_NAME}"
echo -e "  用户名: ${DB_USER}"
echo -e "  密码: ${DB_PASSWORD}"

echo -e "\n连接命令:"
echo -e "  ${YELLOW}mysql -u ${DB_USER} -p${DB_PASSWORD} ${DB_NAME}${NC}"

echo -e "\n下一步操作:"
echo -e "  1. 测试Python连接: ${YELLOW}cd city_brain_system_refactored && python3 -c 'from infrastructure.database.connection import test_connection; print(test_connection())'${NC}"
echo -e "  2. 启动后端服务: ${YELLOW}./start_refactored_backend.sh${NC}"
echo -e "  3. 测试健康检查: ${YELLOW}curl http://localhost:9003/api/v1/health${NC}"
echo -e "  4. 测试企业查询: ${YELLOW}curl -X POST http://localhost:9003/api/v1/company/process -H 'Content-Type: application/json' -d '{\"input_text\": \"查询海尔集团\"}'${NC}"

echo -e "\n${GREEN}✓ 安装完成！配置文件已自动备份${NC}"
