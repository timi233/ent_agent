import type { AxiosError } from 'axios'

export interface ApiErrorDetail {
  status?: number
  title: string
  description: string
}

export function extractApiError(error: unknown): ApiErrorDetail {
  if (isAxiosError(error)) {
    const status = error.response?.status
    const detail = String(error.response?.data?.detail ?? error.message)
    return {
      status,
      title: `请求失败 (${status ?? '网络异常'})`,
      description: detail
    }
  }

  if (error instanceof Error) {
    return {
      title: '操作失败',
      description: error.message
    }
  }

  return {
    title: '操作失败',
    description: '发生未知错误，请稍后再试。'
  }
}

function isAxiosError(error: unknown): error is AxiosError<{ detail?: string }> {
  return typeof error === 'object' && error !== null && (error as AxiosError).isAxiosError === true
}
