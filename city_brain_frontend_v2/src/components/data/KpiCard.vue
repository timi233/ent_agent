<template>
  <article class="kpi" :data-trend="trendDirection">
    <header class="kpi__header">
      <span class="kpi__label">{{ label }}</span>
    </header>
    <div class="kpi__value">{{ formattedValue }}</div>
    <footer class="kpi__footer">
      <span class="kpi__trend" :aria-label="trendLabel">
        {{ trendSymbol }} {{ Math.abs(trend).toFixed(1) }}%
      </span>
      <span v-if="unit" class="kpi__unit">{{ unit }}</span>
    </footer>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  label: string
  value: number
  trend: number
  unit?: string
}

const props = defineProps<Props>()

const trendDirection = computed(() => {
  if (props.trend > 0) return 'up'
  if (props.trend < 0) return 'down'
  return 'neutral'
})

const trendSymbol = computed(() => {
  if (props.trend > 0) return '▲'
  if (props.trend < 0) return '▼'
  return '■'
})

const trendLabel = computed(() => {
  if (props.trend > 0) return '环比上升'
  if (props.trend < 0) return '环比下降'
  return '持平'
})

const formattedValue = computed(() => new Intl.NumberFormat('zh-CN').format(props.value))

const unit = computed(() => props.unit)

const trend = computed(() => props.trend)
</script>

<style scoped lang="scss">
.kpi {
  background: #fff;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
  padding: 20px;
  display: grid;
  gap: 12px;
}

.kpi__label {
  font-size: 14px;
  color: var(--color-neutral-600);
}

.kpi__value {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-primary-dark);
}

.kpi__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
}

.kpi[data-trend='up'] .kpi__trend {
  color: var(--color-success);
}

.kpi[data-trend='down'] .kpi__trend {
  color: var(--color-danger);
}

.kpi[data-trend='neutral'] .kpi__trend {
  color: var(--color-neutral-600);
}

.kpi__unit {
  color: var(--color-neutral-400);
}
</style>
