<script setup lang="ts">
import { ref, computed } from 'vue'
const props = defineProps<{ sampleProduct: Record<string, any> | null }>()
const emit = defineEmits<{ confirm: [rule: any]; cancel: [] }>()

const field = ref('desc')
const template = ref('')

const availableKeys = computed(() => {
  if (!props.sampleProduct) return []
  return Object.entries(props.sampleProduct).filter(([_, v]) => typeof v === 'string' || typeof v === 'number').map(([k]) => k)
})

const preview = computed(() => {
  if (!props.sampleProduct || !template.value) return ''
  let result = template.value
  for (const [key, val] of Object.entries(props.sampleProduct)) {
    if (typeof val === 'string' || typeof val === 'number')
      result = result.replace(new RegExp(`\\{${key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\}`, 'g'), String(val).trim())
  }
  return result.replace(/\{[^}]+\}/g, '').replace(/ +/g, ' ').trim()
})

function insertKey(key: string) { template.value += `{${key}}` }
</script>

<template>
  <div class="p-3 bg-white border border-indigo-200 rounded-md space-y-3">
    <div class="text-sm font-medium text-gray-700">Szablon opisu</div>
    <div>
      <label class="text-xs text-gray-500">Pole docelowe</label>
      <select v-model="field" class="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm mt-1">
        <option value="desc">desc</option><option value="description">description</option>
        <option value="name">name</option><option value="title">title</option>
      </select>
    </div>
    <div>
      <label class="text-xs text-gray-500">Szablon (uzyj {nazwa_pola} jako placeholder)</label>
      <textarea v-model="template" rows="3" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm mt-1 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="np. Kup {name} marki {brand}. {desc}" />
    </div>
    <div v-if="availableKeys.length > 0">
      <label class="text-xs text-gray-500">Dostępne pola (kliknij aby wstawic):</label>
      <div class="flex flex-wrap gap-1 mt-1">
        <button v-for="key in availableKeys" :key="key" class="px-2 py-0.5 text-xs bg-gray-100 hover:bg-indigo-100 text-gray-600 hover:text-indigo-700 rounded cursor-pointer" @click="insertKey(key)">
          {{ '{' }}{{ key }}{{ '}' }}
        </button>
      </div>
    </div>
    <div v-if="preview" class="bg-gray-50 rounded p-2">
      <label class="text-xs text-gray-500">Podglad (pierwszy produkt):</label>
      <p class="text-sm text-gray-700 mt-1">{{ preview }}</p>
    </div>
    <div class="flex gap-2">
      <button class="py-1 px-3 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700 cursor-pointer" @click="emit('confirm', { type: 'description_template', field, template })">Dodaj</button>
      <button class="py-1 px-3 text-sm bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 cursor-pointer" @click="emit('cancel')">Anuluj</button>
    </div>
  </div>
</template>
