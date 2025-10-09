import { getApiClient } from '@utils/apiClient'
import type { AllStatistics, ASStatistics, IPGStatistics } from '../types/opportunities'

/**
 * 商机洞察服务 - 对接后端商机统计API
 * 替换原有的时序数据功能（后端无此API）
 */

/**
 * 获取AS和IPG系统的综合统计信息
 */
export async function fetchAllStatistics(): Promise<AllStatistics> {
  const client = getApiClient()
  const response = await client.get<AllStatistics>('/v1/opportunities/statistics')
  return response.data
}

/**
 * 获取AS系统商机统计信息
 */
export async function fetchASStatistics() {
  const client = getApiClient()
  const response = await client.get<{ success: boolean; data: ASStatistics }>(
    '/v1/opportunities/as/statistics'
  )
  return response.data
}

/**
 * 获取IPG系统商机统计信息
 */
export async function fetchIPGStatistics() {
  const client = getApiClient()
  const response = await client.get<{ success: boolean; data: IPGStatistics }>(
    '/v1/opportunities/ipg/statistics'
  )
  return response.data
}
