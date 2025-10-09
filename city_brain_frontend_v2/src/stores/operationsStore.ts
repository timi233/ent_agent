import { defineStore } from 'pinia'

import {
  fetchOperationTickets,
  createOperationTicket,
  type OperationResponse,
  type CreateTicketPayload,
  type OperationTicket
} from '@services/operationsService'
import { createId } from '@utils/id'
import { extractApiError } from '@utils/error'
import { useFiltersStore } from './filtersStore'

interface OperationsState {
  tickets: OperationResponse['tickets']
  loading: boolean
  error?: string
  creating: boolean
}

export const useOperationsStore = defineStore('operations', {
  state: (): OperationsState => ({
    tickets: [],
    loading: false,
    error: undefined,
    creating: false
  }),
  actions: {
    async load() {
      const filtersStore = useFiltersStore()
      this.loading = true
      this.error = undefined
      try {
        const { tickets } = await fetchOperationTickets(filtersStore.filters)
        this.tickets = tickets
      } catch (error) {
        this.error = extractApiError(error).description
      } finally {
        this.loading = false
      }
    },
    async createTicket(payload: CreateTicketPayload) {
      this.creating = true
      const optimisticTicket: OperationTicket = {
        id: createId('ticket-temp'),
        status: 'open',
        updatedAt: new Date().toISOString(),
        ...payload
      }
      this.tickets = [optimisticTicket, ...this.tickets]

      try {
        const response = await createOperationTicket(payload)
        this.tickets = [response, ...this.tickets.filter((ticket) => ticket.id !== optimisticTicket.id)]
        return response
      } catch (error) {
        this.tickets = this.tickets.filter((ticket) => ticket.id !== optimisticTicket.id)
        this.error = extractApiError(error).description
        throw error
      } finally {
        this.creating = false
      }
    }
  }
})
