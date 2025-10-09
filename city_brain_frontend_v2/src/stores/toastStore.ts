import { defineStore } from 'pinia'

import { createId } from '@utils/id'

export type ToastVariant = 'success' | 'warning' | 'error' | 'info'

export interface ToastPayload {
  id: string
  title: string
  description?: string
  variant?: ToastVariant
  durationMs?: number
}

interface ToastState {
  toasts: ToastPayload[]
}

export const useToastStore = defineStore('toast', {
  state: (): ToastState => ({ toasts: [] }),
  actions: {
    enqueue(toast: Omit<ToastPayload, 'id'>) {
      const payload: ToastPayload = {
        id: createId('toast'),
        durationMs: 5000,
        variant: 'info',
        ...toast
      }

      this.toasts = [...this.toasts, payload]

      if (payload.durationMs) {
        window.setTimeout(() => this.remove(payload.id), payload.durationMs)
      }
    },
    remove(id: string) {
      this.toasts = this.toasts.filter((toast) => toast.id !== id)
    },
    clear() {
      this.toasts = []
    }
  }
})
