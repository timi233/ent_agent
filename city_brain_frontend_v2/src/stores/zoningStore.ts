import { defineStore } from 'pinia'

import { fetchZoningLayers, type ZoningResponse } from '@services/zoningService'
import { extractApiError } from '@utils/error'

interface ZoningState {
  layers: ZoningResponse['layers']
  loading: boolean
  error?: string
}

export const useZoningStore = defineStore('zoning', {
  state: (): ZoningState => ({
    layers: [],
    loading: false,
    error: undefined
  }),
  actions: {
    async load() {
      this.loading = true
      this.error = undefined
      try {
        const response = await fetchZoningLayers()
        this.layers = response.layers
      } catch (error) {
        this.error = extractApiError(error).description
      } finally {
        this.loading = false
      }
    }
  }
})
