<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useFeedsOutStore } from '../stores/feedsOut'
import { extractImageUrls } from '../utils/imageExtractor'
import ProductOverrideModal from './ProductOverrideModal.vue'

const props = defineProps<{ feedOutId: number }>()
const store = useFeedsOutStore()
const products = ref<any[]>([])
const search = ref('')
const loading = ref(false)
const editProduct = ref<any>(null)
const showModal = ref(false)
const placeholderSvg = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40'%3E%3Crect fill='%23f3f4f6' width='40' height='40' rx='4'/%3E%3C/svg%3E"

async function loadProducts() {
  loading.value = true
  try { products.value = await store.getFeedProducts(props.feedOutId, search.value) } finally { loading.value = false }
}
function getImage(p: any): string | null { return extractImageUrls(p.product_value).main }
function getPrice(p: any): string | null { const pv = p.product_value; return pv['@price'] ?? pv['g:price'] ?? pv['price'] ?? null }
function openEdit(p: any) { editProduct.value = p; showModal.value = true }
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
    <div class="mb-3">
      <input v-model="search" type="text" placeholder="Szukaj produktu..."
        class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        @input="onSearch" />
    </div>
    <div class="border rounded-lg overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-700 w-12"></th>
            <th class="text-left px-4 py-3 font-medium text-gray-700">Nazwa</th>
            <th class="text-left px-4 py-3 font-medium text-gray-700 w-24">Cena</th>
            <th class="text-left px-4 py-3 font-medium text-gray-700 w-28">Status</th>
            <th class="px-4 py-3 w-20"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="5" class="px-4 py-8 text-center text-gray-400">Ladowanie...</td></tr>
          <tr v-else-if="products.length === 0"><td colspan="5" class="px-4 py-8 text-center text-gray-400">Brak produktow</td></tr>
          <tr v-for="product in products" :key="product.id" class="border-t hover:bg-gray-50" :class="product.status === 'excluded' ? 'opacity-50' : ''">
            <td class="px-4 py-2"><img :src="getImage(product) || placeholderSvg" class="w-10 h-10 object-cover rounded border border-gray-200" loading="lazy" /></td>
            <td class="px-4 py-2"><span class="text-gray-900 truncate block max-w-xs">{{ product.product_name }}</span></td>
            <td class="px-4 py-2 text-gray-600">{{ getPrice(product) || '-' }}</td>
            <td class="px-4 py-2">
              <span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium"
                :class="{ 'bg-green-100 text-green-700': product.status === 'original', 'bg-yellow-100 text-yellow-700': product.status === 'modified', 'bg-red-100 text-red-700': product.status === 'excluded' }">
                {{ product.status === 'original' ? 'Oryginal' : product.status === 'modified' ? 'Zmieniony' : 'Wykluczony' }}
              </span>
            </td>
            <td class="px-4 py-2 text-right">
              <button class="text-sm text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer" @click="openEdit(product)">Edytuj</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <ProductOverrideModal :show="showModal" :product="editProduct" @close="showModal = false" @save="handleSave" @restore="handleRestore" />
  </div>
</template>
