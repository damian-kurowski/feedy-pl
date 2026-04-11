<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useFeedsInStore } from '../stores/feedsIn'
import { useFeedsOutStore, type FeedOut } from '../stores/feedsOut'
import OnboardingWizard from '../components/OnboardingWizard.vue'
import SmartDashboard from '../components/SmartDashboard.vue'
import api from '../api/client'

const route = useRoute()
const auth = useAuthStore()
const store = useFeedsInStore()
const feedsOutStore = useFeedsOutStore()
const billingMsg = ref('')
const billingType = ref<'success' | 'cancel' | ''>('')
const showOnboarding = ref(false)
const analytics = ref<any>(null)
const qualityScores = ref<Record<number, { score: number; label: string }>>({})


onMounted(async () => {
  if (!localStorage.getItem('onboarding_done')) {
    showOnboarding.value = true
  }

  store.fetchFeeds()
  feedsOutStore.fetchFeeds()

  try {
    const { data } = await api.get('/feeds-in/analytics/summary')
    analytics.value = data
  } catch {}

  if (route.query.billing === 'success') {
    billingMsg.value = 'Plan został zmieniony pomyślnie!'
    billingType.value = 'success'
    auth.fetchUser()
    setTimeout(() => { billingMsg.value = '' }, 5000)
  } else if (route.query.billing === 'cancel') {
    billingMsg.value = 'Płatność anulowana.'
    billingType.value = 'cancel'
    setTimeout(() => { billingMsg.value = '' }, 5000)
  }
})

watch(() => feedsOutStore.feeds, async (feeds) => {
  for (const feed of feeds) {
    if (!qualityScores.value[feed.id]) {
      const result = await feedsOutStore.getQualityScore(feed.id)
      if (result) {
        qualityScores.value[feed.id] = result
      }
    }
  }
}, { immediate: false })

async function openPortal() {
  try {
    const { data } = await api.get('/billing/portal')
    window.open(data.portal_url, '_blank')
  } catch (e: any) {
    alert(e.response?.data?.detail || 'Błąd')
  }
}

function statusColor(status: string) {
  switch (status) {
    case 'fetching': return 'bg-yellow-100 text-yellow-700'
    case 'success': return 'bg-green-100 text-green-700'
    case 'error': return 'bg-red-100 text-red-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}

function typeBadgeColor(type: string) {
  switch (type) {
    case 'ceneo': return 'bg-green-100 text-green-700'
    case 'gmc': return 'bg-blue-100 text-blue-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}

function feedOutPublicUrl(linkOut: string) {
  return `${window.location.origin}/feed/${linkOut}.xml`
}

async function copyToClipboard(text: string) {
  await navigator.clipboard.writeText(text)
}

async function handleDelete(id: number) {
  if (!confirm('Czy na pewno chcesz usunąć ten feed?')) return
  await store.deleteFeed(id)
}

async function handleDeleteOut(id: number) {
  if (!confirm('Czy na pewno chcesz usunąć ten feed wyjściowy?')) return
  await feedsOutStore.deleteFeed(id)
}

async function toggleActive(feedOut: FeedOut) {
  await feedsOutStore.updateFeed(feedOut.id, { active: !feedOut.active })
  await feedsOutStore.fetchFeeds()
}

function closeOnboarding() {
  showOnboarding.value = false
  localStorage.setItem('onboarding_done', '1')
}
</script>

<template>
  <OnboardingWizard v-if="showOnboarding" :show="showOnboarding" @close="closeOnboarding" />
  <div class="max-w-4xl mx-auto px-4 py-8">
    <!-- Billing notification -->
    <div v-if="billingMsg" :class="[billingType === 'success' ? 'bg-green-50 border-green-200 text-green-800' : 'bg-gray-50 border-gray-200 text-gray-700', 'mb-4 p-3 border rounded-md text-sm']">
      {{ billingMsg }}
    </div>

    <!-- Analytics overview -->
    <div v-if="analytics" class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-8">
      <div class="bg-white rounded-2xl border border-gray-200 p-6 text-center hover:shadow-md transition-shadow">
        <p class="font-heading text-3xl font-extrabold text-indigo-600">{{ analytics.total_products }}</p>
        <p class="text-[12px] text-gray-400 mt-1.5 font-medium">Produktów</p>
      </div>
      <div class="bg-white rounded-2xl border border-gray-200 p-6 text-center hover:shadow-md transition-shadow">
        <p class="font-heading text-3xl font-extrabold text-indigo-600">{{ analytics.total_feeds_in }}</p>
        <p class="text-[12px] text-gray-400 mt-1.5 font-medium">Feedów źródłowych</p>
      </div>
      <div class="bg-white rounded-2xl border border-gray-200 p-6 text-center hover:shadow-md transition-shadow">
        <p class="font-heading text-3xl font-extrabold text-indigo-600">{{ analytics.active_feeds_out }}</p>
        <p class="text-[12px] text-gray-400 mt-1.5 font-medium">Feedów aktywnych</p>
      </div>
      <div class="bg-white rounded-2xl border border-gray-200 p-6 text-center hover:shadow-md transition-shadow">
        <p class="font-heading text-3xl font-extrabold text-green-600">{{ analytics.feeds_ok }}</p>
        <p class="text-[12px] text-gray-400 mt-1.5 font-medium">OK</p>
      </div>
      <div class="bg-white rounded-2xl border border-gray-200 p-6 text-center hover:shadow-md transition-shadow">
        <p class="font-heading text-3xl font-extrabold" :class="analytics.feeds_error > 0 ? 'text-red-600' : 'text-gray-300'">{{ analytics.feeds_error }}</p>
        <p class="text-[12px] text-gray-400 mt-1.5 font-medium">Błędów</p>
      </div>
    </div>

    <!-- Plan banner -->
    <div v-if="auth.user" class="mb-8 p-6 bg-white border border-gray-200 rounded-2xl flex items-center justify-between">
      <div>
        <span class="text-sm text-gray-500">Twój plan:</span>
        <span class="ml-2 font-semibold text-indigo-700">{{ auth.user.plan.name }}</span>
        <span class="ml-2 text-xs text-gray-400">({{ auth.user.plan.max_products || '∞' }} produktów, {{ auth.user.plan.max_feeds_out || '∞' }} feedów)</span>
      </div>
      <button v-if="auth.user.plan.name === 'Free'" @click="$router.push('/#pricing')" class="text-sm text-indigo-600 hover:text-indigo-800 font-medium">Zmień plan →</button>
      <button v-else @click="openPortal" class="text-sm text-indigo-600 hover:text-indigo-800 font-medium">Zarządzaj subskrypcją</button>
    </div>

    <!-- Smart Dashboard — recommendations & alerts -->
    <div class="mb-8">
      <SmartDashboard />
    </div>

    <div class="flex items-center justify-between mb-8">
      <h1 class="font-heading text-2xl font-bold text-gray-900">Dashboard</h1>
      <router-link
        to="/feeds-in/new"
        class="inline-flex items-center bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer"
      >
        Dodaj feed źródłowy
      </router-link>
    </div>

    <h2 class="font-heading text-lg font-bold text-gray-900 mb-3">Feedy źródłowe ({{ store.feeds.length }})</h2>

    <div v-if="store.feeds.length === 0" class="text-center py-16 text-gray-500 bg-white border border-gray-200 rounded-2xl">
      <p class="mb-1">Nie masz jeszcze żadnych feedów.</p>
      <p class="text-sm">Dodaj swój pierwszy feed źródłowy -- wklej link do XML z Twojego sklepu.</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="feed in store.feeds"
        :key="feed.id"
        class="bg-white border border-gray-200 rounded-2xl p-6 flex items-center justify-between hover:shadow-md transition-shadow"
      >
        <div class="min-w-0 flex-1">
          <router-link
            :to="`/feeds-in/${feed.id}`"
            class="text-lg font-semibold text-indigo-600 hover:text-indigo-800"
          >
            {{ feed.name }}
          </router-link>
          <p class="text-sm text-gray-500 truncate mt-1">{{ feed.source_url }}</p>
          <p v-if="feed.fetch_status === 'error' && feed.fetch_error" class="text-xs text-red-500 mt-1 truncate">
            {{ feed.fetch_error }}
          </p>
          <span class="text-xs text-gray-400 mt-1">{{ feed.product_count }} produktów</span>
        </div>
        <div class="flex items-center gap-3 ml-4">
          <span
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
            :class="statusColor(feed.fetch_status)"
            :title="feed.fetch_status === 'pending' ? 'Oczekuje' : feed.fetch_status === 'fetching' ? 'Pobieranie...' : feed.fetch_status === 'success' ? 'Gotowy' : feed.fetch_status === 'error' ? 'Błąd' : ''"
          >
            {{ feed.fetch_status === 'pending' ? 'Oczekuje' : feed.fetch_status === 'fetching' ? 'Pobieranie...' : feed.fetch_status === 'success' ? 'Gotowy' : feed.fetch_status === 'error' ? 'Błąd' : feed.fetch_status }}
          </span>
          <button
            class="text-red-500 hover:text-red-700 text-sm cursor-pointer"
            @click="handleDelete(feed.id)"
          >
            Usuń
          </button>
        </div>
      </div>
    </div>

    <!-- Feeds Out Section -->
    <div class="flex items-center justify-between mt-12 mb-4">
      <h2 class="font-heading text-lg font-bold text-gray-900">Feedy wyjściowe ({{ feedsOutStore.feeds.length }})</h2>
    </div>

    <div v-if="feedsOutStore.feeds.length === 0" class="text-center py-12 text-gray-500 bg-white border border-gray-200 rounded-2xl">
      Nie masz feedów wyjściowych. Wybierz feed źródłowy i kliknij "Utwórz feed wyjściowy".
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="feed in feedsOutStore.feeds"
        :key="feed.id"
        class="bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3 min-w-0">
            <router-link
              :to="`/feeds-out/${feed.id}`"
              class="text-lg font-semibold text-indigo-600 hover:text-indigo-800"
            >
              {{ feed.name }}
            </router-link>
            <span
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="typeBadgeColor(feed.type)"
            >
              {{ feed.type }}
            </span>
            <button
              @click="toggleActive(feed)"
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium cursor-pointer"
              :class="feed.active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
            >
              {{ feed.active ? 'Aktywny' : 'Nieaktywny' }}
            </button>
            <span
              v-if="qualityScores[feed.id]"
              class="inline-flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold"
              :class="{
                'bg-green-100 text-green-700': qualityScores[feed.id].score >= 90,
                'bg-yellow-100 text-yellow-700': qualityScores[feed.id].score >= 70 && qualityScores[feed.id].score < 90,
                'bg-orange-100 text-orange-700': qualityScores[feed.id].score >= 50 && qualityScores[feed.id].score < 70,
                'bg-red-100 text-red-700': qualityScores[feed.id].score < 50,
              }"
              :title="`Jakość feedu: ${qualityScores[feed.id].score}% — ${qualityScores[feed.id].label}`"
            >
              {{ qualityScores[feed.id].score }}
            </span>
          </div>
          <button
            class="text-red-500 hover:text-red-700 text-sm cursor-pointer ml-4"
            @click="handleDeleteOut(feed.id)"
          >
            Usuń
          </button>
        </div>
        <div class="mt-2 flex items-center gap-2">
          <span class="text-sm text-gray-500 truncate">Link: {{ feedOutPublicUrl(feed.link_out) }}</span>
          <button
            class="text-xs text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer whitespace-nowrap"
            @click="copyToClipboard(feedOutPublicUrl(feed.link_out))"
          >
            Kopiuj
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
