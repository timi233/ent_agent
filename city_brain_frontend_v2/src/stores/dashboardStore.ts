import { defineStore } from 'pinia'

import type { DashboardResponse } from '@services/dashboardService'
import { fetchDashboardSnapshot } from '@services/dashboardService'
import { useFiltersStore } from './filtersStore'
import { extractApiError } from '@utils/error'

interface DashboardState {
  snapshot: DashboardResponse | null
  loading: boolean
  error?: string
}

export const useDashboardStore = defineStore('dashboard', {
  state: (): DashboardState => ({
    snapshot: null,
    loading: false,
    error: undefined
  }),
  actions: {
    async loadSnapshot() {
      const filtersStore = useFiltersStore()
      this.loading = true
      this.error = undefined
      try {
        const data = await fetchDashboardSnapshot(filtersStore.filters)
        this.snapshot = data
      } catch (error) {
        this.error = extractApiError(error).description
      } finally {
        this.loading = false
      }
    }
  }
})
