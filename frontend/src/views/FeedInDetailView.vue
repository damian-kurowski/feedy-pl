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
    await store.updateFeed(feedId.value, {
      record_path: recordPath.value || null,
      product_name: productName.value || null,
      refresh_interval: refreshInterval.value ? parseInt(refreshInterval.value) : null,
    })
  } finally {
    saving.value = false
  }
}

async function addManualProduct(name: string, value: Record<string, string>) {
  try {
    await api.post(`/feeds-in/${feedId.value}/products`, { product_name: name, product_value: value })
    showAddProduct.value = false
    await loadData()
  } catch {}
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
  } catch {
    fetching.value = false
  }
}
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <div v-if="feed" class="mb-6 flex items-center justify-between flex-wrap gap-3">
      <h1 class="text-2xl font-bold text-gray-900">{{ feed.name }}</h1>
      <div class="flex items-center gap-3">
        <button
          :disabled="fetching"
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 disabled:opacity-50 text-gray-700 text-sm font-medium rounded-md cursor-pointer"
          @click="refetchXml"
        >
          {{ fetching ? 'Pobieranie...' : 'Pobierz XML ponownie' }}
        </button>
        <router-link
          :to="`/feeds-out/new?feed_in_id=${feedId}`"
          class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-md"
        >
          Utwórz feed wyjściowy
        </router-link>
      </div>
    </div>

    <!-- Stats bar -->
    <div v-if="feed" class="grid grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-lg border p-4 text-center">
        <p class="text-2xl font-bold text-indigo-600">{{ products.length }}</p>
        <p class="text-xs text-gray-500 mt-1">Produktów</p>
      </div>
      <div class="bg-white rounded-lg border p-4 text-center">
        <p class="text-2xl font-bold text-indigo-600">{{ elements.length }}</p>
        <p class="text-xs text-gray-500 mt-1">Elementów XML</p>
      </div>
      <div class="bg-white rounded-lg border p-4 text-center">
        <p class="text-2xl font-bold" :class="feed.fetch_status === 'success' ? 'text-green-600' : feed.fetch_status === 'error' ? 'text-red-600' : 'text-gray-600'">
          {{ feed.fetch_status === 'success' ? 'OK' : feed.fetch_status === 'error' ? 'Błąd' : feed.fetch_status }}
        </p>
        <p class="text-xs text-gray-500 mt-1">Status</p>
      </div>
      <div class="bg-white rounded-lg border p-4 text-center">
        <p class="text-2xl font-bold text-indigo-600">{{ feed.last_fetched_at ? new Date(feed.last_fetched_at).toLocaleString('pl-PL') : '-' }}</p>
        <p class="text-xs text-gray-500 mt-1">Ostatni refresh</p>
      </div>
    </div>

    <!-- Refresh interval info -->
    <div v-if="refreshIntervalLabel" class="mb-6 p-3 bg-blue-50 border border-blue-200 rounded-md text-sm text-blue-800">
      Automatyczne odświeżanie: {{ refreshIntervalLabel }}
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Left column: XML Tree -->
      <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-5">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Struktura XML</h2>
        <div v-if="elements.length === 0" class="text-gray-500 text-sm py-4">
          Brak elementów XML. Pobierz XML, aby zobaczyć strukturę.
        </div>
        <div v-else class="max-h-[600px] overflow-y-auto">
          <XmlTree :tree="elements" :selected="selectedPath" @select="handleSelect" />
        </div>
      </div>

      <!-- Right column: Config + Products -->
      <div class="space-y-6">
        <!-- Config section -->
        <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-5">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Konfiguracja</h2>

          <div v-if="selectedPath" class="mb-4 p-3 bg-indigo-50 border border-indigo-200 rounded-md">
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
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
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
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label for="refresh_interval" class="block text-sm font-medium text-gray-700 mb-1">Automatyczne odświeżanie</label>
              <select
                id="refresh_interval"
                v-model="refreshInterval"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Wyłączone</option>
                <option value="60">Co 1 godzinę</option>
                <option value="360">Co 6 godzin</option>
                <option value="1440">Co 24 godziny</option>
              </select>
            </div>

            <button
              :disabled="saving"
              class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 cursor-pointer"
              @click="saveConfig"
            >
              {{ saving ? 'Zapisywanie...' : 'Zapisz' }}
            </button>
          </div>
        </div>

        <!-- Products section -->
        <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Produkty ({{ products.length }})</h2>
            <button @click="showAddProduct = !showAddProduct"
              class="text-xs font-medium text-indigo-600 hover:text-indigo-800 cursor-pointer">
              {{ showAddProduct ? 'Anuluj' : '+ Dodaj ręcznie' }}
            </button>
          </div>
          <ManualProductForm v-if="showAddProduct" @save="addManualProduct" @cancel="showAddProduct = false" class="mb-4" />
          <ProductPreview :products="products" />
        </div>

        <!-- Changelog section -->
        <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-5">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Historia zmian</h2>
          <FeedChangelog :feed-id="feedId" />
        </div>
      </div>
    </div>
  </div>
</template>
