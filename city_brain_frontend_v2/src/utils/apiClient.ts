import axios, { type AxiosInstance } from 'axios'

import { useToastStore } from '@stores/toastStore'
import { useIdentityStore } from '@stores/identityStore'
import { extractApiError } from './error'

class ApiClient {
  private instance: AxiosInstance

  constructor() {
    const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

    this.instance = axios.create({
      baseURL,
      timeout: 15000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.instance.interceptors.request.use((config) => {
      const identityStore = useIdentityStore()
      const token = identityStore.identity?.id
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    this.instance.interceptors.response.use(
      (response) => response,
      (error) => {
        const toastStore = useToastStore()
        const detail = extractApiError(error)

        toastStore.enqueue({
          title: detail.title,
          description: detail.description,
          variant: detail.status && detail.status >= 500 ? 'error' : 'warning'
        })
        return Promise.reject(error)
      }
    )
  }

  get client() {
    return this.instance
  }
}

let apiClient: ApiClient | null = null

export function getApiClient() {
  if (!apiClient) {
    apiClient = new ApiClient()
  }
  return apiClient.client
}
