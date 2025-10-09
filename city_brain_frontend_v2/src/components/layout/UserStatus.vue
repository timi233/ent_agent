<template>
  <div class="user-status">
    <div class="user-status__avatar" aria-hidden="true">{{ initials }}</div>
    <div class="user-status__info">
      <span class="user-status__name">{{ userName }}</span>
      <span class="user-status__role">{{ roleLabel }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { useIdentityStore } from '@stores/identityStore'

const identityStore = useIdentityStore()

const userName = computed(() => identityStore.identity?.displayName ?? '未登录用户')
const roleLabel = computed(() => identityStore.identity?.roleLabel ?? '访客权限')
const initials = computed(() => userName.value.slice(0, 2).toUpperCase())
</script>

<style scoped lang="scss">
.user-status {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #fff;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-soft);
}

.user-status__avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary-dark);
  font-weight: 600;
}

.user-status__info {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
  font-size: 12px;
}

.user-status__name {
  font-weight: 600;
  font-size: 14px;
}

.user-status__role {
  color: var(--color-neutral-600);
}
</style>
