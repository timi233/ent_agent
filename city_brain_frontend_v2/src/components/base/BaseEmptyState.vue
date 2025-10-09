<template>
  <section class="empty">
    <div class="empty__icon" aria-hidden="true">{{ icon }}</div>
    <h2 class="empty__title">{{ title }}</h2>
    <p class="empty__description">{{ description }}</p>
    <slot />
  </section>
</template>

<script setup lang="ts">
interface Props {
  title: string
  description: string
  icon?: string
}

withDefaults(defineProps<Props>(), {
  icon: '🛰️'
})
</script>

<style scoped lang="scss">
.empty {
  border-radius: var(--radius-lg);
  background: #fff;
  padding: 48px 24px;
  text-align: center;
  box-shadow: var(--shadow-soft);
  display: grid;
  justify-items: center;
  gap: 12px;
}

.empty__icon {
  font-size: 32px;
}

.empty__title {
  margin: 0;
  font-size: 20px;
}

.empty__description {
  margin: 0;
  color: var(--color-neutral-600);
  max-width: 480px;
}
</style>
