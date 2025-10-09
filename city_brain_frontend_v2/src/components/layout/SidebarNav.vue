<template>
  <nav class="sidebar">
    <div class="sidebar__brand">
      <span class="sidebar__logo">CB</span>
      <span class="sidebar__title">City Brain</span>
    </div>
    <ul class="sidebar__list">
      <li v-for="link in links" :key="link.to" class="sidebar__item">
        <RouterLink
          :to="link.to"
          class="sidebar__link"
          active-class="sidebar__link--active"
        >
          <span class="sidebar__icon" aria-hidden="true">{{ link.icon }}</span>
          <span class="sidebar__label">{{ link.label }}</span>
        </RouterLink>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

interface SidebarLink {
  to: string
  label: string
  icon: string
}

const links = computed<SidebarLink[]>(() => [
  { to: '/dashboard', label: '仪表盘', icon: '📊' },
  { to: '/insights', label: '洞察分析', icon: '🔍' },
  { to: '/operations', label: '运营管理', icon: '🧭' },
  { to: '/planning', label: '空间规划', icon: '🗺️' },
  { to: '/admin', label: '权限配置', icon: '⚙️' }
])
</script>

<style scoped lang="scss">
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.sidebar__logo {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: rgba(47, 191, 222, 0.2);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.sidebar__title {
  font-size: 18px;
}

.sidebar__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar__item {}

.sidebar__link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  color: rgba(255, 255, 255, 0.8);
  transition: background 0.2s ease, color 0.2s ease;
}

.sidebar__link:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.sidebar__link--active {
  background: rgba(47, 191, 222, 0.2);
  color: #fff;
}

.sidebar__icon {
  font-size: 18px;
}

.sidebar__label {
  white-space: nowrap;
}
</style>
