import { getApiClient } from '@utils/apiClient'

export interface CompanyDetails {
  name: string
  region: string
  address: string
  industry: string
  industry_brain: string
  chain_status: string
  revenue_info: string
  company_status: string
  data_source: string
}

export interface NewsInfo {
  summary: string
  references: string[]
}

export interface CompanyResponse {
  status: string
  message: string
  company_name: string
  details: CompanyDetails
  structured_summary: string
  web_search_info?: NewsInfo
  timestamp: string
}

export interface CompanyRequest {
  input_text: string
}

export async function processCompany(input_text: string): Promise<CompanyResponse> {
  const client = getApiClient()
  const response = await client.post<CompanyResponse>('/v1/company/process', {
    input_text
  })
  return response.data
}
