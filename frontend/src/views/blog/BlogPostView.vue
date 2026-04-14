<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
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

interface RelatedPost {
  id: number
  slug: string
  title: string
  excerpt: string | null
  category: string | null
  reading_minutes: number | null
}

interface TocItem {
  id: string
  text: string
  level: number
}

const route = useRoute()
const post = ref<BlogPost | null>(null)
const loading = ref(true)
const notFound = ref(false)
const toc = ref<TocItem[]>([])
const related = ref<RelatedPost[]>([])
const readingProgress = ref(0)
const articleEl = ref<HTMLElement | null>(null)

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
  toc.value = []
  related.value = []
  try {
    const { data } = await api.get(`/blog/${slug}`)
    post.value = data
    applySeoTags(data)
    await nextTick()
    buildToc()
    await loadRelated(data.id, data.category)
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
}

function slugifyHeading(text: string, idx: number): string {
  const base = text.toLowerCase()
    .replace(/ą/g, 'a').replace(/ć/g, 'c').replace(/ę/g, 'e').replace(/ł/g, 'l')
    .replace(/ń/g, 'n').replace(/ó/g, 'o').replace(/ś/g, 's').replace(/ź/g, 'z').replace(/ż/g, 'z')
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
  return base ? `${base}-${idx}` : `heading-${idx}`
}

function buildToc() {
  if (!articleEl.value) return
  const headings = articleEl.value.querySelectorAll<HTMLHeadingElement>('h2, h3')
  const items: TocItem[] = []
  headings.forEach((h, i) => {
    if (!h.id) h.id = slugifyHeading(h.textContent || '', i)
    items.push({
      id: h.id,
      text: h.textContent || '',
      level: parseInt(h.tagName.substring(1)),
    })
  })
  toc.value = items
}

async function loadRelated(currentId: number, category: string | null) {
  try {
    const { data } = await api.get('/blog')
    const all: RelatedPost[] = data || []
    let filtered = all.filter((p) => p.id !== currentId)
    if (category) {
      const sameCategory = filtered.filter((p) => p.category === category)
      const others = filtered.filter((p) => p.category !== category)
      filtered = [...sameCategory, ...others]
    }
    related.value = filtered.slice(0, 3)
  } catch {
    related.value = []
  }
}

function onScroll() {
  if (!articleEl.value) return
  const rect = articleEl.value.getBoundingClientRect()
  const total = articleEl.value.scrollHeight - window.innerHeight
  const scrolled = -rect.top
  readingProgress.value = Math.max(0, Math.min(100, (scrolled / Math.max(total, 1)) * 100))
}

function scrollToHeading(id: string) {
  const el = document.getElementById(id)
  if (el) {
    const offset = el.getBoundingClientRect().top + window.scrollY - 80
    window.scrollTo({ top: offset, behavior: 'smooth' })
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

async function copyShareLink() {
  try {
    await navigator.clipboard.writeText(window.location.href)
  } catch {}
}

onMounted(() => {
  loadPost(String(route.params.slug))
  window.addEventListener('scroll', onScroll, { passive: true })
})
onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})
watch(() => route.params.slug, (s) => s && loadPost(String(s)))
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- Reading progress bar -->
    <div v-if="post" class="fixed top-0 left-0 right-0 h-1 bg-gray-100 z-50">
      <div class="h-full bg-indigo-600 transition-all duration-150" :style="{ width: `${readingProgress}%` }"></div>
    </div>

    <article v-if="post" ref="articleEl" class="max-w-3xl mx-auto px-4 py-10 sm:py-16">
      <router-link to="/blog" class="text-sm text-indigo-600 hover:text-indigo-800 mb-6 inline-block">&larr; Wróć do bloga</router-link>

      <div class="flex items-center gap-2 text-xs text-gray-400 mb-4 flex-wrap">
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

      <!-- Table of Contents -->
      <nav v-if="toc.length >= 3" class="mt-10 p-5 bg-gray-50 border border-gray-200 rounded-2xl">
        <p class="text-[11px] font-bold uppercase tracking-wider text-gray-500 mb-3">Spis treści</p>
        <ul class="space-y-1.5">
          <li v-for="item in toc" :key="item.id" :class="{ 'pl-4': item.level === 3 }">
            <button
              type="button"
              class="text-sm text-gray-700 hover:text-indigo-600 transition text-left cursor-pointer"
              @click="scrollToHeading(item.id)"
            >
              {{ item.text }}
            </button>
          </li>
        </ul>
      </nav>

      <div class="blog-prose mt-10" v-html="post.html"></div>

      <!-- Share buttons -->
      <div class="mt-12 pt-6 border-t border-gray-100 flex flex-wrap items-center gap-3">
        <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Udostępnij</span>
        <a
          :href="`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent('https://feedy.pl/blog/' + post.slug)}`"
          target="_blank"
          rel="noopener"
          class="text-xs font-medium text-gray-600 hover:text-indigo-600 border border-gray-200 hover:border-indigo-300 rounded-lg px-3 py-1.5 transition"
        >Facebook</a>
        <a
          :href="`https://twitter.com/intent/tweet?url=${encodeURIComponent('https://feedy.pl/blog/' + post.slug)}&text=${encodeURIComponent(post.title)}`"
          target="_blank"
          rel="noopener"
          class="text-xs font-medium text-gray-600 hover:text-indigo-600 border border-gray-200 hover:border-indigo-300 rounded-lg px-3 py-1.5 transition"
        >X</a>
        <a
          :href="`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent('https://feedy.pl/blog/' + post.slug)}`"
          target="_blank"
          rel="noopener"
          class="text-xs font-medium text-gray-600 hover:text-indigo-600 border border-gray-200 hover:border-indigo-300 rounded-lg px-3 py-1.5 transition"
        >LinkedIn</a>
        <button
          type="button"
          class="text-xs font-medium text-gray-600 hover:text-indigo-600 border border-gray-200 hover:border-indigo-300 rounded-lg px-3 py-1.5 transition cursor-pointer"
          @click="copyShareLink"
        >Skopiuj link</button>
      </div>

      <!-- Related posts -->
      <section v-if="related.length > 0" class="mt-16">
        <h2 class="font-heading text-xl font-bold text-gray-900 mb-6">Może Cię zainteresować</h2>
        <div class="grid sm:grid-cols-3 gap-4">
          <router-link
            v-for="r in related"
            :key="r.id"
            :to="`/blog/${r.slug}`"
            class="block p-5 rounded-2xl border border-gray-200 hover:border-indigo-300 hover:shadow-md transition-all bg-white"
          >
            <div class="flex items-center gap-2 text-[11px] text-gray-400 mb-2">
              <span v-if="r.category" class="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full font-medium">{{ r.category }}</span>
              <span v-if="r.reading_minutes">{{ r.reading_minutes }} min</span>
            </div>
            <h3 class="font-heading text-base font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">{{ r.title }}</h3>
            <p v-if="r.excerpt" class="text-xs text-gray-500 mt-2 line-clamp-3">{{ r.excerpt }}</p>
          </router-link>
        </div>
      </section>

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
