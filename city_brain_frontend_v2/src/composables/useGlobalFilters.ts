import { computed } from 'vue'
import { storeToRefs } from 'pinia'

import { useFiltersStore } from '@stores/filtersStore'

export function useGlobalFilters() {
  const filtersStore = useFiltersStore()
  const { filters } = storeToRefs(filtersStore)

  const activeFilters = computed(() =>
    Object.entries(filters.value).flatMap(([key, value]) => {
      if (!value || (Array.isArray(value) && value.length === 0)) {
        return []
      }
      return [{ key, value }]
    })
  )

  function applyFilter(key: keyof typeof filters.value, value: unknown) {
    filtersStore.setFilter(key as never, value as never)
  }

  function resetFilters() {
    filtersStore.reset()
  }

  return {
    filters,
    activeFilters,
    applyFilter,
    resetFilters
  }
}
