<template>
  <div ref="root" class="echart" role="img" :aria-label="ariaLabel"></div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { ECBasicOption } from 'echarts/types/dist/shared'
import { use, registerTheme } from 'echarts/core'
import { LineChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { ECharts } from 'echarts/core'

use([LineChart, BarChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

registerTheme('city-brain', {
  color: ['#2FBFDE', '#1F3C88', '#FFC857', '#2FBF71', '#F25F5C'],
  textStyle: {
    fontFamily: "'Inter', 'Noto Sans SC', sans-serif"
  }
})

interface Props {
  option: ECBasicOption
  ariaLabel?: string
}

const props = defineProps<Props>()

const root = ref<HTMLDivElement | null>(null)
let chart: ECharts | null = null
let cleanupResize: (() => void) | null = null
let echartsModule: typeof import('echarts') | null = null

async function initChart() {
  if (!root.value) return
  const echarts = await ensureECharts()
  chart = echarts.init(root.value, 'city-brain', { renderer: 'canvas' })
  chart.setOption(props.option)
  if (typeof ResizeObserver !== 'undefined') {
    const observer = new ResizeObserver(() => {
      chart?.resize()
    })
    observer.observe(root.value)
    cleanupResize = () => observer.disconnect()
  }
}

async function ensureECharts() {
  if (echartsModule) {
    return echartsModule
  }
  echartsModule = await import('echarts')
  return echartsModule
}

watch(
  () => props.option,
  (option) => {
    if (!chart) return
    chart.setOption(option, true)
  },
  { deep: true }
)

onMounted(() => {
  initChart()
})

onBeforeUnmount(() => {
  cleanupResize?.()
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.echart {
  width: 100%;
  height: 100%;
}
</style>
