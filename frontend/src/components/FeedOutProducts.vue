<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFeedsOutStore } from '../stores/feedsOut'
import { extractImageUrls } from '../utils/imageExtractor'
import ProductOverrideModal from './ProductOverrideModal.vue'

const props = defineProps<{ feedOutId: number }>()
const store = useFeedsOutStore()
const allProducts = ref<any[]>([])
const search = ref('')
const loading = ref(false)
const editProduct = ref<any>(null)
const showModal = ref(false)
const perPage = ref(20)
const currentPage = ref(1)
const statusFilter = ref<'all' | 'original' | 'modified' | 'excluded'>('all')
const placeholderSvg = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40'%3E%3Crect fill='%23f3f4f6' width='40' height='40' rx='4'/%3E%3C/svg%3E"

const filtered = computed(() => {
  let list = allProducts.value
  if (statusFilter.value !== 'all') {
    list = list.filter(p => p.status === statusFilter.value)
  }
  return list
})

const totalPages = computed(() => Math.ceil(filtered.value.length / perPage.value))
const paged = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  return filtered.value.slice(start, start + perPage.value)
})

const counts = computed(() => ({
  all: allProducts.value.length,
  original: allProducts.value.filter(p => p.status === 'original').length,
  modified: allProducts.value.filter(p => p.status === 'modified').length,
  excluded: allProducts.value.filter(p => p.status === 'excluded').length,
}))

async function loadProducts() {
  loading.value = true
  try {
    allProducts.value = await store.getFeedProducts(props.feedOutId, search.value)
    currentPage.value = 1
  } finally { loading.value = false }
}

function getImage(p: any): string | null { return extractImageUrls(p.product_value).main }
function getPrice(p: any): string | null { const pv = p.product_value; return pv['@price'] ?? pv['g:price'] ?? pv['price'] ?? null }
function openEdit(p: any) { editProduct.value = p; showModal.value = true }

async function toggleExclude(product: any) {
  const newExcluded = product.status !== 'excluded'
  await store.upsertOverride(props.feedOutId, product.id, {
    field_overrides: product.override?.field_overrides || {},
    excluded: newExcluded,
  })
  await loadProducts()
}

async function handleSave(overrides: Record<string, string>, excluded: boolean) {
  if (!editProduct.value) return
  await store.upsertOverride(props.feedOutId, editProduct.value.id, { field_overrides: overrides, excluded })
  showModal.value = false; await loadProducts()
}

async function handleRestore() {
  if (!editProduct.value) return
  await store.deleteOverride(props.feedOutId, editProduct.value.id)
  showModal.value = false; await loadProducts()
}

let searchTimeout: ReturnType<typeof setTimeout>
function onSearch() { clearTimeout(searchTimeout); searchTimeout = setTimeout(loadProducts, 300) }
onMounted(loadProducts)
</script>

<template>
  <div>
    <!-- Search + filters bar -->
    <div class="flex flex-wrap items-center gap-3 mb-4">
      <input v-model="search" type="text" placeholder="Szukaj produktu..."
        class="flex-1 min-w-[200px] px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
        @input="onSearch" />

      <div class="flex gap-1">
        <button v-for="f in (['all', 'original', 'modified', 'excluded'] as const)" :key="f"
          class="px-3 py-1.5 text-xs font-medium rounded-lg cursor-pointer transition-colors"
          :class="statusFilter === f
            ? 'bg-indigo-600 text-white'
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
          @click="statusFilter = f; currentPage = 1"
        >
          {{ f === 'all' ? 'Wszystkie' : f === 'original' ? 'Oryginalne' : f === 'modified' ? 'Edytowane' : 'Wykluczone' }}
          <span class="ml-1 opacity-70">({{ counts[f] }})</span>
        </button>
      </div>

      <select v-model="perPage" class="px-2 py-1.5 border border-gray-300 rounded-lg text-xs bg-white" @change="currentPage = 1">
        <option :value="10">10</option>
        <option :value="20">20</option>
        <option :value="50">50</option>
        <option :value="100">100</option>
      </select>
    </div>

    <!-- Product table -->
    <div class="border rounded-xl overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-3 py-3 w-10">
              <span class="text-[11px] text-gray-400">Wkl.</span>
            </th>
            <th class="text-left px-3 py-3 font-medium text-gray-700 w-14"></th>
            <th class="text-left px-3 py-3 font-medium text-gray-700">Nazwa</th>
            <th class="text-left px-3 py-3 font-medium text-gray-700 w-24">Cena</th>
            <th class="text-left px-3 py-3 font-medium text-gray-700 w-28">Status</th>
            <th class="px-3 py-3 w-16"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="6" class="px-4 py-8 text-center text-gray-400">Ładowanie...</td></tr>
          <tr v-else-if="paged.length === 0"><td colspan="6" class="px-4 py-8 text-center text-gray-400">Brak produktów</td></tr>
          <tr v-for="product in paged" :key="product.id"
            class="border-t hover:bg-gray-50 transition-colors"
            :class="product.status === 'excluded' ? 'opacity-40' : ''"
          >
            <!-- Exclude checkbox -->
            <td class="px-3 py-2 text-center">
              <input
                type="checkbox"
                :checked="product.status === 'excluded'"
                class="rounded border-gray-300 text-red-500 focus:ring-red-500/20 cursor-pointer"
                title="Wyklucz z feedu"
                @change="toggleExclude(product)"
              />
            </td>
            <!-- Image -->
            <td class="px-3 py-2">
              <img :src="getImage(product) || placeholderSvg"
                class="w-12 h-12 object-contain rounded border border-gray-200 bg-white"
                loading="lazy" />
            </td>
            <!-- Name -->
            <td class="px-3 py-2">
              <span class="text-gray-900 block max-w-sm truncate">{{ product.product_name }}</span>
            </td>
            <!-- Price -->
            <td class="px-3 py-2 text-gray-600">{{ getPrice(product) || '-' }}</td>
            <!-- Status -->
            <td class="px-3 py-2">
              <span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-medium"
                :class="{
                  'bg-green-100 text-green-700': product.status === 'original',
                  'bg-yellow-100 text-yellow-700': product.status === 'modified',
                  'bg-red-100 text-red-700': product.status === 'excluded',
                }">
                {{ product.status === 'original' ? 'Oryginał' : product.status === 'modified' ? 'Zmieniony' : 'Wykluczony' }}
              </span>
            </td>
            <!-- Actions -->
            <td class="px-3 py-2 text-right">
              <button class="text-xs text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer" @click="openEdit(product)">Edytuj</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between mt-3 text-sm text-gray-500">
      <span>{{ filtered.length }} produktów, strona {{ currentPage }}/{{ totalPages }}</span>
      <div class="flex gap-1">
        <button
          :disabled="currentPage <= 1"
          class="px-3 py-1 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-30 cursor-pointer text-xs"
          @click="currentPage--"
        >Poprzednia</button>
        <button
          v-for="p in Math.min(totalPages, 5)" :key="p"
          class="px-3 py-1 rounded-lg border text-xs cursor-pointer"
          :class="currentPage === p ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-200 hover:bg-gray-50'"
          @click="currentPage = p"
        >{{ p }}</button>
        <button
          :disabled="currentPage >= totalPages"
          class="px-3 py-1 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-30 cursor-pointer text-xs"
          @click="currentPage++"
        >Następna</button>
      </div>
    </div>

    <ProductOverrideModal :show="showModal" :product="editProduct" @close="showModal = false" @save="handleSave" @restore="handleRestore" />
  </div>
</template>
