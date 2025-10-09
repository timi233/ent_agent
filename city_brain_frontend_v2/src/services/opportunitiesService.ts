import { getApiClient } from '@utils/apiClient'
import type {
  OpportunitiesSearchResponse,
  AllStatistics,
  ASOpportunity,
  IPGClient
} from '../types/opportunities'

/**
 * 商机服务 - 对接后端 /api/v1/opportunities 端点
 */

// ==================== 综合查询 ====================

/**
 * 跨AS、IPG、Enterprise_QD和工单综合查询企业信息
 * @param companyName 企业名称
 * @param limitPerSource 每个数据源返回结果数量 (1-50)
 */
export async function searchAllOpportunities(
  companyName: string,
  limitPerSource: number = 10
): Promise<OpportunitiesSearchResponse> {
  const client = getApiClient()
  const response = await client.get<OpportunitiesSearchResponse>('/v1/opportunities/search', {
    params: {
      company_name: companyName,
      limit_per_source: limitPerSource
    }
  })
  return response.data
}

// ==================== 统计数据 ====================

/**
 * 获取AS和IPG系统的综合统计信息
 */
export async function fetchAllStatistics(): Promise<AllStatistics> {
  const client = getApiClient()
  const response = await client.get<AllStatistics>('/v1/opportunities/statistics')
  return response.data
}

// ==================== AS商机查询 ====================

export interface ASSearchParams {
  customer_name?: string
  keyword?: string
  partner?: string
  area?: string
  limit?: number
}

export interface ASSearchResponse {
  success: boolean
  count: number
  data: ASOpportunity[]
}

/**
 * 搜索AS系统商机
 */
export async function searchASOpportunities(
  params: ASSearchParams
): Promise<ASSearchResponse> {
  const client = getApiClient()
  const response = await client.get<ASSearchResponse>('/v1/opportunities/as/search', {
    params
  })
  return response.data
}

/**
 * 获取AS系统商机统计信息
 */
export async function fetchASStatistics() {
  const client = getApiClient()
  const response = await client.get('/v1/opportunities/as/statistics')
  return response.data
}

// ==================== IPG商机查询 ====================

export interface IPGSearchParams {
  client_name?: string
  keyword?: string
  reseller?: string
  province?: string
  limit?: number
}

export interface IPGSearchResponse {
  success: boolean
  count: number
  data: IPGClient[]
}

/**
 * 搜索IPG系统商机
 */
export async function searchIPGClients(
  params: IPGSearchParams
): Promise<IPGSearchResponse> {
  const client = getApiClient()
  const response = await client.get<IPGSearchResponse>('/v1/opportunities/ipg/search', {
    params
  })
  return response.data
}

/**
 * 获取IPG系统商机统计信息
 */
export async function fetchIPGStatistics() {
  const client = getApiClient()
  const response = await client.get('/v1/opportunities/ipg/statistics')
  return response.data
}

// ==================== 健康检查 ====================

/**
 * 商机服务健康检查
 */
export async function checkOpportunitiesHealth() {
  const client = getApiClient()
  const response = await client.get('/v1/opportunities/health')
  return response.data
}
