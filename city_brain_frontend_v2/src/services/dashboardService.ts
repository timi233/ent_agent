import { getApiClient } from '@utils/apiClient'

export interface DashboardMetric {
  id: string
  label: string
  value: number
  trend: number
  unit?: string
}

export interface DashboardResponse {
  metrics: DashboardMetric[]
  alerts: Array<{ id: string; title: string; severity: 'low' | 'medium' | 'high' }>
  updatedAt: string
}

export async function fetchDashboardSnapshot(filters?: Record<string, unknown>) {
  const client = getApiClient()
  const response = await client.get<DashboardResponse>('/v1/dashboard/snapshot', {
    params: filters
  })
  return response.data
}
