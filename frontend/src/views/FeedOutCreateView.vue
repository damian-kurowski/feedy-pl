<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFeedsOutStore } from '../stores/feedsOut'

const route = useRoute()
const router = useRouter()
const store = useFeedsOutStore()

const feedInId = Number(route.query.feed_in_id)
const step = ref(1)
const selectedPlatform = ref('')
const platformInfo = ref<any>(null)
const platforms = ref<any[]>([])
const name = ref('')
const loading = ref(false)
const error = ref('')

onMounted(async () => {
  try { platforms.value = await store.getPlatforms() } catch {}
})

async function selectPlatform(platform: string) {
  selectedPlatform.value = platform
  try { platformInfo.value = await store.getPlatformInfo(platform) } catch {}
  step.value = 2
}

function goBack() {
  if (step.value === 2) { step.value = 1; platformInfo.value = null }
  else if (step.value === 3) { step.value = 2 }
}

async function handleCreate() {
  if (!name.value.trim()) { error.value = 'Nazwa jest wymagana'; return }
  error.value = ''; loading.value = true
  try {
    const templateMap: Record<string, string | undefined> = {
      ceneo: 'ceneo', allegro: 'allegro', gmc: undefined, facebook: undefined,
      skapiec: undefined, domodi: undefined, custom: undefined,
    }
    const feed = await store.createFeed({
      feed_in_id: feedInId, name: name.value.trim(),
      type: selectedPlatform.value, template: templateMap[selectedPlatform.value],
    })
    router.push(`/feeds-out/${feed.id}`)
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Blad podczas tworzenia feedu'
  } finally { loading.value = false }
}
</script>

<template>
  <div class="max-w-3xl mx-auto py-10 px-4">
    <div class="flex items-center gap-2 mb-8">
      <div v-for="s in 3" :key="s" class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium"
          :class="step >= s ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'">{{ s }}</div>
        <span class="text-sm" :class="step >= s ? 'text-gray-900' : 'text-gray-400'">
          {{ s === 1 ? 'Platforma' : s === 2 ? 'Informacje' : 'Utworz' }}
        </span>
        <div v-if="s < 3" class="w-8 h-px bg-gray-300" />
      </div>
    </div>

    <div v-if="step === 1">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Wybierz platforme</h1>
      <p class="text-sm text-gray-500 mb-6">Na jaka platforme chcesz wygenerowac feed produktowy?</p>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <button v-for="p in platforms" :key="p.platform"
          class="border-2 rounded-lg p-5 text-left cursor-pointer transition-colors hover:border-indigo-300 hover:bg-indigo-50"
          :class="selectedPlatform === p.platform ? 'border-indigo-600 bg-indigo-50' : 'border-gray-200'"
          @click="selectPlatform(p.platform)">
          <div class="font-semibold text-gray-900 mb-1">{{ p.name }}</div>
          <div class="text-xs text-gray-500 mb-2">{{ p.description }}</div>
          <div class="text-xs text-indigo-600 font-medium">{{ p.required_count }} pol wymaganych</div>
        </button>
      </div>
    </div>

    <div v-if="step === 2 && platformInfo">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ platformInfo.name }}</h1>
      <p class="text-sm text-gray-500 mb-6">{{ platformInfo.description }}</p>
      <div class="space-y-6">
        <div>
          <h2 class="text-sm font-semibold text-gray-700 mb-2">Pola wymagane</h2>
          <div class="space-y-2">
            <div v-for="f in platformInfo.required_fields" :key="f.field" class="flex items-start gap-2 text-sm">
              <span class="text-green-500 mt-0.5 shrink-0">V</span>
              <div><span class="font-medium text-gray-800">{{ f.field }}</span><span class="text-gray-500 ml-1">— {{ f.description }}</span></div>
            </div>
          </div>
        </div>
        <div>
          <h2 class="text-sm font-semibold text-gray-700 mb-2">Pola zalecane</h2>
          <div class="space-y-2">
            <div v-for="f in platformInfo.recommended_fields" :key="f.field" class="flex items-start gap-2 text-sm">
              <span class="text-gray-400 mt-0.5 shrink-0">o</span>
              <div><span class="font-medium text-gray-600">{{ f.field }}</span><span class="text-gray-500 ml-1">— {{ f.description }}</span></div>
            </div>
          </div>
        </div>
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h2 class="text-sm font-semibold text-blue-800 mb-2">Wskazowki</h2>
          <ul class="space-y-1">
            <li v-for="(tip, idx) in platformInfo.tips" :key="idx" class="text-sm text-blue-700 flex gap-2">
              <span class="shrink-0">-</span><span>{{ tip }}</span>
            </li>
          </ul>
        </div>
      </div>
      <div class="flex items-center gap-4 mt-8">
        <button class="text-sm text-gray-600 hover:text-gray-800 cursor-pointer" @click="goBack">Wstecz</button>
        <button class="py-2 px-6 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-md cursor-pointer" @click="step = 3">Dalej</button>
      </div>
    </div>

    <div v-if="step === 3">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">Utworz feed wyjsciowy</h1>
      <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">{{ error }}</div>
      <div class="bg-gray-50 border rounded-lg p-4 mb-6">
        <div class="text-sm text-gray-500">Platforma: <span class="font-medium text-gray-900">{{ platformInfo?.name }}</span></div>
        <div class="text-sm text-gray-500 mt-1">Pola wymagane: <span class="font-medium text-gray-900">{{ platformInfo?.required_fields?.length }}</span></div>
      </div>
      <div class="mb-6">
        <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Nazwa feeda</label>
        <input id="name" v-model="name" type="text" required
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          :placeholder="`np. ${platformInfo?.name} - Moj Sklep`" />
      </div>
      <div class="flex items-center gap-4">
        <button class="text-sm text-gray-600 hover:text-gray-800 cursor-pointer" @click="goBack">Wstecz</button>
        <button :disabled="loading" class="py-2 px-6 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium rounded-md cursor-pointer" @click="handleCreate">
          {{ loading ? 'Tworzenie...' : 'Utworz feed' }}
        </button>
      </div>
    </div>
  </div>
</template>
