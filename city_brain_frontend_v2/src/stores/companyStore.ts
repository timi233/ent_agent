import { defineStore } from 'pinia'

import type { CompanyResponse } from '@services/companyService'
import { processCompany } from '@services/companyService'
import { extractApiError } from '@utils/error'

interface CompanyState {
  result: CompanyResponse | null
  loading: boolean
  error?: string
}

export const useCompanyStore = defineStore('company', {
  state: (): CompanyState => ({
    result: null,
    loading: false,
    error: undefined
  }),
  actions: {
    async searchCompany(input_text: string) {
      this.loading = true
      this.error = undefined
      try {
        const data = await processCompany(input_text)
        this.result = data
      } catch (error) {
        this.error = extractApiError(error).description
      } finally {
        this.loading = false
      }
    },
    clearResult() {
      this.result = null
      this.error = undefined
    }
  }
})
