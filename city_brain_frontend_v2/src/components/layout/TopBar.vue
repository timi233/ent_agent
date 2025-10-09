<template>
  <div class="topbar">
    <div class="topbar__left">
      <h1 class="topbar__title">{{ pageTitle }}</h1>
      <slot name="contextual"></slot>
    </div>
    <div class="topbar__right">
      <FilterChips />
      <UserStatus />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import FilterChips from '@components/data/FilterChips.vue'
import UserStatus from '@components/layout/UserStatus.vue'

const route = useRoute()

const pageTitle = computed(() => {
  const metaTitle = route.meta.title
  if (typeof metaTitle === 'string') {
    return metaTitle
  }
  return '城市大脑控制台'
})
</script>

<style scoped lang="scss">
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px clamp(16px, 4vw, 48px);
  gap: 24px;
}

.topbar__title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--color-primary-dark);
}

.topbar__left,
.topbar__right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.topbar__right {
  margin-left: auto;
}
</style>
