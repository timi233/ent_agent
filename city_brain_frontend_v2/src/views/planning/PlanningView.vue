<template>
  <div class="planning">
    <BaseCard title="空间规划全景" :loading="loading">
      <template #header>
        <div class="planning__actions">
          <button type="button" class="planning__refresh" @click="reload" :disabled="loading">
            刷新图层
          </button>
        </div>
      </template>
      <div class="planning__map">
        <CityMapCanvas>
          <div class="planning__overlay">
            <h3 class="planning__overlay-title">图层状态</h3>
            <p class="planning__overlay-desc">已选择 {{ activeLayerIds.length }} / {{ layers.length }} 个图层</p>
            <ul class="planning__overlay-list">
              <li v-for="layer in selectedLayers" :key="layer.id">{{ layer.name }}</li>
            </ul>
          </div>
        </CityMapCanvas>
      </div>
    </BaseCard>

    <BaseCard title="图层管理" :loading="loading">
      <template v-if="error" #header>
        <span class="planning__error">{{ error }}</span>
      </template>
      <div v-if="layers.length" class="planning__layers">
        <label
          v-for="layer in layers"
          :key="layer.id"
          class="planning__layer"
        >
          <input
            type="checkbox"
            :value="layer.id"
            :checked="activeLayerIds.includes(layer.id)"
            @change="toggleLayer(layer.id)"
          />
          <div class="planning__layer-info">
            <span class="planning__layer-name">{{ layer.name }}</span>
            <span class="planning__layer-desc">{{ layer.description }}</span>
          </div>
          <span class="planning__layer-type">{{ layer.geometryType }}</span>
        </label>
      </div>
      <BaseEmptyState
        v-else
        title="暂无规划图层"
        description="请确认后端规划服务已提供数据。"
        icon="🛰️"
      />
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import BaseCard from '@components/base/BaseCard.vue'
import BaseEmptyState from '@components/base/BaseEmptyState.vue'
import CityMapCanvas from '@components/data/CityMapCanvas.vue'
import { useZoning } from '@composables/useZoning'

const { layers, loading, error, reload } = useZoning()
const activeLayers = ref<string[]>([])

watch(
  layers,
  (value) => {
    if (value.length && activeLayers.value.length === 0) {
      activeLayers.value = value.map((layer) => layer.id)
    }
  },
  { immediate: true }
)

const activeLayerIds = computed(() => activeLayers.value)

const selectedLayers = computed(() =>
  layers.value.filter((layer) => activeLayerIds.value.includes(layer.id))
)

function toggleLayer(id: string) {
  const set = new Set(activeLayers.value)
  if (set.has(id)) {
    set.delete(id)
  } else {
    set.add(id)
  }
  activeLayers.value = Array.from(set)
}
</script>

<style scoped lang="scss">
.planning {
  display: grid;
  gap: 24px;
}

.planning__actions {
  margin-left: auto;
}

.planning__refresh {
  border: none;
  background: var(--color-accent);
  color: var(--color-primary-dark);
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.planning__map {
  margin-top: 16px;
}

.planning__overlay {
  background: rgba(6, 21, 43, 0.8);
  padding: 16px;
  border-radius: var(--radius-md);
  max-width: 280px;
  display: grid;
  gap: 8px;
}

.planning__overlay-title {
  margin: 0;
  font-size: 16px;
}

.planning__overlay-desc {
  margin: 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.66);
}

.planning__overlay-list {
  margin: 0;
  padding-left: 18px;
  font-size: 13px;
}

.planning__layers {
  display: grid;
  gap: 12px;
}

.planning__layer {
  display: grid;
  gap: 6px;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-neutral-200);
  background: rgba(31, 60, 136, 0.04);
  color: var(--color-primary-dark);
}

.planning__layer-info {
  display: grid;
  gap: 4px;
}

.planning__layer-name {
  font-weight: 600;
}

.planning__layer-desc {
  font-size: 12px;
  color: var(--color-neutral-600);
}

.planning__layer-type {
  font-size: 12px;
  text-transform: uppercase;
  color: var(--color-neutral-400);
}

.planning__error {
  color: var(--color-danger);
}
</style>
