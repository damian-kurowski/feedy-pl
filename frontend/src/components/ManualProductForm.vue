<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  initial?: { name: string; value: Record<string, unknown> } | null
}>()

const emit = defineEmits<{
  save: [name: string, value: Record<string, string>]
  cancel: []
}>()

const name = ref('')
const fields = ref<{ key: string; value: string }[]>([])

function defaultFields() {
  return [
    { key: 'url', value: '' },
    { key: 'price', value: '' },
    { key: 'category', value: '' },
    { key: 'description', value: '' },
    { key: 'image', value: '' },
    { key: 'image_alt_1', value: '' },
    { key: 'image_alt_2', value: '' },
    { key: 'brand', value: '' },
    { key: 'ean', value: '' },
    { key: 'availability', value: '1' },
  ]
}

function loadInitial() {
  if (props.initial) {
    name.value = props.initial.name
    const pv = props.initial.value || {}
    fields.value = Object.entries(pv)
      .filter(([k]) => k !== 'name')
      .map(([k, v]) => ({ key: k, value: String(v ?? '') }))
    if (fields.value.length === 0) fields.value = defaultFields()
  } else {
    name.value = ''
    fields.value = defaultFields()
  }
}

loadInitial()
watch(() => props.initial, loadInitial)

function addField() {
  fields.value.push({ key: '', value: '' })
}

function removeField(idx: number) {
  fields.value.splice(idx, 1)
}

function moveField(idx: number, dir: -1 | 1) {
  const target = idx + dir
  if (target < 0 || target >= fields.value.length) return
  const arr = fields.value
  ;[arr[idx], arr[target]] = [arr[target], arr[idx]]
}

function handleSave() {
  if (!name.value.trim()) return
  const pv: Record<string, string> = {}
  for (const f of fields.value) {
    if (f.key.trim() && f.value.trim()) {
      pv[f.key.trim()] = f.value.trim()
    }
  }
  pv['name'] = name.value.trim()
  emit('save', name.value.trim(), pv)
  if (!props.initial) {
    name.value = ''
    fields.value = defaultFields()
  }
}
</script>

<template>
  <div class="bg-white border border-gray-200 rounded-xl p-5">
    <h3 class="font-heading text-base font-semibold text-gray-900 mb-4">
      {{ props.initial ? 'Edytuj produkt' : 'Dodaj produkt ręcznie' }}
    </h3>

    <div class="space-y-3">
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Nazwa produktu *</label>
        <input v-model="name" type="text" placeholder="np. Koszulka polo męska XL"
          class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
      </div>

      <div v-for="(field, idx) in fields" :key="idx" class="flex items-stretch gap-2">
        <div class="flex flex-col gap-0.5 shrink-0 justify-center">
          <button type="button" @click="moveField(idx, -1)" :disabled="idx === 0"
            class="w-5 h-5 flex items-center justify-center text-gray-400 hover:text-indigo-600 disabled:opacity-20 disabled:cursor-not-allowed cursor-pointer"
            title="Przesuń w górę">
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 15l7-7 7 7"/></svg>
          </button>
          <button type="button" @click="moveField(idx, 1)" :disabled="idx === fields.length - 1"
            class="w-5 h-5 flex items-center justify-center text-gray-400 hover:text-indigo-600 disabled:opacity-20 disabled:cursor-not-allowed cursor-pointer"
            title="Przesuń w dół">
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
          </button>
        </div>
        <input v-model="field.key" type="text" placeholder="Pole (np. price)"
          class="w-1/3 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
        <input v-model="field.value" type="text" :placeholder="field.key === 'price' ? 'np. 49.99' : field.key === 'url' ? 'https://...' : ''"
          class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
        <button type="button" @click="removeField(idx)"
          class="text-red-400 hover:text-red-600 text-xs cursor-pointer px-2" title="Usuń pole">×</button>
      </div>

      <button type="button" @click="addField" class="text-xs text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer">+ Dodaj własne pole</button>
    </div>

    <div class="flex gap-2 mt-4">
      <button type="button" @click="handleSave" :disabled="!name.trim()"
        class="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold rounded-lg cursor-pointer transition">
        {{ props.initial ? 'Zapisz zmiany' : 'Dodaj produkt' }}
      </button>
      <button type="button" @click="emit('cancel')"
        class="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg cursor-pointer transition">
        Anuluj
      </button>
    </div>
  </div>
</template>
