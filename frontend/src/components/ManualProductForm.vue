<script setup lang="ts">
import { ref, watch } from 'vue'
import api from '../api/client'

const props = defineProps<{
  initial?: { name: string; value: Record<string, unknown> } | null
  error?: string
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

function isImageKey(key: string): boolean {
  const lower = (key || '').toLowerCase()
  return lower === 'image' || lower === 'img' || lower === 'photo' || lower === 'picture'
    || lower.startsWith('image') || lower.startsWith('img') || lower.startsWith('photo')
}

const uploadingIdx = ref<number | null>(null)
async function uploadToField(idx: number, event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return
  uploadingIdx.value = idx
  try {
    const formData = new FormData()
    formData.append('file', input.files[0])
    const { data } = await api.post('/images/upload', formData)
    if (fields.value[idx]) fields.value[idx].value = data.url
  } catch {
    alert('Błąd uploadu zdjęcia')
  } finally {
    uploadingIdx.value = null
    input.value = ''
  }
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

    <div v-if="props.error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">{{ props.error }}</div>

    <div class="space-y-3">
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Nazwa produktu *</label>
        <input v-model="name" type="text" placeholder="np. Koszulka polo męska XL"
          class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
      </div>

      <div v-for="(field, idx) in fields" :key="idx" class="flex flex-wrap sm:flex-nowrap items-stretch gap-2 bg-gray-50 sm:bg-transparent rounded-lg p-2 sm:p-0">
        <div class="flex flex-col gap-0.5 shrink-0 justify-center">
          <button type="button" @click="moveField(idx, -1)" :disabled="idx === 0"
            class="w-6 h-6 sm:w-5 sm:h-5 flex items-center justify-center text-gray-400 hover:text-indigo-600 disabled:opacity-20 disabled:cursor-not-allowed cursor-pointer"
            title="Przesuń w górę">
            <svg class="w-3.5 h-3.5 sm:w-3 sm:h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 15l7-7 7 7"/></svg>
          </button>
          <button type="button" @click="moveField(idx, 1)" :disabled="idx === fields.length - 1"
            class="w-6 h-6 sm:w-5 sm:h-5 flex items-center justify-center text-gray-400 hover:text-indigo-600 disabled:opacity-20 disabled:cursor-not-allowed cursor-pointer"
            title="Przesuń w dół">
            <svg class="w-3.5 h-3.5 sm:w-3 sm:h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
          </button>
        </div>
        <input v-model="field.key" type="text" placeholder="Pole (np. price)"
          class="flex-1 sm:flex-none sm:w-1/3 px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
        <button type="button" @click="removeField(idx)"
          class="sm:hidden text-red-400 hover:text-red-600 text-base cursor-pointer px-2" title="Usuń pole">×</button>
        <div class="w-full sm:flex-1 min-w-0">
          <input v-model="field.value" type="text" :placeholder="field.key === 'price' ? 'np. 49.99' : field.key === 'url' ? 'https://...' : ''"
            class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
          <template v-if="isImageKey(field.key)">
            <div v-if="field.value" class="mt-1.5 flex items-center gap-2">
              <img :src="field.value" class="w-10 h-10 object-cover rounded border border-gray-200 bg-gray-50"
                @error="($event.target as HTMLImageElement).style.display='none'" />
              <span v-if="field.value.includes('gstatic.com') || field.value.includes('encrypted-tbn')"
                class="text-[11px] text-amber-600">⚠ Thumbnail Google — może nie ładować się w przeglądarce. Użyj „Wgraj".</span>
            </div>
            <label class="inline-block mt-1 text-[11px] text-indigo-600 hover:text-indigo-800 cursor-pointer font-medium">
              <input type="file" accept="image/*" class="hidden" @change="(e) => uploadToField(idx, e)" />
              {{ uploadingIdx === idx ? 'Przesyłanie...' : '+ Wgraj zdjęcie' }}
            </label>
          </template>
        </div>
        <button type="button" @click="removeField(idx)"
          class="hidden sm:block text-red-400 hover:text-red-600 text-xs cursor-pointer px-2 self-start pt-2" title="Usuń pole">×</button>
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
