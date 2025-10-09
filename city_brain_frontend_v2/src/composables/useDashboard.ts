import { onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'

import { useDashboardStore } from '@stores/dashboardStore'
import { useFiltersStore } from '@stores/filtersStore'

export function useDashboard() {
  const dashboardStore = useDashboardStore()
  const filtersStore = useFiltersStore()
  const { snapshot, loading, error } = storeToRefs(dashboardStore)

  onMounted(() => {
    if (!snapshot.value) {
      dashboardStore.loadSnapshot()
    }
  })

  watch(
    () => filtersStore.filters,
    () => {
      dashboardStore.loadSnapshot()
    },
    { deep: true }
  )

  return {
    snapshot,
    loading,
    error,
    reload: dashboardStore.loadSnapshot
  }
}
