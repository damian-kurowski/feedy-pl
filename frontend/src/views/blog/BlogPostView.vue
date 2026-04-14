<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api/client'

interface BlogPost {
  id: number
  slug: string
  title: string
  html: string
  published_at: string | null
  meta_title: string | null
  meta_description: string | null
  is_indexable: boolean
  is_followable: boolean
  hero_image_path: string | null
  hero_image_alt: string | null
  og_image_path: string | null
  reading_minutes: number | null
  category: string | null
  excerpt: string | null
}

const route = useRoute()
const post = ref<BlogPost | null>(null)
const loading = ref(true)
const notFound = ref(false)

const publishedDate = computed(() => {
  if (!post.value?.published_at) return ''
  try {
    return new Date(post.value.published_at).toLocaleDateString('pl-PL', { day: 'numeric', month: 'long', year: 'numeric' })
  } catch {
    return ''
  }
})

async function loadPost(slug: string) {
  loading.value = true
  notFound.value = false
  post.value = null
  try {
    const { data } = await api.get(`/blog/${slug}`)
    post.value = data
    applySeoTags(data)
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
}

function applySeoTags(p: BlogPost) {
  if (p.meta_title) document.title = p.meta_title
  else document.title = `${p.title} — Feedy Blog`
  const metaDesc = document.querySelector('meta[name="description"]') || (() => {
    const el = document.createElement('meta')
    el.setAttribute('name', 'description')
    document.head.appendChild(el)
    return el
  })()
  metaDesc.setAttribute('content', p.meta_description || p.excerpt || '')

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

onMounted(() => loadPost(String(route.params.slug)))
watch(() => route.params.slug, (s) => s && loadPost(String(s)))
</script>

<template>
  <div class="min-h-screen bg-white">
    <article v-if="post" class="max-w-3xl mx-auto px-4 py-10 sm:py-16">
      <router-link to="/blog" class="text-sm text-indigo-600 hover:text-indigo-800 mb-6 inline-block">&larr; Wróć do bloga</router-link>

      <div class="flex items-center gap-2 text-xs text-gray-400 mb-4">
        <span v-if="publishedDate">{{ publishedDate }}</span>
        <template v-if="post.reading_minutes">
          <span>·</span>
          <span>{{ post.reading_minutes }} min czytania</span>
        </template>
        <template v-if="post.category">
          <span>·</span>
          <span class="bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full font-medium">{{ post.category }}</span>
        </template>
      </div>

      <h1 class="font-heading text-3xl sm:text-4xl font-extrabold text-gray-900 leading-tight">{{ post.title }}</h1>
      <p v-if="post.excerpt" class="mt-4 text-lg text-gray-600">{{ post.excerpt }}</p>

      <figure v-if="post.hero_image_path" class="mt-8">
        <img :src="post.hero_image_path" :alt="post.hero_image_alt || post.title"
          class="w-full rounded-2xl border border-gray-200" loading="eager" />
        <figcaption v-if="post.hero_image_alt" class="text-xs text-gray-400 mt-2">{{ post.hero_image_alt }}</figcaption>
      </figure>

      <div class="prose prose-gray max-w-none mt-10" v-html="post.html"></div>

      <div class="mt-12 pt-8 border-t border-gray-100">
        <router-link to="/blog" class="text-sm text-indigo-600 hover:text-indigo-800">&larr; Więcej wpisów na blogu</router-link>
      </div>
    </article>

    <div v-else-if="loading" class="max-w-3xl mx-auto px-4 py-16 text-gray-400">Ładowanie...</div>

    <div v-else-if="notFound" class="max-w-3xl mx-auto px-4 py-16">
      <h1 class="font-heading text-2xl font-bold text-gray-900 mb-3">Wpis nie znaleziony</h1>
      <p class="text-gray-500 mb-6">Ten wpis nie istnieje lub został usunięty.</p>
      <router-link to="/blog" class="text-indigo-600 hover:text-indigo-800">&larr; Wróć do bloga</router-link>
    </div>
  </div>
</template>
