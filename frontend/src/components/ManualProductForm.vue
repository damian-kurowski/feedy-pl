<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  save: [name: string, value: Record<string, string>]
  cancel: []
}>()

const name = ref('')
const fields = ref<{ key: string; value: string }[]>([
  { key: 'url', value: '' },
  { key: 'price', value: '' },
  { key: 'category', value: '' },
  { key: 'description', value: '' },
  { key: 'image', value: '' },
  { key: 'brand', value: '' },
  { key: 'ean', value: '' },
  { key: 'availability', value: '1' },
])

function addField() {
  fields.value.push({ key: '', value: '' })
}

function removeField(idx: number) {
  fields.value.splice(idx, 1)
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
  // Reset
  name.value = ''
  fields.value.forEach(f => f.value = '')
}
</script>

<template>
  <div class="bg-white border border-gray-200 rounded-xl p-5">
    <h3 class="font-heading text-base font-semibold text-gray-900 mb-4">Dodaj produkt ręcznie</h3>

    <div class="space-y-3">
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Nazwa produktu *</label>
        <input v-model="name" type="text" placeholder="np. Koszulka polo męska XL"
          class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
      </div>

      <div v-for="(field, idx) in fields" :key="idx" class="flex gap-2">
        <input v-model="field.key" type="text" placeholder="Pole (np. price)"
          class="w-1/3 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
        <input v-model="field.value" type="text" :placeholder="field.key === 'price' ? 'np. 49.99' : field.key === 'url' ? 'https://...' : ''"
          class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
        <button @click="removeField(idx)" class="text-red-400 hover:text-red-600 text-xs cursor-pointer px-2" title="Usuń pole">x</button>
      </div>

      <button @click="addField" class="text-xs text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer">+ Dodaj własne pole</button>
    </div>

    <div class="flex gap-2 mt-4">
      <button @click="handleSave" :disabled="!name.trim()"
        class="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold rounded-lg cursor-pointer transition">
        Dodaj produkt
      </button>
      <button @click="emit('cancel')" class="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg cursor-pointer transition">
        Anuluj
      </button>
    </div>
  </div>
</template>
