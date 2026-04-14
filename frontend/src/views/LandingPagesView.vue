<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../api/client'
import { useToast, getApiError } from '../composables/useToast'
import SkeletonCard from '../components/SkeletonCard.vue'

const toast = useToast()

interface LandingPage {
  id: number
  user_id: number
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
  is_published: boolean
}

const pages = ref<LandingPage[]>([])
const editing = ref<Partial<LandingPage> | null>(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const uploadingHero = ref(false)
const uploadingGallery = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/landing-pages')
    pages.value = data
  } catch {
    pages.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)

function newPage() {
  editing.value = {
    title: '',
    slug: '',
    short_description: '',
    full_description: '',
    hero_image: '',
    gallery: [],
    price: '',
    price_negotiable: false,
    location: '',
    cta_text: 'Przejdź do oferty!',
    cta_url: '',
    meta_title: '',
    meta_description: '',
    is_indexable: true,
    is_followable: true,
    is_published: false,
  }
}

function editPage(p: LandingPage) {
  editing.value = { ...p, gallery: [...(p.gallery || [])] }
}

function cancelEdit() {
  editing.value = null
  error.value = ''
}

const titleWordCount = computed(() => {
  if (!editing.value?.title) return 0
  return editing.value.title.trim().split(/\s+/).filter(Boolean).length
})

async function uploadImage(event: Event, target: 'hero' | 'gallery') {
  const input = event.target as HTMLInputElement
  if (!input.files?.length || !editing.value) return
  const flag = target === 'hero' ? uploadingHero : uploadingGallery
  flag.value = true
  try {
    const formData = new FormData()
    formData.append('file', input.files[0])
    const { data } = await api.post('/images/upload', formData)
    if (target === 'hero') {
      editing.value.hero_image = data.url
    } else {
      if (!editing.value.gallery) editing.value.gallery = []
      if (editing.value.gallery.length < 10) {
        editing.value.gallery.push(data.url)
      }
    }
  } catch (e) {
    toast.error(getApiError(e, 'Nie udało się wgrać zdjęcia'))
  } finally {
    flag.value = false
    input.value = ''
  }
}

function removeGalleryImage(idx: number) {
  if (editing.value?.gallery) editing.value.gallery.splice(idx, 1)
}

async function savePage() {
  if (!editing.value) return
  if (titleWordCount.value < 3) {
    error.value = 'Tytuł (H1) musi mieć co najmniej 3 słowa'
    return
  }
  saving.value = true
  error.value = ''
  try {
    const payload = { ...editing.value }
    if ('id' in payload && payload.id) {
      await api.put(`/landing-pages/${payload.id}`, payload)
    } else {
      delete (payload as any).id
      await api.post('/landing-pages', payload)
    }
    editing.value = null
    await load()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Błąd zapisu'
  } finally {
    saving.value = false
  }
}

async function deletePage(id: number) {
  if (!confirm('Usunąć stronę oferty na stałe?')) return
  try {
    await api.delete(`/landing-pages/${id}`)
    await load()
    toast.success('Strona oferty usunięta')
  } catch (e) {
    toast.error(getApiError(e, 'Nie udało się usunąć strony'))
  }
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-3 sm:px-4 py-6 sm:py-10">
    <div class="flex items-center justify-between mb-8 flex-wrap gap-3">
      <div>
        <h1 class="font-heading text-2xl font-bold text-gray-900">Strony ofert</h1>
        <p class="text-sm text-gray-500 mt-1">Publiczne landingi na feedy.pl — każda oferta ma własny URL, SEO tagi i przycisk CTA do Twojego sklepu. <router-link to="/oferty/cennik" class="text-indigo-600 hover:text-indigo-800 font-medium">Zobacz cennik →</router-link></p>
      </div>
      <button v-if="!editing" @click="newPage"
        class="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer">
        + Nowa oferta
      </button>
    </div>

    <!-- Editor -->
    <section v-if="editing" class="bg-white border border-gray-200 rounded-2xl p-5 sm:p-6 mb-8">
      <h2 class="font-heading text-lg font-bold text-gray-900 mb-5">{{ editing.id ? 'Edytuj ofertę' : 'Nowa oferta' }}</h2>

      <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">{{ error }}</div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Tytuł / H1 * (min. 3 słowa)</label>
          <input v-model="editing.title" type="text" placeholder="np. Folia okienna przeciwsłoneczna Rzeszów"
            class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
          <p class="text-xs mt-1" :class="titleWordCount >= 3 ? 'text-green-600' : 'text-red-500'">Słów: {{ titleWordCount }} {{ titleWordCount < 3 ? '(za mało)' : '✓' }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Slug (opcjonalnie)</label>
          <input v-model="editing.slug" type="text" placeholder="np. folia-okienna/moja-oferta"
            class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
          <p class="text-xs text-gray-500 mt-1">Jeśli puste — wygeneruje się automatycznie. Twój user_id zostanie wstawiony po środku.</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Lokalizacja</label>
          <input v-model="editing.location" type="text" placeholder="np. Rzeszów, Podkarpackie"
            class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
        </div>

        <!-- Hero image -->
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Zdjęcie główne</label>
          <div v-if="editing.hero_image" class="mb-2">
            <img :src="editing.hero_image" class="max-h-48 rounded-xl border border-gray-200" />
          </div>
          <label class="inline-block cursor-pointer text-xs font-medium text-indigo-600 hover:text-indigo-800">
            <input type="file" accept="image/*" class="hidden" @change="(e) => uploadImage(e, 'hero')" />
            {{ uploadingHero ? 'Przesyłanie...' : (editing.hero_image ? 'Zmień zdjęcie' : '+ Wgraj zdjęcie') }}
          </label>
        </div>

        <!-- Gallery -->
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Galeria (max 10)</label>
          <div v-if="editing.gallery && editing.gallery.length" class="flex gap-2 flex-wrap mb-2">
            <div v-for="(img, idx) in editing.gallery" :key="idx" class="relative w-20 h-20 border border-gray-200 rounded-lg overflow-hidden">
              <img :src="img" class="w-full h-full object-cover" />
              <button type="button" @click="removeGalleryImage(idx)"
                class="absolute top-0.5 right-0.5 w-5 h-5 bg-black/70 hover:bg-red-600 text-white rounded-full text-xs flex items-center justify-center cursor-pointer">×</button>
            </div>
          </div>
          <label v-if="(editing.gallery?.length ?? 0) < 10" class="inline-block cursor-pointer text-xs font-medium text-indigo-600 hover:text-indigo-800">
            <input type="file" accept="image/*" class="hidden" @change="(e) => uploadImage(e, 'gallery')" />
            {{ uploadingGallery ? 'Przesyłanie...' : '+ Dodaj do galerii' }}
          </label>
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Krótki opis (excerpt)</label>
          <textarea v-model="editing.short_description" rows="2" placeholder="Jedno-dwa zdania"
            class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 resize-none"></textarea>
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Pełny opis (HTML)</label>
          <textarea v-model="editing.full_description" rows="8" placeholder="<p>Tekst opisu...</p>"
            class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-xs font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500/20 resize-y"></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Cena (opcjonalnie)</label>
          <input v-model="editing.price" type="text" placeholder="np. od 199 zł/m²"
            class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
          <label class="flex items-center gap-2 text-xs text-gray-600 mt-2 cursor-pointer">
            <input type="checkbox" v-model="editing.price_negotiable" class="w-3.5 h-3.5 rounded border-gray-300" />
            „Do wyceny indywidualnej"
          </label>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tekst CTA</label>
          <input v-model="editing.cta_text" type="text" placeholder="Przejdź do oferty!"
            class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
        </div>
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">URL CTA (link do Twojej strony)</label>
          <input v-model="editing.cta_url" type="url" placeholder="https://mojsklep.pl/produkt/123"
            class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
          <p class="text-xs text-gray-500 mt-1">Link wyjściowy z <code class="font-mono">rel="ugc sponsored nofollow noopener"</code></p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">SEO: meta title</label>
          <input v-model="editing.meta_title" type="text"
            class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
          <p class="text-xs text-gray-500 mt-1">Puste = taki sam jak tytuł</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">SEO: meta description</label>
          <textarea v-model="editing.meta_description" rows="2" maxlength="320"
            class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 resize-none"></textarea>
        </div>

        <div class="flex items-center gap-5 md:col-span-2 flex-wrap">
          <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
            <input type="checkbox" v-model="editing.is_published" class="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
            Opublikowana
          </label>
          <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
            <input type="checkbox" v-model="editing.is_indexable" class="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
            Indeksowalna
          </label>
          <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
            <input type="checkbox" v-model="editing.is_followable" class="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
            Follow
          </label>
        </div>
      </div>

      <div class="flex gap-2 mt-6">
        <button @click="savePage" :disabled="saving || titleWordCount < 3"
          class="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer">
          {{ saving ? 'Zapisywanie...' : 'Zapisz' }}
        </button>
        <button @click="cancelEdit"
          class="bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-semibold rounded-xl px-5 py-2.5 transition cursor-pointer">
          Anuluj
        </button>
      </div>
    </section>

    <!-- List -->
    <section v-if="!editing">
      <div v-if="loading" class="space-y-3">
        <SkeletonCard v-for="i in 3" :key="i" variant="list" />
      </div>
      <div v-else-if="pages.length === 0" class="text-gray-400 text-sm py-12 text-center border border-dashed border-gray-200 rounded-2xl">
        Jeszcze nie masz żadnych ofert. Kliknij „+ Nowa oferta" aby dodać pierwszą.
      </div>
      <div v-else class="space-y-3">
        <div v-for="p in pages" :key="p.id"
          class="bg-white border border-gray-200 rounded-2xl p-5 flex items-start justify-between gap-4 flex-wrap">
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2 mb-1 flex-wrap">
              <span class="text-[11px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full"
                :class="p.is_published ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                {{ p.is_published ? 'Opublikowana' : 'Szkic' }}
              </span>
              <span v-if="p.location" class="text-[11px] bg-indigo-50 text-indigo-700 rounded-full px-2 py-0.5 font-medium">{{ p.location }}</span>
            </div>
            <h3 class="font-heading text-base font-bold text-gray-900 truncate">{{ p.title }}</h3>
            <p class="text-xs text-gray-500 font-mono mt-1 truncate">/p/{{ p.slug }}</p>
          </div>
          <div class="flex gap-2 shrink-0">
            <a v-if="p.is_published" :href="`/p/${p.slug}`" target="_blank"
              class="text-xs font-medium text-gray-600 hover:text-gray-900 border border-gray-200 hover:border-gray-400 bg-gray-50 hover:bg-gray-100 rounded-lg px-3 py-1.5 transition cursor-pointer">
              Podgląd
            </a>
            <button @click="editPage(p)"
              class="text-xs font-medium text-indigo-600 hover:text-indigo-800 border border-indigo-200 hover:border-indigo-400 bg-indigo-50 hover:bg-indigo-100 rounded-lg px-3 py-1.5 transition cursor-pointer">
              Edytuj
            </button>
            <button @click="deletePage(p.id)"
              class="text-xs font-medium text-red-600 hover:text-red-800 border border-red-200 hover:border-red-400 bg-red-50 hover:bg-red-100 rounded-lg px-3 py-1.5 transition cursor-pointer">
              Usuń
            </button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
