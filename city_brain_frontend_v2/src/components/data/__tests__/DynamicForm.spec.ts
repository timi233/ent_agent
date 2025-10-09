import { render, fireEvent } from '@testing-library/vue'
import { describe, it, expect, vi } from 'vitest'

import DynamicForm, { type DynamicFieldSchema } from '../DynamicForm.vue'

describe('DynamicForm', () => {
  const schema: DynamicFieldSchema[] = [
    {
      name: 'title',
      label: '工单标题',
      props: { type: 'text' },
      rules: [(value) => (!value ? '请输入标题' : undefined)]
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

  it('validates and emits submit when fields pass rules', async () => {
    const handleSubmit = vi.fn()
    const { getByLabelText, getByRole, emitted } = render(DynamicForm, {
      props: {
        schema,
        modelValue: {
          title: '',
          priority: 'medium'
        },
        onSubmit: handleSubmit
      }
    })

    await fireEvent.update(getByLabelText('工单标题'), '智慧井盖巡检')
    await fireEvent.submit(getByRole('button', { name: '提交' }))

    expect(handleSubmit).toHaveBeenCalled()
    const payload = emitted('submit')?.[0][0] as Record<string, unknown>
    expect(payload.title).toBe('智慧井盖巡检')
  })

  it('emits validationFailed when field invalid', async () => {
    const handleValidationFailed = vi.fn()
    const { getByRole } = render(DynamicForm, {
      props: {
        schema,
        modelValue: {
          title: '',
          priority: 'medium'
        },
        onValidationFailed: handleValidationFailed
      }
    })

    await fireEvent.submit(getByRole('button', { name: '提交' }))

    expect(handleValidationFailed).toHaveBeenCalled()
  })
})
