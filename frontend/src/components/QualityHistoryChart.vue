<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import api from '../api/client'

interface Snapshot {
  created_at: string
  quality_score: number
  error_count: number
  warning_count: number
  products_count: number
}

const props = defineProps<{
  feedOutId: number
  days?: number
  variant?: 'sparkline' | 'full'
}>()

const snapshots = ref<Snapshot[]>([])
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get(`/feeds-out/${props.feedOutId}/quality-history`, {
      params: { days: props.days || 30 },
    })
    snapshots.value = data.snapshots || []
  } catch {
    snapshots.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => props.feedOutId, load)

const points = computed(() => {
  if (snapshots.value.length < 2) return ''
  const w = props.variant === 'full' ? 600 : 80
  const h = props.variant === 'full' ? 200 : 28
  const xs = snapshots.value.map((_, i) => (i / (snapshots.value.length - 1)) * w)
  const ys = snapshots.value.map((s) => h - (s.quality_score / 100) * h)
  return xs.map((x, i) => `${x.toFixed(1)},${ys[i].toFixed(1)}`).join(' ')
})

const trend = computed(() => {
  if (snapshots.value.length < 2) return 0
  const first = snapshots.value[0].quality_score
  const last = snapshots.value[snapshots.value.length - 1].quality_score
  return last - first
})

const trendLabel = computed(() => {
  if (snapshots.value.length < 2) return ''
  if (trend.value > 0) return `+${trend.value}`
  return `${trend.value}`
})

const trendColor = computed(() => {
  if (trend.value > 0) return 'text-green-600'
  if (trend.value < 0) return 'text-red-600'
  return 'text-gray-400'
})

const fullViewBox = computed(() => '0 0 600 200')
const sparkViewBox = computed(() => '0 0 80 28')

function formatDate(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleDateString('pl-PL', { day: 'numeric', month: 'short' })
}

function snapshotColor(score: number): string {
  if (score >= 80) return '#16a34a'
  if (score >= 60) return '#ca8a04'
  return '#dc2626'
}
</script>

<template>
  <!-- Sparkline variant — small inline -->
  <div v-if="variant !== 'full'" class="inline-flex items-center gap-2">
    <svg v-if="snapshots.length >= 2" :viewBox="sparkViewBox" class="w-20 h-7" preserveAspectRatio="none">
      <polyline :points="points" fill="none" :stroke="snapshotColor(snapshots[snapshots.length-1].quality_score)" stroke-width="1.5" stroke-linejoin="round" />
    </svg>
    <span v-if="snapshots.length >= 2" class="text-[10px] font-semibold" :class="trendColor">
      {{ trendLabel }}
    </span>
  </div>

  <!-- Full chart variant -->
  <div v-else class="bg-white border border-gray-200 rounded-2xl p-5">
    <div class="flex items-center gap-3 mb-4">
      <h3 class="font-heading text-base font-bold text-gray-900">Historia jakości feedu</h3>
      <span v-if="trend !== 0" class="text-xs font-semibold px-2 py-0.5 rounded-full" :class="trend > 0 ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
        {{ trendLabel }} pkt w {{ days || 30 }} dni
      </span>
    </div>

    <div v-if="loading" class="text-sm text-gray-400 py-8 text-center">Ładowanie wykresu...</div>

    <div v-else-if="snapshots.length < 2" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-200 rounded-xl">
      Brak wystarczającej historii. Wykres pojawi się po kilku weryfikacjach jakości.
    </div>

    <div v-else>
      <svg :viewBox="fullViewBox" class="w-full h-48" preserveAspectRatio="none">
        <!-- Y axis grid lines at 25/50/75/100 -->
        <line v-for="y in [50, 100, 150, 200]" :key="y" :x1="0" :y1="y" :x2="600" :y2="y" stroke="#f3f4f6" stroke-width="1" />
        <line :x1="0" :y1="40" :x2="600" :y2="40" stroke="#10b981" stroke-width="1" stroke-dasharray="4 4" opacity="0.4" />
        <!-- Area under line -->
        <polyline :points="`0,200 ${points} 600,200`" fill="#6366f1" fill-opacity="0.08" stroke="none" />
        <!-- Main line -->
        <polyline :points="points" fill="none" stroke="#6366f1" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" />
        <!-- Data points -->
        <circle v-for="(s, i) in snapshots" :key="i"
          :cx="(i / (snapshots.length - 1)) * 600"
          :cy="200 - (s.quality_score / 100) * 200"
          r="3"
          :fill="snapshotColor(s.quality_score)" />
      </svg>

      <div class="mt-3 flex justify-between text-[10px] text-gray-400 font-medium">
        <span>{{ formatDate(snapshots[0].created_at) }}</span>
        <span class="text-gray-300">|</span>
        <span class="font-bold text-gray-700">Quality Score: {{ snapshots[snapshots.length-1].quality_score }}</span>
        <span class="text-gray-300">|</span>
        <span>{{ formatDate(snapshots[snapshots.length-1].created_at) }}</span>
      </div>

      <div class="mt-4 grid grid-cols-3 gap-3 text-center">
        <div class="bg-gray-50 rounded-lg p-3">
          <p class="text-xl font-extrabold text-gray-900">{{ snapshots[snapshots.length-1].error_count }}</p>
          <p class="text-[10px] uppercase font-semibold text-gray-500 mt-0.5 tracking-wider">Błędy</p>
        </div>
        <div class="bg-gray-50 rounded-lg p-3">
          <p class="text-xl font-extrabold text-gray-900">{{ snapshots[snapshots.length-1].warning_count }}</p>
          <p class="text-[10px] uppercase font-semibold text-gray-500 mt-0.5 tracking-wider">Ostrzeżenia</p>
        </div>
        <div class="bg-gray-50 rounded-lg p-3">
          <p class="text-xl font-extrabold text-gray-900">{{ snapshots[snapshots.length-1].products_count }}</p>
          <p class="text-[10px] uppercase font-semibold text-gray-500 mt-0.5 tracking-wider">Produktów</p>
        </div>
      </div>
    </div>
  </div>
</template>
