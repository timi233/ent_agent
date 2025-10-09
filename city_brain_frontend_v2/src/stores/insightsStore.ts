import { defineStore } from 'pinia'

import { fetchInsightSeries, type InsightResponse } from '@services/insightsService'
import { useFiltersStore } from './filtersStore'
import { extractApiError } from '@utils/error'

interface InsightsState {
  data: InsightResponse | null
  loading: boolean
  error?: string
}

export const useInsightsStore = defineStore('insights', {
  state: (): InsightsState => ({
    data: null,
    loading: false,
    error: undefined
  }),
  actions: {
    async load() {
      const filtersStore = useFiltersStore()
      this.loading = true
      this.error = undefined
      try {
        const data = await fetchInsightSeries(filtersStore.filters)
        this.data = data
      } catch (error) {
        this.error = extractApiError(error).description
      } finally {
        this.loading = false
      }
    }
  }
})
