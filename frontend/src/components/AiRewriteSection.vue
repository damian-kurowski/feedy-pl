<script setup lang="ts">
import { ref } from 'vue'
import api from '../api/client'

const props = defineProps<{ feedOutId: number }>()
const loading = ref(false)
const applying = ref(false)
const rewrites = ref<any[]>([])
const selected = ref<Set<number>>(new Set())
const error = ref('')

async function generateRewrites() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.post(`/feeds-out/${props.feedOutId}/ai-rewrite`, { limit: 10 })
    rewrites.value = data.rewrites
    selected.value = new Set(data.rewrites.filter((r: any) => r.changed).map((r: any) => r.product_id))
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Błąd generowania opisów AI'
  } finally { loading.value = false }
}

function toggleSelect(id: number) {
  if (selected.value.has(id)) selected.value.delete(id)
  else selected.value.add(id)
}

async function applySelected() {
  applying.value = true
  try {
    const items = rewrites.value
      .filter(r => r.changed && selected.value.has(r.product_id))
      .map(r => ({ product_id: r.product_id, field: 'desc', value: r.rewritten }))
    await api.post(`/feeds-out/${props.feedOutId}/ai-rewrite/apply`, { rewrites: items })
    rewrites.value = []
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Błąd stosowania opisow'
  } finally { applying.value = false }
}
</script>

<template>
  <div>
    <p class="text-sm text-gray-500 mb-4">Uzyj AI do przepisania opisow produktow pod wymogi platformy docelowej.</p>

    <div v-if="error" class="mb-3 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">{{ error }}</div>

    <button
      v-if="rewrites.length === 0"
      :disabled="loading"
      class="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-medium rounded-md text-sm cursor-pointer"
      @click="generateRewrites"
    >
      {{ loading ? 'Generowanie...' : 'Generuj opisy AI (10 produktów)' }}
    </button>

    <div v-if="rewrites.length > 0" class="space-y-3 mt-4">
      <div v-for="r in rewrites" :key="r.product_id" class="border rounded-lg p-3" :class="r.changed ? 'border-purple-200 bg-purple-50' : 'border-gray-200 bg-gray-50'">
        <div class="flex items-center gap-2 mb-2">
          <input v-if="r.changed" type="checkbox" :checked="selected.has(r.product_id)" @change="toggleSelect(r.product_id)" class="rounded" />
          <span class="text-sm font-medium text-gray-900">{{ r.product_name }}</span>
          <span v-if="!r.changed" class="text-xs text-gray-400">Bez zmian</span>
        </div>
        <div v-if="r.changed">
          <p class="text-xs text-gray-400 mb-1">Oryginal:</p>
          <p class="text-xs text-gray-600 mb-2">{{ r.original }}</p>
          <p class="text-xs text-purple-600 mb-1">AI wersja:</p>
          <p class="text-xs text-purple-800">{{ r.rewritten }}</p>
        </div>
      </div>

      <div class="flex gap-2 mt-4">
        <button
          :disabled="applying || selected.size === 0"
          class="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-medium rounded-md text-sm cursor-pointer"
          @click="applySelected"
        >
          {{ applying ? 'Stosowanie...' : `Zastosuj wybrane (${selected.size})` }}
        </button>
        <button class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md text-sm cursor-pointer" @click="rewrites = []">
          Anuluj
        </button>
      </div>
    </div>
  </div>
</template>
