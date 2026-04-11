<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api/client'

const data = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const { data: d } = await api.get('/feeds-in/recommendations')
    data.value = d
  } catch {} finally { loading.value = false }
})

function severityColor(severity: string) {
  switch (severity) {
    case 'critical': return 'bg-red-50 border-red-200 text-red-800'
    case 'warning': return 'bg-yellow-50 border-yellow-200 text-yellow-800'
    case 'info': return 'bg-blue-50 border-blue-200 text-blue-800'
    default: return 'bg-gray-50 border-gray-200 text-gray-800'
  }
}

function severityIcon(severity: string) {
  switch (severity) {
    case 'critical': return '!'
    case 'warning': return '~'
    case 'info': return 'i'
    default: return '?'
  }
}

function severityDot(severity: string) {
  switch (severity) {
    case 'critical': return 'bg-red-500'
    case 'warning': return 'bg-yellow-500'
    case 'info': return 'bg-blue-500'
    default: return 'bg-gray-500'
  }
}
</script>

<template>
  <div v-if="loading" class="text-sm text-gray-400 py-4">Analizuję Twoje feedy...</div>

  <div v-else-if="data" class="space-y-4">
    <!-- Alerts — critical issues -->
    <div v-if="data.alerts.length > 0">
      <div v-for="(alert, idx) in data.alerts" :key="'a'+idx"
        class="flex items-start gap-3 p-4 rounded-xl border mb-2"
        :class="severityColor(alert.severity)"
      >
        <span class="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white"
          :class="severityDot(alert.severity)">{{ severityIcon(alert.severity) }}</span>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-semibold">{{ alert.title }}</p>
          <p class="text-xs mt-0.5 opacity-80">{{ alert.description }}</p>
        </div>
        <router-link
          v-if="alert.action"
          :to="alert.action.url"
          class="shrink-0 text-xs font-semibold px-3 py-1.5 rounded-lg bg-white/80 hover:bg-white transition-colors"
        >
          {{ alert.action.label }}
        </router-link>
      </div>
    </div>

    <!-- Recommendations — things to improve -->
    <div v-if="data.recommendations.length > 0">
      <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Do poprawy</h3>
      <div class="space-y-2">
        <div v-for="(rec, idx) in data.recommendations" :key="'r'+idx"
          class="flex items-start gap-3 p-4 bg-white rounded-xl border border-gray-200 hover:border-gray-300 transition-colors"
        >
          <span class="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold"
            :class="rec.quality_score != null
              ? (rec.quality_score >= 70 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700')
              : 'bg-gray-100 text-gray-600'"
          >
            {{ rec.quality_score != null ? rec.quality_score + '%' : rec.icon === 'barcode' ? 'EAN' : rec.icon === 'image' ? 'IMG' : '!' }}
          </span>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900">{{ rec.title }}</p>
            <p class="text-xs text-gray-500 mt-0.5">{{ rec.description }}</p>
          </div>
          <router-link
            v-if="rec.action"
            :to="rec.action.url"
            class="shrink-0 text-xs font-medium text-indigo-600 hover:text-indigo-800 px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors"
          >
            {{ rec.action.label }}
          </router-link>
        </div>
      </div>
    </div>

    <!-- Suggestions — growth opportunities -->
    <div v-if="data.suggestions.length > 0">
      <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Sugestie</h3>
      <div class="grid sm:grid-cols-3 gap-2">
        <div v-for="(sug, idx) in data.suggestions" :key="'s'+idx"
          class="p-4 bg-gradient-to-br from-indigo-50 to-white rounded-xl border border-indigo-100 hover:border-indigo-200 transition-colors"
        >
          <p class="text-sm font-medium text-gray-900">{{ sug.title }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ sug.description }}</p>
          <router-link
            v-if="sug.action"
            :to="sug.action.url"
            class="inline-block mt-3 text-xs font-semibold text-indigo-600 hover:text-indigo-800"
          >
            {{ sug.action.label }} →
          </router-link>
        </div>
      </div>
    </div>

    <!-- All good state -->
    <div v-if="data.alerts.length === 0 && data.recommendations.length === 0"
      class="p-6 bg-green-50 border border-green-200 rounded-2xl text-center"
    >
      <p class="text-green-800 font-semibold">Wszystko działa prawidłowo</p>
      <p class="text-green-600 text-sm mt-1">Brak alertów i problemów do naprawy.</p>
    </div>
  </div>
</template>
