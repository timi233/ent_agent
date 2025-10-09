import type { Meta, StoryObj } from '@storybook/vue3'

import KpiCard from './KpiCard.vue'

const meta: Meta<typeof KpiCard> = {
  title: 'Data/KpiCard',
  component: KpiCard,
  args: {
    label: '新增企业',
    value: 1280,
    trend: 6.4,
    unit: '家'
  }
}

export default meta

type Story = StoryObj<typeof KpiCard>

export const Default: Story = {}

export const NegativeTrend: Story = {
  args: {
    label: '能耗指数',
    value: 85,
    trend: -3.2,
    unit: 'kWh'
  }
}
