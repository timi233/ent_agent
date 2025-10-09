import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

const mockFetchOperationTickets = vi.fn()
const mockCreateOperationTicket = vi.fn()

vi.mock('@services/operationsService', () => ({
  fetchOperationTickets: mockFetchOperationTickets,
  createOperationTicket: mockCreateOperationTicket
}))

import { useOperationsStore } from '../operationsStore'

const sampleTickets = [
  {
    id: 'ticket-1',
    title: '智慧路灯离线排查',
    status: 'open',
    priority: 'high',
    owner: '张三',
    updatedAt: '2024-03-20T08:00:00Z'
  }
] as const

describe('useOperationsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    mockFetchOperationTickets.mockResolvedValue({ tickets: sampleTickets })
    mockCreateOperationTicket.mockReset()
  })

  it('loads tickets via fetchOperationTickets', async () => {
    const store = useOperationsStore()

    await store.load()

    expect(mockFetchOperationTickets).toHaveBeenCalled()
    expect(store.tickets).toHaveLength(1)
    expect(store.tickets[0].title).toBe('智慧路灯离线排查')
  })

  it('creates ticket optimistically and replaces with backend response', async () => {
    const store = useOperationsStore()
    await store.load()

    mockCreateOperationTicket.mockResolvedValue({
      id: 'ticket-2',
      title: '新建停车场规划',
      status: 'open',
      priority: 'medium',
      owner: '李四',
      updatedAt: '2024-03-21T02:00:00Z'
    })

    await store.createTicket({
      title: '新建停车场规划',
      priority: 'medium',
      owner: '李四'
    })

    expect(store.tickets[0].id).toBe('ticket-2')
    expect(store.creating).toBe(false)
  })

  it('rolls back optimistic ticket when request fails', async () => {
    const store = useOperationsStore()
    await store.load()

    mockCreateOperationTicket.mockRejectedValueOnce(new Error('网络异常'))

    await expect(
      store.createTicket({
        title: '测试失败',
        priority: 'low',
        owner: '王五'
      })
    ).rejects.toThrowError('网络异常')

    expect(store.tickets).toHaveLength(1)
    expect(store.error).toBe('网络异常')
    expect(store.creating).toBe(false)
  })
})
