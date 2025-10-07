<template>
  <div class="opportunities-section">
    <!-- 加载中 -->
    <div class="company-crm" v-if="loading">
      <h3>相关商机信息</h3>
      <el-skeleton :rows="2" animated />
    </div>

    <!-- 有数据 -->
    <div class="company-crm" v-else-if="!loading && !error && totalCount > 0">
      <h3>相关商机信息</h3>
      <div class="crm-content">
        <!-- 统计摘要 -->
        <div class="crm-summary">
          <p class="crm-stats">
            共找到 <strong>{{ totalCount }}</strong> 条记录
            <span v-if="asOpportunities.length > 0">
              <el-tag type="success" size="small" style="margin-left: 8px;">
                AS系统: {{ asOpportunities.length }}条
              </el-tag>
            </span>
            <span v-if="ipgClients.length > 0">
              <el-tag type="warning" size="small" style="margin-left: 5px;">
                IPG系统: {{ ipgClients.length }}条
              </el-tag>
            </span>
            <span v-if="qdEnterprises.length > 0">
              <el-tag type="primary" size="small" style="margin-left: 5px;">
                企业档案: {{ qdEnterprises.length }}条
              </el-tag>
            </span>
            <span v-if="workOrders.length > 0">
              <el-tag type="danger" size="small" style="margin-left: 5px;">
                相关工单: {{ workOrders.length }}条
              </el-tag>
            </span>
          </p>
        </div>

        <!-- AS系统商机列表 -->
        <div class="system-section" v-if="asOpportunities.length > 0">
          <h4 class="system-title">
            <span class="system-badge as-badge">AS</span>
            AS系统商机 ({{ asOpportunities.length }}条)
          </h4>
          <div class="opportunities-list">
            <div
              v-for="opp in asOpportunities"
              :key="'as-' + opp.id"
              class="opportunity-card"
            >
              <div class="opportunity-header">
                <h5 class="opportunity-name">{{ opp.customer_name || '未命名商机' }}</h5>
                <el-tag
                  :type="getStatusTagType(opp.statename)"
                  size="small"
                >
                  {{ opp.statename || opp.status || '未知状态' }}
                </el-tag>
              </div>

              <div class="opportunity-details">
                <div class="detail-row" v-if="opp.product_name">
                  <span class="detail-label">产品名称：</span>
                  <span class="detail-value">{{ opp.product_name }}</span>
                </div>
                <div class="detail-row" v-if="opp.budget">
                  <span class="detail-label">预算金额：</span>
                  <span class="detail-value amount">{{ opp.budget }} 万元</span>
                </div>
                <div class="detail-row" v-if="opp.partner_name">
                  <span class="detail-label">合作伙伴：</span>
                  <span class="detail-value">{{ opp.partner_name }}</span>
                </div>
                <div class="detail-row" v-if="opp.area">
                  <span class="detail-label">所属地区：</span>
                  <span class="detail-value">{{ opp.area }}</span>
                </div>
                <div class="detail-row" v-if="opp.contact_person || opp.mobile">
                  <span class="detail-label">联系方式：</span>
                  <span class="detail-value">
                    {{ opp.contact_person || '' }}
                    {{ opp.mobile ? '(' + opp.mobile + ')' : '' }}
                  </span>
                </div>
                <div class="detail-row" v-if="opp.create_time">
                  <span class="detail-label">创建时间：</span>
                  <span class="detail-value">{{ formatDate(opp.create_time) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- IPG系统商机列表 -->
        <div class="system-section" v-if="ipgClients.length > 0">
          <h4 class="system-title">
            <span class="system-badge ipg-badge">IPG</span>
            IPG系统客户商机 ({{ ipgClients.length }}条)
          </h4>
          <div class="opportunities-list">
            <div
              v-for="client in ipgClients"
              :key="'ipg-' + client.id"
              class="opportunity-card"
            >
              <div class="opportunity-header">
                <h5 class="opportunity-name">{{ client.client_name || '未命名客户' }}</h5>
                <el-tag
                  :type="getStatusTagType(client.status)"
                  size="small"
                >
                  {{ client.status || '未知状态' }}
                </el-tag>
              </div>

              <div class="opportunity-details">
                <div class="detail-row" v-if="client.sell_product">
                  <span class="detail-label">销售产品：</span>
                  <span class="detail-value">{{ client.sell_product }}</span>
                </div>
                <div class="detail-row" v-if="client.agent_num">
                  <span class="detail-label">授权点数：</span>
                  <span class="detail-value amount">{{ client.agent_num }} 点</span>
                </div>
                <div class="detail-row" v-if="client.reseller_name">
                  <span class="detail-label">代理商：</span>
                  <span class="detail-value">{{ client.reseller_name }}</span>
                </div>
                <div class="detail-row" v-if="client.trade || client.trade2">
                  <span class="detail-label">所属行业：</span>
                  <span class="detail-value">{{ client.trade }}{{ client.trade2 ? ' / ' + client.trade2 : '' }}</span>
                </div>
                <div class="detail-row" v-if="client.location_province || client.location_city">
                  <span class="detail-label">所在地区：</span>
                  <span class="detail-value">
                    {{ client.location_province }}{{ client.location_city ? ' ' + client.location_city : '' }}
                  </span>
                </div>
                <div class="detail-row" v-if="client.contact || client.contact_phone">
                  <span class="detail-label">联系方式：</span>
                  <span class="detail-value">
                    {{ client.contact || '' }}
                    {{ client.contact_phone ? '(' + client.contact_phone + ')' : '' }}
                  </span>
                </div>
                <div class="detail-row" v-if="client.faith_in">
                  <span class="detail-label">成交信心：</span>
                  <span class="detail-value" :class="'faith-' + client.faith_in">{{ client.faith_in }}</span>
                </div>
                <div class="detail-row" v-if="client.create_time">
                  <span class="detail-label">创建时间：</span>
                  <span class="detail-value">{{ formatDate(client.create_time) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- QD企业档案列表 -->
        <div class="system-section" v-if="qdEnterprises.length > 0">
          <h4 class="system-title">
            <span class="system-badge qd-badge">青岛</span>
            企业档案
          </h4>
          <div class="opportunities-list">
            <div
              v-for="enterprise in qdEnterprises"
              :key="'qd-' + enterprise.name"
              class="opportunity-card"
            >
              <div class="opportunity-header">
                <h5 class="opportunity-name">{{ enterprise.name || '未命名企业' }}</h5>
                <el-tag type="info" size="small">企业档案</el-tag>
              </div>

              <div class="opportunity-details">
                <div class="detail-row" v-if="enterprise.industry">
                  <span class="detail-label">所属行业：</span>
                  <span class="detail-value">{{ enterprise.industry }}</span>
                </div>
                <div class="detail-row" v-if="enterprise.address">
                  <span class="detail-label">企业地址：</span>
                  <span class="detail-value">{{ enterprise.address }}</span>
                </div>
                <div class="detail-row" v-if="enterprise.region">
                  <span class="detail-label">所在地区：</span>
                  <span class="detail-value">{{ enterprise.region }}</span>
                </div>
                <div class="detail-row" v-if="enterprise.employee_scale">
                  <span class="detail-label">员工规模：</span>
                  <span class="detail-value">{{ enterprise.employee_scale }}</span>
                </div>
                <div class="detail-row" v-if="enterprise.business_summary">
                  <span class="detail-label">业务概况：</span>
                  <span class="detail-value">{{ enterprise.business_summary }}</span>
                </div>
                <div class="detail-row" v-if="enterprise.ranking_description">
                  <span class="detail-label">行业地位：</span>
                  <span class="detail-value">{{ enterprise.ranking_description }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">近三年营收：</span>
                  <span class="detail-value">{{ getRevenueInfo(enterprise) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 工单列表 -->
        <div class="system-section" v-if="workOrders.length > 0">
          <h4 class="system-title">
            <span class="system-badge work-order-badge">工单</span>
            相关工单数据
          </h4>
          <div class="opportunities-list">
            <div
              v-for="order in workOrders"
              :key="'work-order-' + order.record_id"
              class="opportunity-card"
            >
              <div class="opportunity-header">
                <h5 class="opportunity-name">{{ order.customer_company || '未命名客户' }}</h5>
                <el-tag
                  :type="getStatusTagType(order.status)"
                  size="small"
                >
                  {{ order.status || '未知状态' }}
                </el-tag>
              </div>

              <div class="opportunity-details">
                <div class="detail-row" v-if="order.application_no">
                  <span class="detail-label">申请单号：</span>
                  <span class="detail-value">{{ order.application_no }}</span>
                </div>
                <div class="detail-row" v-if="order.work_type">
                  <span class="detail-label">工单类型：</span>
                  <span class="detail-value">{{ order.work_type }}</span>
                </div>
                <div class="detail-row" v-if="order.work_content">
                  <span class="detail-label">工作内容：</span>
                  <span class="detail-value">{{ order.work_content }}</span>
                </div>
                <div class="detail-row" v-if="order.customer_contact || order.customer_phone_secondary">
                  <span class="detail-label">客户联系：</span>
                  <span class="detail-value">
                    {{ order.customer_contact || '' }}
                    {{ order.customer_phone_secondary ? '(' + order.customer_phone_secondary + ')' : '' }}
                  </span>
                </div>
                <div class="detail-row" v-if="order.service_start_date">
                  <span class="detail-label">服务开始：</span>
                  <span class="detail-value">{{ formatDate(order.service_start_date) }}</span>
                </div>
                <div class="detail-row" v-if="order.after_sales_engineer_primary_name">
                  <span class="detail-label">服务工程师：</span>
                  <span class="detail-value">{{ order.after_sales_engineer_primary_name }}</span>
                </div>
                <div class="detail-row" v-if="order.priority">
                  <span class="detail-label">优先级：</span>
                  <span class="detail-value">{{ order.priority }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 无数据 -->
    <div class="company-crm no-data" v-else-if="!loading && !error && totalCount === 0">
      <h3>相关商机信息</h3>
      <div class="no-crm-data">
        <p>暂未找到该企业的相关商机信息</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OpportunitiesSection',
  props: {
    asOpportunities: {
      type: Array,
      default: () => []
    },
    ipgClients: {
      type: Array,
      default: () => []
    },
    qdEnterprises: {
      type: Array,
      default: () => []
    },
    workOrders: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    totalCount() {
      return this.asOpportunities.length + this.ipgClients.length + this.qdEnterprises.length + this.workOrders.length
    }
  },
  methods: {
    getRevenueInfo(enterprise) {
      // 检查是否有营收数据
      const hasRevenue2021 = enterprise.revenue_2021 && enterprise.revenue_2021 !== null
      const hasRevenue2022 = enterprise.revenue_2022 && enterprise.revenue_2022 !== null
      const hasRevenue2023 = enterprise.revenue_2023 && enterprise.revenue_2023 !== null

      if (!hasRevenue2021 && !hasRevenue2022 && !hasRevenue2023) {
        return '暂无相关数据'
      }

      // 构建营收信息字符串
      const revenues = []
      if (hasRevenue2021) revenues.push(`2021年: ${enterprise.revenue_2021}万元`)
      if (hasRevenue2022) revenues.push(`2022年: ${enterprise.revenue_2022}万元`)
      if (hasRevenue2023) revenues.push(`2023年: ${enterprise.revenue_2023}万元`)

      return revenues.join('；')
    },
    getStatusTagType(status) {
      if (!status) return 'info'

      const statusStr = String(status).toLowerCase()

      // AS系统状态
      if (statusStr.includes('成功') || statusStr.includes('已提交')) return 'success'
      if (statusStr.includes('审核') || statusStr.includes('待')) return 'warning'
      if (statusStr.includes('失败') || statusStr.includes('拒绝')) return 'danger'

      // IPG系统状态
      if (statusStr.includes('报备成功')) return 'success'
      if (statusStr.includes('初期') || statusStr.includes('沟通')) return 'info'
      if (statusStr.includes('必签')) return 'success'
      if (statusStr.includes('可控')) return 'warning'
      if (statusStr.includes('丢单')) return 'danger'

      return 'info'
    },
    formatDate(dateString) {
      if (!dateString) return '暂无'
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        })
      } catch (error) {
        return dateString
      }
    }
  }
}
</script>

<style scoped>
.opportunities-section {
  width: 100%;
}

.company-crm {
  background: #f8fafc;
  border-radius: 10px;
  padding: 20px;
  margin-top: 20px;
}

.company-crm h3 {
  margin-top: 0;
  color: #303133;
  border-bottom: 2px solid #e6e8eb;
  padding-bottom: 10px;
}

.company-crm.no-data {
  text-align: center;
}

.crm-content {
  margin-top: 15px;
}

.crm-summary {
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.crm-stats {
  margin: 0;
  color: #606266;
  font-size: 0.95rem;
}

.system-section {
  margin-bottom: 25px;
}

.system-section:last-child {
  margin-bottom: 0;
}

.system-title {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.system-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.as-badge {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: white;
}

.ipg-badge {
  background: linear-gradient(135deg, #e6a23c 0%, #f0b659 100%);
  color: white;
}

.qd-badge {
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  color: white;
}

.opportunities-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.opportunity-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  border-left: 4px solid #409EFF;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.opportunity-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.opportunity-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 10px;
}

.opportunity-name {
  margin: 0;
  color: #303133;
  font-size: 1.05rem;
  font-weight: 600;
  flex: 1;
  line-height: 1.4;
}

.opportunity-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.detail-label {
  font-weight: 500;
  color: #606266;
  font-size: 0.9rem;
  min-width: 80px;
  flex-shrink: 0;
}

.detail-value {
  color: #303133;
  font-size: 0.9rem;
  flex: 1;
  word-break: break-word;
}

.detail-value.amount {
  color: #e6a23c;
  font-weight: 600;
}

.detail-value.faith-高 {
  color: #67c23a;
  font-weight: 600;
}

.detail-value.faith-中 {
  color: #e6a23c;
  font-weight: 600;
}

.detail-value.faith-低 {
  color: #f56c6c;
  font-weight: 600;
}

.no-crm-data {
  text-align: center;
  padding: 30px 20px;
  color: #909399;
}

.no-crm-data p {
  margin: 0;
  font-style: italic;
}

.work-order-badge {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
  color: white;
}
</style>
