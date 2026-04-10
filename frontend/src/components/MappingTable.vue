<script setup lang="ts">
import { computed } from 'vue'
import type { StructureElement } from '../stores/feedsOut'
import { isImageField } from '../utils/imageExtractor'

const props = defineProps<{
  rows: StructureElement[]
  sampleProduct: Record<string, any> | null
}>()

const emit = defineEmits<{
  remove: [index: number]
  add: []
}>()

const sourceKeys = computed(() => {
  if (!props.sampleProduct) return []
  return Object.keys(props.sampleProduct)
})

function previewValue(pathIn: string | null): string {
  if (!pathIn || !props.sampleProduct) return ''
  const val = props.sampleProduct[pathIn]
  if (val === undefined || val === null) return ''
  if (typeof val === 'object') return '[obiekt]'
  const str = String(val)
  return str.length > 60 ? str.slice(0, 60) + '...' : str
}

function previewImageUrl(pathIn: string | null): string | null {
  if (!pathIn || !props.sampleProduct || !isImageField(pathIn)) return null
  const val = props.sampleProduct[pathIn]
  if (typeof val === 'string' && val.startsWith('http')) return val
  if (typeof val === 'object' && val) {
    const obj = val as Record<string, unknown>
    for (const v of Object.values(obj)) {
      if (typeof v === 'object' && v) {
        const inner = v as Record<string, unknown>
        if (typeof inner['@url'] === 'string') return inner['@url']
      }
      if (typeof v === 'string' && v.startsWith('http')) return v
    }
  }
  return null
}
</script>

<template>
  <div class="overflow-x-auto">
    <table class="w-full text-sm border border-gray-200 rounded-lg">
      <thead class="bg-gray-50">
        <tr>
          <th class="text-left px-4 py-3 font-medium text-gray-700">Pole wyjściowe</th>
          <th class="text-left px-4 py-3 font-medium text-gray-700">Źródło</th>
          <th class="text-left px-4 py-3 font-medium text-gray-700">Typ</th>
          <th class="text-left px-4 py-3 font-medium text-gray-700">Podgląd</th>
          <th class="px-4 py-3 w-12"></th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, idx) in rows"
          :key="idx"
          class="border-t border-gray-100 hover:bg-gray-50 transition-colors"
        >
          <!-- Pole wyjściowe -->
          <td class="px-4 py-3">
            <span v-if="!row.custom_element" class="text-sm font-medium text-gray-900">
              {{ row.element_name_out }}
            </span>
            <input
              v-else
              v-model="row.element_name_out"
              type="text"
              class="w-full px-2 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="np. nazwa"
            />
          </td>

          <!-- Źródło (dropdown) -->
          <td class="px-4 py-3">
            <select
              v-model="row.path_in"
              class="w-full px-2 py-1.5 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option :value="null">-- Wybierz pole --</option>
              <option v-for="key in sourceKeys" :key="key" :value="key">
                {{ key }}
              </option>
            </select>
          </td>

          <!-- Typ -->
          <td class="px-4 py-3">
            <span
              v-if="row.attribute"
              class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
            >
              atrybut
            </span>
            <span
              v-else
              class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
            >
              element
            </span>
          </td>

          <!-- Podgląd -->
          <td class="px-4 py-3 text-gray-500 truncate max-w-[200px] text-sm">
            <div v-if="previewImageUrl(row.path_in)" class="flex items-center gap-2">
              <img
                :src="previewImageUrl(row.path_in)!"
                alt="Preview"
                class="w-8 h-8 object-cover rounded border border-gray-200"
              />
              <span class="truncate text-xs">{{ previewValue(row.path_in) }}</span>
            </div>
            <span v-else>{{ previewValue(row.path_in) }}</span>
          </td>

          <!-- Usuń -->
          <td class="px-4 py-3 text-center">
            <button
              type="button"
              class="text-red-400 hover:text-red-600 transition-colors cursor-pointer"
              title="Usuń pole"
              @click="emit('remove', idx)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </td>
        </tr>
        <tr v-if="rows.length === 0">
          <td colspan="5" class="px-4 py-6 text-center text-gray-400">
            Brak pól. Dodaj pierwsze pole poniżej.
          </td>
        </tr>
      </tbody>
    </table>
    <button
      type="button"
      class="mt-3 text-sm text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer"
      @click="emit('add')"
    >
      + Dodaj pole
    </button>
  </div>
</template>
