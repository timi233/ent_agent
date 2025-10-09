import { defineStore } from 'pinia'
import { searchAllOpportunities } from '@services/opportunitiesService'
import type { OpportunitiesSearchResponse } from '../types/opportunities'
import { extractApiError } from '@utils/error'

interface OpportunitiesState {
  searchResult: OpportunitiesSearchResponse | null
  loading: boolean
  error?: string
}

export const useOpportunitiesStore = defineStore('opportunities', {
  state: (): OpportunitiesState => ({
    searchResult: null,
    loading: false,
    error: undefined
  }),

  getters: {
    /**
     * 是否有查询结果
     */
    hasResults: (state): boolean => {
      return state.searchResult !== null && state.searchResult.summary.total_count > 0
    },

    /**
     * AS商机数量
     */
    asCount: (state): number => {
      return state.searchResult?.summary.as_count || 0
    },

    /**
     * IPG客户数量
     */
    ipgCount: (state): number => {
      return state.searchResult?.summary.ipg_count || 0
    },

    /**
     * 企业档案数量
     */
    qdCount: (state): number => {
      return state.searchResult?.summary.qd_count || 0
    },

    /**
     * 工单数量
     */
    workOrderCount: (state): number => {
      return state.searchResult?.summary.work_order_count || 0
    },

    /**
     * 总记录数
     */
    totalCount: (state): number => {
      return state.searchResult?.summary.total_count || 0
    }
  },

  actions: {
    /**
     * 搜索企业相关的所有商机/工单数据
     * @param companyName 企业名称
     * @param limitPerSource 每个数据源返回的结果数量
     */
    async searchOpportunities(companyName: string, limitPerSource: number = 10) {
      this.loading = true
      this.error = undefined

      try {
        const data = await searchAllOpportunities(companyName, limitPerSource)
        this.searchResult = data
      } catch (error) {
        this.error = extractApiError(error).description
        this.searchResult = null
      } finally {
        this.loading = false
      }
    },

    /**
     * 清空查询结果
     */
    clearResults() {
      this.searchResult = null
      this.error = undefined
    }
  }
})
