import { getApiClient } from '@utils/apiClient'

export interface OperationTicket {
  id: string
  title: string
  status: 'open' | 'in_progress' | 'closed'
  priority: 'low' | 'medium' | 'high'
  owner: string
  updatedAt: string
}

export interface OperationResponse {
  tickets: OperationTicket[]
}

export async function fetchOperationTickets(params?: Record<string, unknown>) {
  const client = getApiClient()
  const response = await client.get<OperationResponse>('/v1/operations/tickets', {
    params
  })
  return response.data
}

export interface CreateTicketPayload {
  title: string
  priority: OperationTicket['priority']
  owner: string
}

export async function createOperationTicket(payload: CreateTicketPayload) {
  const client = getApiClient()
  const response = await client.post<OperationTicket>('/v1/operations/tickets', payload)
  return response.data
}
