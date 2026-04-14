<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'

interface SearchResult {
  id: number
  feed_in_id: number
  feed_in_name: string
  product_name: string
  ean: string | null
  price: string | null
  category: string | null
  image: string | null
  custom_product: boolean
}

const open = ref(false)
const query = ref('')
const results = ref<SearchResult[]>([])
const loading = ref(false)
const activeIdx = ref(0)
const inputRef = ref<HTMLInputElement | null>(null)
const router = useRouter()

const RECENT_KEY = 'global_search_recent_v1'
const recent = ref<string[]>([])

function loadRecent() {
  try {
    recent.value = JSON.parse(localStorage.getItem(RECENT_KEY) || '[]')
  } catch { recent.value = [] }
}
function saveRecent(q: string) {
  if (!q.trim()) return
  const next = [q, ...recent.value.filter((x) => x !== q)].slice(0, 5)
  recent.value = next
  try { localStorage.setItem(RECENT_KEY, JSON.stringify(next)) } catch {}
}

let searchTimeout: ReturnType<typeof setTimeout>
watch(query, (q) => {
  clearTimeout(searchTimeout)
  if (!q || q.trim().length < 2) {
    results.value = []
    return
  }
  loading.value = true
  searchTimeout = setTimeout(async () => {
    try {
      const { data } = await api.get('/feeds-in/search/global', { params: { q } })
      results.value = data.results || []
      activeIdx.value = 0
    } catch {
      results.value = []
    } finally {
      loading.value = false
    }
  }, 200)
})

function onKeydown(e: KeyboardEvent) {
  // Cmd+K / Ctrl+K to open
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    openModal()
    return
  }
  if (!open.value) return
  if (e.key === 'Escape') {
    closeModal()
  } else if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeIdx.value = Math.min(activeIdx.value + 1, results.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeIdx.value = Math.max(activeIdx.value - 1, 0)
  } else if (e.key === 'Enter' && results.value[activeIdx.value]) {
    e.preventDefault()
    selectResult(results.value[activeIdx.value])
  }
}

async function openModal() {
  open.value = true
  loadRecent()
  await nextTick()
  inputRef.value?.focus()
}

function closeModal() {
  open.value = false
  query.value = ''
  results.value = []
  activeIdx.value = 0
}

function selectResult(r: SearchResult) {
  saveRecent(query.value)
  router.push(`/feeds-in/${r.feed_in_id}`)
  closeModal()
}

function selectRecent(q: string) {
  query.value = q
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))

defineExpose({ openModal })
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[90] flex items-start justify-center bg-black/50 backdrop-blur-sm p-4 sm:p-10"
      role="dialog"
      aria-modal="true"
      aria-label="Wyszukiwarka produktów"
      @click.self="closeModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] flex flex-col overflow-hidden">
        <!-- Search input -->
        <div class="flex items-center gap-3 px-4 py-3 border-b border-gray-200">
          <svg class="w-5 h-5 text-gray-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" /></svg>
          <input
            ref="inputRef"
            v-model="query"
            type="text"
            placeholder="Szukaj produktu po nazwie, EAN, SKU lub kategorii..."
            class="flex-1 bg-transparent text-base text-gray-900 placeholder-gray-400 focus:outline-none"
            aria-label="Wyszukaj produkt"
          />
          <kbd class="hidden sm:inline-block text-[10px] font-semibold text-gray-400 border border-gray-200 rounded px-1.5 py-0.5">ESC</kbd>
        </div>

        <!-- Results -->
        <div class="overflow-y-auto flex-1">
          <div v-if="loading" class="p-8 text-center text-sm text-gray-400">Wyszukiwanie...</div>

          <div v-else-if="!query && recent.length > 0" class="p-3">
            <p class="text-[11px] uppercase font-semibold text-gray-400 tracking-wider px-3 py-2">Ostatnie wyszukiwania</p>
            <button
              v-for="q in recent"
              :key="q"
              type="button"
              class="w-full text-left px-3 py-2 hover:bg-gray-50 rounded-lg text-sm text-gray-700 cursor-pointer flex items-center gap-2"
              @click="selectRecent(q)"
            >
              <svg class="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" /></svg>
              {{ q }}
            </button>
          </div>

          <div v-else-if="!query" class="p-8 text-center text-sm text-gray-400">
            Wpisz min. 2 znaki, aby rozpocząć wyszukiwanie
          </div>

          <div v-else-if="results.length === 0" class="p-8 text-center text-sm text-gray-400">
            Brak wyników dla „{{ query }}"
          </div>

          <ul v-else class="py-2">
            <li
              v-for="(r, idx) in results"
              :key="r.id"
              class="px-3 py-2.5 cursor-pointer flex items-start gap-3"
              :class="idx === activeIdx ? 'bg-indigo-50' : 'hover:bg-gray-50'"
              @click="selectResult(r)"
              @mouseenter="activeIdx = idx"
            >
              <img v-if="r.image" :src="r.image" :alt="r.product_name" class="w-10 h-10 object-contain rounded border border-gray-200 bg-white shrink-0" loading="lazy" @error="($event.target as HTMLImageElement).style.display='none'" />
              <div v-else class="w-10 h-10 rounded bg-gray-100 shrink-0"></div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{{ r.product_name }}</p>
                <div class="flex items-center gap-2 text-[11px] text-gray-500 mt-0.5">
                  <span class="truncate max-w-[150px]">{{ r.feed_in_name }}</span>
                  <template v-if="r.ean"><span>·</span><span class="font-mono">{{ r.ean }}</span></template>
                  <template v-if="r.price"><span>·</span><span>{{ r.price }}</span></template>
                  <template v-if="r.custom_product"><span>·</span><span class="text-indigo-600">ręczny</span></template>
                </div>
              </div>
              <kbd v-if="idx === activeIdx" class="hidden sm:inline-block text-[10px] font-semibold text-gray-400 border border-gray-200 rounded px-1.5 py-0.5 self-center">↵</kbd>
            </li>
          </ul>
        </div>

        <!-- Footer hints -->
        <div class="px-4 py-2 border-t border-gray-100 bg-gray-50 flex items-center gap-4 text-[11px] text-gray-400">
          <span class="flex items-center gap-1"><kbd class="border border-gray-200 rounded px-1">↑</kbd><kbd class="border border-gray-200 rounded px-1">↓</kbd> nawigacja</span>
          <span class="flex items-center gap-1"><kbd class="border border-gray-200 rounded px-1">↵</kbd> wybierz</span>
          <span class="ml-auto">{{ results.length }} {{ results.length === 1 ? 'wynik' : results.length < 5 ? 'wyniki' : 'wyników' }}</span>
        </div>
      </div>
    </div>
  </Teleport>
</template>
