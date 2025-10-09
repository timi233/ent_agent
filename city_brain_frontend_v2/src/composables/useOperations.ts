import { onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'

import { useOperationsStore } from '@stores/operationsStore'
import { useFiltersStore } from '@stores/filtersStore'

export function useOperations() {
  const operationsStore = useOperationsStore()
  const filtersStore = useFiltersStore()
  const { tickets, loading, error } = storeToRefs(operationsStore)

  onMounted(() => {
    if (tickets.value.length === 0) {
      operationsStore.load()
    }
  })

  watch(
    () => filtersStore.filters,
    () => {
      operationsStore.load()
    },
    { deep: true }
  )

  return {
    tickets,
    loading,
    error,
    reload: operationsStore.load
  }
}
