-- 城市大脑企业信息处理系统数据库初始化脚本
-- 创建日期: 2025-10-01
-- 版本: 1.0

-- ============================================
-- 1. 创建数据库
-- ============================================
CREATE DATABASE IF NOT EXISTS City_Brain_DB
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE City_Brain_DB;

-- ============================================
-- 2. 地区表 (QD_area)
-- ============================================
DROP TABLE IF EXISTS QD_area;
CREATE TABLE QD_area (
    area_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '地区ID',
    city_name VARCHAR(50) NOT NULL COMMENT '城市名称',
    district_name VARCHAR(50) NOT NULL COMMENT '区县名称',
    district_code VARCHAR(20) COMMENT '区县代码',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_city (city_name),
    INDEX idx_district (district_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='地区信息表';

-- ============================================
-- 3. 行业表 (QD_industry)
-- ============================================
DROP TABLE IF EXISTS QD_industry;
CREATE TABLE QD_industry (
    industry_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '行业ID',
    industry_name VARCHAR(100) NOT NULL COMMENT '行业名称',
    industry_type VARCHAR(50) COMMENT '行业类型',
    industry_remark TEXT COMMENT '行业备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_name (industry_name),
    INDEX idx_type (industry_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='行业信息表';

-- ============================================
-- 4. 产业大脑表 (QD_industry_brain)
-- ============================================
DROP TABLE IF EXISTS QD_industry_brain;
CREATE TABLE QD_industry_brain (
    brain_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '产业大脑ID',
    brain_name VARCHAR(100) NOT NULL COMMENT '产业大脑名称',
    area_id INT COMMENT '所属地区ID',
    build_year YEAR COMMENT '建设年份',
    brain_remark TEXT COMMENT '产业大脑备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    FOREIGN KEY (area_id) REFERENCES QD_area(area_id) ON DELETE SET NULL,
    INDEX idx_area (area_id),
    INDEX idx_name (brain_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产业大脑信息表';

-- ============================================
-- 5. 链主企业表 (QD_enterprise_chain_leader)
-- ============================================
DROP TABLE IF EXISTS QD_enterprise_chain_leader;
CREATE TABLE QD_enterprise_chain_leader (
    enterprise_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '企业ID',
    enterprise_name VARCHAR(255) NOT NULL COMMENT '企业名称',
    industry_id INT COMMENT '所属行业ID',
    area_id INT COMMENT '所属地区ID',
    enterprise_remark TEXT COMMENT '企业备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    FOREIGN KEY (industry_id) REFERENCES QD_industry(industry_id) ON DELETE SET NULL,
    FOREIGN KEY (area_id) REFERENCES QD_area(area_id) ON DELETE SET NULL,
    INDEX idx_name (enterprise_name),
    INDEX idx_industry (industry_id),
    INDEX idx_area (area_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='链主企业信息表';

-- ============================================
-- 6. 客户企业表 (QD_customer)
-- ============================================
DROP TABLE IF EXISTS QD_customer;
CREATE TABLE QD_customer (
    customer_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '客户ID',
    customer_name VARCHAR(255) NOT NULL COMMENT '客户企业名称',
    address VARCHAR(500) COMMENT '企业地址',
    data_source VARCHAR(50) COMMENT '数据来源',
    tag_result INT COMMENT '标签结果',
    industry_id INT COMMENT '所属行业ID',
    brain_id INT COMMENT '关联产业大脑ID',
    chain_leader_id INT COMMENT '链主企业ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    FOREIGN KEY (industry_id) REFERENCES QD_industry(industry_id) ON DELETE SET NULL,
    FOREIGN KEY (brain_id) REFERENCES QD_industry_brain(brain_id) ON DELETE SET NULL,
    FOREIGN KEY (chain_leader_id) REFERENCES QD_enterprise_chain_leader(enterprise_id) ON DELETE SET NULL,
    INDEX idx_name (customer_name),
    INDEX idx_industry (industry_id),
    INDEX idx_brain (brain_id),
    INDEX idx_chain_leader (chain_leader_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户企业信息表';

-- ============================================
-- 7. 产业大脑行业关联表 (QD_brain_industry_rel)
-- ============================================
DROP TABLE IF EXISTS QD_brain_industry_rel;
CREATE TABLE QD_brain_industry_rel (
    rel_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '关系ID',
    brain_id INT NOT NULL COMMENT '产业大脑ID',
    industry_id INT NOT NULL COMMENT '行业ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    FOREIGN KEY (brain_id) REFERENCES QD_industry_brain(brain_id) ON DELETE CASCADE,
    FOREIGN KEY (industry_id) REFERENCES QD_industry(industry_id) ON DELETE CASCADE,
    UNIQUE KEY uk_brain_industry (brain_id, industry_id),
    INDEX idx_brain (brain_id),
    INDEX idx_industry (industry_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产业大脑行业关联表';

-- ============================================
-- 8. 企业信息缓存表 (company_cache)
-- ============================================
DROP TABLE IF EXISTS company_cache;
CREATE TABLE company_cache (
    cache_id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '缓存ID',
    cache_key VARCHAR(255) NOT NULL COMMENT '缓存键（标准化企业名）',
    payload TEXT NOT NULL COMMENT '缓存数据（JSON格式）',
    schema_version VARCHAR(10) DEFAULT 'v1' COMMENT '数据schema版本',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    expires_at TIMESTAMP NOT NULL COMMENT '过期时间',

    UNIQUE KEY uk_cache_key (cache_key),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='企业信息缓存表';

-- ============================================
-- 9. 插入示例数据 - 地区
-- ============================================
INSERT INTO QD_area (city_name, district_name, district_code) VALUES
('青岛市', '市南区', '370202'),
('青岛市', '市北区', '370203'),
('青岛市', '李沧区', '370213'),
('青岛市', '崂山区', '370212'),
('青岛市', '黄岛区', '370211'),
('青岛市', '城阳区', '370214'),
('青岛市', '即墨区', '370215');

-- ============================================
-- 10. 插入示例数据 - 行业
-- ============================================
INSERT INTO QD_industry (industry_name, industry_type, industry_remark) VALUES
('电子信息', '高新技术产业', '包括集成电路、电子元器件、计算机等'),
('智能家电', '制造业', '智能家电及相关产品制造'),
('生物医药', '高新技术产业', '生物制药、医疗器械等'),
('新能源汽车', '制造业', '新能源汽车及零部件'),
('纺织服装', '传统制造业', '纺织品、服装制造'),
('食品饮料', '制造业', '食品加工、饮料制造'),
('化工材料', '制造业', '化工产品、新材料'),
('机械装备', '制造业', '机械设备、工程机械'),
('海洋科技', '高新技术产业', '海洋工程、海洋资源开发'),
('现代物流', '服务业', '物流、仓储、运输'),
('软件服务', '高新技术产业', '软件开发、信息服务'),
('文化创意', '服务业', '文化传媒、创意设计'),
('金融服务', '服务业', '金融、保险、证券');

-- ============================================
-- 11. 插入示例数据 - 产业大脑
-- ============================================
INSERT INTO QD_industry_brain (brain_name, area_id, build_year, brain_remark) VALUES
('智能家电产业大脑', 1, 2022, '聚焦智能家电产业链，提供数字化服务'),
('电子信息产业大脑', 2, 2021, '服务电子信息产业，推动数字化转型'),
('海洋科技产业大脑', 5, 2022, '服务海洋经济，整合海洋科技资源'),
('新能源汽车产业大脑', 6, 2023, '新能源汽车产业链数字化平台'),
('生物医药产业大脑', 4, 2022, '生物医药产业数字化服务平台'),
('纺织服装产业大脑', 3, 2021, '纺织服装产业链数字化服务');

-- ============================================
-- 12. 插入示例数据 - 产业大脑与行业关联
-- ============================================
INSERT INTO QD_brain_industry_rel (brain_id, industry_id) VALUES
(1, 2),  -- 智能家电产业大脑 - 智能家电
(2, 1),  -- 电子信息产业大脑 - 电子信息
(2, 11), -- 电子信息产业大脑 - 软件服务
(3, 9),  -- 海洋科技产业大脑 - 海洋科技
(4, 4),  -- 新能源汽车产业大脑 - 新能源汽车
(5, 3),  -- 生物医药产业大脑 - 生物医药
(6, 5);  -- 纺织服装产业大脑 - 纺织服装

-- ============================================
-- 13. 插入示例数据 - 链主企业
-- ============================================
INSERT INTO QD_enterprise_chain_leader (enterprise_name, industry_id, area_id, enterprise_remark) VALUES
('海尔集团', 2, 4, '全球领先的智能家电企业'),
('海信集团', 1, 1, '知名电子信息企业'),
('青岛啤酒股份有限公司', 6, 1, '国内知名啤酒品牌'),
('中车青岛四方机车车辆股份有限公司', 8, 6, '轨道交通装备制造企业'),
('青岛港集团', 10, 5, '世界级港口物流企业');

-- ============================================
-- 14. 插入示例数据 - 客户企业
-- ============================================
INSERT INTO QD_customer (customer_name, address, data_source, industry_id, brain_id, chain_leader_id) VALUES
('海尔智家股份有限公司', '青岛市崂山区海尔路1号', 'manual', 2, 1, 1),
('青岛海信电器股份有限公司', '青岛市市南区东海西路17号', 'manual', 1, 2, 2),
('青岛啤酒（崂山）有限公司', '青岛市崂山区海尔路1号', 'manual', 6, NULL, 3),
('青岛中集冷藏箱制造有限公司', '青岛市黄岛区铁山工业园', 'manual', 8, NULL, NULL),
('青岛双星轮胎工业有限公司', '青岛市市北区徐州路98号', 'manual', 7, NULL, NULL),
('青岛海湾化学有限公司', '青岛市黄岛区', 'manual', 7, NULL, NULL),
('青岛软件园发展有限公司', '青岛市崂山区松岭路169号', 'manual', 11, 2, NULL),
('青岛华大基因研究院', '青岛市崂山区', 'manual', 3, 5, NULL),
('青岛特锐德电气股份有限公司', '青岛市崂山区株洲路20号', 'manual', 4, 4, NULL),
('青岛纺织集团有限公司', '青岛市李沧区', 'manual', 5, 6, NULL);

-- ============================================
-- 15. 创建视图 - 企业完整信息视图
-- ============================================
DROP VIEW IF EXISTS v_customer_full_info;
CREATE VIEW v_customer_full_info AS
SELECT
    c.customer_id,
    c.customer_name,
    c.address,
    c.data_source,
    c.tag_result,
    i.industry_id,
    i.industry_name,
    i.industry_type,
    b.brain_id,
    b.brain_name,
    e.enterprise_id AS chain_leader_id,
    e.enterprise_name AS chain_leader_name,
    a.area_id,
    a.city_name,
    a.district_name,
    c.created_at,
    c.updated_at
FROM QD_customer c
LEFT JOIN QD_industry i ON c.industry_id = i.industry_id
LEFT JOIN QD_industry_brain b ON c.brain_id = b.brain_id
LEFT JOIN QD_enterprise_chain_leader e ON c.chain_leader_id = e.enterprise_id
LEFT JOIN QD_area a ON e.area_id = a.area_id;

-- ============================================
-- 16. 创建存储过程 - 按名称查询企业
-- ============================================
DROP PROCEDURE IF EXISTS sp_get_customer_by_name;

DELIMITER //
CREATE PROCEDURE sp_get_customer_by_name(IN p_customer_name VARCHAR(255))
BEGIN
    SELECT * FROM v_customer_full_info
    WHERE customer_name = p_customer_name
    LIMIT 1;
END //
DELIMITER ;

-- ============================================
-- 17. 数据统计查询
-- ============================================
-- 查看各表数据量
SELECT 'QD_area' AS table_name, COUNT(*) AS record_count FROM QD_area
UNION ALL
SELECT 'QD_industry', COUNT(*) FROM QD_industry
UNION ALL
SELECT 'QD_industry_brain', COUNT(*) FROM QD_industry_brain
UNION ALL
SELECT 'QD_enterprise_chain_leader', COUNT(*) FROM QD_enterprise_chain_leader
UNION ALL
SELECT 'QD_customer', COUNT(*) FROM QD_customer
UNION ALL
SELECT 'QD_brain_industry_rel', COUNT(*) FROM QD_brain_industry_rel;

-- ============================================
-- 完成
-- ============================================
SELECT '数据库初始化完成！' AS status;
SELECT VERSION() AS mysql_version;
SELECT DATABASE() AS current_database;
