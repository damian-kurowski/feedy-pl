<script setup lang="ts">
import { ref, onMounted } from 'vue'

const visible = ref(false)
const showDetails = ref(false)
const analyticsConsent = ref(true)

onMounted(() => {
  const consent = localStorage.getItem('cookie_consent')
  if (!consent) {
    visible.value = true
  } else {
    // Already consented — load analytics if accepted
    const parsed = JSON.parse(consent)
    if (parsed.analytics) {
      loadGA4()
    }
  }
})

function acceptAll() {
  localStorage.setItem('cookie_consent', JSON.stringify({
    necessary: true,
    analytics: true,
    accepted_at: new Date().toISOString(),
  }))
  loadGA4()
  visible.value = false
}

function acceptSelected() {
  localStorage.setItem('cookie_consent', JSON.stringify({
    necessary: true,
    analytics: analyticsConsent.value,
    accepted_at: new Date().toISOString(),
  }))
  if (analyticsConsent.value) {
    loadGA4()
  }
  visible.value = false
}

function rejectAll() {
  localStorage.setItem('cookie_consent', JSON.stringify({
    necessary: true,
    analytics: false,
    accepted_at: new Date().toISOString(),
  }))
  visible.value = false
}

function loadGA4() {
  // Don't load twice
  if (document.querySelector('script[src*="googletagmanager"]')) return

  const script = document.createElement('script')
  script.async = true
  script.src = 'https://www.googletagmanager.com/gtag/js?id=G-FXG667NT02'
  document.head.appendChild(script)

  ;(window as any).dataLayer = (window as any).dataLayer || []
  function gtag(...args: any[]) { (window as any).dataLayer.push(args) }
  gtag('js', new Date())
  gtag('config', 'G-FXG667NT02', { anonymize_ip: true })
}
</script>

<template>
  <div
    v-if="visible"
    class="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-2xl px-4 py-5 sm:px-6"
  >
    <div class="max-w-4xl mx-auto">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="flex-1">
          <p class="text-sm text-gray-700 font-medium mb-1">Ta strona używa plików cookie</p>
          <p class="text-xs text-gray-500 leading-relaxed">
            Używamy niezbędnych plików cookie do działania serwisu oraz opcjonalnych cookie analitycznych (Google Analytics) do ulepszania naszych usług.
            Szczegóły w <router-link to="/polityka-cookies" class="text-indigo-600 underline">polityce cookies</router-link>
            i <router-link to="/polityka-prywatnosci" class="text-indigo-600 underline">polityce prywatności</router-link>.
          </p>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <button
            @click="rejectAll"
            class="px-4 py-2 text-xs font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition cursor-pointer"
          >
            Odrzuć opcjonalne
          </button>
          <button
            @click="showDetails = !showDetails"
            class="px-4 py-2 text-xs font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition cursor-pointer"
          >
            Ustawienia
          </button>
          <button
            @click="acceptAll"
            class="px-5 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition cursor-pointer"
          >
            Akceptuję wszystkie
          </button>
        </div>
      </div>

      <!-- Details panel -->
      <div v-if="showDetails" class="mt-4 pt-4 border-t border-gray-100">
        <div class="space-y-3">
          <label class="flex items-center gap-3">
            <input type="checkbox" checked disabled class="rounded border-gray-300 text-indigo-600" />
            <div>
              <span class="text-sm font-medium text-gray-700">Niezbędne</span>
              <span class="text-xs text-gray-400 ml-2">Zawsze aktywne</span>
              <p class="text-xs text-gray-500">Wymagane do działania logowania, sesji i podstawowych funkcji serwisu.</p>
            </div>
          </label>
          <label class="flex items-center gap-3 cursor-pointer">
            <input v-model="analyticsConsent" type="checkbox" class="rounded border-gray-300 text-indigo-600 cursor-pointer" />
            <div>
              <span class="text-sm font-medium text-gray-700">Analityczne</span>
              <span class="text-xs text-gray-400 ml-2">Google Analytics 4</span>
              <p class="text-xs text-gray-500">Pomagają nam zrozumieć jak korzystasz z serwisu. Dane anonimizowane (anonymize_ip).</p>
            </div>
          </label>
        </div>
        <div class="mt-4 flex justify-end">
          <button
            @click="acceptSelected"
            class="px-5 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition cursor-pointer"
          >
            Zapisz ustawienia
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
