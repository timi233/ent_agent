<template>
  <div class="shell">
    <aside class="shell__sidebar">
      <SidebarNav />
    </aside>
    <main class="shell__main">
      <header class="shell__topbar">
        <TopBar />
      </header>
      <section class="shell__content">
        <slot />
      </section>
    </main>
    <ToastHost />
  </div>
</template>

<script setup lang="ts">
import SidebarNav from './SidebarNav.vue'
import TopBar from './TopBar.vue'
import ToastHost from '@components/feedback/ToastHost.vue'
</script>

<style scoped lang="scss">
.shell {
  display: grid;
  min-height: 100vh;
  grid-template-columns: 260px 1fr;
  background: var(--color-neutral-100);
  color: var(--color-neutral-800);

  @media (max-width: 1024px) {
    grid-template-columns: 80px 1fr;
  }
}

.shell__sidebar {
  background: var(--color-primary-dark);
  color: #fff;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.shell__main {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.shell__topbar {
  position: sticky;
  top: 0;
  z-index: 5;
  backdrop-filter: blur(8px);
  background: rgba(245, 247, 250, 0.85);
  border-bottom: 1px solid var(--color-neutral-200);
}

.shell__content {
  flex: 1;
  padding: 24px clamp(16px, 4vw, 48px);
}
</style>
