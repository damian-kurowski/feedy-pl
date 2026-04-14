<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { extractImageUrls, isImageField } from '../utils/imageExtractor'
import api from '../api/client'

const props = defineProps<{ show: boolean; product: any | null }>()
const emit = defineEmits<{ close: []; save: [overrides: Record<string, string>, excluded: boolean]; restore: [] }>()

const overrides = ref<Record<string, string>>({})
const excluded = ref(false)

watch(() => props.product, (p) => {
  if (p?.override) { overrides.value = { ...p.override.field_overrides }; excluded.value = p.override.excluded }
  else { overrides.value = {}; excluded.value = false }
}, { immediate: true })

const fields = computed(() => {
  if (!props.product) return []
  return Object.entries(props.product.product_value)
    .filter(([_, v]) => typeof v === 'string' || typeof v === 'number')
    .map(([key, val]) => ({ key, original: String(val) }))
})

const mainImage = computed(() => props.product ? extractImageUrls(props.product.product_value).main : null)

const uploading = ref(false)

async function handleImageUpload(key: string, event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', input.files[0])
    const { data } = await api.post('/images/upload', formData)
    overrides.value = { ...overrides.value, [key]: data.url }
  } catch {
    // upload failed silently
  } finally { uploading.value = false }
}

function setOverride(key: string, value: string) {
  if (value === '' || value === fields.value.find(f => f.key === key)?.original) {
    const copy = { ...overrides.value }; delete copy[key]; overrides.value = copy
  } else { overrides.value = { ...overrides.value, [key]: value } }
}

function copyToClipboard(value: string) {
  void navigator.clipboard.writeText(value)
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show && product" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60" @click.self="emit('close')">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[85vh] flex flex-col">
        <div class="p-4 border-b flex items-center gap-3">
          <img v-if="mainImage" :src="mainImage" class="w-10 h-10 object-cover rounded border" />
          <div class="min-w-0 flex-1">
            <h3 class="font-semibold text-gray-900 truncate">{{ product.product_name }}</h3>
            <span class="text-xs" :class="product.status === 'modified' ? 'text-yellow-600' : product.status === 'excluded' ? 'text-red-600' : 'text-gray-400'">
              {{ product.status === 'modified' ? 'Zmieniony' : product.status === 'excluded' ? 'Wykluczony' : 'Oryginał' }}
            </span>
          </div>
          <button class="text-gray-400 hover:text-gray-600 cursor-pointer" @click="emit('close')">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        <div class="p-4 overflow-y-auto flex-1 space-y-3">
          <label class="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md cursor-pointer">
            <input type="checkbox" v-model="excluded" class="rounded" />
            <span class="text-sm text-red-700">Wyklucz z feedu wyjściowego</span>
          </label>
          <div v-for="field in fields" :key="field.key" class="border rounded-md p-3">
            <label class="text-xs font-medium text-gray-500 block mb-1">{{ field.key }}</label>
            <div class="flex items-center gap-1 mb-1">
              <span class="text-xs text-gray-400 truncate flex-1">Oryginał: {{ field.original }}</span>
              <button
                class="text-[10px] text-indigo-500 hover:text-indigo-700 cursor-pointer shrink-0 px-1"
                @click.stop="copyToClipboard(field.original)"
                title="Kopiuj wartość"
              >kopiuj</button>
            </div>
            <input type="text" :value="overrides[field.key] ?? ''" :placeholder="field.original"
              class="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              @input="setOverride(field.key, ($event.target as HTMLInputElement).value)" />
            <div v-if="isImageField(field.key)" class="mt-1">
              <label class="text-xs text-indigo-600 hover:text-indigo-800 cursor-pointer font-medium">
                {{ uploading ? 'Wgrywanie...' : 'Wgraj nowe zdjecie' }}
                <input type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="handleImageUpload(field.key, $event)" :disabled="uploading" />
              </label>
            </div>
          </div>
        </div>
        <div class="p-4 border-t flex items-center justify-between">
          <button v-if="product.override" class="text-sm text-red-600 hover:text-red-800 cursor-pointer" @click="emit('restore')">Przywróć oryginał</button>
          <div v-else></div>
          <div class="flex gap-2">
            <button class="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-md cursor-pointer" @click="emit('close')">Anuluj</button>
            <button class="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white rounded-md cursor-pointer" @click="emit('save', overrides, excluded)">Zapisz</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
