<script setup lang="ts">
import { ref } from 'vue'
import type { Product } from '../stores/feedsIn'
import { extractImageUrls } from '../utils/imageExtractor'
import ImageLightbox from './ImageLightbox.vue'

defineProps<{
  products: Product[]
}>()

const expanded = ref<Set<number>>(new Set())
const lightboxImages = ref<string[]>([])
const showLightbox = ref(false)

const placeholderSvg = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48'%3E%3Crect fill='%23f3f4f6' width='48' height='48' rx='6'/%3E%3Ctext x='24' y='28' text-anchor='middle' fill='%239ca3af' font-size='10'%3EBrak%3C/text%3E%3C/svg%3E"

function toggle(id: number) {
  if (expanded.value.has(id)) {
    expanded.value.delete(id)
  } else {
    expanded.value.add(id)
  }
}

function getMainImage(product: Product): string | null {
  const images = extractImageUrls(product.product_value as Record<string, unknown>)
  return images.main
}

function getAllImages(product: Product): string[] {
  const images = extractImageUrls(product.product_value as Record<string, unknown>)
  const all: string[] = []
  if (images.main) all.push(images.main)
  all.push(...images.additional)
  return all
}

function openLightbox(product: Product) {
  lightboxImages.value = getAllImages(product)
  showLightbox.value = true
}

function getPrice(product: Product): string | null {
  const pv = product.product_value as Record<string, unknown>
  return (pv['@price'] ?? pv['g:price'] ?? pv['price'] ?? null) as string | null
}

function getCategory(product: Product): string | null {
  const pv = product.product_value as Record<string, unknown>
  return (pv['cat'] ?? pv['g:product_type'] ?? pv['category'] ?? null) as string | null
}

function handleImgError(e: Event) {
  (e.target as HTMLImageElement).src = placeholderSvg
}
</script>

<template>
  <div>
    <div v-if="products.length === 0" class="text-gray-500 text-sm py-4">
      Brak produktow do wyswietlenia.
    </div>
    <div v-for="product in products" :key="product.id" class="border border-gray-200 rounded-md mb-2">
      <button
        class="w-full text-left px-4 py-3 flex items-center gap-3 hover:bg-gray-50 cursor-pointer"
        @click="toggle(product.id)"
      >
        <img
          :src="getMainImage(product) || placeholderSvg"
          :alt="product.product_name"
          class="w-12 h-12 object-cover rounded border border-gray-200 shrink-0"
          loading="lazy"
          @error="handleImgError"
        />
        <div class="flex-1 min-w-0">
          <span class="font-medium text-gray-900 text-sm block truncate">{{ product.product_name }}</span>
          <span v-if="getCategory(product)" class="text-xs text-gray-400 truncate block">{{ getCategory(product) }}</span>
        </div>
        <span v-if="getPrice(product)" class="text-sm font-medium text-gray-700 shrink-0">{{ getPrice(product) }}</span>
        <svg
          class="w-4 h-4 text-gray-400 transition-transform shrink-0"
          :class="{ 'rotate-180': expanded.has(product.id) }"
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      <div v-if="expanded.has(product.id)" class="px-4 pb-3 space-y-3">
        <div v-if="getAllImages(product).length > 0" class="flex gap-2 flex-wrap">
          <img
            v-for="(img, idx) in getAllImages(product).slice(0, 6)"
            :key="idx"
            :src="img"
            :alt="`Zdjecie ${idx + 1}`"
            class="w-20 h-20 object-cover rounded border border-gray-200 cursor-pointer hover:ring-2 hover:ring-indigo-400"
            loading="lazy"
            @click.stop="openLightbox(product)"
            @error="handleImgError"
          />
        </div>
        <pre class="text-xs bg-gray-50 p-3 rounded overflow-x-auto">{{ JSON.stringify(product.product_value, null, 2) }}</pre>
      </div>
    </div>
    <ImageLightbox :images="lightboxImages" :show="showLightbox" @close="showLightbox = false" />
  </div>
</template>
