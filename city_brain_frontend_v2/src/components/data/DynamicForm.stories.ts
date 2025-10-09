import type { Meta, StoryObj } from '@storybook/vue3'

import DynamicForm, { type DynamicFieldSchema } from './DynamicForm.vue'

const schema: DynamicFieldSchema[] = [
  {
    name: 'title',
    label: '工单标题',
    props: { type: 'text', placeholder: '例如：智慧停车摄像头离线' },
    rules: [
      (value) => (!value ? '请输入标题' : undefined),
      (value) => (typeof value === 'string' && value.length < 4 ? '不少于 4 个字符' : undefined)
    ]
  },
  {
    name: 'priority',
    label: '优先级',
    component: 'select',
    options: [
      { label: '高', value: 'high' },
      { label: '中', value: 'medium' },
      { label: '低', value: 'low' }
    ]
  }
]

const meta: Meta<typeof DynamicForm> = {
  title: 'Data/DynamicForm',
  component: DynamicForm,
  args: {
    schema,
    modelValue: {
      title: '',
      priority: 'medium'
    }
  }
}

export default meta

type Story = StoryObj<typeof DynamicForm>

export const Default: Story = {
  render: (args) => ({
    components: { DynamicForm },
    setup() {
      return { args }
    },
    template: `
      <DynamicForm v-bind="args" @submit="console.log('submit', $event)" />
    `
  })
}
