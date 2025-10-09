<template>
  <div class="filters" role="toolbar" aria-label="全局筛选器">
    <div v-if="activeFilters.length === 0" class="filters__empty">选择筛选条件</div>
    <button
      v-for="filter in activeFilters"
      :key="filter.key"
      type="button"
      class="filters__chip"
      @click="handleRemove(filter.key)"
    >
      <span class="filters__label">{{ labels[filter.key] ?? filter.key }}</span>
      <span class="filters__value">{{ formatValue(filter.value) }}</span>
      <span aria-hidden="true">×</span>
    </button>
    <button
      v-if="activeFilters.length > 0"
      type="button"
      class="filters__reset"
      @click="resetFilters"
    >清除筛选</button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useGlobalFilters } from '@composables/useGlobalFilters'

const { activeFilters, resetFilters, applyFilter } = useGlobalFilters()

const labels: Record<string, string> = {
  district: '行政区',
  timespan: '时间范围',
  layers: '数据图层'
}

function handleRemove(key: string) {
  applyFilter(key as never, key === 'layers' ? [] : undefined)
}

function formatValue(value: unknown) {
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  return String(value)
}
</script>

<style scoped lang="scss">
.filters {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.filters__chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid var(--color-accent);
  background: rgba(47, 191, 222, 0.15);
  color: var(--color-primary-dark);
  cursor: pointer;
}

.filters__chip:hover {
  background: rgba(47, 191, 222, 0.25);
}

.filters__label {
  font-weight: 600;
}

.filters__value {
  font-size: 12px;
  color: var(--color-neutral-600);
}

.filters__reset {
  border: none;
  background: transparent;
  color: var(--color-danger);
  cursor: pointer;
  font-size: 12px;
}

.filters__empty {
  font-size: 12px;
  color: var(--color-neutral-600);
}
</style>
