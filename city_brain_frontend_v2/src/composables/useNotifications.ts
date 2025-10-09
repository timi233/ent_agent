import { onBeforeUnmount, ref } from 'vue'

import { useToastStore } from '@stores/toastStore'

interface NotificationPayload {
  id: string
  title: string
  message: string
  variant?: 'success' | 'warning' | 'error' | 'info'
}

export function useNotifications() {
  const socketRef = ref<WebSocket | null>(null)
  const toastStore = useToastStore()

  function connect() {
    const url = import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:9003/ws/notifications'
    socketRef.value = new WebSocket(url)

    socketRef.value.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as NotificationPayload
        toastStore.enqueue({
          title: payload.title,
          description: payload.message,
          variant: payload.variant ?? 'info'
        })
      } catch (error) {
        console.warn('Failed to parse notification payload', error)
      }
    }

    socketRef.value.onclose = () => {
      socketRef.value = null
    }
  }

  function disconnect() {
    socketRef.value?.close()
    socketRef.value = null
  }

  onBeforeUnmount(() => {
    disconnect()
  })

  return {
    connect,
    disconnect,
    isConnected: () => socketRef.value !== null
  }
}
