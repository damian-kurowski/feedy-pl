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

function timeAgo(dateStr: string | null): string {
  if (!dateStr) return 'nigdy'
  const now = new Date()
  const date = new Date(dateStr)
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000)
  if (diff < 60) return 'przed chwilą'
  if (diff < 3600) return `${Math.floor(diff / 60)} min temu`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h temu`
  if (diff < 172800) return 'wczoraj'
  return `${Math.floor(diff / 86400)} dni temu`
}

function statusDotColor(status: string): string {
  switch (status) {
    case 'success': return 'bg-green-400'
    case 'fetching': return 'bg-yellow-400 animate-pulse'
    case 'error': return 'bg-red-400'
    default: return 'bg-gray-300'
  }
}

function statusLabel(status: string): string {
  switch (status) {
    case 'success': return 'Gotowy'
    case 'fetching': return 'Pobieranie...'
    case 'error': return 'Błąd'
    case 'pending': return 'Oczekuje'
    default: return status
  }
}

function qualityScoreColor(score: number): string {
  if (score >= 90) return 'text-green-600 bg-green-50 ring-green-200'
  if (score >= 70) return 'text-yellow-600 bg-yellow-50 ring-yellow-200'
  if (score >= 50) return 'text-orange-600 bg-orange-50 ring-orange-200'
  return 'text-red-600 bg-red-50 ring-red-200'
}
</script>

<template>
  <OnboardingWizard v-if="showOnboarding" :show="showOnboarding" @close="closeOnboarding" />
  <div class="max-w-5xl mx-auto px-3 sm:px-4 py-6 sm:py-10">

    <!-- Billing notification -->
    <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="opacity-0 -translate-y-2" enter-to-class="opacity-100 translate-y-0" leave-active-class="transition duration-200 ease-in" leave-from-class="opacity-100" leave-to-class="opacity-0">
      <div v-if="billingMsg" :class="[billingType === 'success' ? 'bg-green-50 border-green-200 text-green-800' : 'bg-gray-50 border-gray-200 text-gray-700', 'mb-6 p-4 border rounded-2xl text-sm flex items-center gap-3']">
        <svg v-if="billingType === 'success'" class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        {{ billingMsg }}
      </div>
    </Transition>

    <!-- Page header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="font-heading text-2xl font-bold text-gray-900">Dashboard</h1>
        <p class="text-sm text-gray-400 mt-1">Przegląd Twoich feedów produktowych</p>
      </div>
      <router-link
        to="/feeds-in/new"
        class="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/25 cursor-pointer active:scale-[0.98]"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg>
        Dodaj feed
      </router-link>
    </div>

    <!-- Analytics Cards -->
    <div v-if="analytics" class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
      <!-- Products -->
      <div class="relative overflow-hidden bg-gradient-to-br from-indigo-50 to-white rounded-2xl border border-indigo-100/50 p-6 hover:shadow-md hover:shadow-indigo-100/50 transition-all duration-300">
        <div class="absolute top-3 right-3 w-10 h-10 rounded-xl bg-indigo-100/80 flex items-center justify-center">
          <svg class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" /></svg>
        </div>
        <p class="font-heading text-3xl font-extrabold text-gray-900 tabular-nums animate-fade-in">{{ analytics.total_products }}</p>
        <p class="text-xs text-gray-500 mt-1 font-medium">Produktów</p>
      </div>
      <!-- Source feeds -->
      <div class="relative overflow-hidden bg-gradient-to-br from-indigo-50 to-white rounded-2xl border border-indigo-100/50 p-6 hover:shadow-md hover:shadow-indigo-100/50 transition-all duration-300">
        <div class="absolute top-3 right-3 w-10 h-10 rounded-xl bg-indigo-100/80 flex items-center justify-center">
          <svg class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" /></svg>
        </div>
        <p class="font-heading text-3xl font-extrabold text-gray-900 tabular-nums animate-fade-in">{{ analytics.total_feeds_in }}</p>
        <p class="text-xs text-gray-500 mt-1 font-medium">Feedów źródłowych</p>
      </div>
      <!-- Active feeds -->
      <div class="relative overflow-hidden bg-gradient-to-br from-indigo-50 to-white rounded-2xl border border-indigo-100/50 p-6 hover:shadow-md hover:shadow-indigo-100/50 transition-all duration-300">
        <div class="absolute top-3 right-3 w-10 h-10 rounded-xl bg-indigo-100/80 flex items-center justify-center">
          <svg class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg>
        </div>
        <p class="font-heading text-3xl font-extrabold text-gray-900 tabular-nums animate-fade-in">{{ analytics.active_feeds_out }}</p>
        <p class="text-xs text-gray-500 mt-1 font-medium">Feedów aktywnych</p>
      </div>
      <!-- OK -->
      <div class="relative overflow-hidden bg-gradient-to-br from-green-50 to-white rounded-2xl border border-green-100/50 p-6 hover:shadow-md hover:shadow-green-100/50 transition-all duration-300">
        <div class="absolute top-3 right-3 w-10 h-10 rounded-xl bg-green-100/80 flex items-center justify-center">
          <svg class="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </div>
        <p class="font-heading text-3xl font-extrabold text-gray-900 tabular-nums animate-fade-in">{{ analytics.feeds_ok }}</p>
        <p class="text-xs text-gray-500 mt-1 font-medium">OK</p>
      </div>
      <!-- Errors -->
      <div class="relative overflow-hidden rounded-2xl p-6 transition-all duration-300" :class="analytics.feeds_error > 0 ? 'bg-gradient-to-br from-red-50 to-white border border-red-100/50 hover:shadow-md hover:shadow-red-100/50' : 'bg-gradient-to-br from-gray-50 to-white border border-gray-100/50 hover:shadow-md'">
        <div class="absolute top-3 right-3 w-10 h-10 rounded-xl flex items-center justify-center" :class="analytics.feeds_error > 0 ? 'bg-red-100/80' : 'bg-gray-100/80'">
          <svg class="w-5 h-5" :class="analytics.feeds_error > 0 ? 'text-red-600' : 'text-gray-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>
        </div>
        <p class="font-heading text-3xl font-extrabold tabular-nums animate-fade-in" :class="analytics.feeds_error > 0 ? 'text-red-600' : 'text-gray-300'">{{ analytics.feeds_error }}</p>
        <p class="text-xs text-gray-500 mt-1 font-medium">Błędów</p>
      </div>
    </div>

    <!-- Plan banner -->
    <div v-if="auth.user" class="mb-8 p-5 bg-white border border-gray-200 rounded-2xl flex items-center justify-between hover:border-indigo-200 transition-colors">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-indigo-100 flex items-center justify-center">
          <svg class="w-4.5 h-4.5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" /></svg>
        </div>
        <div>
          <span class="text-sm text-gray-500">Twój plan:</span>
          <span class="ml-1.5 font-semibold text-indigo-700">{{ auth.user.plan.name }}</span>
          <span class="ml-2 text-xs text-gray-400">({{ auth.user.plan.max_products || '∞' }} produktów, {{ auth.user.plan.max_feeds_out || '∞' }} feedów)</span>
        </div>
      </div>
      <button v-if="auth.user.plan.name === 'Free'" @click="$router.push('/#pricing')" class="text-sm text-indigo-600 hover:text-indigo-800 font-medium transition-colors">Zmień plan →</button>
      <button v-else @click="openPortal" class="text-sm text-indigo-600 hover:text-indigo-800 font-medium transition-colors">Zarządzaj subskrypcją</button>
    </div>

    <!-- Smart Dashboard -->
    <div class="mb-8">
      <SmartDashboard />
    </div>

    <!-- Source Feeds Section -->
    <div class="flex items-center gap-3 mb-4">
      <h2 class="font-heading text-lg font-bold text-gray-900">Feedy źródłowe</h2>
      <span class="bg-indigo-100 text-indigo-700 text-xs font-bold px-2.5 py-0.5 rounded-full">{{ store.feeds.length }}</span>
    </div>

    <!-- Empty state: source feeds -->
    <div v-if="store.feeds.length === 0" class="text-center py-20 bg-gradient-to-b from-indigo-50/50 to-white rounded-2xl border border-dashed border-indigo-200 mb-8">
      <div class="w-16 h-16 mx-auto bg-indigo-100 rounded-2xl flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12.75 19.5v-.75a7.5 7.5 0 00-7.5-7.5H4.5m0-6.75h.75c7.87 0 14.25 6.38 14.25 14.25v.75M6 18.75a.75.75 0 11-1.5 0 .75.75 0 011.5 0z" /></svg>
      </div>
      <h3 class="font-heading text-lg font-bold text-gray-900">Dodaj swój pierwszy feed</h3>
      <p class="text-sm text-gray-500 mt-2 max-w-sm mx-auto">Wklej link do XML ze sklepu — Shoper, WooCommerce, PrestaShop lub inny.</p>
      <router-link
        to="/feeds-in/new"
        class="inline-flex items-center gap-2 mt-6 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/25 cursor-pointer"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg>
        Dodaj feed źródłowy
      </router-link>
    </div>

    <!-- Source feed cards -->
    <div v-else class="grid md:grid-cols-2 gap-4 mb-8">
      <div
        v-for="feed in store.feeds"
        :key="feed.id"
        class="bg-white rounded-2xl border border-gray-200 p-5 hover:shadow-lg hover:border-indigo-200 transition-all duration-300 group"
      >
        <div class="flex items-start justify-between">
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full shrink-0" :class="statusDotColor(feed.fetch_status)"></span>
              <router-link
                :to="`/feeds-in/${feed.id}`"
                class="font-heading text-base font-bold text-gray-900 group-hover:text-indigo-600 transition-colors truncate"
              >
                {{ feed.name }}
              </router-link>
            </div>
            <p class="text-xs text-gray-400 mt-1.5 truncate pl-4">{{ feed.source_url }}</p>
            <p v-if="feed.fetch_status === 'error' && feed.fetch_error" class="text-xs text-red-500 mt-1.5 pl-4 truncate">
              {{ feed.fetch_error }}
            </p>
            <div class="flex items-center gap-4 mt-3 pl-4">
              <span class="text-xs text-gray-500 font-medium">{{ feed.product_count }} produktów</span>
              <span class="text-xs text-gray-400">{{ timeAgo(feed.last_fetched_at) }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2 ml-3 shrink-0">
            <span
              class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold"
              :class="statusColor(feed.fetch_status)"
            >
              {{ statusLabel(feed.fetch_status) }}
            </span>
            <button
              class="w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:text-red-500 hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-all cursor-pointer"
              @click="handleDelete(feed.id)"
              title="Usuń feed"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Output Feeds Section -->
    <div class="flex items-center gap-3 mb-4 mt-12">
      <h2 class="font-heading text-lg font-bold text-gray-900">Feedy wyjściowe</h2>
      <span class="bg-indigo-100 text-indigo-700 text-xs font-bold px-2.5 py-0.5 rounded-full">{{ feedsOutStore.feeds.length }}</span>
    </div>

    <!-- Empty state: output feeds -->
    <div v-if="feedsOutStore.feeds.length === 0" class="text-center py-16 bg-gradient-to-b from-indigo-50/50 to-white rounded-2xl border border-dashed border-purple-200">
      <div class="w-14 h-14 mx-auto bg-indigo-100 rounded-2xl flex items-center justify-center mb-4">
        <svg class="w-7 h-7 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" /></svg>
      </div>
      <h3 class="font-heading text-base font-bold text-gray-900">Brak feedów wyjściowych</h3>
      <p class="text-sm text-gray-500 mt-2 max-w-sm mx-auto">Wybierz feed źródłowy i kliknij "Utwórz feed wyjściowy".</p>
    </div>

    <!-- Output feed cards -->
    <div v-else class="grid md:grid-cols-2 gap-4">
      <div
        v-for="feed in feedsOutStore.feeds"
        :key="feed.id"
        class="bg-white rounded-2xl border border-gray-200 p-5 hover:shadow-lg hover:border-purple-200 transition-all duration-300 group"
      >
        <div class="flex items-start justify-between">
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2.5 flex-wrap">
              <router-link
                :to="`/feeds-out/${feed.id}`"
                class="font-heading text-base font-bold text-gray-900 group-hover:text-indigo-600 transition-colors truncate"
              >
                {{ feed.name }}
              </router-link>
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-bold uppercase tracking-wide"
                :class="typeBadgeColor(feed.type)"
              >
                {{ feed.type }}
              </span>
              <button
                @click="toggleActive(feed)"
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold cursor-pointer transition-colors"
                :class="feed.active ? 'bg-green-100 text-emerald-700 hover:bg-emerald-200' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'"
              >
                <span class="w-1.5 h-1.5 rounded-full" :class="feed.active ? 'bg-green-500' : 'bg-gray-400'"></span>
                {{ feed.active ? 'Aktywny' : 'Nieaktywny' }}
              </button>
            </div>
            <div class="flex items-center gap-2 mt-3">
              <div class="flex items-center gap-1.5 min-w-0 bg-gray-50 rounded-lg px-3 py-1.5 flex-1">
                <svg class="w-3.5 h-3.5 text-gray-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.86-3.397a4.5 4.5 0 00-1.242-7.244l4.5-4.5a4.5 4.5 0 016.364 6.364l-1.757 1.757" /></svg>
                <span class="text-xs text-gray-500 truncate">{{ feedOutPublicUrl(feed.link_out) }}</span>
              </div>
              <button
                class="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-indigo-500 hover:text-indigo-700 hover:bg-indigo-50 transition-all cursor-pointer"
                @click="copyToClipboard(feedOutPublicUrl(feed.link_out))"
                title="Kopiuj link"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9.75a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184" /></svg>
              </button>
            </div>
          </div>
          <div class="flex items-center gap-2 ml-3 shrink-0">
            <!-- Quality Score Ring -->
            <span
              v-if="qualityScores[feed.id]"
              class="inline-flex items-center justify-center w-10 h-10 rounded-full text-xs font-bold ring-2"
              :class="qualityScoreColor(qualityScores[feed.id].score)"
              :title="`Jakość feedu: ${qualityScores[feed.id].score}% — ${qualityScores[feed.id].label}`"
            >
              {{ qualityScores[feed.id].score }}
            </span>
            <button
              class="w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:text-red-500 hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-all cursor-pointer"
              @click="handleDeleteOut(feed.id)"
              title="Usuń feed"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in {
  animation: fade-in 0.5s ease-out both;
}
</style>
