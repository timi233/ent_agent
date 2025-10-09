<template>
  <form class="form" @submit.prevent="submit">
    <fieldset class="form__fields" :disabled="loading">
      <div v-for="field in schema" :key="field.name" class="form__field">
        <label :for="field.name" class="form__label">{{ field.label }}</label>
        <component
          :is="field.component ?? 'input'"
          v-model="draft[field.name]"
          :id="field.name"
          class="form__control"
          v-bind="field.props"
          @blur="() => validateField(field.name)"
        >
          <option v-for="option in field.options ?? []" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </component>
        <p v-if="errors[field.name]" class="form__error">{{ errors[field.name] }}</p>
      </div>
    </fieldset>
    <slot name="footer">
      <button type="submit" class="form__submit" :disabled="loading">提交</button>
    </slot>
  </form>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from 'vue'

export interface OptionItem {
  label: string
  value: string
}

export interface FieldSchema {
  name: string
  label: string
  component?: string
  props?: Record<string, unknown>
  options?: OptionItem[]
  rules?: Array<(value: unknown) => string | void>
}

interface Props {
  schema: FieldSchema[]
  modelValue: Record<string, unknown>
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<{
  (event: 'update:modelValue', payload: Record<string, unknown>): void
  (event: 'submit', payload: Record<string, unknown>): void
  (event: 'validationFailed', payload: Record<string, string>): void
}>()

const draft = reactive<Record<string, unknown>>({ ...props.modelValue })
const errors = reactive<Record<string, string>>({})

watch(
  () => props.modelValue,
  (value) => {
    Object.assign(draft, value)
  }
)

watch(
  draft,
  (value) => {
    emit('update:modelValue', { ...value })
  },
  { deep: true }
)

function validateField(name: string) {
  const field = props.schema.find((item) => item.name === name)
  if (!field?.rules?.length) {
    errors[name] = ''
    return true
  }

  for (const rule of field.rules) {
    const result = rule(draft[name])
    if (typeof result === 'string') {
      errors[name] = result
      return false
    }
  }

  errors[name] = ''
  return true
}

function validateForm() {
  let valid = true
  props.schema.forEach((field) => {
    const fieldValid = validateField(field.name)
    if (!fieldValid) {
      valid = false
    }
  })
  return valid
}

function submit() {
  if (!validateForm()) {
    emit('validationFailed', { ...errors })
    return
  }
  emit('submit', { ...draft })
}

const schema = computed(() => props.schema)

export type { FieldSchema as DynamicFieldSchema }
</script>

<style scoped lang="scss">
.form {
  display: grid;
  gap: 16px;
}

.form__fields {
  padding: 0;
  border: none;
  margin: 0;
  display: grid;
  gap: 16px;
}

.form__field {
  display: grid;
  gap: 8px;
}

.form__label {
  font-weight: 600;
}

.form__control {
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  font: inherit;
}

.form__error {
  margin: 0;
  font-size: 12px;
  color: var(--color-danger);
}

.form__submit {
  border: none;
  background: var(--color-primary);
  color: #fff;
  padding: 10px 20px;
  border-radius: var(--radius-md);
  cursor: pointer;
}
</style>
