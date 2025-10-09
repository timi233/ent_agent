<template>
  <div class="operations">
    <BaseCard title="快速创建工单" :loading="creating">
      <DynamicForm
        :schema="formSchema"
        v-model="ticketForm"
        :loading="creating"
        @submit="submitTicket"
        @validationFailed="handleValidationFailed"
      >
        <template #footer>
          <button type="submit" class="operations__submit" :disabled="creating">提交工单</button>
        </template>
      </DynamicForm>
    </BaseCard>

    <BaseCard title="工单队列" :loading="loading">
      <template #header>
        <div class="operations__actions">
          <select
            class="operations__select"
            aria-label="按优先级筛选"
            @change="onPriorityChange($event.target.value as PriorityFilter)"
          >
            <option value="all">全部优先级</option>
            <option value="high">高</option>
            <option value="medium">中</option>
            <option value="low">低</option>
          </select>
        </div>
      </template>
      <DataTable
        :columns="columns"
        :rows="rows"
        :loading="loading"
        @sort="onSort"
      >
        <template #cell-status="{ row }">
          <span :class="['operations__status', `operations__status--${row.status}`]">
            {{ statusLabel(row.status as TicketStatus) }}
          </span>
        </template>
        <template #cell-priority="{ row }">
          <span :class="['operations__priority', `operations__priority--${row.priority}`]">
            {{ priorityLabel(row.priority as TicketPriority) }}
          </span>
        </template>
      </DataTable>
    </BaseCard>

    <BaseCard title="空间图层" :loading="zoningLoading">
      <template #header>
        <button type="button" class="operations__refresh" @click="reloadZoning" :disabled="zoningLoading">
          刷新图层
        </button>
      </template>
      <ul v-if="layers.length" class="operations__layers">
        <li v-for="layer in layers" :key="layer.id" class="operations__layer">
          <div class="operations__layer-name">{{ layer.name }}</div>
          <div class="operations__layer-meta">{{ layer.description }}</div>
          <span class="operations__layer-type">{{ layer.geometryType }}</span>
        </li>
      </ul>
      <BaseEmptyState
        v-else
        title="暂无图层数据"
        description="确认后端规划服务已开启或稍后再试。"
        icon="🗺️"
      />
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { storeToRefs } from 'pinia'

import BaseCard from '@components/base/BaseCard.vue'
import BaseEmptyState from '@components/base/BaseEmptyState.vue'
import DataTable from '@components/data/DataTable.vue'
import DynamicForm, { type DynamicFieldSchema } from '@components/data/DynamicForm.vue'
import { useOperations } from '@composables/useOperations'
import { useZoning } from '@composables/useZoning'
import { useOperationsStore } from '@stores/operationsStore'
import { useToastStore } from '@stores/toastStore'
import { extractApiError } from '@utils/error'

import type { OperationTicket } from '@services/operationsService'

type TicketStatus = OperationTicket['status']
type TicketPriority = OperationTicket['priority']
type PriorityFilter = TicketPriority | 'all'

const operationsStore = useOperationsStore()
const { creating } = storeToRefs(operationsStore)

const { tickets, loading } = useOperations()
const { layers, loading: zoningLoading, reload: reloadZoning } = useZoning()
const toastStore = useToastStore()

const priorityFilter = ref<PriorityFilter>('all')
const sortState = ref<{ key: string; direction: 'asc' | 'desc' | null }>({
  key: 'updatedAt',
  direction: 'desc'
})

const columns = [
  { key: 'title', label: '工单', sortable: true },
  { key: 'status', label: '状态', sortable: true },
  { key: 'priority', label: '优先级', sortable: true },
  { key: 'owner', label: '责任人', sortable: true },
  { key: 'updatedAt', label: '更新时间', sortable: true }
]

const rows = computed(() => {
  const filtered = tickets.value.filter((ticket) =>
    priorityFilter.value === 'all' ? true : ticket.priority === priorityFilter.value
  )
  const sorted = [...filtered]
  if (sortState.value.direction && sortState.value.key) {
    sorted.sort((a, b) => {
      const valueA = a[sortState.value.key as keyof OperationTicket]
      const valueB = b[sortState.value.key as keyof OperationTicket]

      if (valueA === valueB) return 0
      const order = sortState.value.direction === 'asc' ? 1 : -1

      if (valueA > valueB) return order
      return -order
    })
  }

  return sorted.map((ticket) => ({
    ...ticket,
    updatedAt: new Intl.DateTimeFormat('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(ticket.updatedAt))
  }))
})

const ticketForm = reactive<Record<string, unknown>>({
  title: '',
  owner: '',
  priority: 'medium'
})

const formSchema: DynamicFieldSchema[] = [
  {
    name: 'title',
    label: '工单标题',
    props: { type: 'text', placeholder: '例如：智慧停车摄像头离线' },
    rules: [
      (value) => (!value ? '请输入标题' : undefined),
      (value) => (typeof value === 'string' && value.length < 4 ? '不少于 4 个字符' : undefined)
    ]
  },
  {
    name: 'owner',
    label: '责任人',
    props: { type: 'text', placeholder: '填写处理人姓名' },
    rules: [(value) => (!value ? '请输入责任人' : undefined)]
  },
  {
    name: 'priority',
    label: '优先级',
    component: 'select',
    options: [
      { label: '高', value: 'high' },
      { label: '中', value: 'medium' },
      { label: '低', value: 'low' }
    ]
  }
]

async function submitTicket(payload: Record<string, unknown>) {
  try {
    await operationsStore.createTicket({
      title: String(payload.title ?? ''),
      owner: String(payload.owner ?? ''),
      priority: (payload.priority as TicketPriority) ?? 'medium'
    })
    toastStore.enqueue({
      title: '工单已创建',
      description: '新的运营工单已加入队列。',
      variant: 'success'
    })
    ticketForm.title = ''
    ticketForm.owner = ''
    ticketForm.priority = 'medium'
  } catch (error) {
    const detail = extractApiError(error)
    toastStore.enqueue({
      title: detail.title,
      description: detail.description,
      variant: 'error'
    })
  }
}

function handleValidationFailed(formErrors: Record<string, string>) {
  const message = Object.values(formErrors)
    .filter(Boolean)
    .shift()
  if (message) {
    toastStore.enqueue({
      title: '校验失败',
      description: message,
      variant: 'warning'
    })
  }
}

function onPriorityChange(value: PriorityFilter) {
  priorityFilter.value = value
}

function onSort(payload: { key: string; direction: 'asc' | 'desc' | null }) {
  sortState.value = payload
}

function statusLabel(status: TicketStatus) {
  return {
    open: '待处理',
    in_progress: '处理中',
    closed: '已关闭'
  }[status]
}

function priorityLabel(priority: TicketPriority) {
  return {
    high: '高',
    medium: '中',
    low: '低'
  }[priority]
}
</script>

<style scoped lang="scss">
.operations {
  display: grid;
  gap: 24px;
}

.operations__refresh {
  border: none;
  background: var(--color-accent);
  color: var(--color-primary-dark);
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.operations__actions {
  margin-left: auto;
}

.operations__submit {
  border: none;
  background: var(--color-primary);
  color: #fff;
  padding: 10px 20px;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.operations__select {
  border-radius: var(--radius-sm);
  padding: 8px 12px;
  border: 1px solid var(--color-neutral-200);
  background: #fff;
}

.operations__status,
.operations__priority {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
}

.operations__status--open {
  background: rgba(255, 200, 87, 0.2);
  color: var(--color-warning);
}

.operations__status--in_progress {
  background: rgba(47, 191, 222, 0.2);
  color: var(--color-accent);
}

.operations__status--closed {
  background: rgba(47, 191, 113, 0.2);
  color: var(--color-success);
}

.operations__priority--high {
  background: rgba(242, 95, 92, 0.2);
  color: var(--color-danger);
}

.operations__priority--medium {
  background: rgba(255, 200, 87, 0.2);
  color: var(--color-warning);
}

.operations__priority--low {
  background: rgba(47, 191, 113, 0.2);
  color: var(--color-success);
}

.operations__layers {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 12px;
}

.operations__layer {
  display: grid;
  gap: 4px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: rgba(31, 60, 136, 0.05);
}

.operations__layer-name {
  font-weight: 600;
}

.operations__layer-meta {
  color: var(--color-neutral-600);
  font-size: 12px;
}

.operations__layer-type {
  font-size: 12px;
  color: var(--color-neutral-400);
  text-transform: uppercase;
}
</style>
