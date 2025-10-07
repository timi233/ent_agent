# 数据库设计方案

## 📋 概述

本文档详细描述了城市大脑企业信息处理系统的数据库设计方案，包括新的统一表结构设计、数据迁移策略和数据质量管理方案。

## 🗄️ 现有数据库结构分析

### 当前表结构
1. **QD_customer** (客户企业表) - 261条记录
2. **QD_enterprise_chain_leader** (链主企业表) - 62条记录
3. **QD_area** (地区表) - 5条记录
4. **QD_industry** (行业表) - 13条记录
5. **QD_industry_brain** (产业大脑表) - 6条记录
6. **QD_brain_industry_rel** (产业大脑行业关联表)

### 存在的问题
- 企业信息分散在多个表中
- 缺乏统一的企业标识
- 地址信息不规范
- 缺少数据质量管理机制

## 🏗️ 新数据库设计

### 1. 统一企业表 (enterprise)
```sql
CREATE TABLE enterprise (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '企业ID',
    name VARCHAR(255) NOT NULL COMMENT '企业名称',
    unified_social_credit_code VARCHAR(32) UNIQUE COMMENT '统一社会信用代码',
    enterprise_type ENUM('customer', 'chain_leader', 'supplier', 'other') NOT NULL COMMENT '企业类型',
    status ENUM('active', 'inactive', 'merged', 'dissolved') DEFAULT 'active' COMMENT '企业状态',
    registration_capital DECIMAL(15,2) COMMENT '注册资本',
    establishment_date DATE COMMENT '成立日期',
    business_scope TEXT COMMENT '经营范围',
    legal_representative VARCHAR(100) COMMENT '法定代表人',
    contact_phone VARCHAR(50) COMMENT '联系电话',
    contact_email VARCHAR(100) COMMENT '联系邮箱',
    website VARCHAR(255) COMMENT '官方网站',
    employee_count INT COMMENT '员工数量',
    annual_revenue DECIMAL(15,2) COMMENT '年营收',
    data_source ENUM('manual', 'web_search', 'api', 'import') NOT NULL DEFAULT 'manual' COMMENT '数据来源',
    import_batch VARCHAR(50) COMMENT '导入批次',
    confidence_score DECIMAL(3,2) DEFAULT 1.00 COMMENT '数据可信度',
    verified_at TIMESTAMP NULL COMMENT '验证时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_name (name),
    INDEX idx_type (enterprise_type),
    INDEX idx_credit_code (unified_social_credit_code),
    INDEX idx_status (status),
    INDEX idx_batch (import_batch),
    FULLTEXT idx_name_fulltext (name, business_scope)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='统一企业信息表';
```

### 2. 企业地址表 (enterprise_address)
```sql
CREATE TABLE enterprise_address (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '地址ID',
    enterprise_id BIGINT NOT NULL COMMENT '企业ID',
    address_type ENUM('registered', 'office', 'factory', 'branch') NOT NULL COMMENT '地址类型',
    province VARCHAR(50) COMMENT '省份',
    city VARCHAR(50) COMMENT '城市',
    district VARCHAR(50) COMMENT '区县',
    street VARCHAR(100) COMMENT '街道',
    detailed_address TEXT COMMENT '详细地址',
    postal_code VARCHAR(10) COMMENT '邮政编码',
    longitude DECIMAL(10,7) COMMENT '经度',
    latitude DECIMAL(10,7) COMMENT '纬度',
    data_source ENUM('manual', 'web_search', 'api', 'geocoding') NOT NULL COMMENT '数据来源',
    confidence_score DECIMAL(3,2) DEFAULT 1.00 COMMENT '数据可信度',
    verified_at TIMESTAMP NULL COMMENT '验证时间',
    is_primary BOOLEAN DEFAULT FALSE COMMENT '是否主要地址',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    FOREIGN KEY (enterprise_id) REFERENCES enterprise(id) ON DELETE CASCADE,
    INDEX idx_enterprise_type (enterprise_id, address_type),
    INDEX idx_location (province, city, district),
    INDEX idx_coordinates (longitude, latitude)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='企业地址信息表';
```

### 3. 行业信息表 (industry)
```sql
CREATE TABLE industry (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '行业ID',
    name VARCHAR(100) NOT NULL COMMENT '行业名称',
    code VARCHAR(20) UNIQUE COMMENT '行业代码',
    parent_id BIGINT NULL COMMENT '父级行业ID',
    level TINYINT NOT NULL DEFAULT 1 COMMENT '行业层级',
    industry_type VARCHAR(50) COMMENT '行业类型',
    description TEXT COMMENT '行业描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    FOREIGN KEY (parent_id) REFERENCES industry(id),
    INDEX idx_parent (parent_id),
    INDEX idx_code (code),
    INDEX idx_level (level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='行业信息表';
```

### 4. 产业大脑表 (industry_brain)
```sql
CREATE TABLE industry_brain (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '产业大脑ID',
    name VARCHAR(100) NOT NULL COMMENT '产业大脑名称',
    code VARCHAR(20) UNIQUE COMMENT '产业大脑代码',
    area_id BIGINT COMMENT '所属地区ID',
    build_year YEAR COMMENT '建设年份',
    investment_amount DECIMAL(15,2) COMMENT '投资金额',
    leading_enterprise_id BIGINT COMMENT '牵头企业ID',
    status ENUM('planning', 'building', 'operating', 'upgrading') DEFAULT 'planning' COMMENT '建设状态',
    description TEXT COMMENT '产业大脑描述',
    key_technologies TEXT COMMENT '关键技术',
    service_capabilities TEXT COMMENT '服务能力',
    achievement_indicators TEXT COMMENT '成效指标',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    FOREIGN KEY (area_id) REFERENCES area(id),
    FOREIGN KEY (leading_enterprise_id) REFERENCES enterprise(id),
    INDEX idx_area (area_id),
    INDEX idx_status (status),
    INDEX idx_year (build_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产业大脑信息表';
```

### 5. 企业关系表 (enterprise_relationship)
```sql
CREATE TABLE enterprise_relationship (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '关系ID',
    source_enterprise_id BIGINT NOT NULL COMMENT '源企业ID',
    target_enterprise_id BIGINT NOT NULL COMMENT '目标企业ID',
    relationship_type ENUM('chain_leader', 'supplier', 'customer', 'partner', 'subsidiary', 'parent') NOT NULL COMMENT '关系类型',
    industry_id BIGINT COMMENT '关联行业ID',
    brain_id BIGINT COMMENT '关联产业大脑ID',
    relationship_strength DECIMAL(3,2) DEFAULT 1.00 COMMENT '关系强度',
    start_date DATE COMMENT '关系开始时间',
    end_date DATE COMMENT '关系结束时间',
    description TEXT COMMENT '关系描述',
    data_source ENUM('manual', 'web_search', 'api', 'analysis') NOT NULL COMMENT '数据来源',
    verified BOOLEAN DEFAULT FALSE COMMENT '是否已验证',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    FOREIGN KEY (source_enterprise_id) REFERENCES enterprise(id),
    FOREIGN KEY (target_enterprise_id) REFERENCES enterprise(id),
    FOREIGN KEY (industry_id) REFERENCES industry(id),
    FOREIGN KEY (brain_id) REFERENCES industry_brain(id),
    INDEX idx_source (source_enterprise_id),
    INDEX idx_target (target_enterprise_id),
    INDEX idx_type (relationship_type),
    INDEX idx_industry_brain (industry_id, brain_id),
    UNIQUE KEY uk_relationship (source_enterprise_id, target_enterprise_id, relationship_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='企业关系表';
```

### 6. 数据质量日志表 (data_quality_log)
```sql
CREATE TABLE data_quality_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    table_name VARCHAR(100) NOT NULL COMMENT '表名',
    record_id BIGINT NOT NULL COMMENT '记录ID',
    field_name VARCHAR(100) NOT NULL COMMENT '字段名',
    issue_type ENUM('missing', 'incorrect', 'outdated', 'duplicate', 'format_error') NOT NULL COMMENT '问题类型',
    old_value TEXT COMMENT '原值',
    new_value TEXT COMMENT '新值',
    correction_method ENUM('manual', 'auto_web_search', 'auto_api', 'rule_based', 'ai_correction') NOT NULL COMMENT '修正方法',
    confidence_score DECIMAL(3,2) COMMENT '置信度',
    verified BOOLEAN DEFAULT FALSE COMMENT '是否已验证',
    verified_by VARCHAR(100) COMMENT '验证人',
    verified_at TIMESTAMP NULL COMMENT '验证时间',
    correction_cost DECIMAL(8,2) COMMENT '修正成本',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_table_record (table_name, record_id),
    INDEX idx_issue_type (issue_type),
    INDEX idx_method (correction_method),
    INDEX idx_verified (verified),
    INDEX idx_created_date (DATE(created_at))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据质量日志表';
```

## 🔄 数据迁移策略

### 阶段一：影子表创建
```sql
-- 创建数据迁移映射表
CREATE TABLE legacy_mapping (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    new_enterprise_id BIGINT NOT NULL,
    legacy_table ENUM('QD_customer', 'QD_enterprise_chain_leader') NOT NULL,
    legacy_id INT NOT NULL,
    migration_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    migration_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (new_enterprise_id) REFERENCES enterprise(id),
    UNIQUE KEY uk_legacy (legacy_table, legacy_id),
    INDEX idx_status (migration_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据迁移映射表';
```

### 阶段二：数据迁移脚本
```python
def migrate_legacy_data():
    """
    数据迁移主函数
    """
    # 1. 迁移客户企业数据
    migrate_customers()
    
    # 2. 迁移链主企业数据
    migrate_chain_leaders()
    
    # 3. 建立企业关系
    establish_relationships()
    
    # 4. 数据验证
    validate_migration()
    
    # 5. 生成迁移报告
    generate_migration_report()

def migrate_customers():
    """迁移QD_customer表数据"""
    customers = db.execute("SELECT * FROM QD_customer")
    
    for customer in customers:
        # 创建企业记录
        enterprise_id = create_enterprise_from_customer(customer)
        
        # 创建地址记录
        if customer.address:
            create_address_from_customer(enterprise_id, customer)
        
        # 创建映射记录
        create_legacy_mapping(enterprise_id, 'QD_customer', customer.customer_id)

def migrate_chain_leaders():
    """迁移QD_enterprise_chain_leader表数据"""
    chain_leaders = db.execute("SELECT * FROM QD_enterprise_chain_leader")
    
    for leader in chain_leaders:
        # 检查是否已存在同名企业
        existing = check_existing_enterprise(leader.enterprise_name)
        
        if existing:
            # 更新企业类型为链主企业
            update_enterprise_type(existing.id, 'chain_leader')
            enterprise_id = existing.id
        else:
            # 创建新的企业记录
            enterprise_id = create_enterprise_from_chain_leader(leader)
        
        # 创建映射记录
        create_legacy_mapping(enterprise_id, 'QD_enterprise_chain_leader', leader.enterprise_id)
```

### 阶段三：数据验证
```sql
-- 验证迁移完整性
SELECT 
    legacy_table,
    COUNT(*) as total_records,
    SUM(CASE WHEN migration_status = 'completed' THEN 1 ELSE 0 END) as migrated,
    SUM(CASE WHEN migration_status = 'failed' THEN 1 ELSE 0 END) as failed
FROM legacy_mapping
GROUP BY legacy_table;

-- 检查重复企业
SELECT name, COUNT(*) as count
FROM enterprise
GROUP BY name
HAVING COUNT(*) > 1;

-- 验证地址信息
SELECT 
    e.name,
    COUNT(ea.id) as address_count,
    SUM(CASE WHEN ea.is_primary THEN 1 ELSE 0 END) as primary_count
FROM enterprise e
LEFT JOIN enterprise_address ea ON e.id = ea.enterprise_id
GROUP BY e.id, e.name
HAVING primary_count != 1;
```

## 📊 数据质量管理

### 数据质量指标
1. **完整性**: 必填字段的填充率
2. **准确性**: 数据格式和内容的正确性
3. **一致性**: 跨表数据的一致性
4. **及时性**: 数据的更新频率
5. **唯一性**: 重复数据的控制

### 数据质量监控
```sql
-- 数据完整性检查
SELECT 
    'enterprise' as table_name,
    'name' as field_name,
    COUNT(*) as total_records,
    COUNT(name) as filled_records,
    ROUND(COUNT(name) * 100.0 / COUNT(*), 2) as completeness_rate
FROM enterprise
UNION ALL
SELECT 
    'enterprise' as table_name,
    'unified_social_credit_code' as field_name,
    COUNT(*) as total_records,
    COUNT(unified_social_credit_code) as filled_records,
    ROUND(COUNT(unified_social_credit_code) * 100.0 / COUNT(*), 2) as completeness_rate
FROM enterprise;

-- 数据准确性检查
SELECT 
    id,
    name,
    unified_social_credit_code,
    CASE 
        WHEN unified_social_credit_code IS NOT NULL 
             AND LENGTH(unified_social_credit_code) != 18 
        THEN 'Invalid length'
        WHEN unified_social_credit_code IS NOT NULL 
             AND unified_social_credit_code NOT REGEXP '^[0-9A-Z]{18}$' 
        THEN 'Invalid format'
        ELSE 'Valid'
    END as credit_code_status
FROM enterprise
WHERE unified_social_credit_code IS NOT NULL
HAVING credit_code_status != 'Valid';
```

### 自动修正规则
```python
class DataQualityRules:
    @staticmethod
    def validate_credit_code(code: str) -> bool:
        """验证统一社会信用代码"""
        if not code or len(code) != 18:
            return False
        return re.match(r'^[0-9A-Z]{18}$', code) is not None
    
    @staticmethod
    def standardize_phone(phone: str) -> str:
        """标准化电话号码"""
        if not phone:
            return phone
        
        # 移除所有非数字字符
        digits = re.sub(r'\D', '', phone)
        
        # 格式化手机号码
        if len(digits) == 11 and digits.startswith('1'):
            return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
        
        # 格式化固定电话
        if len(digits) >= 7:
            if len(digits) == 7:
                return f"{digits[:3]}-{digits[3:]}"
            elif len(digits) == 8:
                return f"{digits[:4]}-{digits[4:]}"
            elif len(digits) >= 10:
                area_code = digits[:-8] if len(digits) > 10 else digits[:3]
                number = digits[-8:]
                return f"{area_code}-{number[:4]}-{number[4:]}"
        
        return phone
    
    @staticmethod
    def extract_city_from_address(address: str) -> str:
        """从地址中提取城市信息"""
        if not address:
            return None
        
        # 青岛市及其区县的匹配模式
        qingdao_patterns = [
            r'青岛市',
            r'市南区', r'市北区', r'李沧区', r'崂山区', 
            r'城阳区', r'黄岛区', r'即墨区', r'胶州市', 
            r'平度市', r'莱西市'
        ]
        
        for pattern in qingdao_patterns:
            if re.search(pattern, address):
                if pattern == r'青岛市':
                    return '青岛市'
                else:
                    return pattern.replace('区', '').replace('市', '')
        
        return None
```

## 🔧 索引优化策略

### 主要索引
```sql
-- 企业表索引
CREATE INDEX idx_enterprise_name_type ON enterprise(name, enterprise_type);
CREATE INDEX idx_enterprise_status_created ON enterprise(status, created_at);
CREATE INDEX idx_enterprise_batch_source ON enterprise(import_batch, data_source);

-- 地址表索引
CREATE INDEX idx_address_location_full ON enterprise_address(province, city, district, street);
CREATE INDEX idx_address_enterprise_primary ON enterprise_address(enterprise_id, is_primary);

-- 关系表索引
CREATE INDEX idx_relationship_source_type ON enterprise_relationship(source_enterprise_id, relationship_type);
CREATE INDEX idx_relationship_industry_brain ON enterprise_relationship(industry_id, brain_id);

-- 质量日志索引
CREATE INDEX idx_quality_log_table_field ON data_quality_log(table_name, field_name);
CREATE INDEX idx_quality_log_date_type ON data_quality_log(DATE(created_at), issue_type);
```

### 分区策略
```sql
-- 按时间分区数据质量日志表
ALTER TABLE data_quality_log 
PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p2026 VALUES LESS THAN (2027),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

## 📈 性能优化建议

### 查询优化
1. **使用覆盖索引**: 减少回表查询
2. **分页优化**: 使用游标分页替代OFFSET
3. **批量操作**: 减少数据库连接次数
4. **读写分离**: 主从数据库架构

### 存储优化
1. **数据压缩**: 使用InnoDB压缩
2. **归档策略**: 定期归档历史数据
3. **分表策略**: 按业务维度分表

---

*文档版本：v1.0*
*更新时间：2025年9月26日*