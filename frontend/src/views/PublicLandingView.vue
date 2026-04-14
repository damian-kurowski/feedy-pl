<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/client'

interface LandingPage {
  id: number
  slug: string
  title: string
  short_description: string | null
  full_description: string | null
  hero_image: string | null
  gallery: string[] | null
  price: string | null
  price_negotiable: boolean
  location: string | null
  cta_text: string | null
  cta_url: string | null
  meta_title: string | null
  meta_description: string | null
  is_indexable: boolean
  is_followable: boolean
  published_at: string | null
}

const route = useRoute()
const page = ref<LandingPage | null>(null)
const loading = ref(true)
const notFound = ref(false)
const activeImage = ref<string | null>(null)

const slug = computed(() => {
  const parts = route.params.pathMatch
  if (Array.isArray(parts)) return parts.join('/')
  return String(parts || '')
})

async function loadPage(slugPath: string) {
  loading.value = true
  notFound.value = false
  page.value = null
  activeImage.value = null
  try {
    const { data } = await api.get(`/landing/${slugPath}`)
    page.value = data
    activeImage.value = data.hero_image || (data.gallery && data.gallery[0]) || null
    applySeo(data)
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
}

function applySeo(p: LandingPage) {
  document.title = p.meta_title || `${p.title} — Feedy`
  const metaDesc = document.querySelector('meta[name="description"]') || (() => {
    const el = document.createElement('meta')
    el.setAttribute('name', 'description')
    document.head.appendChild(el)
    return el
  })()
  metaDesc.setAttribute('content', p.meta_description || p.short_description || '')

  const robots = document.querySelector('meta[name="robots"]') || (() => {
    const el = document.createElement('meta')
    el.setAttribute('name', 'robots')
    document.head.appendChild(el)
    return el
  })()
  const parts = []
  parts.push(p.is_indexable ? 'index' : 'noindex')
  parts.push(p.is_followable ? 'follow' : 'nofollow')
  robots.setAttribute('content', parts.join(','))
}

async function trackClick() {
  if (!slug.value) return
  try {
    await api.post(`/landing/${slug.value}/click`)
  } catch {
    // ignore — click is fire-and-forget
  }
}

onMounted(() => loadPage(slug.value))
watch(slug, (s) => s && loadPage(s))
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <div v-if="page" class="max-w-5xl mx-auto px-3 sm:px-6 py-8 sm:py-12">
      <!-- Top bar with location -->
      <div v-if="page.location" class="mb-4 flex items-center gap-2 text-sm text-gray-500">
        <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
        </svg>
        {{ page.location }}
      </div>

      <h1 class="font-heading text-3xl sm:text-4xl font-extrabold text-gray-900 leading-tight mb-6">{{ page.title }}</h1>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
        <!-- Gallery + description -->
        <div class="lg:col-span-2">
          <div v-if="activeImage" class="bg-white border border-gray-200 rounded-2xl overflow-hidden">
            <img :src="activeImage" :alt="page.title" class="w-full h-auto max-h-[520px] object-contain bg-gray-50" loading="eager" />
          </div>
          <div v-if="page.gallery && page.gallery.length > 1" class="mt-3 flex gap-2 flex-wrap">
            <button v-if="page.hero_image" @click="activeImage = page.hero_image"
              class="w-16 h-16 rounded-lg border overflow-hidden cursor-pointer"
              :class="activeImage === page.hero_image ? 'border-indigo-500 ring-2 ring-indigo-200' : 'border-gray-200'">
              <img :src="page.hero_image" class="w-full h-full object-cover" />
            </button>
            <button v-for="(img, idx) in page.gallery" :key="idx" @click="activeImage = img"
              class="w-16 h-16 rounded-lg border overflow-hidden cursor-pointer"
              :class="activeImage === img ? 'border-indigo-500 ring-2 ring-indigo-200' : 'border-gray-200'">
              <img :src="img" class="w-full h-full object-cover" />
            </button>
          </div>

          <div v-if="page.full_description" class="mt-8 blog-prose" v-html="page.full_description"></div>
        </div>

        <!-- Side card -->
        <aside class="lg:col-span-1">
          <div class="bg-white border border-gray-200 rounded-2xl p-6 sticky top-20">
            <p v-if="page.price" class="text-3xl font-heading font-extrabold text-indigo-600">{{ page.price }}</p>
            <p v-else-if="page.price_negotiable" class="text-2xl font-heading font-bold text-gray-700">Do wyceny indywidualnej</p>

            <p v-if="page.short_description" class="mt-4 text-sm text-gray-600 leading-relaxed">{{ page.short_description }}</p>

            <a
              v-if="page.cta_url"
              :href="page.cta_url"
              target="_blank"
              rel="ugc sponsored nofollow noopener"
              class="mt-6 block text-center bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl px-5 py-3 transition-all hover:shadow-lg hover:shadow-indigo-500/20"
              @click="trackClick"
            >
              {{ page.cta_text || 'Przejdź do oferty!' }}
            </a>

            <p class="mt-4 text-[11px] text-gray-400 text-center">Oferta opublikowana na feedy.pl</p>
          </div>
        </aside>
      </div>
    </div>

    <div v-else-if="loading" class="max-w-3xl mx-auto px-4 py-16 text-gray-400">Ładowanie...</div>

    <div v-else-if="notFound" class="max-w-3xl mx-auto px-4 py-16">
      <h1 class="font-heading text-2xl font-bold text-gray-900 mb-3">Oferta nie znaleziona</h1>
      <p class="text-gray-500">Ta oferta nie istnieje lub została usunięta.</p>
    </div>
  </div>
</template>
