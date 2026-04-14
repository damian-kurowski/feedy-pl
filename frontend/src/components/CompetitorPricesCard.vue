<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import api from '../api/client'
import { useToast, getApiError } from '../composables/useToast'

const props = defineProps<{ feedId: number }>()
const toast = useToast()

interface Item {
  product_id: number
  product_name: string
  ean: string | null
  our_price: number | null
  lowest_price: number | null
  lowest_seller: string | null
  total_offers: number | null
  scraped_at: string | null
  diff_pct: number | null
  status: 'losing' | 'winning' | 'unknown'
}
interface Report {
  feed_in_id: number
  total_products: number
  with_snapshots: number
  winning: number
  losing: number
  no_data: number
  items: Item[]
}

const report = ref<Report | null>(null)
const loading = ref(false)
const scraping = ref(false)
const filter = ref<'all' | 'losing' | 'winning' | 'unknown'>('all')
const accessDenied = ref(false)

async function load() {
  loading.value = true
  accessDenied.value = false
  try {
    const { data } = await api.get(`/competitor-prices/feed/${props.feedId}`)
    report.value = data
  } catch (e: any) {
    if (e?.response?.status === 403) {
      accessDenied.value = true
    } else {
      toast.error(getApiError(e, 'Nie udało się załadować cen konkurencji'))
    }
  } finally {
    loading.value = false
  }
}

async function scrape() {
  scraping.value = true
  try {
    const { data } = await api.post(`/competitor-prices/feed/${props.feedId}/scrape`, null, { params: { limit: 20 } })
    if (data.scraped > 0) {
      toast.success(`Sprawdzono ${data.scraped} produktów na Ceneo`)
      await load()
    } else if (data.queued === 0) {
      toast.info('Wszystkie produkty zostały już sprawdzone w ostatnich 24h')
    } else {
      toast.warning(`Sprawdzanie nieudane (${data.failed} błędów). Spróbuj ponownie później.`)
    }
  } catch (e) {
    toast.error(getApiError(e, 'Nie udało się sprawdzić cen'))
  } finally {
    scraping.value = false
  }
}

const filtered = computed(() => {
  if (!report.value) return []
  if (filter.value === 'all') return report.value.items
  return report.value.items.filter((it) => it.status === filter.value)
})

const losingPct = computed(() => {
  if (!report.value || report.value.with_snapshots === 0) return 0
  return Math.round((report.value.losing / report.value.with_snapshots) * 100)
})

function formatScraped(iso: string | null): string {
  if (!iso) return '—'
  const diff = Date.now() - new Date(iso).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 60) return `${m} min temu`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h} h temu`
  return `${Math.floor(h / 24)} dni temu`
}

onMounted(load)
watch(() => props.feedId, load)
</script>

<template>
  <section class="bg-white border border-gray-200 rounded-2xl p-6">
    <div class="flex items-center justify-between gap-3 mb-5 flex-wrap">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
          <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18 9 11.25l4.306 4.306a11.95 11.95 0 0 1 5.814-5.518l2.74-1.22m0 0-5.94-2.281m5.94 2.28-2.28 5.941" /></svg>
        </div>
        <div>
          <h2 class="font-heading text-lg font-bold text-gray-900">Ceny konkurencji na Ceneo</h2>
          <p class="text-xs text-gray-500">Sprawdź pozycję cenową swoich produktów wobec konkurencji</p>
        </div>
      </div>
      <button v-if="!accessDenied"
        type="button"
        @click="scrape"
        :disabled="scraping || loading"
        class="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl px-4 py-2 transition cursor-pointer flex items-center gap-2"
      >
        <svg v-if="!scraping" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182M2.985 19.644l3.181-3.182" /></svg>
        {{ scraping ? 'Sprawdzanie...' : 'Sprawdź ceny' }}
      </button>
    </div>

    <!-- Pro upgrade banner -->
    <div v-if="accessDenied" class="p-6 bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-200 rounded-2xl text-center">
      <div class="inline-block text-[10px] font-bold uppercase tracking-wider bg-indigo-600 text-white px-2 py-0.5 rounded-full mb-3">PRO Feature</div>
      <h3 class="font-heading text-lg font-bold text-gray-900 mb-2">Śledzenie konkurencji na Ceneo</h3>
      <p class="text-sm text-gray-600 mb-4 max-w-md mx-auto">Sprawdzaj automatycznie pozycję cenową swoich produktów na Ceneo. Wykryj kiedy konkurencja jest tańsza i reaguj.</p>
      <router-link to="/oferty/cennik" class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 transition shadow">
        Zobacz plan Pro →
      </router-link>
    </div>

    <template v-else>
      <div v-if="loading && !report" class="text-sm text-gray-400">Ładowanie...</div>

      <template v-else-if="report">
        <!-- Summary cards -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
          <div class="bg-gray-50 rounded-xl p-4 text-center">
            <p class="text-2xl font-extrabold text-gray-900">{{ report.with_snapshots }}/{{ report.total_products }}</p>
            <p class="text-[10px] uppercase font-semibold text-gray-500 mt-1 tracking-wider">Sprawdzone</p>
          </div>
          <div class="bg-green-50 rounded-xl p-4 text-center">
            <p class="text-2xl font-extrabold text-green-700">{{ report.winning }}</p>
            <p class="text-[10px] uppercase font-semibold text-green-600 mt-1 tracking-wider">Najtańsi</p>
          </div>
          <div class="bg-red-50 rounded-xl p-4 text-center">
            <p class="text-2xl font-extrabold text-red-700">{{ report.losing }}</p>
            <p class="text-[10px] uppercase font-semibold text-red-600 mt-1 tracking-wider">Drożsi</p>
          </div>
          <div class="bg-amber-50 rounded-xl p-4 text-center">
            <p class="text-2xl font-extrabold text-amber-700">{{ losingPct }}%</p>
            <p class="text-[10px] uppercase font-semibold text-amber-600 mt-1 tracking-wider">% drożsi</p>
          </div>
        </div>

        <div v-if="report.no_data === report.total_products" class="p-4 bg-blue-50 border border-blue-200 rounded-xl text-sm text-blue-800">
          ℹ Kliknij „Sprawdź ceny" aby uruchomić pierwsze skanowanie. Sprawdzimy produkty z poprawnym EAN. Ostatnie 24h cache'ujemy.
        </div>

        <div v-else>
          <!-- Filter buttons -->
          <div class="flex gap-2 mb-3 flex-wrap">
            <button v-for="f in (['all', 'losing', 'winning', 'unknown'] as const)" :key="f"
              type="button"
              @click="filter = f"
              class="text-xs font-medium px-3 py-1.5 rounded-lg transition cursor-pointer"
              :class="filter === f ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
            >
              {{ f === 'all' ? 'Wszystkie' : f === 'losing' ? '⚠ Drożsi' : f === 'winning' ? '✓ Najtańsi' : 'Bez danych' }}
            </button>
          </div>

          <!-- Items table -->
          <div class="max-h-96 overflow-y-auto border border-gray-200 rounded-xl">
            <table class="w-full text-xs">
              <thead class="bg-gray-50 border-b border-gray-200 sticky top-0">
                <tr>
                  <th class="text-left p-2 font-semibold text-gray-600">Produkt</th>
                  <th class="text-right p-2 font-semibold text-gray-600">Twoja cena</th>
                  <th class="text-right p-2 font-semibold text-gray-600">Najtańsza</th>
                  <th class="text-left p-2 font-semibold text-gray-600">Sprzedawca</th>
                  <th class="text-right p-2 font-semibold text-gray-600">Różnica</th>
                  <th class="text-left p-2 font-semibold text-gray-600">Sprawdzono</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="it in filtered.slice(0, 200)" :key="it.product_id">
                  <td class="p-2 text-gray-900 max-w-[200px] truncate">{{ it.product_name }}</td>
                  <td class="p-2 text-right text-gray-700">{{ it.our_price ? it.our_price.toFixed(2) + ' zł' : '—' }}</td>
                  <td class="p-2 text-right text-gray-700">{{ it.lowest_price ? it.lowest_price.toFixed(2) + ' zł' : '—' }}</td>
                  <td class="p-2 text-gray-500 max-w-[150px] truncate">{{ it.lowest_seller || '—' }}</td>
                  <td class="p-2 text-right font-semibold"
                      :class="it.status === 'losing' ? 'text-red-600' : it.status === 'winning' ? 'text-green-600' : 'text-gray-400'">
                    <template v-if="it.diff_pct !== null">
                      {{ it.diff_pct > 0 ? '+' : '' }}{{ it.diff_pct }}%
                    </template>
                    <template v-else>—</template>
                  </td>
                  <td class="p-2 text-gray-400">{{ formatScraped(it.scraped_at) }}</td>
                </tr>
              </tbody>
            </table>
            <p v-if="filtered.length > 200" class="text-[11px] text-gray-400 p-2 text-center">
              (pokazano pierwsze 200 z {{ filtered.length }})
            </p>
          </div>
        </div>
      </template>
    </template>
  </section>
</template>
