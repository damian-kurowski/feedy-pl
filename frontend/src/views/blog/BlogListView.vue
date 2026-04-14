<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../../api/client'
import SkeletonCard from '../../components/SkeletonCard.vue'

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
      <div v-if="loading" class="space-y-6">
        <SkeletonCard v-for="i in 3" :key="i" :rows="3" />
      </div>

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

        <div v-if="posts.length === 0 && visibleLegacyArticles.length === 0" class="text-center py-16 border border-dashed border-gray-200 rounded-2xl bg-gray-50">
          <div class="w-12 h-12 mx-auto rounded-xl bg-indigo-100 flex items-center justify-center mb-4">
            <svg class="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"/></svg>
          </div>
          <p class="font-heading text-lg font-bold text-gray-900">Wkrótce nowe poradniki</p>
          <p class="text-sm text-gray-500 mt-2 max-w-md mx-auto">Pracujemy nad pierwszymi wpisami. Tymczasem zarejestruj się i wypróbuj Feedy za darmo.</p>
          <router-link to="/register" class="inline-flex items-center gap-2 mt-5 px-5 py-2.5 text-sm font-semibold rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 transition shadow-sm">
            Załóż darmowe konto
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"/></svg>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>
