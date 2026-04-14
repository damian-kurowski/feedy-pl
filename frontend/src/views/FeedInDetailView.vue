<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useFeedsInStore } from '../stores/feedsIn'
import type { XmlElement, Product } from '../stores/feedsIn'
import XmlTree from '../components/XmlTree.vue'
import ProductPreview from '../components/ProductPreview.vue'
import FeedChangelog from '../components/FeedChangelog.vue'
import ManualProductForm from '../components/ManualProductForm.vue'
import api from '../api/client'
import { useToast, getApiError } from '../composables/useToast'

const toast = useToast()

const route = useRoute()
const store = useFeedsInStore()

const feedId = computed(() => Number(route.params.id))
const feed = computed(() => store.feeds.find((f) => f.id === feedId.value))

const elements = ref<XmlElement[]>([])
const products = ref<Product[]>([])
const selectedPath = ref<string>()
const recordPath = ref('')
const productName = ref('')
const refreshInterval = ref<string>('')
const saving = ref(false)
const fetching = ref(false)
const showAddProduct = ref(false)
const editingProduct = ref<Product | null>(null)

const refreshIntervalLabel = computed(() => {
  if (!feed.value?.refresh_interval) return null
  const minutes = feed.value.refresh_interval
  if (minutes <= 60) return 'Co 1 godzinę'
  if (minutes <= 360) return 'Co 6 godzin'
  return 'Co 24 godziny'
})

let pollTimer: ReturnType<typeof setInterval> | undefined

onMounted(async () => {
  if (store.feeds.length === 0) {
    await store.fetchFeeds()
  }
  if (feed.value) {
    recordPath.value = feed.value.record_path || ''
    productName.value = feed.value.product_name || ''
    refreshInterval.value = feed.value.refresh_interval?.toString() || ''
  }
  await loadData()
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

async function loadData() {
  const [els, prods] = await Promise.all([
    store.getElements(feedId.value),
    store.getProducts(feedId.value),
  ])
  elements.value = els
  products.value = prods
}

function handleSelect(path: string) {
  selectedPath.value = path
}

function useAsRecordPath() {
  if (selectedPath.value) {
    recordPath.value = selectedPath.value
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const prevRecordPath = feed.value?.record_path || ''
    const prevProductName = feed.value?.product_name || ''
    await store.updateFeed(feedId.value, {
      record_path: recordPath.value || null,
      product_name: productName.value || null,
      refresh_interval: refreshInterval.value ? parseInt(refreshInterval.value) : null,
    })
    const pathChanged = (recordPath.value || '') !== prevRecordPath
    const nameChanged = (productName.value || '') !== prevProductName
    if (pathChanged || nameChanged) {
      await refetchXml()
    }
  } finally {
    saving.value = false
  }
}

const productFormError = ref('')
async function addManualProduct(name: string, value: Record<string, string>) {
  productFormError.value = ''
  try {
    if (editingProduct.value) {
      await api.put(`/feeds-in/${feedId.value}/products/${editingProduct.value.id}`, { product_name: name, product_value: value })
      editingProduct.value = null
    } else {
      await api.post(`/feeds-in/${feedId.value}/products`, { product_name: name, product_value: value })
    }
    showAddProduct.value = false
    await loadData()
  } catch (e: any) {
    productFormError.value = e?.response?.data?.detail || e?.message || 'Błąd zapisu produktu'
  }
}

function startEditProduct(product: Product) {
  editingProduct.value = product
  showAddProduct.value = true
}

async function deleteProduct(id: number) {
  if (!confirm('Na pewno usunąć ten produkt?')) return
  try {
    await api.delete(`/feeds-in/${feedId.value}/products/${id}`)
    await loadData()
    toast.success('Produkt usunięty')
  } catch (e) {
    toast.error(getApiError(e, 'Nie udało się usunąć produktu'))
  }
}

function cancelProductForm() {
  showAddProduct.value = false
  editingProduct.value = null
}

async function refetchXml() {
  fetching.value = true
  try {
    const result = await store.fetchFeedXml(feedId.value)
    // If completed synchronously, refresh immediately
    if (result.status === 'completed') {
      await store.fetchFeeds()
      await loadData()
      fetching.value = false
      return
    }
    // Otherwise poll for async (Celery) completion
    let iterations = 0
    pollTimer = setInterval(async () => {
      iterations++
      await store.fetchFeeds()
      const current = store.feeds.find((f) => f.id === feedId.value)
      if (current && (current.fetch_status === 'success' || current.fetch_status === 'error') || iterations >= 30) {
        if (pollTimer) clearInterval(pollTimer)
        pollTimer = undefined
        fetching.value = false
        await loadData()
      }
    }, 2000)
  } catch (e) {
    fetching.value = false
    toast.error(getApiError(e, 'Nie udało się pobrać XML'))
  }
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-3 sm:px-4 py-6 sm:py-8">
    <!-- Header -->
    <div v-if="feed" class="mb-8">
      <router-link to="/dashboard" class="text-xs text-gray-400 hover:text-indigo-600 transition-colors mb-3 inline-flex items-center gap-1">
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" /></svg>
        Dashboard
      </router-link>
      <div class="flex items-center justify-between flex-wrap gap-3 mt-2">
        <div class="flex items-center gap-3">
          <h1 class="font-heading text-2xl font-bold text-gray-900">{{ feed.name }}</h1>
          <span
            class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
            :class="feed.fetch_status === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : feed.fetch_status === 'error' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-gray-50 text-gray-600 border border-gray-200'"
          >
            <span
              class="w-1.5 h-1.5 rounded-full"
              :class="feed.fetch_status === 'success' ? 'bg-emerald-500' : feed.fetch_status === 'error' ? 'bg-red-500' : 'bg-gray-400'"
            ></span>
            {{ feed.fetch_status === 'success' ? 'Aktywny' : feed.fetch_status === 'error' ? 'Błąd' : feed.fetch_status }}
          </span>
        </div>
        <div class="flex items-center gap-2">
          <button
            :disabled="fetching"
            class="bg-gray-100 hover:bg-gray-200 disabled:opacity-50 text-gray-700 text-sm font-medium rounded-xl px-4 py-2 transition cursor-pointer"
            @click="refetchXml"
          >
            {{ fetching ? 'Pobieranie...' : 'Pobierz XML ponownie' }}
          </button>
          <router-link
            :to="`/feeds-out/new?feed_in_id=${feedId}`"
            class="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer"
          >
            Utwórz feed wyjściowy
          </router-link>
        </div>
      </div>
    </div>

    <!-- Stats bar -->
    <div v-if="feed" class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
      <div class="relative overflow-hidden bg-gradient-to-br from-indigo-50 to-white rounded-2xl border border-indigo-100/50 p-5 hover:shadow-md transition-shadow">
        <div class="absolute top-2 right-2 w-8 h-8 rounded-lg bg-indigo-100/80 flex items-center justify-center">
          <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" /></svg>
        </div>
        <p class="font-heading text-2xl font-extrabold text-gray-900">{{ products.length }}</p>
        <p class="text-xs text-gray-500 mt-0.5">Produktów</p>
      </div>
      <div class="relative overflow-hidden bg-gradient-to-br from-indigo-50 to-white rounded-2xl border border-indigo-100/50 p-5 hover:shadow-md transition-shadow">
        <div class="absolute top-2 right-2 w-8 h-8 rounded-lg bg-indigo-100/80 flex items-center justify-center">
          <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" /></svg>
        </div>
        <p class="font-heading text-2xl font-extrabold text-gray-900">{{ elements.length }}</p>
        <p class="text-xs text-gray-500 mt-0.5">Elementów XML</p>
      </div>
      <div class="relative overflow-hidden bg-gradient-to-br from-indigo-50 to-white rounded-2xl border border-indigo-100/50 p-5 hover:shadow-md transition-shadow">
        <div class="absolute top-2 right-2 w-8 h-8 rounded-lg bg-indigo-100/80 flex items-center justify-center">
          <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </div>
        <p class="font-heading text-2xl font-extrabold" :class="feed.fetch_status === 'success' ? 'text-emerald-600' : feed.fetch_status === 'error' ? 'text-red-600' : 'text-gray-600'">
          {{ feed.fetch_status === 'success' ? 'OK' : feed.fetch_status === 'error' ? 'Błąd' : feed.fetch_status }}
        </p>
        <p class="text-xs text-gray-500 mt-0.5">Status</p>
      </div>
      <div class="relative overflow-hidden bg-gradient-to-br from-indigo-50 to-white rounded-2xl border border-indigo-100/50 p-5 hover:shadow-md transition-shadow">
        <div class="absolute top-2 right-2 w-8 h-8 rounded-lg bg-indigo-100/80 flex items-center justify-center">
          <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </div>
        <p class="font-heading text-lg font-extrabold text-gray-900">{{ feed.last_fetched_at ? new Date(feed.last_fetched_at).toLocaleString('pl-PL') : '-' }}</p>
        <p class="text-xs text-gray-500 mt-0.5">Ostatni refresh</p>
      </div>
    </div>

    <!-- Refresh interval info -->
    <div v-if="refreshIntervalLabel" class="mb-8 p-4 bg-gradient-to-r from-indigo-50 to-white border border-indigo-100 rounded-2xl flex items-center gap-3">
      <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center shrink-0">
        <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" /></svg>
      </div>
      <span class="text-sm text-indigo-800">Automatyczne odświeżanie: {{ refreshIntervalLabel }}</span>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Left column: XML Tree -->
      <section class="bg-white border border-gray-200 rounded-2xl p-6">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
            <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" /></svg>
          </div>
          <h2 class="font-heading text-lg font-bold text-gray-900">Struktura XML</h2>
        </div>
        <div v-if="elements.length === 0" class="text-gray-500 text-sm py-4">
          Brak elementów XML. Pobierz XML, aby zobaczyć strukturę.
        </div>
        <div v-else class="max-h-[600px] overflow-y-auto">
          <XmlTree :tree="elements" :selected="selectedPath" @select="handleSelect" />
        </div>
      </section>

      <!-- Right column: Config + Products -->
      <div class="space-y-6">
        <!-- Config section -->
        <section class="bg-white border border-gray-200 rounded-2xl p-6">
          <div class="flex items-center gap-3 mb-5">
            <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
              <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            </div>
            <h2 class="font-heading text-lg font-bold text-gray-900">Konfiguracja</h2>
          </div>

          <div v-if="selectedPath" class="mb-4 p-4 bg-indigo-50 border border-indigo-200 rounded-xl">
            <p class="text-sm text-indigo-800 mb-2">Zaznaczono: <code class="font-mono">{{ selectedPath }}</code></p>
            <button
              class="text-sm text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer"
              @click="useAsRecordPath"
            >
              Użyj jako ścieżkę do produktów
            </button>
          </div>

          <div class="space-y-4">
            <div>
              <label for="record_path" class="block text-sm font-medium text-gray-700 mb-1">Ścieżka do produktów</label>
              <p class="text-xs text-gray-500 mb-1">Wskaż element XML, który reprezentuje pojedynczy produkt</p>
              <input
                id="record_path"
                v-model="recordPath"
                type="text"
                placeholder="np. feed/entry"
                class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              />
            </div>

            <div>
              <label for="product_name" class="block text-sm font-medium text-gray-700 mb-1">Pole z nazwą produktu</label>
              <p class="text-xs text-gray-500 mb-1">Wskaż element zawierający nazwę produktu</p>
              <input
                id="product_name"
                v-model="productName"
                type="text"
                placeholder="np. feed/entry/title"
                class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              />
            </div>

            <div>
              <label for="refresh_interval" class="block text-sm font-medium text-gray-700 mb-1">Automatyczne odświeżanie</label>
              <select
                id="refresh_interval"
                v-model="refreshInterval"
                class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              >
                <option value="">Wyłączone</option>
                <option value="60">Co 1 godzinę</option>
                <option value="360">Co 6 godzin</option>
                <option value="1440">Co 24 godziny</option>
              </select>
            </div>

            <button
              :disabled="saving"
              class="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer"
              @click="saveConfig"
            >
              {{ saving ? 'Zapisywanie...' : 'Zapisz i odśwież' }}
            </button>
          </div>
        </section>

        <!-- Products section -->
        <section class="bg-white border border-gray-200 rounded-2xl p-6">
          <div class="flex items-center justify-between mb-5">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
                <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" /></svg>
              </div>
              <h2 class="font-heading text-lg font-bold text-gray-900">Produkty ({{ products.length }})</h2>
            </div>
            <button @click="showAddProduct ? cancelProductForm() : (showAddProduct = true)"
              class="text-xs font-medium text-indigo-600 hover:text-indigo-800 cursor-pointer">
              {{ showAddProduct ? 'Anuluj' : '+ Dodaj ręcznie' }}
            </button>
          </div>
          <ManualProductForm
            v-if="showAddProduct"
            :initial="editingProduct ? { name: editingProduct.product_name, value: editingProduct.product_value } : null"
            :error="productFormError"
            class="mb-4"
            @save="addManualProduct"
            @cancel="cancelProductForm"
          />
          <ProductPreview :products="products" @delete="deleteProduct" @edit="startEditProduct" />
        </section>

        <!-- Changelog section -->
        <section class="bg-white border border-gray-200 rounded-2xl p-6">
          <div class="flex items-center gap-3 mb-5">
            <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
              <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
            <h2 class="font-heading text-lg font-bold text-gray-900">Historia zmian</h2>
          </div>
          <FeedChangelog :feed-id="feedId" />
        </section>
      </div>
    </div>
  </div>
</template>
