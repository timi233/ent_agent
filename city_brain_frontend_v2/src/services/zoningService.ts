import { getApiClient } from '@utils/apiClient'

export interface ZoningLayer {
  id: string
  name: string
  description: string
  geometryType: 'polygon' | 'line' | 'point'
}

export interface ZoningResponse {
  layers: ZoningLayer[]
}

export async function fetchZoningLayers() {
  const client = getApiClient()
  const response = await client.get<ZoningResponse>('/v1/zoning/layers')
  return response.data
}
