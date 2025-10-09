import { defineStore } from 'pinia'

export interface GlobalFilters {
  district?: string
  timespan?: string
  layers?: string[]
}

interface FiltersState {
  filters: GlobalFilters
}

export const useFiltersStore = defineStore('filters', {
  state: (): FiltersState => ({
    filters: {}
  }),
  actions: {
    setFilter<Key extends keyof GlobalFilters>(key: Key, value: GlobalFilters[Key]) {
      this.filters = { ...this.filters, [key]: value }
    },
    reset() {
      this.filters = {}
    }
  }
})
