<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useFeedsInStore } from '../stores/feedsIn'

const store = useFeedsInStore()
const router = useRouter()

const name = ref('')
const sourceUrl = ref('')
const error = ref('')
const loading = ref(false)

const nameValid = computed(() => name.value.trim().length >= 3)
const urlValid = computed(() => {
  if (!sourceUrl.value.trim()) return false
  try {
    const u = new URL(sourceUrl.value)
    return u.protocol === 'http:' || u.protocol === 'https:'
  } catch {
    return false
  }
})
const formValid = computed(() => nameValid.value && urlValid.value)

async function handleSubmit() {
  if (!formValid.value) return
  error.value = ''
  loading.value = true
  try {
    const feed = await store.createFeed(name.value.trim(), sourceUrl.value.trim())
    await store.fetchFeedXml(feed.id)
    router.push(`/feeds-in/${feed.id}`)
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    error.value = err.response?.data?.detail || 'Wystąpił błąd podczas tworzenia feedu.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-lg mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Dodaj feed źródłowy</h1>

    <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
      {{ error }}
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-5">
      <div>
        <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Nazwa</label>
        <p class="text-xs text-gray-500 mb-1">Nazwa do Twojej wygody, np. „Shoper - główny feed". Min. 3 znaki.</p>
        <input
          id="name"
          v-model="name"
          type="text"
          required
          minlength="3"
          maxlength="100"
          placeholder="np. Mój sklep - GMC"
          class="w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          :class="name.length === 0 || nameValid ? 'border-gray-300' : 'border-red-300'"
        />
        <p v-if="name.length > 0 && !nameValid" class="text-xs text-red-600 mt-1">Nazwa musi mieć co najmniej 3 znaki</p>
      </div>

      <div>
        <label for="source_url" class="block text-sm font-medium text-gray-700 mb-1">URL źródła</label>
        <p class="text-xs text-gray-500 mb-1">Link do XML z panelu sklepu (Shoper, WooCommerce, itp.)</p>
        <input
          id="source_url"
          v-model="sourceUrl"
          type="url"
          required
          placeholder="https://sklep.shoparena.pl/..."
          class="w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          :class="sourceUrl.length === 0 || urlValid ? 'border-gray-300' : 'border-red-300'"
        />
        <p v-if="sourceUrl.length > 0 && !urlValid" class="text-xs text-red-600 mt-1">Wprowadź prawidłowy adres URL (https://...)</p>
        <p v-else-if="urlValid" class="text-xs text-green-600 mt-1">✓ Prawidłowy URL</p>
      </div>

      <div class="flex items-center gap-3">
        <button
          type="submit"
          :disabled="loading || !formValid"
          class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 cursor-pointer"
        >
          {{ loading ? 'Tworzenie...' : 'Utwórz' }}
        </button>
        <router-link to="/dashboard" class="text-sm text-gray-600 hover:text-gray-800">Anuluj</router-link>
      </div>
    </form>
  </div>
</template>
