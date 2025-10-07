# 城市大脑企业信息处理系统方案

## 系统概述
本系统旨在处理用户输入的企业信息，通过提取公司名称并结合本地数据库和联网搜索，生成企业及其关联产业信息的结构化总结。

## 数据库结构说明

### 核心数据表
1. **QD_customer** (客户企业表) - 存储企业基本信息
   - customer_id: 企业ID (主键)
   - customer_name: 企业名称
   - data_source: 数据来源
   - address: 企业地址
   - tag_result: 标记结果
   - industry_id: 关联行业ID (外键)
   - brain_id: 关联产业大脑ID (外键)
   - chain_leader_id: 关联链主企业ID (外键)

2. **QD_area** (地区表) - 存储地区信息
   - area_id: 地区ID (主键)
   - city_name: 城市名称
   - district_name: 区县名称
   - district_code: 区县代码

3. **QD_industry** (行业表) - 存储行业信息
   - industry_id: 行业ID (主键)
   - industry_name: 行业名称
   - industry_type: 行业类型
   - industry_remark: 行业备注

4. **QD_industry_brain** (产业大脑表) - 存储产业大脑信息
   - brain_id: 产业大脑ID (主键)
   - brain_name: 产业大脑名称
   - area_id: 关联地区ID (外键)
   - build_year: 建设年份
   - brain_remark: 产业大脑备注

5. **QD_enterprise_chain_leader** (链主企业表) - 存储链主企业信息
   - enterprise_id: 企业ID (主键)
   - enterprise_name: 企业名称
   - area_id: 关联地区ID (外键)
   - industry_id: 关联行业ID (外键)
   - enterprise_remark: 企业备注

6. **QD_brain_industry_rel** (产业大脑行业关联表) - 产业大脑与行业的关联关系
   - rel_id: 关联ID (主键)
   - brain_id: 产业大脑ID (外键)
   - industry_id: 行业ID (外键)

## 数据处理流程

### 1. 用户输入与公司名称提取
- 接收用户输入信息，通过文本提取工具（如正则匹配或 NLP 模型）识别并提取公司名称
- 若未提取到公司名称，提示用户补充相关信息

### 2. 本地数据库检索判断
- 使用提取的公司名称查询本地数据库QD_customer表
- 存在本地数据时，执行步骤 3；不存在时，执行步骤 5

### 3. 本地数据查询与验证
- 从QD_customer表提取本地数据库中该公司的基础信息：
  - 企业名称、地址、数据来源等
- 通过industry_id关联QD_industry表获取：
  - 所属行业、行业类型、行业备注等
- 通过brain_id关联QD_industry_brain表获取：
  - 产业大脑信息、建设年份、关联地区等
- 通过chain_leader_id关联QD_enterprise_chain_leader表获取：
  - 链主企业信息、关联行业、关联地区等
- 通过area_id关联QD_area表获取：
  - 企业所在城市、区县等地区信息

### 4. 本地数据处理分支
#### 4.1 若所有基础信息和关联信息均完整：
- 将全部数据提交至 LLM，生成结构化总结
- 输出总结结果给用户

#### 4.2 若存在信息缺失：
- 记录缺失字段，通过联网搜索补充缺失信息
- 将完整数据提交至 LLM 格式化处理
- 更新本地数据库（补充缺失字段及关联信息）
- 返回步骤 2 重新执行本地数据库检索

### 5. 无本地数据处理流程
- 联网搜索该公司的基础信息（最近三年营收、人员规模等）
- 根据公司所属地区，联网获取对应地区的产业信息、链主企业信息、产业大脑信息并建立关联
- 将全部信息提交至 LLM 格式化处理
- 将完整数据录入本地数据库的相应表中：
  - QD_customer: 存储企业基本信息
  - QD_industry: 存储行业信息（如不存在）
  - QD_industry_brain: 存储产业大脑信息（如不存在）
  - QD_enterprise_chain_leader: 存储链主企业信息（如不存在）
  - QD_area: 存储地区信息（如不存在）
  - QD_brain_industry_rel: 存储产业大脑与行业的关联关系（如不存在）
- 返回步骤 2 重新执行本地数据库检索

## 数据库统计信息
- 客户企业数量: 261家
- 行业数量: 13个
- 地区数量: 5个 (均为青岛市下辖区县)
- 产业大脑数量: 6个
- 链主企业数量: 62家
- 产业大脑与行业关联关系: 15个