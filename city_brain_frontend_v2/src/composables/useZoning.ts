import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'

import { useZoningStore } from '@stores/zoningStore'

export function useZoning() {
  const zoningStore = useZoningStore()
  const { layers, loading, error } = storeToRefs(zoningStore)

  onMounted(() => {
    if (layers.value.length === 0) {
      zoningStore.load()
    }
  })

  return {
    layers,
    loading,
    error,
    reload: zoningStore.load
  }
}
