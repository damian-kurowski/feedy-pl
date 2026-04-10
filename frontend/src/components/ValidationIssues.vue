<script setup lang="ts">
import { ref, computed } from 'vue'

export interface Issue {
  level: string
  field: string
  message: string
  product_id: string
  product_name: string
  rule: string
}

const props = defineProps<{
  issues: Issue[]
}>()

const activeFilter = ref<'all' | 'error' | 'warning'>('all')

const filtered = computed(() => {
  if (activeFilter.value === 'all') return props.issues
  return props.issues.filter(i => i.level === activeFilter.value)
})

const errorCount = computed(() => props.issues.filter(i => i.level === 'error').length)
const warningCount = computed(() => props.issues.filter(i => i.level === 'warning').length)
</script>

<template>
  <div>
    <div class="flex gap-2 mb-3">
      <button
        class="px-3 py-1 text-xs font-medium rounded-full cursor-pointer"
        :class="activeFilter === 'all' ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
        @click="activeFilter = 'all'"
      >
        Wszystko ({{ issues.length }})
      </button>
      <button
        class="px-3 py-1 text-xs font-medium rounded-full cursor-pointer"
        :class="activeFilter === 'error' ? 'bg-red-600 text-white' : 'bg-red-50 text-red-600 hover:bg-red-100'"
        @click="activeFilter = 'error'"
      >
        Bledy ({{ errorCount }})
      </button>
      <button
        class="px-3 py-1 text-xs font-medium rounded-full cursor-pointer"
        :class="activeFilter === 'warning' ? 'bg-yellow-600 text-white' : 'bg-yellow-50 text-yellow-600 hover:bg-yellow-100'"
        @click="activeFilter = 'warning'"
      >
        Ostrzezenia ({{ warningCount }})
      </button>
    </div>
    <div class="space-y-1 max-h-80 overflow-y-auto">
      <div
        v-for="(issue, idx) in filtered.slice(0, 50)"
        :key="idx"
        class="flex items-start gap-2 px-3 py-2 rounded text-sm"
        :class="issue.level === 'error' ? 'bg-red-50' : 'bg-yellow-50'"
      >
        <span class="shrink-0 mt-0.5" :class="issue.level === 'error' ? 'text-red-500' : 'text-yellow-500'">
          {{ issue.level === 'error' ? 'x' : '!' }}
        </span>
        <div class="min-w-0">
          <p :class="issue.level === 'error' ? 'text-red-700' : 'text-yellow-700'">{{ issue.message }}</p>
          <p class="text-xs text-gray-400 mt-0.5 truncate">
            Produkt: {{ issue.product_name }} ({{ issue.product_id }}) | Pole: {{ issue.field }}
          </p>
        </div>
      </div>
      <p v-if="filtered.length === 0" class="text-sm text-gray-400 py-2">Brak problemow w tej kategorii.</p>
      <p v-if="filtered.length > 50" class="text-xs text-gray-400 py-2">Pokazano 50 z {{ filtered.length }} problemow.</p>
    </div>
  </div>
</template>
