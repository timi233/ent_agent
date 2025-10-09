<template>
  <section class="card" :aria-busy="loading ? 'true' : 'false'">
    <header v-if="title || $slots.header" class="card__header">
      <h2 v-if="title" class="card__title">{{ title }}</h2>
      <slot name="header"></slot>
    </header>
    <div class="card__body">
      <slot />
    </div>
    <footer v-if="$slots.footer" class="card__footer">
      <slot name="footer"></slot>
    </footer>
    <div v-if="loading" class="card__loader">加载中…</div>
  </section>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  loading?: boolean
}

withDefaults(defineProps<Props>(), {
  title: undefined,
  loading: false
})
</script>

<style scoped lang="scss">
.card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
  padding: 20px 24px;
  gap: 16px;
}

.card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.card__title {
  margin: 0;
  font-size: 18px;
  color: var(--color-primary-dark);
}

.card__footer {
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid var(--color-neutral-200);
}

.card__loader {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  font-size: 14px;
  font-weight: 600;
  color: var(--color-primary);
}
</style>
