<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../../api/client'

interface BlogPostListItem {
  id: number
  slug: string
  title: string
  published_at: string | null
  hero_image_path: string | null
  hero_image_alt: string | null
  reading_minutes: number | null
  category: string | null
  excerpt: string | null
  meta_description: string | null
}

const posts = ref<BlogPostListItem[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await api.get('/blog')
    posts.value = data
  } catch {
    posts.value = []
  } finally {
    loading.value = false
  }
})

function formatDate(iso: string | null): string {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleDateString('pl-PL', { day: 'numeric', month: 'long', year: 'numeric' })
  } catch {
    return ''
  }
}

// Legacy static articles — kept for backward compatibility and SEO
const legacyArticles = computed(() => [
  {
    slug: 'jak-dodac-produkty-do-ceneo',
    title: 'Jak dodać produkty do Ceneo — kompletny poradnik 2026',
    date: '11 kwietnia 2026',
    readingMinutes: 10,
    category: 'Ceneo',
    categoryClass: 'bg-indigo-100 text-indigo-700',
    excerpt: 'Krok po kroku: jak stworzyć feed XML dla Ceneo, jakie pola są wymagane, jak uniknąć odrzucenia ofert i jak automatycznie aktualizować dane produktowe.',
  },
  {
    slug: 'jak-stworzyc-feed-xml',
    title: 'Jak stworzyć feed XML dla sklepu internetowego',
    date: '11 kwietnia 2026',
    readingMinutes: 8,
    category: 'Poradnik',
    categoryClass: 'bg-green-100 text-green-700',
    excerpt: 'Czym jest feed produktowy, jakie formaty XML istnieją, jak wybrać odpowiedni dla Ceneo, Google Shopping i Allegro.',
  },
  {
    slug: 'ceneo-odrzuca-oferty',
    title: 'Ceneo odrzuca oferty — jak naprawić feed?',
    date: '11 kwietnia 2026',
    readingMinutes: 6,
    category: 'Troubleshooting',
    categoryClass: 'bg-red-100 text-red-700',
    excerpt: 'Najczęstsze przyczyny odrzuceń: brak wymaganych pól, zły format ceny, nieprawidłowy EAN. Jak je zdiagnozować i naprawić.',
  },
])

const hiddenLegacySlugs = computed(() => new Set(posts.value.map((p) => p.slug)))
const visibleLegacyArticles = computed(() => legacyArticles.value.filter((a) => !hiddenLegacySlugs.value.has(a.slug)))
</script>

<template>
  <div class="min-h-screen bg-white">
    <section class="bg-gradient-to-br from-indigo-600 to-indigo-800 text-white py-12 sm:py-16">
      <div class="max-w-4xl mx-auto px-4">
        <h1 class="font-heading text-3xl sm:text-4xl font-extrabold">Blog Feedy</h1>
        <p class="mt-3 text-base sm:text-lg text-indigo-100">Poradniki, instrukcje i nowości ze świata feedów produktowych</p>
      </div>
    </section>

    <div class="max-w-4xl mx-auto px-4 py-10 sm:py-16">
      <div v-if="loading" class="text-gray-400 text-sm">Ładowanie wpisów...</div>

      <div v-else class="space-y-6 sm:space-y-8">
        <!-- DB posts first -->
        <router-link
          v-for="post in posts"
          :key="post.id"
          :to="`/blog/${post.slug}`"
          class="block group"
        >
          <article class="border border-gray-200 rounded-2xl p-5 sm:p-6 hover:border-indigo-200 hover:shadow-md transition-all">
            <div class="flex flex-wrap items-center gap-2 text-xs text-gray-400 mb-3">
              <span v-if="post.published_at">{{ formatDate(post.published_at) }}</span>
              <template v-if="post.reading_minutes">
                <span>·</span>
                <span>{{ post.reading_minutes }} min czytania</span>
              </template>
              <template v-if="post.category">
                <span>·</span>
                <span class="bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full font-medium">{{ post.category }}</span>
              </template>
            </div>
            <h2 class="font-heading text-lg sm:text-xl font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">{{ post.title }}</h2>
            <p v-if="post.excerpt || post.meta_description" class="mt-2 text-gray-600 text-sm leading-relaxed">{{ post.excerpt || post.meta_description }}</p>
          </article>
        </router-link>

        <!-- Legacy static articles fallback -->
        <router-link
          v-for="legacy in visibleLegacyArticles"
          :key="legacy.slug"
          :to="`/blog/${legacy.slug}`"
          class="block group"
        >
          <article class="border border-gray-200 rounded-2xl p-5 sm:p-6 hover:border-indigo-200 hover:shadow-md transition-all">
            <div class="flex flex-wrap items-center gap-2 text-xs text-gray-400 mb-3">
              <span>{{ legacy.date }}</span>
              <span>·</span>
              <span>{{ legacy.readingMinutes }} min czytania</span>
              <span>·</span>
              <span :class="legacy.categoryClass" class="px-2 py-0.5 rounded-full font-medium">{{ legacy.category }}</span>
            </div>
            <h2 class="font-heading text-lg sm:text-xl font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">{{ legacy.title }}</h2>
            <p class="mt-2 text-gray-600 text-sm leading-relaxed">{{ legacy.excerpt }}</p>
          </article>
        </router-link>

        <div v-if="posts.length === 0 && visibleLegacyArticles.length === 0" class="text-gray-400 text-sm py-12 text-center">
          Brak wpisów.
        </div>
      </div>
    </div>
  </div>
</template>
