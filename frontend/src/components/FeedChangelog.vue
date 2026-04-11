<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api/client'

const props = defineProps<{ feedId: number }>()
const changes = ref<any[]>([])
const total = ref(0)
const loading = ref(false)
const limit = ref(20)

async function loadChanges() {
  loading.value = true
  try {
    const { data } = await api.get(`/feeds-in/${props.feedId}/changelog`, { params: { limit: limit.value } })
    changes.value = data.changes
    total.value = data.total
  } finally { loading.value = false }
}

function icon(type: string) {
  switch (type) {
    case 'added': return { symbol: '+', color: 'text-green-600 bg-green-50' }
    case 'removed': return { symbol: '-', color: 'text-red-600 bg-red-50' }
    case 'price_changed': return { symbol: '$', color: 'text-blue-600 bg-blue-50' }
    case 'modified': return { symbol: '~', color: 'text-yellow-600 bg-yellow-50' }
    default: return { symbol: '?', color: 'text-gray-600 bg-gray-50' }
  }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('pl-PL', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function loadMore() {
  limit.value += 20
  loadChanges()
}

onMounted(loadChanges)
</script>

<template>
  <div>
    <div v-if="loading && changes.length === 0" class="text-sm text-gray-400 py-4">Ładowanie...</div>
    <div v-else-if="changes.length === 0" class="text-sm text-gray-400 py-4">Brak zmian w historii. Zmiany pojawią się po kolejnym odświeżeniu feedu.</div>
    <div v-else class="space-y-2">
      <div v-for="change in changes" :key="change.id" class="flex items-start gap-3 py-2 border-b border-gray-100 last:border-0">
        <span class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0" :class="icon(change.change_type).color">
          {{ icon(change.change_type).symbol }}
        </span>
        <div class="flex-1 min-w-0">
          <span class="text-sm text-gray-900">{{ change.product_name }}</span>
          <span v-if="change.change_type === 'price_changed' && change.details" class="text-xs text-gray-500 ml-2">
            {{ change.details.old_price }} → {{ change.details.new_price }}
          </span>
          <span v-if="change.change_type === 'modified' && change.details?.changed_fields" class="text-xs text-gray-400 ml-2">
            ({{ change.details.changed_fields.join(', ') }})
          </span>
          <span v-if="change.change_type === 'added'" class="text-xs text-green-500 ml-2">nowy produkt</span>
          <span v-if="change.change_type === 'removed'" class="text-xs text-red-500 ml-2">usunięty</span>
        </div>
        <span class="text-xs text-gray-400 shrink-0">{{ formatDate(change.created_at) }}</span>
      </div>
    </div>
    <button v-if="changes.length < total" class="mt-3 text-sm text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer" @click="loadMore">
      Pokaz wiecej ({{ total - changes.length }} pozostalo)
    </button>
  </div>
</template>
