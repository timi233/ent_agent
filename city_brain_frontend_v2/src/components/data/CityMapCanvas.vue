<template>
  <div class="map" role="img" aria-label="城市规划示意图">
    <div class="map__grid"></div>
    <div class="map__glow"></div>
    <div class="map__content">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
// 视觉占位组件，用于后续接入真实地图 SDK。
</script>

<style scoped lang="scss">
.map {
  position: relative;
  width: 100%;
  height: 420px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: radial-gradient(circle at 20% 20%, rgba(47, 191, 222, 0.25), transparent 60%),
    radial-gradient(circle at 80% 30%, rgba(31, 60, 136, 0.35), transparent 65%),
    #06152b;
  box-shadow: var(--shadow-medium);
  color: #fff;
}

.map__grid {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(255, 255, 255, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.06) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
}

.map__glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 80%, rgba(47, 191, 222, 0.35), transparent 70%);
  mix-blend-mode: screen;
  pointer-events: none;
}

.map__content {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: flex-start;
  padding: 24px;
}
</style>
