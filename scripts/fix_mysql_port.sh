#!/bin/bash
# 修改MySQL端口为3307，避免与Docker中的MySQL冲突
# 使用方法: sudo bash fix_mysql_port.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
NEW_PORT=3307
DB_NAME="City_Brain_DB"
DB_USER="City_Brain_user_mysql"
DB_PASSWORD="CityBrain@2024"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}修改MySQL端口为 ${NEW_PORT}${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请使用 sudo 运行此脚本${NC}"
    exit 1
fi

# 1. 停止MySQL服务
echo -e "\n${YELLOW}[1/6] 停止MySQL服务...${NC}"
systemctl stop mysql || true
sleep 2

# 2. 备份配置文件
echo -e "\n${YELLOW}[2/6] 备份配置文件...${NC}"
MYSQL_CONF="/etc/mysql/mysql.conf.d/mysqld.cnf"
if [ -f "$MYSQL_CONF" ]; then
    cp "$MYSQL_CONF" "${MYSQL_CONF}.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${GREEN}✓ 配置文件已备份${NC}"
else
    echo -e "${RED}✗ 配置文件不存在: $MYSQL_CONF${NC}"
    exit 1
fi

# 3. 修改MySQL端口
echo -e "\n${YELLOW}[3/6] 修改MySQL端口为 ${NEW_PORT}...${NC}"

# 检查是否已存在port配置
if grep -q "^port" "$MYSQL_CONF"; then
    # 如果存在，替换
    sed -i "s/^port.*/port = ${NEW_PORT}/" "$MYSQL_CONF"
else
    # 如果不存在，在[mysqld]段后添加
    sed -i "/\[mysqld\]/a port = ${NEW_PORT}" "$MYSQL_CONF"
fi

# 确认修改
if grep -q "port = ${NEW_PORT}" "$MYSQL_CONF"; then
    echo -e "${GREEN}✓ 端口配置已更新为 ${NEW_PORT}${NC}"
    echo -e "${YELLOW}配置内容:${NC}"
    grep "port = ${NEW_PORT}" "$MYSQL_CONF"
else
    echo -e "${RED}✗ 端口配置更新失败${NC}"
    exit 1
fi

# 4. 启动MySQL服务
echo -e "\n${YELLOW}[4/6] 启动MySQL服务...${NC}"
systemctl start mysql

# 等待MySQL启动
echo -e "${YELLOW}等待MySQL服务启动...${NC}"
for i in {1..30}; do
    if mysqladmin ping -P ${NEW_PORT} -h localhost --silent 2>/dev/null; then
        echo -e "${GREEN}✓ MySQL服务已在端口 ${NEW_PORT} 上启动${NC}"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# 5. 验证端口
echo -e "\n${YELLOW}[5/6] 验证MySQL端口...${NC}"
if netstat -tuln 2>/dev/null | grep ":${NEW_PORT}" >/dev/null; then
    echo -e "${GREEN}✓ MySQL正在监听端口 ${NEW_PORT}${NC}"
    netstat -tuln | grep ":${NEW_PORT}"
elif ss -tuln 2>/dev/null | grep ":${NEW_PORT}" >/dev/null; then
    echo -e "${GREEN}✓ MySQL正在监听端口 ${NEW_PORT}${NC}"
    ss -tuln | grep ":${NEW_PORT}"
else
    echo -e "${RED}✗ MySQL未在端口 ${NEW_PORT} 上监听${NC}"
    echo -e "${YELLOW}查看MySQL状态:${NC}"
    systemctl status mysql --no-pager || true
    exit 1
fi

# 6. 创建数据库和用户（如果还没创建）
echo -e "\n${YELLOW}[6/6] 创建数据库和用户...${NC}"

mysql -P ${NEW_PORT} <<-EOSQL 2>&1 | grep -v "mysql: "
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

    -- 显示数据库
    SHOW DATABASES LIKE '${DB_NAME}';
EOSQL

echo -e "${GREEN}✓ 数据库和用户创建成功${NC}"

# 7. 导入数据库结构
echo -e "\n${YELLOW}导入数据库结构和数据...${NC}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SQL_FILE="${SCRIPT_DIR}/init_database.sql"

if [ -f "$SQL_FILE" ]; then
    mysql -P ${NEW_PORT} ${DB_NAME} < "$SQL_FILE" 2>&1 | head -20
    echo -e "${GREEN}✓ 数据库结构和数据导入成功${NC}"
else
    echo -e "${YELLOW}⚠ SQL文件不存在: $SQL_FILE${NC}"
    echo -e "${YELLOW}稍后可手动导入${NC}"
fi

# 8. 验证数据
echo -e "\n${YELLOW}验证数据导入...${NC}"
mysql -P ${NEW_PORT} ${DB_NAME} <<-EOSQL
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
    SELECT '产业大脑关联表', COUNT(*) FROM QD_brain_industry_rel;
EOSQL

# 9. 更新项目配置文件
echo -e "\n${YELLOW}更新项目配置文件...${NC}"
PROJECT_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"

# 更新 city_brain_system_refactored/.env
ENV_FILE_REFACTORED="${PROJECT_ROOT}/city_brain_system_refactored/.env"
if [ -f "$ENV_FILE_REFACTORED" ]; then
    cp "$ENV_FILE_REFACTORED" "${ENV_FILE_REFACTORED}.backup.$(date +%Y%m%d_%H%M%S)"
    sed -i "s/^DB_HOST=.*/DB_HOST=localhost/" "$ENV_FILE_REFACTORED"
    sed -i "s/^DB_PORT=.*/DB_PORT=${NEW_PORT}/" "$ENV_FILE_REFACTORED"
    sed -i "s/^DB_USERNAME=.*/DB_USERNAME=${DB_USER}/" "$ENV_FILE_REFACTORED"
    sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD=${DB_PASSWORD}/" "$ENV_FILE_REFACTORED"
    sed -i "s/^DB_DATABASE=.*/DB_DATABASE=${DB_NAME}/" "$ENV_FILE_REFACTORED"
    echo -e "${GREEN}✓ 已更新: ${ENV_FILE_REFACTORED}${NC}"
fi

# 更新 city_brain_system/.env
ENV_FILE_LEGACY="${PROJECT_ROOT}/city_brain_system/.env"
if [ -f "$ENV_FILE_LEGACY" ]; then
    cp "$ENV_FILE_LEGACY" "${ENV_FILE_LEGACY}.backup.$(date +%Y%m%d_%H%M%S)"
    sed -i "s/^DB_HOST=.*/DB_HOST=localhost/" "$ENV_FILE_LEGACY"
    sed -i "s/^DB_PORT=.*/DB_PORT=${NEW_PORT}/" "$ENV_FILE_LEGACY"
    sed -i "s/^DB_USERNAME=.*/DB_USERNAME=${DB_USER}/" "$ENV_FILE_LEGACY"
    sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD=${DB_PASSWORD}/" "$ENV_FILE_LEGACY"
    sed -i "s/^DB_DATABASE=.*/DB_DATABASE=${DB_NAME}/" "$ENV_FILE_LEGACY"
    echo -e "${GREEN}✓ 已更新: ${ENV_FILE_LEGACY}${NC}"
fi

# 10. 测试连接
echo -e "\n${YELLOW}测试数据库连接...${NC}"
if mysql -P ${NEW_PORT} -u ${DB_USER} -p${DB_PASSWORD} ${DB_NAME} -e "SELECT 1" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ 数据库连接测试成功！${NC}"

    echo -e "\n${YELLOW}示例数据:${NC}"
    mysql -P ${NEW_PORT} -u ${DB_USER} -p${DB_PASSWORD} ${DB_NAME} -e "SELECT customer_name AS 企业名称, address AS 地址 FROM QD_customer LIMIT 3;" 2>/dev/null
else
    echo -e "${RED}✗ 数据库连接测试失败${NC}"
fi

# 完成
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✓ MySQL端口修改完成！${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n数据库信息:"
echo -e "  主机: localhost"
echo -e "  端口: ${GREEN}${NEW_PORT}${NC} (已修改)"
echo -e "  数据库: ${DB_NAME}"
echo -e "  用户名: ${DB_USER}"
echo -e "  密码: ${DB_PASSWORD}"

echo -e "\n连接命令:"
echo -e "  ${YELLOW}mysql -P ${NEW_PORT} -u ${DB_USER} -p${DB_PASSWORD} ${DB_NAME}${NC}"

echo -e "\n端口状态:"
echo -e "  ${GREEN}✓ 3306端口: Docker MySQL${NC}"
echo -e "  ${GREEN}✓ ${NEW_PORT}端口: 新安装的MySQL（本项目使用）${NC}"

echo -e "\n下一步:"
echo -e "  1. 测试Python连接: ${YELLOW}cd city_brain_system_refactored && python3 -c 'from infrastructure.database.connection import test_connection; print(test_connection())'${NC}"
echo -e "  2. 启动后端服务: ${YELLOW}./start_refactored_backend.sh${NC}"
echo -e "  3. 测试API: ${YELLOW}curl http://localhost:9003/api/v1/health${NC}"

echo -e "\n${GREEN}✓ 配置完成！${NC}"
