<template>
  <div class="opportunity-card">
    <div class="opportunity-card__header">
      <div class="opportunity-card__title">
        <h4>{{ title }}</h4>
        <span v-if="badge" :class="['opportunity-card__badge', `opportunity-card__badge--${badge.type}`]">
          {{ badge.text }}
        </span>
      </div>
      <span v-if="status" :class="['opportunity-card__status', `opportunity-card__status--${statusType}`]">
        {{ status }}
      </span>
    </div>

    <div class="opportunity-card__content">
      <slot />
    </div>

    <div v-if="$slots.footer" class="opportunity-card__footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  status?: string
  badge?: {
    text: string
    type: 'as' | 'ipg' | 'qd' | 'work-order'
  }
}

const props = defineProps<Props>()

// 根据status文本推断状态类型
const statusType = computed(() => {
  if (!props.status) return 'default'

  const statusLower = props.status.toLowerCase()

  // 成功/完成类状态
  if (statusLower.includes('完成') || statusLower.includes('成交') || statusLower.includes('已关闭')) {
    return 'success'
  }

  // 进行中类状态
  if (statusLower.includes('进行') || statusLower.includes('跟进') || statusLower.includes('处理')) {
    return 'progress'
  }

  // 警告类状态
  if (statusLower.includes('待') || statusLower.includes('pending')) {
    return 'warning'
  }

  return 'default'
})
</script>

<style scoped lang="scss">
.opportunity-card {
  background: white;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  padding: 16px;
  transition: box-shadow 0.2s;

  &:hover {
    box-shadow: 0 4px 12px rgba(31, 60, 136, 0.1);
  }
}

.opportunity-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 12px;
}

.opportunity-card__title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;

  h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--color-neutral-900);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.opportunity-card__badge {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;

  &--as {
    background: rgba(34, 197, 94, 0.1);
    color: #16a34a;
  }

  &--ipg {
    background: rgba(249, 115, 22, 0.1);
    color: #ea580c;
  }

  &--qd {
    background: rgba(59, 130, 246, 0.1);
    color: #2563eb;
  }

  &--work-order {
    background: rgba(220, 38, 38, 0.1);
    color: #dc2626;
  }
}

.opportunity-card__status {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;

  &--success {
    background: rgba(34, 197, 94, 0.1);
    color: var(--color-success);
  }

  &--progress {
    background: rgba(59, 130, 246, 0.1);
    color: var(--color-accent);
  }

  &--warning {
    background: rgba(251, 191, 36, 0.1);
    color: var(--color-warning);
  }

  &--default {
    background: rgba(107, 114, 128, 0.1);
    color: var(--color-neutral-600);
  }
}

.opportunity-card__content {
  color: var(--color-neutral-700);
  font-size: 14px;
  line-height: 1.6;
}

.opportunity-card__footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-neutral-200);
  font-size: 13px;
  color: var(--color-neutral-600);
}
</style>
