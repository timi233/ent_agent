<template>
  <div class="table-wrapper">
    <table class="table">
      <thead>
        <tr>
          <th v-for="column in columns" :key="column.key" scope="col">
            <button
              v-if="column.sortable"
              type="button"
              class="table__sort"
              @click="toggleSort(column.key)"
            >
              {{ column.label }}
              <span class="table__sort-icon" aria-hidden="true">
                {{ sortIndicator(column.key) }}
              </span>
            </button>
            <span v-else>{{ column.label }}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td :colspan="columns.length" class="table__loading">加载中…</td>
        </tr>
        <tr v-else-if="rows.length === 0">
          <td :colspan="columns.length" class="table__empty">暂无数据</td>
        </tr>
        <tr v-else v-for="row in rows" :key="rowKey(row)">
          <td v-for="column in columns" :key="column.key">
            <slot :name="`cell-${column.key}`" :row="row">
              {{ row[column.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="showFooter" class="table__footer">
      <button type="button" class="table__footer-btn" @click="emit('prev')" :disabled="!canPrev">
        上一页
      </button>
      <span class="table__footer-meta">第 {{ page }} / {{ pageCount }} 页</span>
      <button type="button" class="table__footer-btn" @click="emit('next')" :disabled="!canNext">
        下一页
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue'

interface Column {
  key: string
  label: string
  sortable?: boolean
}

interface Props {
  columns: Column[]
  rows: Record<string, unknown>[]
  loading?: boolean
  page?: number
  pageCount?: number
  canPrev?: boolean
  canNext?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  page: 1,
  pageCount: 1,
  canPrev: false,
  canNext: false
})

const columns = computed(() => props.columns)
const rows = computed(() => props.rows)
const loading = computed(() => props.loading)
const page = computed(() => props.page)
const pageCount = computed(() => props.pageCount)
const canPrev = computed(() => props.canPrev)
const canNext = computed(() => props.canNext)

const emit = defineEmits<{
  (event: 'sort', payload: { key: string; direction: 'asc' | 'desc' | null }): void
  (event: 'prev'): void
  (event: 'next'): void
}>()

const sortState = reactive<{ key: string | null; direction: 'asc' | 'desc' | null }>({
  key: null,
  direction: null
})

const showFooter = computed(() => props.pageCount > 1)

function toggleSort(key: string) {
  if (sortState.key !== key) {
    sortState.key = key
    sortState.direction = 'asc'
  } else {
    sortState.direction = sortState.direction === 'asc' ? 'desc' : sortState.direction === 'desc' ? null : 'asc'
    if (!sortState.direction) {
      sortState.key = null
    }
  }

  emit('sort', { key: sortState.key ?? key, direction: sortState.direction })
}

function sortIndicator(key: string) {
  if (sortState.key !== key) return '↕'
  if (sortState.direction === 'asc') return '↑'
  if (sortState.direction === 'desc') return '↓'
  return '↕'
}

function rowKey(row: Record<string, unknown>) {
  return row.id ?? JSON.stringify(row)
}
</script>

<style scoped lang="scss">
.table-wrapper {
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
  overflow: hidden;
  background: #fff;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--color-neutral-200);
}

th {
  background: rgba(31, 60, 136, 0.05);
  font-weight: 600;
}

.table__sort {
  background: transparent;
  border: none;
  font: inherit;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: inherit;
}

.table__loading,
.table__empty {
  text-align: center;
  color: var(--color-neutral-600);
  font-size: 14px;
}

.table__footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(31, 60, 136, 0.05);
}

.table__footer-btn {
  border: none;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  background: var(--color-primary);
  color: #fff;
  cursor: pointer;
}

.table__footer-btn:disabled {
  background: var(--color-neutral-200);
  color: var(--color-neutral-600);
  cursor: not-allowed;
}

.table__footer-meta {
  font-size: 12px;
  color: var(--color-neutral-600);
}
</style>
