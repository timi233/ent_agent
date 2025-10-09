<template>
  <BaseEmptyState
    title="页面不存在"
    description="请检查链接是否正确，或返回仪表盘继续探索城市数据。"
  >
    <RouterLink to="/dashboard" class="notfound__link">返回仪表盘</RouterLink>
  </BaseEmptyState>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'

import BaseEmptyState from '@components/base/BaseEmptyState.vue'
</script>

<style scoped>
.notfound__link {
  color: var(--color-primary);
  font-weight: 600;
}
</style>
