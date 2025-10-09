<template>
  <div class="statistics-panel">
    <div v-if="title" class="statistics-panel__header">
      <h3>{{ title }}</h3>
      <span v-if="subtitle" class="statistics-panel__subtitle">{{ subtitle }}</span>
    </div>

    <div class="statistics-panel__grid">
      <div v-for="(stat, index) in statistics" :key="index" class="stat-item">
        <div class="stat-item__label">{{ stat.label }}</div>
        <div class="stat-item__value">
          {{ formatValue(stat.value, stat.format) }}
          <span v-if="stat.unit" class="stat-item__unit">{{ stat.unit }}</span>
        </div>
        <div v-if="stat.description" class="stat-item__description">
          {{ stat.description }}
        </div>
      </div>
    </div>

    <div v-if="$slots.footer" class="statistics-panel__footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
export interface Statistic {
  label: string
  value: number | string
  unit?: string
  description?: string
  format?: 'number' | 'currency' | 'percentage' | 'none'
}

interface Props {
  title?: string
  subtitle?: string
  statistics: Statistic[]
}

defineProps<Props>()

/**
 * 格式化数值显示
 */
function formatValue(value: number | string, format?: string): string {
  if (typeof value === 'string') {
    return value
  }

  switch (format) {
    case 'currency':
      return new Intl.NumberFormat('zh-CN', {
        style: 'decimal',
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
      }).format(value)

    case 'percentage':
      return `${(value * 100).toFixed(1)}%`

    case 'number':
      return new Intl.NumberFormat('zh-CN').format(value)

    case 'none':
      return String(value)

    default:
      // 自动判断：大于1000的数字使用千位分隔符
      if (value >= 1000) {
        return new Intl.NumberFormat('zh-CN').format(value)
      }
      return String(value)
  }
}
</script>

<style scoped lang="scss">
.statistics-panel {
  background: white;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  padding: 20px;
}

.statistics-panel__header {
  margin-bottom: 20px;

  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--color-neutral-900);
  }
}

.statistics-panel__subtitle {
  display: block;
  margin-top: 4px;
  font-size: 14px;
  color: var(--color-neutral-600);
}

.statistics-panel__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-item__label {
  font-size: 13px;
  color: var(--color-neutral-600);
  font-weight: 500;
}

.stat-item__value {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1.2;
}

.stat-item__unit {
  font-size: 16px;
  font-weight: 500;
  color: var(--color-neutral-600);
  margin-left: 4px;
}

.stat-item__description {
  font-size: 12px;
  color: var(--color-neutral-500);
  margin-top: 2px;
}

.statistics-panel__footer {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--color-neutral-200);
}
</style>
