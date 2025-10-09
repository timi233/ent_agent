<template>
  <div class="dashboard">
    <!-- 搜索区域 -->
    <section class="dashboard__search">
      <BaseCard title="企业信息查询">
        <div class="search-box">
          <input
            v-model="searchInput"
            type="text"
            placeholder="请输入企业名称，例如：临工重机"
            class="search-input"
            @keyup.enter="handleSearch"
          />
          <button
            class="search-button"
            :disabled="loading || !searchInput.trim()"
            @click="handleSearch"
          >
            {{ loading ? '查询中...' : '查询' }}
          </button>
        </div>
      </BaseCard>
    </section>

    <!-- 结果展示区域 -->
    <div v-if="result" class="dashboard__results">
      <!-- 企业基本信息 KPI 卡片 -->
      <section class="dashboard__kpis" role="list">
        <KpiCard
          v-if="result.details.name"
          role="listitem"
          label="企业名称"
          :value="result.details.name"
          unit=""
        />
        <KpiCard
          v-if="result.details.industry"
          role="listitem"
          label="所属行业"
          :value="result.details.industry"
          unit=""
        />
        <KpiCard
          v-if="result.details.region"
          role="listitem"
          label="所在地区"
          :value="result.details.region"
          unit=""
        />
        <KpiCard
          v-if="result.details.industry_brain"
          role="listitem"
          label="产业大脑"
          :value="result.details.industry_brain"
          unit=""
        />
      </section>

      <!-- 详细信息卡片 -->
      <div class="dashboard__grid">
        <BaseCard title="企业详情" :loading="loading">
          <div class="company-details">
            <div v-if="result.details.address" class="detail-item">
              <span class="detail-label">详细地址：</span>
              <span class="detail-value">{{ result.details.address }}</span>
            </div>
            <div v-if="result.details.chain_status" class="detail-item">
              <span class="detail-label">产业链状态：</span>
              <span class="detail-value">{{ result.details.chain_status }}</span>
            </div>
            <div v-if="result.details.revenue_info" class="detail-item">
              <span class="detail-label">营收信息：</span>
              <span class="detail-value">{{ result.details.revenue_info }}</span>
            </div>
            <div v-if="result.details.company_status" class="detail-item">
              <span class="detail-label">企业地位：</span>
              <span class="detail-value">{{ result.details.company_status }}</span>
            </div>
            <div v-if="result.details.data_source" class="detail-item">
              <span class="detail-label">数据来源：</span>
              <span class="detail-value">{{ result.details.data_source }}</span>
            </div>
          </div>
        </BaseCard>

        <BaseCard title="AI 智能摘要" :loading="loading">
          <div class="ai-summary">
            {{ result.structured_summary || '暂无摘要信息' }}
          </div>
        </BaseCard>
      </div>

      <!-- 新闻资讯 -->
      <BaseCard
        v-if="result.web_search_info?.summary"
        title="相关资讯"
        :loading="loading"
      >
        <div class="news-info">
          <p class="news-summary">{{ result.web_search_info.summary }}</p>
          <div v-if="result.web_search_info.references?.length" class="news-references">
            <h4>参考来源：</h4>
            <ul>
              <li v-for="(ref, index) in result.web_search_info.references" :key="index">
                <a :href="ref" target="_blank" rel="noopener noreferrer">{{ ref }}</a>
              </li>
            </ul>
          </div>
        </div>
      </BaseCard>

      <!-- 商机/工单数据 -->
      <div v-if="oppResult && oppResult.summary.total_count > 0" class="dashboard__opportunities">
        <h3 class="section-title">
          关联数据
          <span class="count-badge">{{ oppResult.summary.total_count }} 条记录</span>
        </h3>

        <!-- AS商机 -->
        <BaseCard v-if="oppResult.data.as_opportunities.length > 0" title="AS商机" :loading="oppLoading">
          <div class="opportunities-grid">
            <OpportunityCard
              v-for="opp in oppResult.data.as_opportunities"
              :key="'as-' + opp.id"
              :title="opp.product_name || opp.customer_name"
              :status="opp.statename || opp.status"
              :badge="{ text: 'AS系统', type: 'as' }"
            >
              <div class="opp-detail-row" v-if="opp.customer_name">
                <span class="label">客户：</span>{{ opp.customer_name }}
              </div>
              <div class="opp-detail-row" v-if="opp.partner_name">
                <span class="label">合作伙伴：</span>{{ opp.partner_name }}
              </div>
              <div class="opp-detail-row" v-if="opp.budget">
                <span class="label">预算：</span>{{ opp.budget.toLocaleString() }} 元
              </div>
              <div class="opp-detail-row" v-if="opp.area || opp.areaname">
                <span class="label">地区：</span>{{ opp.areaname || opp.area }}
              </div>
              <template #footer v-if="opp.expected_close_date">
                预计成交：{{ opp.expected_close_date }}
              </template>
            </OpportunityCard>
          </div>
        </BaseCard>

        <!-- IPG客户 -->
        <BaseCard v-if="oppResult.data.ipg_clients.length > 0" title="IPG客户" :loading="oppLoading">
          <div class="opportunities-grid">
            <OpportunityCard
              v-for="client in oppResult.data.ipg_clients"
              :key="'ipg-' + client.id"
              :title="client.client_name"
              :status="client.status"
              :badge="{ text: 'IPG系统', type: 'ipg' }"
            >
              <div class="opp-detail-row" v-if="client.trade">
                <span class="label">行业：</span>{{ client.trade }}
              </div>
              <div class="opp-detail-row" v-if="client.reseller_name">
                <span class="label">代理商：</span>{{ client.reseller_name }}
              </div>
              <div class="opp-detail-row" v-if="client.location_province">
                <span class="label">省份：</span>{{ client.location_province }}
              </div>
              <div class="opp-detail-row" v-if="client.agent_num">
                <span class="label">代理数：</span>{{ client.agent_num }}
              </div>
              <template #footer v-if="client.contact">
                联系人：{{ client.contact }}
              </template>
            </OpportunityCard>
          </div>
        </BaseCard>

        <!-- 企业档案 -->
        <BaseCard v-if="oppResult.data.qd_enterprises.length > 0" title="企业档案" :loading="oppLoading">
          <div class="opportunities-grid">
            <OpportunityCard
              v-for="ent in oppResult.data.qd_enterprises"
              :key="'qd-' + ent.name"
              :title="ent.name"
              :badge="{ text: '企业档案', type: 'qd' }"
            >
              <div class="opp-detail-row" v-if="ent.industry">
                <span class="label">行业：</span>{{ ent.industry }}
              </div>
              <div class="opp-detail-row" v-if="ent.region">
                <span class="label">地区：</span>{{ ent.region }}
              </div>
              <div class="opp-detail-row" v-if="ent.revenue_2023 || ent.revenue_2022">
                <span class="label">营收：</span>
                {{ (ent.revenue_2023 || ent.revenue_2022)?.toLocaleString() }} 万元
                ({{ ent.revenue_2023 ? '2023' : '2022' }})
              </div>
              <div class="opp-detail-row" v-if="ent.ranking_description">
                <span class="label">排名：</span>{{ ent.ranking_description }}
              </div>
              <template #footer v-if="ent.business_summary">
                {{ ent.business_summary.substring(0, 50) }}{{ ent.business_summary.length > 50 ? '...' : '' }}
              </template>
            </OpportunityCard>
          </div>
        </BaseCard>

        <!-- 工单记录 -->
        <BaseCard v-if="oppResult.data.work_orders.length > 0" title="服务工单" :loading="oppLoading">
          <div class="opportunities-grid">
            <OpportunityCard
              v-for="order in oppResult.data.work_orders"
              :key="'wo-' + order.record_id"
              :title="order.workflow_name || '服务工单'"
              :status="order.status"
              :badge="{ text: '工单', type: 'work-order' }"
            >
              <div class="opp-detail-row" v-if="order.customer_company">
                <span class="label">客户：</span>{{ order.customer_company }}
              </div>
              <div class="opp-detail-row" v-if="order.work_type">
                <span class="label">类型：</span>{{ order.work_type }}
              </div>
              <div class="opp-detail-row" v-if="order.priority">
                <span class="label">优先级：</span>{{ order.priority }}
              </div>
              <div class="opp-detail-row" v-if="order.work_content">
                <span class="label">内容：</span>{{ order.work_content.substring(0, 40) }}...
              </div>
              <template #footer v-if="order.after_sales_engineer_primary_name">
                工程师：{{ order.after_sales_engineer_primary_name }}
              </template>
            </OpportunityCard>
          </div>
        </BaseCard>
      </div>
    </div>

    <!-- 空状态 -->
    <BaseEmptyState
      v-else-if="!loading"
      title="请输入企业名称开始查询"
      description="支持查询企业的基本信息、行业分析、AI 智能摘要等"
      icon="🔍"
    />

    <!-- 错误提示 -->
    <BaseCard v-if="error" title="查询失败">
      <div class="error-message">{{ error }}</div>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { storeToRefs } from 'pinia'

import BaseCard from '@components/base/BaseCard.vue'
import BaseEmptyState from '@components/base/BaseEmptyState.vue'
import KpiCard from '@components/data/KpiCard.vue'
import OpportunityCard from '@components/data/OpportunityCard.vue'
import { useCompanyStore } from '@stores/companyStore'
import { useOpportunitiesStore } from '@stores/opportunitiesStore'

const companyStore = useCompanyStore()
const opportunitiesStore = useOpportunitiesStore()

const { result, loading, error } = storeToRefs(companyStore)
const { searchResult: oppResult, loading: oppLoading } = storeToRefs(opportunitiesStore)

const searchInput = ref('')

const handleSearch = async () => {
  if (!searchInput.value.trim()) return

  // 查询企业基本信息
  await companyStore.searchCompany(searchInput.value.trim())

  // 同时查询商机/工单数据
  if (result.value?.company_name) {
    await opportunitiesStore.searchOpportunities(result.value.company_name, 5)
  }
}

// 监听企业查询结果，自动触发商机查询
watch(result, (newResult) => {
  if (newResult?.company_name) {
    opportunitiesStore.searchOpportunities(newResult.company_name, 5)
  }
})
</script>

<style scoped lang="scss">
.dashboard {
  display: grid;
  gap: 24px;
}

.dashboard__search {
  margin-bottom: 8px;
}

.search-box {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid rgba(31, 60, 136, 0.2);
  border-radius: var(--radius-md);
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s;

  &:focus {
    border-color: rgba(31, 60, 136, 0.5);
  }
}

.search-button {
  padding: 12px 32px;
  background: rgba(31, 60, 136, 0.9);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;

  &:hover:not(:disabled) {
    background: rgba(31, 60, 136, 1);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.dashboard__kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.dashboard__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
}

.company-details {
  display: grid;
  gap: 16px;
}

.detail-item {
  display: flex;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(31, 60, 136, 0.1);

  &:last-child {
    border-bottom: none;
  }
}

.detail-label {
  font-weight: 600;
  color: var(--color-neutral-700);
  min-width: 120px;
}

.detail-value {
  color: var(--color-neutral-900);
}

.ai-summary {
  padding: 16px;
  background: rgba(31, 60, 136, 0.05);
  border-radius: var(--radius-md);
  line-height: 1.8;
  color: var(--color-neutral-800);
  white-space: pre-wrap;
}

.news-info {
  display: grid;
  gap: 16px;
}

.news-summary {
  line-height: 1.8;
  color: var(--color-neutral-800);
}

.news-references {
  h4 {
    font-size: 14px;
    color: var(--color-neutral-700);
    margin-bottom: 8px;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;

    li {
      padding: 4px 0;

      a {
        color: rgba(31, 60, 136, 0.8);
        text-decoration: none;
        font-size: 14px;

        &:hover {
          text-decoration: underline;
        }
      }
    }
  }
}

.error-message {
  padding: 16px;
  background: rgba(220, 38, 38, 0.1);
  border-radius: var(--radius-md);
  color: #dc2626;
}

.dashboard__opportunities {
  margin-top: 32px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-neutral-900);
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.count-badge {
  font-size: 14px;
  font-weight: 500;
  padding: 4px 12px;
  background: rgba(31, 60, 136, 0.1);
  color: rgba(31, 60, 136, 0.8);
  border-radius: 999px;
}

.opportunities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.opp-detail-row {
  font-size: 14px;
  color: var(--color-neutral-700);
  margin-bottom: 6px;

  &:last-child {
    margin-bottom: 0;
  }

  .label {
    font-weight: 600;
    color: var(--color-neutral-600);
    margin-right: 4px;
  }
}
</style>
