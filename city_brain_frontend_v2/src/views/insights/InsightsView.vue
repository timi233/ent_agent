<template>
  <div class="insights">
    <BaseCard title="指标趋势" :loading="loading">
      <div v-if="datasets.length" class="insights__chart">
        <EChartsPanel :option="chartOption" aria-label="多指标趋势对比" />
      </div>
      <BaseEmptyState
        v-else
        title="暂无分析数据"
        description="调整筛选条件或等待数据刷新后再试。"
        icon="📉"
      />
    </BaseCard>

    <BaseCard title="数据明细" :loading="loading">
      <DataTable
        :columns="columns"
        :rows="tableRows"
        :loading="loading"
        @sort="handleSort"
      />
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import BaseCard from '@components/base/BaseCard.vue'
import BaseEmptyState from '@components/base/BaseEmptyState.vue'
import DataTable from '@components/data/DataTable.vue'
import EChartsPanel from '@components/data/EChartsPanel.vue'
import { useInsights } from '@composables/useInsights'

const { data, loading } = useInsights()
const sortState = ref<{ key: string; direction: 'asc' | 'desc' | null }>({
  key: 'timestamp',
  direction: 'desc'
})

const datasets = computed(() => data.value?.datasets ?? [])

const timestamps = computed(() => {
  const stampSet = new Set<string>()
  datasets.value.forEach((dataset) => dataset.series.forEach((point) => stampSet.add(point.timestamp)))
  return Array.from(stampSet).sort()
})

const chartOption = computed(() => {
  const xAxisData = timestamps.value.map((timestamp) =>
    new Intl.DateTimeFormat('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      month: '2-digit',
      day: '2-digit'
    }).format(new Date(timestamp))
  )

  return {
    tooltip: { trigger: 'axis' },
    legend: { data: datasets.value.map((dataset) => dataset.label) },
    grid: { top: 32, left: 48, right: 16, bottom: 32 },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xAxisData
    },
    yAxis: { type: 'value' },
    series: datasets.value.map((dataset) => ({
      name: dataset.label,
      type: 'line',
      smooth: true,
      data: timestamps.value.map((timestamp) => {
        const point = dataset.series.find((item) => item.timestamp === timestamp)
        return point?.value ?? null
      })
    }))
  }
})

const columns = [
  { key: 'dataset', label: '指标', sortable: true },
  { key: 'timestamp', label: '时间', sortable: true },
  { key: 'value', label: '数值', sortable: true }
]

const tableRows = computed(() => {
  const rows = datasets.value.flatMap((dataset) =>
    dataset.series.map((point) => ({
      id: `${dataset.id}-${point.timestamp}`,
      dataset: dataset.label,
      timestamp: point.timestamp,
      value: point.value
    }))
  )

  if (sortState.value.direction && sortState.value.key) {
    rows.sort((a, b) => {
      const valueA = a[sortState.value.key as keyof typeof a]
      const valueB = b[sortState.value.key as keyof typeof b]

      if (valueA === valueB) return 0
      const order = sortState.value.direction === 'asc' ? 1 : -1

      if (valueA > valueB) return order
      return -order
    })
  }

  return rows.map((row) => ({
    ...row,
    timestamp: new Intl.DateTimeFormat('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit'
    }).format(new Date(row.timestamp))
  }))
})

function handleSort(payload: { key: string; direction: 'asc' | 'desc' | null }) {
  sortState.value = payload
}
</script>

<style scoped lang="scss">
.insights {
  display: grid;
  gap: 24px;
}

.insights__chart {
  height: 360px;
  border-radius: var(--radius-md);
  background: rgba(31, 60, 136, 0.05);
  padding: 16px;
}
</style>
