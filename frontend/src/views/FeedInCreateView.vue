<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useFeedsInStore } from '../stores/feedsIn'

const store = useFeedsInStore()
const router = useRouter()

const name = ref('')
const sourceUrl = ref('')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    const feed = await store.createFeed(name.value, sourceUrl.value)
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
        <p class="text-xs text-gray-500 mb-1">Nazwa do Twojej wygody, np. 'Shoper - główny feed'</p>
        <input
          id="name"
          v-model="name"
          type="text"
          required
          placeholder="np. Mój sklep - GMC"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        />
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
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>

      <div class="flex items-center gap-3">
        <button
          type="submit"
          :disabled="loading"
          class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 cursor-pointer"
        >
          {{ loading ? 'Tworzenie...' : 'Utwórz' }}
        </button>
        <router-link to="/dashboard" class="text-sm text-gray-600 hover:text-gray-800">Anuluj</router-link>
      </div>
    </form>
  </div>
</template>
