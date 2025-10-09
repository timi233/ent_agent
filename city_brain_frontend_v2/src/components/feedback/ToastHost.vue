<template>
  <div class="toast-host" role="status" aria-live="polite">
    <transition-group name="toast">
      <article
        v-for="toast in toasts"
        :key="toast.id"
        class="toast"
        :data-variant="toast.variant"
      >
        <div class="toast__content">
          <h2 class="toast__title">{{ toast.title }}</h2>
          <p v-if="toast.description" class="toast__description">{{ toast.description }}</p>
        </div>
        <button type="button" class="toast__dismiss" @click="removeToast(toast.id)">
          关闭
        </button>
      </article>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useToastStore } from '@stores/toastStore'

const toastStore = useToastStore()
const { toasts } = storeToRefs(toastStore)

function removeToast(id: string) {
  toastStore.remove(id)
}
</script>

<style scoped lang="scss">
.toast-host {
  position: fixed;
  right: 24px;
  bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 30;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

.toast {
  min-width: 280px;
  max-width: 400px;
  padding: 16px 20px;
  border-radius: var(--radius-md);
  background: #fff;
  box-shadow: var(--shadow-soft);
  border-left: 4px solid var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.toast[data-variant='success'] {
  border-left-color: var(--color-success);
}

.toast[data-variant='warning'] {
  border-left-color: var(--color-warning);
}

.toast[data-variant='error'] {
  border-left-color: var(--color-danger);
}

.toast__title {
  margin: 0;
  font-size: 16px;
}

.toast__description {
  margin: 4px 0 0;
  color: var(--color-neutral-600);
  font-size: 13px;
}

.toast__dismiss {
  border: none;
  background: transparent;
  color: var(--color-neutral-600);
  cursor: pointer;
  font-size: 12px;
}
</style>
