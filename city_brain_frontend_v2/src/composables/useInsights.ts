import { onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'

import { useInsightsStore } from '@stores/insightsStore'
import { useFiltersStore } from '@stores/filtersStore'

export function useInsights() {
  const insightsStore = useInsightsStore()
  const filtersStore = useFiltersStore()
  const { data, loading, error } = storeToRefs(insightsStore)

  onMounted(() => {
    if (!data.value) {
      insightsStore.load()
    }
  })

  watch(
    () => filtersStore.filters,
    () => {
      insightsStore.load()
    },
    { deep: true }
  )

  return {
    data,
    loading,
    error,
    reload: insightsStore.load
  }
}
