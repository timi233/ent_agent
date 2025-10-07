<template>
  <div class="home">
    <div class="header">
      <h1>城市大脑企业信息处理系统</h1>
      <p>请输入您想了解的企业名称，我们将为您提供详细的企业信息和产业关联分析</p>
    </div>
    
    <div class="input-container">
      <el-input
        v-model="inputMessage"
        placeholder="请输入企业名称或相关信息..."
        @keyup.enter="processCompany"
        :disabled="isLoading"
        size="large"
      >
        <template #append>
          <el-button 
            type="primary" 
            @click="processCompany" 
            :loading="isLoading"
            :disabled="!inputMessage.trim() || isLoading"
            size="large"
          >
            查询企业信息
          </el-button>
        </template>
      </el-input>
      <div class="cache-toggle" style="margin-top:12px; display:flex; align-items:center; gap:10px;">
        <span style="color:#606266;">使用本地缓存</span>
        <el-switch v-model="useLocalCache" active-text="开启" inactive-text="关闭" />
      </div>
    </div>
    
    <div class="result-container" v-if="result">
      <div class="result-header">
        <h2>查询结果</h2>
        <el-button 
          type="info" 
          plain 
          @click="clearResult"
          size="small"
        >
          清空结果
        </el-button>
      </div>
      
      <div class="result-content">
        <div 
          v-if="result.status === 'success'" 
          class="success-result"
        >
          <!-- CRM 商机数据区块（上移，优先展示数据库查询结果） -->
          <div class="company-crm" v-if="!sections?.crm?.loading && !sections?.crm?.error && crmOpportunities.opportunities.length > 0">
            <h3>相关商机信息</h3>
            <div class="crm-content">
              <div class="crm-summary" v-if="crmOpportunities.pagination">
                <p class="crm-stats">
                  共找到 <strong>{{ crmOpportunities.pagination.total_count }}</strong> 条商机记录
                  <span v-if="crmOpportunities.statuses.length > 0">
                    ，状态分布：
                    <el-tag 
                      v-for="status in crmOpportunities.statuses" 
                      :key="status" 
                      size="small" 
                      style="margin-left: 5px;"
                    >
                      {{ status }}
                    </el-tag>
                  </span>
                </p>
              </div>
              
              <div class="opportunities-list">
                <div 
                  v-for="opportunity in crmOpportunities.opportunities" 
                  :key="opportunity.id"
                  class="opportunity-card"
                >
                  <div class="opportunity-header">
                    <h4 class="opportunity-name">{{ opportunity.opportunity_name || '未命名商机' }}</h4>
                    <el-tag 
                      :type="getStatusTagType(opportunity.status)" 
                      size="small"
                    >
                      {{ opportunity.status || '未知状态' }}
                    </el-tag>
                  </div>
                  
                  <div class="opportunity-details">
                    <div class="detail-row">
                      <span class="detail-label">客户名称：</span>
                      <span class="detail-value">{{ opportunity.customer_name || '暂无' }}</span>
                    </div>
                    <div class="detail-row" v-if="opportunity.description">
                      <span class="detail-label">商机描述：</span>
                      <span class="detail-value">{{ opportunity.description }}</span>
                    </div>
                    <div class="detail-row" v-if="opportunity.expected_amount_wan">
                      <span class="detail-label">预计合同额：</span>
                      <span class="detail-value amount">{{ opportunity.expected_amount_wan }} 万元</span>
                    </div>
                    <div class="detail-row" v-if="opportunity.owner_name">
                      <span class="detail-label">负责人：</span>
                      <span class="detail-value">{{ opportunity.owner_name }}</span>
                    </div>
                    <div class="detail-row" v-if="opportunity.expected_deal_date">
                      <span class="detail-label">预计交易日期：</span>
                      <span class="detail-value">{{ formatDate(opportunity.expected_deal_date) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="crm-pagination" v-if="crmOpportunities.pagination && crmOpportunities.pagination.total_pages > 1">
                <el-button 
                  size="small" 
                  @click="loadMoreOpportunities"
                  :loading="sections.crm.loading"
                  v-if="crmOpportunities.pagination.has_next"
                >
                  加载更多商机
                </el-button>
              </div>
            </div>
          </div>

          <div class="company-crm" v-else-if="sections?.crm?.loading">
            <!-- CRM 骨架占位：在 CRM 分块未就绪时显示 -->
            <h3>相关商机信息</h3>
            <el-skeleton :rows="2" animated />
          </div>

          <div class="company-crm no-data" v-else-if="!sections?.crm?.loading && !sections?.crm?.error && crmOpportunities.opportunities.length === 0">
            <!-- CRM 无数据提示 -->
            <h3>相关商机信息</h3>
            <div class="no-crm-data">
              <p>暂未找到该企业的相关商机信息</p>
            </div>
          </div>

          <div class="company-info">
            <div v-if="!sections?.info?.loading && !sections?.info?.error">
              <div class="company-info-header">
                <h3>企业信息摘要</h3>
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="showEditDialog = true"
                  :disabled="!result.data || (!result.data.customer_id && !result.data.details && !result.data.company_name)"
                >
                  修正数据
                </el-button>
              </div>
              
              <div class="info-rows">
                <!-- 第1行：企业名称 所在地区 企业地址 -->
                <div class="row">
                  <div class="cell">
                    <span class="info-label">企业名称</span>
                    <span class="info-value">{{ displayVal('name') || (result.data?.company_name || '暂无') }}</span>
                  </div>
                  <div class="cell">
                    <span class="info-label">所在地区</span>
                    <span class="info-value">{{ displayVal('district_name') }}</span>
                  </div>
                  <div class="cell">
                    <span class="info-label">企业地址</span>
                    <span class="info-value">{{ displayVal('address') }}</span>
                  </div>
                </div>
                <!-- 第2行：所属行业 企业地位 所属产业大脑 -->
                <div class="row">
                  <div class="cell">
                    <span class="info-label">所属行业</span>
                    <span class="info-value">{{ displayVal('industry') }}</span>
                  </div>
                  <div class="cell">
                    <span class="info-label">企业地位</span>
                    <span class="info-value">{{ displayVal('company_status') }}</span>
                  </div>
                  <div class="cell empty"></div>
                </div>
                <!-- 第3行：产业链 产业链状态 -->
                <div class="row">
                  <div class="cell">
                    <span class="info-label">产业链</span>
                    <span class="info-value">{{ displayVal('industry_chain') }}</span>
                  </div>
                  <div class="cell">
                    <span class="info-label">产业链状态</span>
                    <span class="info-value">{{ displayVal('chain_status') }}</span>
                  </div>
                  <div class="cell empty"></div>
                </div>
              </div>
              
              <div class="source-info" v-if="result.source">
                <p><strong>数据来源:</strong> {{ result.source === 'web_search' ? '网络搜索' : '本地数据库' }}</p>
              </div>
            </div>
            <div v-else>
              <!-- info 骨架占位：在 info 分块未就绪时显示 -->
              <el-skeleton :rows="4" animated />
            </div>
          </div>
          
          <!-- 产业大脑和产业链相关信息（数据库与结构化字段，优先展示） -->
          <div class="company-chain" v-if="displayVal('industry_brain') !== '暂无' || displayVal('industry_chain') !== '暂无' || displayVal('chain_status') !== '暂无'">
            <h3>产业大脑和产业链相关信息</h3>
            <div class="info-rows">
              <div class="row">
                <div class="cell" v-if="displayVal('industry_brain') !== '暂无'">
                  <span class="info-label">所属产业大脑</span>
                  <span class="info-value">{{ displayVal('industry_brain') }}</span>
                </div>
                <div class="cell" v-if="displayVal('industry_chain') !== '暂无'">
                  <span class="info-label">产业链</span>
                  <span class="info-value">{{ displayVal('industry_chain') }}</span>
                </div>
                <div class="cell" v-if="displayVal('chain_status') !== '暂无'">
                  <span class="info-label">产业链状态</span>
                  <span class="info-value">{{ displayVal('chain_status') }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 联网核查数据（网络返回较慢，单独分区展示） -->
          <div class="company-info" v-if="result?.data?.summary || (result?.data?.news && (result.data.news.summary || (result.data.news.references && result.data.news.references.length > 0)))">
            <h3>近三年营收情况</h3>
            <div class="info-rows">
              <div class="row full">
                <div class="cell">
                  <span class="info-label">近三年营收情况</span>
                  <span class="info-value">{{ displayVal('revenue_info') }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 企业新闻区块 -->
          <div class="company-news" v-if="!sections?.news?.loading && !sections?.news?.error && result.data && result.data.news">
            <h3>企业商业资讯</h3>
            <div class="news-content">
              <div class="news-summary" v-html="formatNewsContent(result.data.news.summary)"></div>
              <div class="news-references" v-if="result.data.news.references && result.data.news.references.length > 0">
                <h4>参考资料</h4>
                <ul class="reference-list">
                  <li 
                    v-for="(ref, index) in result.data.news.references" 
                    :key="index"
                    :id="'ref-' + (index + 1)"
                    class="reference-item"
                  >
                    <span class="reference-number">【{{ index + 1 }}】</span>
                    <a 
                      :href="ref.url" 
                      target="_blank" 
                      class="reference-link"
                      @click="trackReferenceClick(ref, index + 1)"
                    >
                      {{ ref.title }}
                    </a>
                    <span class="reference-source" v-if="ref.source">
                      - {{ ref.source }}
                    </span>
                  </li>
                </ul>
              </div>
              <div class="no-references-notice" v-else>
                <p class="notice-text">注：当前资讯为AI分析总结，如需查看原始资料，请访问相关企业官方公告或财经媒体。</p>
              </div>
            </div>
          </div>

          <div class="company-news" v-else>
            <!-- news 骨架占位：在 news 分块未就绪时显示 -->
            <el-skeleton :rows="3" animated />
          </div>


        </div>
        
        <div 
          v-else-if="result.status === 'error'" 
          class="error-result"
        >
          <h3>查询失败</h3>
          <p>{{ result.message || '抱歉，处理您的请求时出现了问题，请稍后重试。' }}</p>
        </div>
      </div>
    </div>
    
    <div class="loading-container" v-if="isLoading">
      <div class="loading-content">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>{{ loadingMessage }}</p>
      </div>
    </div>

    <!-- 修正数据对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="修正企业数据"
      width="600px"
      :before-close="handleEditDialogClose"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        label-width="120px"
        v-loading="editLoading"
      >
        <el-form-item label="企业名称">
          <el-input v-model="editForm.customer_name" disabled />
        </el-form-item>
        <el-form-item label="所属行业">
          <el-input v-model="editForm.industry_name" placeholder="请输入所属行业" />
        </el-form-item>
        <el-form-item label="产业大脑">
          <el-input v-model="editForm.brain_name" placeholder="请输入产业大脑" />
        </el-form-item>
        <el-form-item label="产业链状态">
          <el-input v-model="editForm.chain_status" placeholder="请输入产业链状态" />
        </el-form-item>
        <el-form-item label="所在地区">
          <el-input v-model="editForm.district_name" placeholder="请输入所在地区" />
        </el-form-item>
        <el-form-item label="企业地址">
          <el-input v-model="editForm.address" type="textarea" placeholder="请输入企业地址" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="submitEdit" :loading="editLoading">
            保存修正
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import { Loading } from '@element-plus/icons-vue'

export default {
  name: 'Home',
  components: {
    Loading
  },
  data() {
    return {
      inputMessage: '',
      result: null,
      isLoading: false,
      useLocalCache: true,
      loadingMessage: '正在处理您的请求...',
      showEditDialog: false,
      editLoading: false,
      editForm: {
        customer_name: '',
        industry_name: '',
        brain_name: '',
        chain_status: '',
        district_name: '',
        address: ''
      },
      sections: {
        summary: { loading: false, error: false },
        info: { loading: false, error: false },
        news: { loading: false, error: false },
        crm: { loading: false, error: false }
      },
      crmOpportunities: {
        opportunities: [],
        pagination: null,
        statuses: []
      }
    }
  },
  mounted() {
    this.loadConfig();
  },
  computed: {
    parsedSummary() {
      if (!this.result) {
        return {};
      }
      
      // 优先使用data字段中的结构化数据
      if (this.result.data) {
        const data = this.result.data;
        return {
          company_name: data.customer_name || data.company_name,
          industry: data.industry_name || data.industry,
          brain_name: data.brain_name,
          chain_status: data.chain_status,
          district_name: data.district_name,
          address: data.address,
          data_source: data.data_source
        };
      }
      
      // 如果没有data字段，尝试解析summary
      if (this.result.summary) {
        if (typeof this.result.summary === 'string') {
          try {
            return JSON.parse(this.result.summary);
          } catch (e) {
            console.error('解析summary失败:', e);
            // 如果解析失败，返回原始字符串作为单个值
            return { info: this.result.summary };
          }
        }
        return this.result.summary;
      }
      
      return {};
    },
    displayData() {
      if (!this.result) {
        return {};
      }
      
      // 优先使用 data.details 字段
      if (this.result.data && this.result.data.details) {
        const details = { ...this.result.data.details };
        // 移除标签结果字段
        delete details['标签结果'];
        return details;
      }
      
      // 如果没有 details，尝试使用 raw_details
      if (this.result.data && this.result.data.raw_details) {
        const details = { ...this.result.data.raw_details };
        delete details['标签结果'];
        return details;
      }
      
      // 如果没有 details，使用 parsedSummary
      return this.parsedSummary;
    }
  },
  watch: {
    showEditDialog(newVal) {
      if (newVal && this.result && this.result.data) {
        // 填充编辑表单
        this.editForm = {
          customer_name: this.result.data.customer_name || this.result.data.company_name || '',
          industry_name: this.result.data.industry_name || '',
          brain_name: this.result.data.brain_name || '',
          chain_status: this.result.data.chain_status || '',
          district_name: this.result.data.district_name || '',
          address: this.result.data.address || ''
        }
      }
    }
  },
  methods: {
    async loadConfig() {
      try {
        const resp = await axios.get('/api/v1/company/config');
        const val = (resp && resp.data && typeof resp.data.cache_enabled !== 'undefined') ? !!resp.data.cache_enabled : true;
        this.useLocalCache = val;
      } catch (e) {
        console.warn('读取缓存配置失败，使用默认值', e);
        this.useLocalCache = true;
      }
    },
    async processCompany() {
      if (!this.inputMessage.trim() || this.isLoading) return

      // 初始化状态
      this.isLoading = true
      this.result = null
      this.loadingMessage = '正在处理您的请求...'
      this.sections.summary = { loading: true, error: false }
      this.sections.info = { loading: true, error: false }
      this.sections.news = { loading: true, error: false }
      this.sections.crm = { loading: true, error: false }

      // 并行启动：本地快速路径 + 网络路径 + CRM 商机数据
      const localPromise = this.fetchLocalFast(this.inputMessage)
      const networkPromise = this.fetchNetwork(this.inputMessage)
      const crmPromise = this.fetchCRMOpportunities(this.inputMessage)

      // 三者完成后结束整体 loading（分块状态由各自方法独立控制）
      const settled = await Promise.allSettled([localPromise, networkPromise, crmPromise])
      console.log('并行请求完成:', settled)
      this.isLoading = false
    },
    handleProgressiveUpdate(data) {
      console.log('处理API响应数据:', data)
      
      // 更新加载消息
      if (data.message) {
        this.loadingMessage = data.message
      }

      // 直接处理完整的API响应
      if (data.status === 'success' || data.status === 'completed') {
        this.result = {
          status: 'success',
          data: {
            company_name: data.data?.company_name || data.data?.final_result?.company_name || '',
            summary: data.data?.final_result?.summary || data.data?.summary || '',
            details: data.data?.final_result?.details || data.data?.details || {},
            news: data.data?.final_result?.news || data.data?.news || { summary: '', references: [] }
          }
        }
        
        const resData = this.result.data || {}
        const hasSummary = !!(resData.summary && String(resData.summary).trim())
        const hasNews = !!(resData.news && (String(resData.news.summary || '').trim() || (resData.news.references && resData.news.references.length)))
        // 成功后公司信息先结束loading，不因details为空而阻塞展示（可使用回退字段）
        this.sections.info.loading = false
        this.sections.info.error = false
        // 摘要与新闻根据内容判断
        this.sections.summary.loading = !hasSummary
        this.sections.summary.error = false
        this.sections.news.loading = !hasNews
        this.sections.news.error = false
        console.log('设置结果数据并更新分块状态:', this.result)
        this.isLoading = false
      } else if (data.status === 'error') {
        this.result = {
          status: 'error',
          message: data.message || '处理过程中出现错误'
        }
        this.isLoading = false
      }
    },

    // 本地快速路径：优先返回基础企业信息（details/company_name）
    async fetchLocalFast(input) {
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 30000) // 30秒快速路径

        const resp = await fetch('/api/v1/company/process/progressive', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            input_text: input,
            // 使用本地缓存优先路径：开启缓存（disable_cache:false），关闭外网（enable_network:false）
            disable_cache: !this.useLocalCache ? true : false,
            enable_network: false
          }),
          signal: controller.signal
        })
        clearTimeout(timeoutId)

        if (!resp.ok) throw new Error(`Local path failed: ${resp.status}`)
        const data = await resp.json()
        console.log('local fast响应:', data)

        // 合并到 result，但只更新 info 相关字段
        this.mergeResult(data, { update: ['info'] })
        // info 分块结束 loading
        this.sections.info.loading = false
        this.sections.info.error = false
      } catch (e) {
        console.warn('本地快速路径失败:', e)
        // 只标记 info 分块失败，不影响其他分块
        this.sections.info.loading = false
        this.sections.info.error = true
      }
    },

    // 网络路径：补充摘要与新闻
    async fetchNetwork(input) {
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 120000) // 2分钟

        const resp = await fetch('/api/v1/company/process/progressive', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            input_text: input,
            // 网络路径：根据开关决定是否禁用缓存；启用外网
            disable_cache: !this.useLocalCache,
            enable_network: true
          }),
          signal: controller.signal
        })
        clearTimeout(timeoutId)

        if (!resp.ok) throw new Error(`Network path failed: ${resp.status}`)
        const data = await resp.json()
        console.log('network响应:', data)

        // 合并到 result，更新 summary 与 news（以及可能更完整的 info）
        this.mergeResult(data, { update: ['summary', 'news', 'info'] })

        // 根据内容结束分块 loading
        const d = this.result?.data || {}
        const hasSummary = !!(d.summary && String(d.summary).trim())
        const hasNews = !!(d.news && (String(d.news?.summary || '').trim() || (d.news?.references && d.news.references.length)))
        this.sections.summary.loading = !hasSummary
        this.sections.summary.error = false
        this.sections.news.loading = !hasNews
        this.sections.news.error = false
        // info 也可能获得更完整的数据
        this.sections.info.loading = false
        this.sections.info.error = false
      } catch (e) {
        console.error('网络路径失败:', e)
        this.sections.summary.loading = false
        this.sections.summary.error = true
        this.sections.news.loading = false
        this.sections.news.error = true
      }
    },

    // 结果合并器：根据服务返回结构将数据并入 result
    mergeResult(apiData, options = { update: ['info', 'summary', 'news'] }) {
      if (apiData?.message) {
        this.loadingMessage = apiData.message
      }
      const payload = apiData?.data || {}
      const final = payload.final_result || payload

      if (!this.result || this.result.status !== 'success') {
        this.result = { status: 'success', data: { company_name: '', summary: '', details: {}, news: { summary: '', references: [] } }, source: payload.source || undefined }
      }

      const target = this.result.data
      // info
      if (options.update.includes('info')) {
        target.company_name = final.company_name || target.company_name || ''
        target.details = final.details || final.raw_details || target.details || {}
      }
      // summary
      if (options.update.includes('summary')) {
        target.summary = final.summary || target.summary || ''
      }
      // news
      if (options.update.includes('news')) {
        target.news = final.news || target.news || { summary: '', references: [] }
      }
    },

    clearResult() {
      this.result = null
      this.sections.summary = { loading: false, error: false }
      this.sections.info = { loading: false, error: false }
      this.sections.news = { loading: false, error: false }
      this.sections.crm = { loading: false, error: false }
      this.crmOpportunities = {
        opportunities: [],
        pagination: null,
        statuses: []
      }
    },

    // CRM 商机数据获取
    async fetchCRMOpportunities(companyName) {
      try {
        this.sections.crm.loading = true
        this.sections.crm.error = false
        
        console.log('获取CRM商机数据:', companyName)
        
        const response = await axios.get('/api/v1/crm/opportunities', {
          params: {
            company_name: companyName,
            page: 1,
            page_size: 5
          }
        })
        
        if (response.data && response.data.opportunities) {
          this.crmOpportunities.opportunities = response.data.opportunities
          this.crmOpportunities.pagination = response.data.pagination
          
          // 获取状态列表
          try {
            const statusResponse = await axios.get('/api/v1/crm/statuses')
            if (statusResponse.data && statusResponse.data.statuses) {
              this.crmOpportunities.statuses = statusResponse.data.statuses
            }
          } catch (statusError) {
            console.warn('获取CRM状态列表失败:', statusError)
          }
          
          console.log('CRM商机数据获取成功:', this.crmOpportunities)
        }
        
        this.sections.crm.loading = false
        this.sections.crm.error = false
        
      } catch (error) {
        console.error('获取CRM商机数据失败:', error)
        this.sections.crm.loading = false
        this.sections.crm.error = true
        this.crmOpportunities = {
          opportunities: [],
          pagination: null,
          statuses: []
        }
      }
    },

    // 加载更多商机数据
    async loadMoreOpportunities() {
      if (!this.crmOpportunities.pagination || !this.crmOpportunities.pagination.has_next) {
        return
      }
      
      try {
        this.sections.crm.loading = true
        
        const nextPage = this.crmOpportunities.pagination.page + 1
        const response = await axios.get('/api/v1/crm/opportunities', {
          params: {
            company_name: this.inputMessage,
            page: nextPage,
            page_size: 5
          }
        })
        
        if (response.data && response.data.opportunities) {
          // 追加新数据
          this.crmOpportunities.opportunities.push(...response.data.opportunities)
          this.crmOpportunities.pagination = response.data.pagination
        }
        
        this.sections.crm.loading = false
        
      } catch (error) {
        console.error('加载更多商机数据失败:', error)
        this.sections.crm.loading = false
        this.$message.error('加载更多商机数据失败')
      }
    },

    // 获取状态标签类型
    getStatusTagType(status) {
      const typeMap = {
        '必签': 'success',
        '可控': 'warning', 
        '参与': 'info',
        '丢单': 'danger'
      }
      return typeMap[status] || 'info'
    },

    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return '暂无'
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('zh-CN')
      } catch (error) {
        return dateString
      }
    },
    formatLabel(key) {
      const labelMap = {
        'industry_chain': '产业链',
        'name': '企业名称',
        'company_name': '企业名称',
        'customer_name': '企业名称',
        '企业名称': '企业名称',
        'description': '企业描述',
        'website': '官方网站',
        'industry': '所属行业',
        'industry_name': '所属行业',
        '所属行业': '所属行业',
        'address': '企业地址',
        '企业地址': '企业地址',
        'contact': '联系方式',
        'brain_name': '产业大脑',
        'industry_brain': '产业大脑',
        '产业大脑': '产业大脑',
        'chain_status': '产业链状态',
        '产业链状态': '产业链状态',
        'revenue_info': '近三年营收情况',
        '近三年营收情况': '近三年营收情况',
        'company_status': '企业地位',
        '企业地位': '企业地位',
        'district_name': '所在地区',
        '所在地区': '所在地区',
        'area_name': '所在地区',
        'data_source': '数据来源',
        '数据来源': '数据来源',
        'info': '企业信息'
      }
      return labelMap[key] || key
    },
    handleEditDialogClose() {
      this.showEditDialog = false
      this.resetEditForm()
    },
    resetEditForm() {
      this.editForm = {
        customer_name: '',
        industry_name: '',
        brain_name: '',
        chain_status: '',
        district_name: '',
        address: ''
      }
    },
    async submitEdit() {
      if (!this.result.data) {
        this.$message.error('无法获取企业数据，请重新查询')
        return
      }

      this.editLoading = true
      try {
        const updates = {}
        
        // 获取当前数据，支持多种数据结构
        const currentData = this.result.data.details || this.result.data
        
        // 只提交有变化的字段
        if (this.editForm.industry_name !== (currentData.industry_name || currentData.industry || '')) {
          updates.industry_name = this.editForm.industry_name
        }
        if (this.editForm.brain_name !== (currentData.brain_name || currentData.industry_brain || '')) {
          updates.brain_name = this.editForm.brain_name
        }
        if (this.editForm.chain_status !== (currentData.chain_status || '')) {
          updates.chain_status = this.editForm.chain_status
        }
        if (this.editForm.district_name !== (currentData.district_name || currentData.region || '')) {
          updates.district_name = this.editForm.district_name
        }
        if (this.editForm.address !== (currentData.address || '')) {
          updates.address = this.editForm.address
        }

        if (Object.keys(updates).length === 0) {
          this.$message.info('没有检测到数据变化')
          this.showEditDialog = false
          return
        }

        // 构建请求数据
        const requestData = {
          updates: updates
        }

        // 如果有customer_id，使用原有的更新接口
        if (this.result.data.customer_id) {
          requestData.customer_id = this.result.data.customer_id
          
          const response = await axios.post('/api/v1/update-company', requestData)
          
          if (response.data.status === 'success') {
            this.$message.success('企业信息修正成功！')
            this.showEditDialog = false
            // 重新查询以获取最新数据
            await this.processCompany()
          } else {
            this.$message.error(response.data.message || '修正失败')
          }
        } else {
          // 对于链主企业等没有customer_id的情况，使用企业名称
          const companyName = currentData.name || currentData.company_name || currentData.customer_name || this.editForm.customer_name
          
          if (!companyName) {
            this.$message.error('无法获取企业名称，请重新查询')
            return
          }
          
          // 调用链主企业更新API
          const response = await axios.post('/api/v1/update-chain-leader-company', {
            company_name: companyName,
            updates: updates
          })
          
          if (response.data.status === 'success') {
            this.$message.success('链主企业数据修正请求已提交！')
            this.showEditDialog = false
            console.log('链主企业数据修正成功:', response.data)
          } else {
            this.$message.error(response.data.message || '链主企业数据修正失败')
          }
        }
      } catch (error) {
        console.error('修正数据失败:', error)
        if (error.response && error.response.status === 404) {
          this.$message.error('企业信息不存在，请重新查询')
        } else {
          this.$message.error('修正数据时出现错误，请稍后重试')
        }
      } finally {
        this.editLoading = false
      }
    },
    formatNewsContent(content) {
      if (!content) return ''
      // 1) 清理不可见控制字符
      let text = String(content).replace(/[\x00-\x1F\x7F-\x9F]/g, '')
      // 1.1) 移除裸露的网址，避免在摘要中出现URL（仅在引用区展示）
      text = text
        .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '$1')   // Markdown 链接 -> 文本
        .replace(/!\[([^\]]*)\]\((https?:\/\/[^\s)]+)\)/g, '$1') // Markdown 图片 -> 替换为alt文本
        .replace(/https?:\/\/[^\s)\]]+/g, '')                    // http/https 裸URL
        .replace(/\bwww\.[^\s)\]]+/g, '')                        // www. 裸URL
      // 1.2) 去除常见Markdown内联标记（粗体、斜体、行内代码、引用符）
      text = text
        .replace(/\*\*([^*]+)\*\*/g, '$1')
        .replace(/\*([^*]+)\*/g, '$1')
        .replace(/`([^`]+)`/g, '$1')
        .replace(/^>\s?/gm, '')
      // 2) 规范化：补充换行，修复标题/列表紧贴问题
      // 非行首出现的 ###/##/# 前补换行
      text = text.replace(/([^\n])###\s*/g, '$1\n### ')
      text = text.replace(/([^\n])##\s*/g, '$1\n## ')
      text = text.replace(/([^\n])#\s*/g, '$1\n# ')
      // 标题符后补空格
      text = text.replace(/(#{1,3})([^\s#])/g, '$1 $2')
      // 列表项前补换行（仅匹配以 "- " 作为列表标记）
      text = text.replace(/([^\n])\s*-\s+/g, '$1\n- ')

      // --- START: CUSTOM CLEANUP ---
      // 移除标题行中多余的 '#'
      text = text.replace(/^(#+\s*)#\s*/gm, '$1');
      // 移除只包含 '#' 的标题行
      text = text.replace(/^#+\s*#*\s*$/gm, '');
      // --- END: CUSTOM CLEANUP ---

      // 3) 将引用标记预先转换为占位，避免与列表解析冲突
      const hasReferences = this.result &&
        this.result.data &&
        this.result.data.news &&
        this.result.data.news.references &&
        this.result.data.news.references.length > 0
      if (hasReferences) {
        text = text.replace(/【(\d+)】/g, '<<REF:$1>>')
      } else {
        text = text.replace(/【(\d+)】/g, '<<REFNL:$1>>')
      }
      // 4) 标题渲染（### -> h4，##/# -> h3）
      text = text.replace(/^###\s*(.+)$/gm, '<h4>$1</h4>')
      text = text.replace(/^##\s*(.+)$/gm, '<h3>$1</h3>')
      text = text.replace(/^#\s*(.+)$/gm, '<h3>$1</h3>')
      // 5) 列表解析：把连续以 "- " 开头的行聚为一个 ul 列表
      const lines = text.split(/\n/)
      const out = []
      let inList = false
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]
        if (line.trim() === '') continue; // 忽略空行，减少 <br>

        const listMatch = /^\s*-\s+(.+)$/.exec(line)
        if (listMatch) {
          if (!inList) {
            out.push('<ul class="news-list">')
            inList = true
          }
          out.push(`<li>${listMatch[1]}</li>`)
        } else {
          if (inList) {
            out.push('</ul>')
            inList = false
          }
          out.push(line)
        }
      }
      if (inList) out.push('</ul>')
      let html = out.join('\n')
      // 5) 合并多余空行与换行渲染
      html = html.replace(/\n{2,}/g, '\n\n') // 多个换行变2个
      html = html.replace(/\n/g, '<br/>')
      // 6) 还原引用锚点/标记
      if (hasReferences) {
        html = html.replace(/<<REF:(\d+)>>/g, '<a href="#ref-$1" class="reference-anchor">【$1】</a>')
      } else {
        html = html.replace(/<<REFNL:(\d+)>>/g, '<span class="reference-marker-no-link">【$1】</span>')
      }
      // 7) 将实体标签恢复为真实 HTML（仅我们刚刚生成的标签）
      html = html
        .replace(/<ul class="news-list">/g, '<ul class="news-list">')
        .replace(/<\/ul>/g, '</ul>')
        .replace(/<li>/g, '<li>')
        .replace(/<\/li>/g, '</li>')
        .replace(/<br\/>/g, '<br/>')
        .replace(/<h4>/g, '<h4>').replace(/<\/h4>/g, '</h4>')
        .replace(/<h3>/g, '<h3>').replace(/<\/h3>/g, '</h3>')
        .replace(/<a href="#ref-(\d+)" class="reference-anchor">【\1】<\/a>/g, (_m, n) => `<a href="#ref-${n}" class="reference-anchor">【${n}】</a>`)
        .replace(/<span class="reference-marker-no-link">【(\d+)】<\/span>/g, (_m, n) => `<span class="reference-marker-no-link">【${n}】</span>`)
      
      // --- FINAL HTML CLEANUP ---
      // 1) 清理紧跟在块级元素后的 <br/>
      html = html.replace(/(<\/(h3|h4|ul)>)\s*<br\/>/g, '$1');
      // 2) 清理块级元素之前的 <br/>
      html = html.replace(/<br\/>\s*(<(h3|h4|ul)>)/g, '$1');

      // 3) 移除列表结构中的多余 <br/>：<ul> 后、<li> 后、</ul> 前
      html = html.replace(/<ul([^>]*)>\s*<br\/?>/g, '<ul$1>');      // <ul>后紧跟的<br>
      html = html.replace(/(<\/li>)\s*<br\/?>/g, '$1');              // 每个<li>后的<br>
      html = html.replace(/<br\/?>\s*<\/ul>/g, '</ul>');             // </ul>前的<br>

      // 4) 删除空项：仅包含 "- " 的列表项
      html = html.replace(/<li>\s*-\s*<\/li>/g, '');

      // 5) 删除摘要中出现的“参考来源”纯文本（引用列表单独在 news-references 中展示）
      html = html.replace(/(?:^|<br\/>)\s*参考来源\s*(?=<br\/>|$)/g, '');
      // 5.1) 若摘要中包含“参考来源”及其后续文本，整体移除以避免留白
      html = html.replace(/参考来源[\s\S]*$/g, '');

      // 6) 清理多个连续的 <br/>，保留最多一个作为分隔
      html = html.replace(/(<br\s*\/?>\s*){2,}/g, '<br/>');

      // 7) 去除摘要首尾的多余 <br/>
      html = html.replace(/^(\s*<br\/>\s*)+/, '');
      html = html.replace(/(\s*<br\/>\s*)+$/, '');
      // 7.1) 去除摘要末尾残留的短横线或空标记
      html = html.replace(/(?:<br\/>\s*)*-\s*$/g, '');

      return html
    },
    scrollToReference(refNumber) {
      const element = document.querySelector(`.reference-item:nth-child(${refNumber})`)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' })
        element.classList.add('highlight')
        setTimeout(() => {
          element.classList.remove('highlight')
        }, 2000)
      }
    },
    trackReferenceClick(reference, number) {
      console.log(`用户点击了参考资料 ${number}:`, reference.title)
      // 这里可以添加点击统计逻辑
    },
    getDetail(key) {
      try {
        return (this.result && this.result.data && this.result.data.details)
          ? this.result.data.details[key]
          : ''
      } catch (e) {
        return ''
      }
    },
    displayVal(key) {
      const v = this.getDetail(key)
      return (v === null || v === undefined || v === '') ? '暂无' : v
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  box-sizing: border-box;
}

.header {
  text-align: center;
  margin-bottom: 30px;
  color: white;
}

.header h1 {
  margin: 0 0 10px 0;
  font-size: 2.5rem;
  font-weight: 600;
}

.header p {
  margin: 0;
  font-size: 1.1rem;
  opacity: 0.9;
}

.input-container {
  max-width: 800px;
  margin: 0 auto 30px;
  background: white;
  padding: 25px;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.result-container {
  max-width: 1000px;
  margin: 0 auto 30px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.result-header {
  padding: 20px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-header h2 {
  margin: 0;
  color: #303133;
}

.result-content {
  padding: 25px;
}

.success-result {
  /* 已包含在模板中 */
}

.company-info {
  background: #f8fafc;
  border-radius: 10px;
  padding: 20px;
}

/* 结构化信息布局样式 */
.info-rows {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 15px;
}
.info-rows .row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.info-rows .row.full {
  grid-template-columns: 1fr;
}
.info-rows .cell {
  display: flex;
  flex-direction: column;
  background: white;
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}
.info-rows .cell.empty {
  background: transparent;
  border: none;
  padding: 0;
}
.info-rows .info-label {
  font-weight: bold;
  color: #606266;
  font-size: 0.9rem;
  margin-bottom: 5px;
}
.info-rows .info-value {
  color: #303133;
  word-break: break-word;
}

.company-info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.company-info-header h3 {
  margin: 0;
  color: #303133;
  border-bottom: 2px solid #e6e8eb;
  padding-bottom: 10px;
  flex: 1;
}

.company-info h3 {
  margin-top: 0;
  color: #303133;
  border-bottom: 2px solid #e6e8eb;
  padding-bottom: 10px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
  background: white;
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}

.info-label {
  font-weight: bold;
  color: #606266;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.info-value {
  color: #303133;
  word-break: break-word;
}

.source-info {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e6e8eb;
  color: #909399;
  font-style: italic;
}

.error-result {
  text-align: center;
  padding: 40px 20px;
}

.error-result h3 {
  color: #f56c6c;
  margin-bottom: 15px;
}

.error-result p {
  color: #606266;
}

.loading-container {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
  padding: 40px 20px;
}

.loading-content {
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.loading-content .el-icon {
  font-size: 40px;
  color: #409EFF;
  margin-bottom: 15px;
}

.loading-content p {
  color: #606266;
  margin: 0;
}

/* 企业新闻样式 */
.company-news {
  background: #f8fafc;
  border-radius: 10px;
  padding: 20px;
  margin-top: 20px;
}

.company-news h3 {
  margin-top: 0;
  color: #303133;
  border-bottom: 2px solid #e6e8eb;
  padding-bottom: 10px;
}

/* CRM 商机数据样式 */
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

.company-chain {
  background: #f8fafc;
  border-radius: 10px;
  padding: 20px;
  margin-top: 20px;
}

.company-chain h3 {
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
  margin-bottom: 15px;
}

.crm-stats {
  margin: 0;
  color: #606266;
  font-size: 0.95rem;
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
  font-size: 1.1rem;
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

.crm-pagination {
  text-align: center;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e6e8eb;
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

.news-content {
  margin-top: 20px;
}

.news-summary {
  background: white;
  padding: 16px;
  border-radius: 12px;
  line-height: 1.5;
  color: #303133;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  font-size: 1rem;
}

.news-summary p {
  margin: 0 0 16px 0;
}

.news-summary p:last-child {
  margin-bottom: 0;
}

.news-summary ul.news-list {
  margin: 8px 0;
  padding-left: 0;
  list-style: none;
}

.news-summary ul.news-list li {
  position: relative;
  padding: 4px 0 4px 20px;
  margin-bottom: 4px;
  color: #303133;
}

.news-summary ul.news-list li::before {
  content: "•";
  position: absolute;
  left: 8px;
  top: 6px;
  color: #409EFF;
  font-weight: bold;
  font-size: 1rem;
}

.news-summary h3, .news-summary h4 {
  margin: 12px 0 8px 0;
  color: #303133;
  font-weight: 600;
}

.news-summary h3 {
  font-size: 1.2rem;
  border-bottom: 1px solid #e6e8eb;
  padding-bottom: 6px;
}

.news-summary h4 {
  font-size: 1.1rem;
  color: #606266;
}

.reference-marker, .reference-anchor {
  color: #409EFF;
  cursor: pointer;
  text-decoration: none;
  font-weight: 600;
  background: linear-gradient(135deg, #e8f4ff 0%, #f0f9ff 100%);
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.85rem;
  transition: all 0.3s ease;
  display: inline-block;
  margin: 0 2px;
  border: 1px solid #d4edff;
}

.reference-marker:hover, .reference-anchor:hover {
  color: #ffffff;
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  text-decoration: none;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.reference-marker-no-link {
  color: #909399;
  cursor: default;
  background: #f5f5f5;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  display: inline-block;
  margin: 0 2px;
  border: 1px solid #e4e7ed;
}

.news-references {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
}

.news-references h4 {
  color: #303133;
  font-size: 1.2rem;
  margin: 0 0 20px 0;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;
}

.news-references h4::before {
  content: "📚";
  font-size: 1.3rem;
}

.reference-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 16px;
}

.reference-item {
  background: linear-gradient(135deg, #fafbfc 0%, #f8fafc 100%);
  padding: 20px;
  border-radius: 12px;
  border-left: 4px solid #e6e8eb;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
  border: 1px solid #f0f0f0;
}

.reference-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, #409EFF, #67c23a, #e6a23c);
  transform: scaleX(0);
  transition: transform 0.4s ease;
}

.reference-item:hover {
  background: linear-gradient(135deg, #f0f9ff 0%, #e8f4ff 100%);
  border-left-color: #409EFF;
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.15);
}

.reference-item:hover::before {
  transform: scaleX(1);
}

.reference-item.highlight {
  background: linear-gradient(135deg, #fff7e6 0%, #fef5e7 100%);
  border-left-color: #e6a23c;
  animation: highlight-pulse 1s ease-in-out;
}

@keyframes highlight-pulse {
  0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(230, 162, 60, 0.4); }
  50% { transform: scale(1.02); box-shadow: 0 0 0 10px rgba(230, 162, 60, 0); }
  100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(230, 162, 60, 0); }
}

.reference-number {
  color: #409EFF;
  font-weight: 700;
  margin-right: 12px;
  font-size: 0.9rem;
  background: linear-gradient(135deg, #e8f4ff 0%, #f0f9ff 100%);
  padding: 6px 10px;
  border-radius: 8px;
  display: inline-block;
  min-width: 36px;
  text-align: center;
  border: 1px solid #d4edff;
}

.reference-link {
  color: #303133;
  text-decoration: none;
  font-weight: 500;
  font-size: 1rem;
  line-height: 1.6;
  display: inline-block;
  margin-top: 4px;
  transition: color 0.3s ease;
}

.reference-link:hover {
  color: #409EFF;
  text-decoration: none;
}

.reference-source {
  color: #909399;
  font-size: 0.9rem;
  margin-left: 12px;
  font-style: italic;
  opacity: 0.8;
}

.no-references-notice {
  margin-top: 24px;
  padding: 24px;
  background: linear-gradient(135deg, #fff9e6 0%, #fef7e0 100%);
  border-radius: 12px;
  border-left: 4px solid #e6a23c;
  position: relative;
  overflow: hidden;
  border: 1px solid #f7e6a3;
}

.no-references-notice::before {
  content: "💡";
  position: absolute;
  top: 24px;
  right: 24px;
  font-size: 1.8rem;
  opacity: 0.6;
}

.no-references-notice::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 60px;
  height: 60px;
  background: radial-gradient(circle, rgba(230, 162, 60, 0.1) 0%, transparent 70%);
  border-radius: 50%;
}

.notice-text {
  margin: 0;
  color: #8b6914;
  font-size: 1rem;
  line-height: 1.7;
  font-weight: 500;
}

/* 响应式设计优化 */
@media (max-width: 768px) {
  .news-summary, .news-references, .no-references-notice {
    padding: 18px;
    margin-bottom: 18px;
  }
  
  .reference-item {
    padding: 16px;
  }
  
  .reference-number {
    padding: 4px 8px;
    font-size: 0.85rem;
    min-width: 32px;
  }
  
  .reference-link {
    font-size: 0.95rem;
  }
  
  .news-references h4 {
    font-size: 1.1rem;
  }
  
  .news-summary h3 {
    font-size: 1.1rem;
  }
  
  .news-summary h4 {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .news-summary, .news-references, .no-references-notice {
    padding: 16px;
  }
  
  .reference-item {
    padding: 14px;
  }
  
  .news-references h4::before {
    font-size: 1.1rem;
  }
  
  .no-references-notice::before {
    font-size: 1.5rem;
    top: 16px;
    right: 16px;
  }
}

@media (max-width: 768px) {
  .home {
    padding: 10px;
  }

  .header h1 {
    font-size: 2rem;
  }

  .header p {
    font-size: 1rem;
  }

  .input-container,
  .result-container {
    padding: 15px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .result-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>
