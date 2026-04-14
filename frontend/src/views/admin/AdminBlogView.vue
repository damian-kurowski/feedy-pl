<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '../../stores/auth'
import api from '../../api/client'
import { useToast, getApiError } from '../../composables/useToast'
import SkeletonCard from '../../components/SkeletonCard.vue'

const toast = useToast()
const AUTOSAVE_KEY = 'admin_blog_draft_v1'
const AUTOSAVE_INTERVAL_MS = 5000

interface BlogPost {
  id: number
  slug: string
  title: string
  html: string
  is_published: boolean
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

const auth = useAuthStore()
const posts = ref<BlogPost[]>([])
const editing = ref<Partial<BlogPost> | null>(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const showPreview = ref(false)
const lastAutosaveAt = ref<Date | null>(null)
let autosaveTimer: ReturnType<typeof setInterval> | null = null

const titleLen = computed(() => (editing.value?.title || '').length)
const metaTitleLen = computed(() => (editing.value?.meta_title || '').length)
const metaDescLen = computed(() => (editing.value?.meta_description || '').length)
const slugRegex = /^[a-z0-9-]+$/
const slugValid = computed(() => !editing.value?.slug || slugRegex.test(editing.value.slug))

function lenColor(len: number, ideal: [number, number]) {
  if (len === 0) return 'text-gray-400'
  if (len < ideal[0]) return 'text-amber-600'
  if (len > ideal[1]) return 'text-red-600'
  return 'text-green-600'
}

function persistDraftLocal() {
  if (!editing.value) return
  try {
    localStorage.setItem(AUTOSAVE_KEY, JSON.stringify(editing.value))
    lastAutosaveAt.value = new Date()
  } catch {
    // localStorage quota — ignore
  }
}

function loadDraftLocal(): Partial<BlogPost> | null {
  try {
    const raw = localStorage.getItem(AUTOSAVE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function clearDraftLocal() {
  try {
    localStorage.removeItem(AUTOSAVE_KEY)
  } catch {}
  lastAutosaveAt.value = null
}

const STAFF_EMAILS = ['test@feedy.pl', 'kurowsski@gmail.com', 'admin@feedy.pl']
const isStaff = computed(() => auth.user && STAFF_EMAILS.includes(auth.user.email))

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/admin/blog')
    posts.value = data
  } catch {
    posts.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (auth.token && !auth.user) await auth.fetchUser()
  if (isStaff.value) await load()
  else loading.value = false
})

function blankPost(): Partial<BlogPost> {
  return {
    slug: '',
    title: '',
    html: '<h2>Pierwszy nagłówek</h2>\n<p>Treść...</p>',
    is_published: false,
    meta_title: '',
    meta_description: '',
    is_indexable: true,
    is_followable: true,
    hero_image_path: '',
    hero_image_alt: '',
    og_image_path: '',
    reading_minutes: 5,
    category: '',
    excerpt: '',
  }
}

function newPost() {
  const draft = loadDraftLocal()
  if (draft && !('id' in draft)) {
    if (confirm('Znaleziono niezapisany szkic nowego wpisu. Wczytać?')) {
      editing.value = draft
      showPreview.value = false
      return
    }
    clearDraftLocal()
  }
  editing.value = blankPost()
  showPreview.value = false
}

function editPost(p: BlogPost) {
  editing.value = { ...p }
  showPreview.value = false
  clearDraftLocal()
}

function cancelEdit() {
  if (editing.value && !('id' in editing.value && editing.value.id)) {
    if (lastAutosaveAt.value && !confirm('Niezapisany szkic zostanie odrzucony. Kontynuować?')) {
      return
    }
  }
  editing.value = null
  error.value = ''
  clearDraftLocal()
}

// Autosave: every AUTOSAVE_INTERVAL_MS while editing
watch(editing, (val) => {
  if (autosaveTimer) {
    clearInterval(autosaveTimer)
    autosaveTimer = null
  }
  if (val && !val.id) {
    autosaveTimer = setInterval(persistDraftLocal, AUTOSAVE_INTERVAL_MS)
  }
}, { deep: true })

async function savePost() {
  if (!editing.value) return
  if (editing.value.slug && !slugRegex.test(editing.value.slug)) {
    error.value = 'Slug może zawierać tylko małe litery, cyfry i myślniki (a-z, 0-9, -)'
    return
  }
  saving.value = true
  error.value = ''
  try {
    const payload = { ...editing.value }
    if ('id' in payload && payload.id) {
      await api.put(`/admin/blog/${payload.id}`, payload)
      toast.success('Wpis zaktualizowany')
    } else {
      delete (payload as any).id
      await api.post('/admin/blog', payload)
      toast.success('Wpis utworzony')
    }
    editing.value = null
    clearDraftLocal()
    await load()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Błąd zapisu'
    toast.error(getApiError(e, 'Nie udało się zapisać wpisu'))
  } finally {
    saving.value = false
  }
}

async function deletePost(id: number) {
  if (!confirm('Usunąć wpis na stałe?')) return
  try {
    await api.delete(`/admin/blog/${id}`)
    await load()
    toast.success('Wpis usunięty')
  } catch (e) {
    toast.error(getApiError(e, 'Nie udało się usunąć wpisu'))
  }
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-3 sm:px-4 py-6 sm:py-10">
    <div v-if="!isStaff && !loading" class="bg-red-50 border border-red-200 rounded-2xl p-6 text-red-700">
      <h1 class="font-heading text-lg font-bold mb-2">Brak dostępu</h1>
      <p class="text-sm">Ta strona jest dostępna tylko dla administratorów.</p>
    </div>

    <template v-else>
      <div class="flex items-center justify-between mb-8 flex-wrap gap-3">
        <div>
          <h1 class="font-heading text-2xl font-bold text-gray-900">Admin: Blog</h1>
          <p class="text-sm text-gray-500 mt-1">Zarządzaj wpisami blogowymi</p>
        </div>
        <button v-if="!editing" @click="newPost"
          class="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer">
          + Nowy wpis
        </button>
      </div>

      <!-- Editor -->
      <section v-if="editing" class="bg-white border border-gray-200 rounded-2xl p-5 sm:p-6 mb-8">
        <div class="flex items-center justify-between mb-5 flex-wrap gap-3">
          <h2 class="font-heading text-lg font-bold text-gray-900">{{ editing.id ? 'Edytuj wpis' : 'Nowy wpis' }}</h2>
          <div class="flex items-center gap-3">
            <span v-if="lastAutosaveAt && !editing.id" class="text-[11px] text-gray-400">
              Zapisano lokalnie: {{ lastAutosaveAt.toLocaleTimeString('pl-PL') }}
            </span>
            <button
              type="button"
              @click="showPreview = !showPreview"
              class="text-xs font-semibold text-indigo-600 hover:text-indigo-800 border border-indigo-200 hover:border-indigo-400 bg-indigo-50 hover:bg-indigo-100 rounded-lg px-3 py-1.5 transition cursor-pointer"
            >
              {{ showPreview ? 'Ukryj podgląd' : 'Podgląd' }}
            </button>
          </div>
        </div>

        <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">{{ error }}</div>

        <!-- Preview overlay -->
        <div v-if="showPreview" class="mb-6 border border-gray-200 rounded-xl bg-gray-50 p-5 sm:p-8">
          <p class="text-[10px] font-semibold uppercase tracking-wider text-gray-400 mb-2">Podgląd wpisu</p>
          <article>
            <div class="flex flex-wrap items-center gap-2 text-xs text-gray-400 mb-2">
              <span v-if="editing.category" class="bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full font-medium">{{ editing.category }}</span>
              <span v-if="editing.reading_minutes">{{ editing.reading_minutes }} min czytania</span>
            </div>
            <h1 class="font-heading text-2xl sm:text-3xl font-extrabold text-gray-900 leading-tight mb-2">{{ editing.title || '(brak tytułu)' }}</h1>
            <p v-if="editing.excerpt" class="text-base text-gray-600 mb-4">{{ editing.excerpt }}</p>
            <img v-if="editing.hero_image_path" :src="editing.hero_image_path" :alt="editing.hero_image_alt || editing.title || ''" class="w-full max-h-72 object-cover rounded-xl border border-gray-200 mb-6" />
            <div class="prose prose-sm sm:prose-base max-w-none" v-html="editing.html || '<p class=\'text-gray-400\'>(brak treści)</p>'"></div>
          </article>
          <div class="mt-6 pt-4 border-t border-gray-200 text-xs text-gray-400 space-y-1">
            <p>URL: <code class="font-mono text-gray-600">/blog/{{ editing.slug || '...' }}</code></p>
            <p>SEO title: <code class="font-mono text-gray-600">{{ editing.meta_title || editing.title || '...' }}</code></p>
            <p>SEO description: <code class="font-mono text-gray-600">{{ editing.meta_description || editing.excerpt || '...' }}</code></p>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Tytuł (H1)</label>
            <input v-model="editing.title" type="text"
              class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
            <p class="text-xs mt-1" :class="lenColor(titleLen, [30, 70])">{{ titleLen }} znaków · idealnie 30-70</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Slug (URL)</label>
            <input v-model="editing.slug" type="text" placeholder="np. jak-zrobic-feed"
              class="w-full px-3.5 py-2.5 bg-gray-50 border rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
              :class="slugValid ? 'border-gray-200 focus:border-indigo-500' : 'border-red-300 focus:border-red-500'" />
            <p v-if="!slugValid" class="text-xs text-red-600 mt-1">Tylko a-z, 0-9, myślniki</p>
            <p v-else class="text-xs text-gray-400 mt-1">URL: /blog/{{ editing.slug || '...' }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Kategoria</label>
            <input v-model="editing.category" type="text" placeholder="np. Ceneo"
              class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Krótki opis (excerpt)</label>
            <textarea v-model="editing.excerpt" rows="2"
              class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 resize-none"></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Hero image URL</label>
            <input v-model="editing.hero_image_path" type="text" placeholder="https://..."
              class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Hero image alt</label>
            <input v-model="editing.hero_image_alt" type="text"
              class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Meta title (SEO)</label>
            <input v-model="editing.meta_title" type="text" maxlength="80"
              class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
            <p class="text-xs mt-1" :class="lenColor(metaTitleLen, [50, 60])">{{ metaTitleLen }}/60 znaków</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Czas czytania (min)</label>
            <input v-model.number="editing.reading_minutes" type="number" min="1"
              class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Meta description (SEO)</label>
            <textarea v-model="editing.meta_description" rows="2" maxlength="320"
              class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 resize-none"></textarea>
            <p class="text-xs mt-1" :class="lenColor(metaDescLen, [120, 160])">{{ metaDescLen }}/160 znaków</p>
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Treść (HTML)</label>
            <textarea v-model="editing.html" rows="16"
              class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-xs font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500/20 resize-y"></textarea>
            <p class="text-xs text-gray-500 mt-1">Wklej gotowy HTML (&lt;h2&gt;, &lt;p&gt;, &lt;ul&gt;, &lt;strong&gt;, &lt;a&gt;).</p>
          </div>
          <div class="flex items-center gap-5 md:col-span-2 flex-wrap">
            <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
              <input type="checkbox" v-model="editing.is_published" class="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
              Opublikowany
            </label>
            <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
              <input type="checkbox" v-model="editing.is_indexable" class="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
              Indeksowalny (index)
            </label>
            <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
              <input type="checkbox" v-model="editing.is_followable" class="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
              Follow
            </label>
          </div>
        </div>

        <div class="flex gap-2 mt-6">
          <button @click="savePost" :disabled="saving || !editing.slug || !editing.title || !editing.html"
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
        <div v-else-if="posts.length === 0" class="text-gray-400 text-sm py-12 text-center border border-dashed border-gray-200 rounded-2xl">
          Brak wpisów. Kliknij „+ Nowy wpis" aby dodać pierwszy.
        </div>
        <div v-else class="space-y-3">
          <div v-for="p in posts" :key="p.id"
            class="bg-white border border-gray-200 rounded-2xl p-5 flex items-start justify-between gap-4 flex-wrap">
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2 mb-1 flex-wrap">
                <span class="text-[11px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full"
                  :class="p.is_published ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                  {{ p.is_published ? 'Opublikowany' : 'Szkic' }}
                </span>
                <span v-if="p.category" class="text-[11px] bg-indigo-100 text-indigo-700 rounded-full px-2 py-0.5 font-medium">{{ p.category }}</span>
              </div>
              <h3 class="font-heading text-base font-bold text-gray-900 truncate">{{ p.title }}</h3>
              <p class="text-xs text-gray-500 font-mono mt-1">/{{ p.slug }}</p>
            </div>
            <div class="flex gap-2 shrink-0">
              <button @click="editPost(p)"
                class="text-xs font-medium text-indigo-600 hover:text-indigo-800 border border-indigo-200 hover:border-indigo-400 bg-indigo-50 hover:bg-indigo-100 rounded-lg px-3 py-1.5 transition cursor-pointer">
                Edytuj
              </button>
              <button @click="deletePost(p.id)"
                class="text-xs font-medium text-red-600 hover:text-red-800 border border-red-200 hover:border-red-400 bg-red-50 hover:bg-red-100 rounded-lg px-3 py-1.5 transition cursor-pointer">
                Usuń
              </button>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>
