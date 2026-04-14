<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api/client'

const router = useRouter()
const auth = useAuthStore()

async function selectPlan(planId: number) {
  if (!auth.isLoggedIn) {
    router.push(`/register?plan=${planId}`)
    return
  }
  if (planId === 1) {
    router.push('/dashboard')
    return
  }
  try {
    const { data } = await api.post('/billing/checkout', { plan_id: planId })
    window.location.href = data.checkout_url
  } catch (e: any) {
    alert(e.response?.data?.detail || 'Płatności jeszcze nie skonfigurowane. Skontaktuj się z kontakt@feedy.pl.')
  }
}

// ROI calculator
const products = ref(1000)
const aov = ref(150)
const conversionLift = 0.012  // realistic 1.2% extra conversion from richer/validated feeds + multi-channel exposure
const monthlyRevenueLift = computed(() => Math.round(products.value * aov.value * conversionLift))
const yearlyRevenueLift = computed(() => monthlyRevenueLift.value * 12)
const proCost = 149
const roiMultiple = computed(() => proCost > 0 ? Math.round(monthlyRevenueLift.value / proCost) : 0)
function fmt(n: number): string {
  return n.toLocaleString('pl-PL')
}
</script>

<template>
  <!-- HERO -->
  <section class="bg-gradient-to-br from-indigo-600 to-indigo-800 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28 text-center">
      <div class="inline-block px-3 py-1 rounded-full bg-white/10 border border-white/20 text-xs font-semibold text-indigo-100 mb-6 tracking-wider">
        🇵🇱 POLSKIE NARZĘDZIE · 14 DNI ZA DARMO · BEZ KARTY
      </div>
      <h1 class="font-heading text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.1]">
        Zarządzaj feedami produktowymi<br class="hidden sm:inline" /> z jednego miejsca
      </h1>
      <p class="mt-6 max-w-2xl mx-auto text-lg sm:text-xl text-indigo-100/90 leading-relaxed">
        Pobieraj XML z dowolnego sklepu, transformuj i generuj feedy dla Ceneo, Google Merchant Center, Allegro i innych porównywarek — w 5 minut, bez programowania.
      </p>
      <div class="mt-10 flex flex-col sm:flex-row gap-3 justify-center">
        <router-link
          to="/register"
          class="inline-flex items-center justify-center px-8 py-3.5 text-sm font-semibold rounded-xl bg-white text-indigo-700 hover:bg-indigo-50 transition-all shadow-lg shadow-indigo-900/20 hover:-translate-y-0.5"
        >
          Zacznij za darmo
        </router-link>
        <a
          href="#pricing"
          class="inline-flex items-center justify-center px-8 py-3.5 text-sm font-semibold rounded-xl border-2 border-white/20 text-white hover:bg-white/10 hover:border-white/30 transition-all"
        >
          Zobacz cennik
        </a>
      </div>
      <p class="mt-5 text-[13px] text-indigo-200/80">
        ✓ Bez karty kredytowej · ✓ Setup w 5 minut · ✓ Anuluj jednym klikiem · ✓ Hostowane w EU, RODO
      </p>
    </div>
  </section>

  <!-- SOCIAL PROOF BAR — platforms + comparison sites -->
  <section class="py-10 bg-white border-b border-gray-100">
    <div class="max-w-7xl mx-auto px-4">
      <p class="text-center text-xs font-semibold text-gray-400 uppercase tracking-[0.2em] mb-6">Integrujemy z platformami, na których sprzedajesz</p>
      <div class="flex flex-wrap justify-center items-center gap-x-10 gap-y-4">
        <span class="text-xl font-bold text-gray-300 hover:text-gray-500 transition">Shoper</span>
        <span class="text-xl font-bold text-gray-300 hover:text-gray-500 transition">WooCommerce</span>
        <span class="text-xl font-bold text-gray-300 hover:text-gray-500 transition">PrestaShop</span>
        <span class="text-xl font-bold text-gray-300 hover:text-gray-500 transition">Magento</span>
        <span class="text-xl font-bold text-gray-300 hover:text-gray-500 transition">Shopify</span>
      </div>
      <p class="text-center text-xs font-semibold text-gray-400 uppercase tracking-[0.2em] mt-10 mb-6">Generujemy feedy do</p>
      <div class="flex flex-wrap justify-center items-center gap-x-8 gap-y-3">
        <span class="text-base font-semibold text-gray-400">Ceneo</span>
        <span class="text-gray-200">·</span>
        <span class="text-base font-semibold text-gray-400">Google Shopping</span>
        <span class="text-gray-200">·</span>
        <span class="text-base font-semibold text-gray-400">Allegro</span>
        <span class="text-gray-200">·</span>
        <span class="text-base font-semibold text-gray-400">Skąpiec</span>
        <span class="text-gray-200">·</span>
        <span class="text-base font-semibold text-gray-400">Facebook Catalog</span>
        <span class="text-gray-200">·</span>
        <span class="text-base font-semibold text-gray-400">Domodi</span>
      </div>
    </div>
  </section>

  <!-- PROBLEM / SOLUTION -->
  <section class="py-24 bg-white">
    <div class="max-w-5xl mx-auto px-4">
      <div class="grid md:grid-cols-2 gap-16 items-center">
        <div>
          <p class="text-sm font-bold text-red-500 uppercase tracking-wider mb-3">Bez Feedy</p>
          <h2 class="font-heading text-2xl font-bold text-gray-900 mb-6">Ręczne zarządzanie feedami to koszmar</h2>
          <ul class="space-y-4">
            <li class="flex gap-3 text-gray-600">
              <svg class="w-6 h-6 text-red-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" /></svg>
              Godziny spędzone na edycji XML dla każdej porównywarki
            </li>
            <li class="flex gap-3 text-gray-600">
              <svg class="w-6 h-6 text-red-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" /></svg>
              Odrzucone oferty przez brak wymaganych pól
            </li>
            <li class="flex gap-3 text-gray-600">
              <svg class="w-6 h-6 text-red-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" /></svg>
              Nieaktualne ceny i stany magazynowe
            </li>
            <li class="flex gap-3 text-gray-600">
              <svg class="w-6 h-6 text-red-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" /></svg>
              Każda porównywarka wymaga innego formatu
            </li>
          </ul>
        </div>
        <div>
          <p class="text-sm font-bold text-green-600 uppercase tracking-wider mb-3">Z Feedy</p>
          <h2 class="font-heading text-2xl font-bold text-gray-900 mb-6">Jedno kliknięcie i gotowe</h2>
          <ul class="space-y-4">
            <li class="flex gap-3 text-gray-600">
              <svg class="w-6 h-6 text-green-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Automatyczne parsowanie i mapowanie pól
            </li>
            <li class="flex gap-3 text-gray-600">
              <svg class="w-6 h-6 text-green-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Wbudowana walidacja Quality Score
            </li>
            <li class="flex gap-3 text-gray-600">
              <svg class="w-6 h-6 text-green-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Auto-refresh co 1, 6 lub 24 godziny
            </li>
            <li class="flex gap-3 text-gray-600">
              <svg class="w-6 h-6 text-green-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              6 porównywarek z jednego źródłowego XML
            </li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- HOW IT WORKS -->
  <section class="py-24 bg-gray-50">
    <div class="max-w-5xl mx-auto px-4">
      <p class="text-center text-sm font-bold text-indigo-600 uppercase tracking-wider mb-3">Jak to działa</p>
      <h2 class="font-heading text-3xl sm:text-4xl font-bold text-center text-gray-900 mb-4">Trzy kroki do gotowego feeda</h2>
      <p class="text-center text-gray-500 text-lg mb-16 max-w-2xl mx-auto">Bez programowania, bez wtyczek, bez czekania.</p>

      <div class="grid sm:grid-cols-3 gap-8">
        <div>
          <div class="w-12 h-12 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-lg mb-4">1</div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">Wklej link do XML</h3>
          <p class="text-gray-500 text-sm">Skopiuj URL feeda z panelu sklepu (Shoper, WooCommerce, PrestaShop). System pobierze i przeanalizuje produkty.</p>
        </div>
        <div>
          <div class="w-12 h-12 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-lg mb-4">2</div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">Wybierz porównywarkę</h3>
          <p class="text-gray-500 text-sm">Ceneo, Google, Allegro, Skąpiec, Facebook, Domodi — kliknij szablon i pola zmapują się automatycznie.</p>
        </div>
        <div>
          <div class="w-12 h-12 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-lg mb-4">3</div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">Gotowy link XML</h3>
          <p class="text-gray-500 text-sm">Skopiuj link i wklej w panelu porównywarki. Feed odświeża się sam.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- FEATURES — 2x3 grid, bigger -->
  <section class="py-24 bg-white">
    <div class="max-w-7xl mx-auto px-4">
      <p class="text-center text-sm font-bold text-indigo-600 uppercase tracking-wider mb-3">Funkcje</p>
      <h2 class="font-heading text-3xl sm:text-4xl font-bold text-center text-gray-900 mb-4">Wszystko w jednym narzędziu</h2>
      <p class="text-center text-gray-500 text-lg mb-16 max-w-2xl mx-auto">Zapomnij o ręcznej edycji XML. Feedy robi to za Ciebie.</p>

      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
        <div class="group p-8 rounded-2xl border border-gray-100 hover:border-indigo-200 hover:bg-indigo-50/50 transition-all duration-300">
          <div class="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" /></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">Parsowanie dowolnego XML</h3>
          <p class="text-gray-500 text-sm">Wklej URL — system rozpozna strukturę i wyciągnie produkty automatycznie.</p>
        </div>

        <div class="group p-8 rounded-2xl border border-gray-100 hover:border-indigo-200 hover:bg-indigo-50/50 transition-all duration-300">
          <div class="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25a2.25 2.25 0 0 1-2.25-2.25v-2.25Z" /></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">Szablony Ceneo, GMC, Allegro</h3>
          <p class="text-gray-500 text-sm">Gotowe mapowania pól. Kliknij szablon — feed generuje się w sekundzie.</p>
        </div>

        <div class="group p-8 rounded-2xl border border-gray-100 hover:border-indigo-200 hover:bg-indigo-50/50 transition-all duration-300">
          <div class="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182M2.985 19.644l3.181-3.182" /></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">Auto-refresh co 1h / 6h / 24h</h3>
          <p class="text-gray-500 text-sm">Feedy same się odświeżają. Ceny i dostępność zawsze aktualne.</p>
        </div>

        <div class="group p-8 rounded-2xl border border-gray-100 hover:border-indigo-200 hover:bg-indigo-50/50 transition-all duration-300">
          <div class="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 0 1-.659 1.591l-5.432 5.432a2.25 2.25 0 0 0-.659 1.591v2.927a2.25 2.25 0 0 1-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 0 0-.659-1.591L3.659 7.409A2.25 2.25 0 0 1 3 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0 1 12 3Z" /></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">Reguły filtrowania i modyfikacji</h3>
          <p class="text-gray-500 text-sm">Ukryj produkty bez zdjęć, zmień tytuły, filtruj kategorie. If/then rules.</p>
        </div>

        <div class="group p-8 rounded-2xl border border-gray-100 hover:border-indigo-200 hover:bg-indigo-50/50 transition-all duration-300">
          <div class="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" /></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">Walidacja przed wysłaniem</h3>
          <p class="text-gray-500 text-sm">Sprawdź czy feed przejdzie w Ceneo/GMC zanim wyślesz. Zero odrzuceń.</p>
        </div>

        <div class="group p-8 rounded-2xl border border-gray-100 hover:border-indigo-200 hover:bg-indigo-50/50 transition-all duration-300">
          <div class="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 0 0-2.455 2.456Z" /></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">AI optymalizacja tytułów</h3>
          <p class="text-gray-500 text-sm">Automatycznie ulepsz tytuły produktów — dodaj markę, wyczyść formatowanie.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- COMPARISON TABLE — us vs competitors -->
  <section class="py-24 bg-gray-50">
    <div class="max-w-4xl mx-auto px-4">
      <p class="text-center text-sm font-bold text-indigo-600 uppercase tracking-wider mb-3">Porównanie</p>
      <h2 class="font-heading text-3xl sm:text-4xl font-bold text-center text-gray-900 mb-12">Dlaczego Feedy, a nie inne narzędzia?</h2>

      <div class="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-gray-50 border-b">
              <th class="text-left p-4 font-medium text-gray-500">Funkcja</th>
              <th class="p-4 text-center font-bold text-indigo-600 bg-indigo-50">Feedy</th>
              <th class="p-4 text-center font-medium text-gray-500">DataFeedWatch</th>
              <th class="p-4 text-center font-medium text-gray-500">Channable</th>
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr>
              <td class="p-4 text-gray-700">Cena (1000 produktów)</td>
              <td class="p-4 text-center font-bold text-indigo-600 bg-indigo-50/50">49 zł/mies.</td>
              <td class="p-4 text-center text-gray-500">~280 zł/mies.</td>
              <td class="p-4 text-center text-gray-500">~260 zł/mies.</td>
            </tr>
            <tr>
              <td class="p-4 text-gray-700">Liczba porównywarek w cenie</td>
              <td class="p-4 text-center font-bold text-indigo-600 bg-indigo-50/50">Bez limitu</td>
              <td class="p-4 text-center text-gray-500">1 kanał</td>
              <td class="p-4 text-center text-gray-500">1 kanał</td>
            </tr>
            <tr>
              <td class="p-4 text-gray-700">Ceneo + Skąpiec + Allegro</td>
              <td class="p-4 text-center bg-indigo-50/50"><svg class="w-5 h-5 mx-auto text-green-500" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg></td>
              <td class="p-4 text-center"><svg class="w-5 h-5 mx-auto text-green-500" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg></td>
              <td class="p-4 text-center text-gray-400">Częściowo</td>
            </tr>
            <tr>
              <td class="p-4 text-gray-700">Interfejs po polsku</td>
              <td class="p-4 text-center bg-indigo-50/50"><svg class="w-5 h-5 mx-auto text-green-500" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg></td>
              <td class="p-4 text-center text-gray-400">Angielski</td>
              <td class="p-4 text-center text-gray-400">Angielski</td>
            </tr>
            <tr>
              <td class="p-4 text-gray-700">Darmowy plan na zawsze</td>
              <td class="p-4 text-center bg-indigo-50/50"><svg class="w-5 h-5 mx-auto text-green-500" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg></td>
              <td class="p-4 text-center"><svg class="w-5 h-5 mx-auto text-red-400" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" /></svg></td>
              <td class="p-4 text-center"><svg class="w-5 h-5 mx-auto text-red-400" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" /></svg></td>
            </tr>
            <tr>
              <td class="p-4 text-gray-700">Polski support + faktura VAT</td>
              <td class="p-4 text-center bg-indigo-50/50"><svg class="w-5 h-5 mx-auto text-green-500" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg></td>
              <td class="p-4 text-center text-gray-400">EN tylko</td>
              <td class="p-4 text-center text-gray-400">EN tylko</td>
            </tr>
            <tr>
              <td class="p-4 text-gray-700">BLIK + Przelewy24</td>
              <td class="p-4 text-center bg-indigo-50/50"><svg class="w-5 h-5 mx-auto text-green-500" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg></td>
              <td class="p-4 text-center"><svg class="w-5 h-5 mx-auto text-red-400" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" /></svg></td>
              <td class="p-4 text-center"><svg class="w-5 h-5 mx-auto text-red-400" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" /></svg></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- PRICING -->
  <section id="pricing" class="py-24 bg-gray-50">
    <div class="max-w-7xl mx-auto px-4">
      <p class="text-center text-sm font-bold text-indigo-600 uppercase tracking-wider mb-3">Cennik</p>
      <h2 class="font-heading text-3xl sm:text-4xl font-bold text-center text-gray-900 mb-4">Prosty cennik, bez ukrytych kosztów</h2>
      <p class="text-center text-gray-500 text-lg mb-6 max-w-2xl mx-auto">Wszystkie porównywarki w cenie. Bez limitu kanałów. Bez dodatkowych opłat.</p>
      <p class="text-center text-sm text-gray-400 mb-16">14 dni bezpłatnego trialu na każdy płatny plan · BLIK · Przelewy24 · karta · faktura VAT</p>

      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
        <!-- Free -->
        <div class="bg-white rounded-2xl border border-gray-200 p-8 flex flex-col hover:shadow-lg transition-shadow">
          <h3 class="text-lg font-bold text-gray-900">Free</h3>
          <p class="mt-4 flex items-baseline gap-1">
            <span class="text-5xl font-extrabold text-gray-900">0 zł</span>
            <span class="text-gray-500">/mies.</span>
          </p>
          <p class="mt-2 text-sm text-gray-500">Na zawsze, bez karty kredytowej</p>
          <ul class="mt-8 space-y-3 text-sm text-gray-600 flex-1">
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              200 produktów
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              1 feed wyjściowy
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Wszystkie szablony
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Ręczne odświeżanie
            </li>
          </ul>
          <button @click="selectPlan(1)" class="mt-8 w-full py-3 rounded-xl border-2 border-gray-200 text-gray-700 font-semibold hover:border-indigo-300 hover:text-indigo-600 transition cursor-pointer">
            Załóż darmowe konto
          </button>
        </div>

        <!-- Starter -->
        <div class="bg-white rounded-2xl border border-gray-200 p-8 flex flex-col hover:shadow-lg transition-shadow">
          <h3 class="text-lg font-bold text-gray-900">Starter</h3>
          <p class="mt-4 flex items-baseline gap-1">
            <span class="text-5xl font-extrabold text-gray-900">49 zł</span>
            <span class="text-gray-500">/mies.</span>
          </p>
          <p class="mt-2 text-sm text-gray-500">14 dni za darmo · anulujesz kiedy chcesz</p>
          <ul class="mt-8 space-y-3 text-sm text-gray-600 flex-1">
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              1 000 produktów
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              3 feedy wyjściowe
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Auto-refresh
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Mapowanie kategorii
            </li>
          </ul>
          <button @click="selectPlan(2)" class="mt-8 w-full py-3 rounded-xl border-2 border-indigo-200 text-indigo-600 font-semibold hover:bg-indigo-50 transition cursor-pointer">
            Spróbuj 14 dni za darmo
          </button>
        </div>

        <!-- Pro -->
        <div class="relative bg-white rounded-2xl border-2 border-indigo-600 p-8 flex flex-col shadow-xl shadow-indigo-100">
          <div class="absolute -top-4 left-1/2 -translate-x-1/2">
            <span class="inline-block px-4 py-1.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-bold rounded-full uppercase tracking-wider shadow-lg">Najpopularniejszy</span>
          </div>
          <h3 class="text-lg font-bold text-gray-900">Pro</h3>
          <p class="mt-4 flex items-baseline gap-1">
            <span class="text-5xl font-extrabold text-gray-900">149 zł</span>
            <span class="text-gray-500">/mies.</span>
          </p>
          <p class="mt-2 text-sm text-gray-500">14 dni za darmo · brak setup fee</p>
          <ul class="mt-8 space-y-3 text-sm text-gray-600 flex-1">
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              10 000 produktów
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              10 feedów wyjściowych
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Reguły + AI optymalizacja opisów
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Walidacja + Quality Score
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Override per produkt
            </li>
          </ul>
          <button @click="selectPlan(3)" class="mt-8 w-full py-3 rounded-xl bg-indigo-600 text-white font-bold hover:bg-indigo-700 shadow-lg shadow-indigo-200 transition cursor-pointer">
            Spróbuj Pro 14 dni za darmo
          </button>
        </div>

        <!-- Business -->
        <div class="bg-white rounded-2xl border border-gray-200 p-8 flex flex-col hover:shadow-lg transition-shadow">
          <h3 class="text-lg font-bold text-gray-900">Business</h3>
          <p class="mt-4 flex items-baseline gap-1">
            <span class="text-5xl font-extrabold text-gray-900">349 zł</span>
            <span class="text-gray-500">/mies.</span>
          </p>
          <p class="mt-2 text-sm text-gray-500">Custom onboarding · SLA</p>
          <ul class="mt-8 space-y-3 text-sm text-gray-600 flex-1">
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              50 000 produktów
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Bez limitu feedów
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              White-label branding
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Multi-user / organizacje
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Priorytetowy support
            </li>
          </ul>
          <button @click="selectPlan(4)" class="mt-8 w-full py-3 rounded-xl border-2 border-indigo-200 text-indigo-600 font-semibold hover:bg-indigo-50 transition cursor-pointer">
            Skontaktuj się
          </button>
        </div>
      </div>

      <!-- Trust badges row -->
      <div class="mt-12 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-xs text-gray-400">
        <span class="inline-flex items-center gap-1.5">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 0 1-1.043 3.296 3.745 3.745 0 0 1-3.296 1.043A3.745 3.745 0 0 1 12 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 0 1-3.296-1.043 3.745 3.745 0 0 1-1.043-3.296A3.745 3.745 0 0 1 3 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 0 1 1.043-3.296 3.746 3.746 0 0 1 3.296-1.043A3.746 3.746 0 0 1 12 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 0 1 3.296 1.043 3.746 3.746 0 0 1 1.043 3.296A3.745 3.745 0 0 1 21 12Z"/></svg>
          RODO compliant
        </span>
        <span>·</span>
        <span class="inline-flex items-center gap-1.5">🇪🇺 Hostowane w EU</span>
        <span>·</span>
        <span class="inline-flex items-center gap-1.5">🔒 SSL · backupy 24h</span>
        <span>·</span>
        <span class="inline-flex items-center gap-1.5">💳 BLIK · Przelewy24 · karta</span>
        <span>·</span>
        <span class="inline-flex items-center gap-1.5">📄 Faktura VAT automatycznie</span>
      </div>
    </div>
  </section>

  <!-- ROI CALCULATOR -->
  <section class="py-24 bg-white">
    <div class="max-w-4xl mx-auto px-4">
      <p class="text-center text-sm font-bold text-indigo-600 uppercase tracking-wider mb-3">Kalkulator ROI</p>
      <h2 class="font-heading text-3xl sm:text-4xl font-bold text-center text-gray-900 mb-4">Sprawdź, ile zarobisz dodatkowo z lepszymi feedami</h2>
      <p class="text-center text-gray-500 text-lg mb-12 max-w-2xl mx-auto">Walidacja, AI tytuły i ekspozycja w 6 porównywarkach typowo dodaje ~1,2% do konwersji.</p>

      <div class="bg-gradient-to-br from-indigo-50 to-white border border-indigo-100 rounded-3xl p-8 sm:p-12">
        <div class="grid sm:grid-cols-2 gap-8 mb-10">
          <div>
            <label for="roi-products" class="block text-sm font-semibold text-gray-700 mb-2">Liczba produktów w sklepie</label>
            <input
              id="roi-products"
              v-model.number="products"
              type="number"
              min="1"
              max="100000"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-lg font-semibold text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
            />
          </div>
          <div>
            <label for="roi-aov" class="block text-sm font-semibold text-gray-700 mb-2">Średnia wartość koszyka (zł)</label>
            <input
              id="roi-aov"
              v-model.number="aov"
              type="number"
              min="1"
              max="100000"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-lg font-semibold text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
            />
          </div>
        </div>

        <div class="grid sm:grid-cols-3 gap-4 text-center">
          <div class="bg-white rounded-2xl border border-gray-100 p-5">
            <p class="text-xs text-gray-500 font-semibold uppercase tracking-wider mb-1">Dodatkowy przychód / mies.</p>
            <p class="font-heading text-3xl font-extrabold text-indigo-600">+{{ fmt(monthlyRevenueLift) }} zł</p>
          </div>
          <div class="bg-white rounded-2xl border border-gray-100 p-5">
            <p class="text-xs text-gray-500 font-semibold uppercase tracking-wider mb-1">Dodatkowy przychód / rok</p>
            <p class="font-heading text-3xl font-extrabold text-indigo-600">+{{ fmt(yearlyRevenueLift) }} zł</p>
          </div>
          <div class="bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl p-5 text-white">
            <p class="text-xs text-indigo-100 font-semibold uppercase tracking-wider mb-1">ROI vs Pro (149 zł/mies.)</p>
            <p class="font-heading text-3xl font-extrabold">{{ roiMultiple }}×</p>
          </div>
        </div>

        <p class="mt-6 text-center text-xs text-gray-400">
          Szacunek bazujący na średnim wpływie czystego, zwalidowanego feedu z ekspozycją w 6 porównywarkach. Twoje wyniki zależą od branży i marży.
        </p>

        <div class="mt-8 text-center">
          <router-link
            to="/register"
            class="inline-flex items-center gap-2 px-7 py-3 text-sm font-semibold rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 shadow-lg shadow-indigo-200 transition-all hover:-translate-y-0.5"
          >
            Załóż konto i sprawdź na żywo
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" /></svg>
          </router-link>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA -->
  <section class="py-24 bg-gradient-to-br from-indigo-600 to-indigo-800 text-white">
    <div class="max-w-4xl mx-auto px-4 text-center">
      <h2 class="font-heading text-3xl sm:text-4xl font-extrabold mb-6">Gotowy na lepsze feedy?</h2>
      <p class="text-xl text-indigo-100 mb-10 max-w-2xl mx-auto">Załóż konto w 30 sekund. Bez karty kredytowej. 200 produktów za darmo na zawsze.</p>
      <router-link
        to="/register"
        class="inline-flex items-center gap-2 px-10 py-4 text-lg font-bold rounded-xl bg-white text-indigo-700 hover:bg-indigo-50 shadow-xl shadow-indigo-900/30 transition-all hover:-translate-y-0.5"
      >
        Zacznij za darmo — to trwa 30 sekund
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" /></svg>
      </router-link>
    </div>
  </section>

  <!-- FAQ -->
  <section class="py-24 bg-white">
    <div class="max-w-3xl mx-auto px-4">
      <h2 class="font-heading text-3xl font-bold text-center text-gray-900 mb-12">Często zadawane pytania</h2>
      <div class="space-y-4">
        <details class="group bg-gray-50 rounded-xl border border-gray-200 transition-all open:bg-white open:shadow-md">
          <summary class="p-5 font-semibold text-gray-900 cursor-pointer flex justify-between items-center">
            Czy Feedy działa z moim sklepem?
            <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /></svg>
          </summary>
          <p class="px-5 pb-5 text-gray-600">Feedy działa z każdym sklepem, który generuje XML z produktami — Shoper, WooCommerce, PrestaShop, Magento, Shopify i inne. Wystarczy wkleić link do XML. Jeśli Twój sklep nie generuje XML, możesz dodawać produkty ręcznie albo skontaktować się z nami — pomożemy podpiąć dowolne źródło.</p>
        </details>

        <details class="group bg-gray-50 rounded-xl border border-gray-200 transition-all open:bg-white open:shadow-md">
          <summary class="p-5 font-semibold text-gray-900 cursor-pointer flex justify-between items-center">
            Jak długo trwa setup?
            <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /></svg>
          </summary>
          <p class="px-5 pb-5 text-gray-600">5 minut. Wklejasz link do XML ze swojego sklepu, wybierasz szablon Ceneo/Google/Allegro, kopiujesz wygenerowany URL feedu i wklejasz w panelu porównywarki. Bez programowania.</p>
        </details>

        <details class="group bg-gray-50 rounded-xl border border-gray-200 transition-all open:bg-white open:shadow-md">
          <summary class="p-5 font-semibold text-gray-900 cursor-pointer flex justify-between items-center">
            Jak szybko feed się odświeża?
            <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /></svg>
          </summary>
          <p class="px-5 pb-5 text-gray-600">Możesz ustawić automatyczne odświeżanie co 1, 6 lub 24 godziny. Feed jest zawsze aktualny — ceny i dostępność synchronizują się automatycznie.</p>
        </details>

        <details class="group bg-gray-50 rounded-xl border border-gray-200 transition-all open:bg-white open:shadow-md">
          <summary class="p-5 font-semibold text-gray-900 cursor-pointer flex justify-between items-center">
            Czy mogę przetestować za darmo?
            <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /></svg>
          </summary>
          <p class="px-5 pb-5 text-gray-600">Tak. Plan Free pozwala na 200 produktów i 1 feed wyjściowy — bez karty kredytowej, bez limitu czasowego. Każdy płatny plan ma dodatkowo 14 dni triala — anulujesz jednym klikiem, bez tłumaczenia.</p>
        </details>

        <details class="group bg-gray-50 rounded-xl border border-gray-200 transition-all open:bg-white open:shadow-md">
          <summary class="p-5 font-semibold text-gray-900 cursor-pointer flex justify-between items-center">
            Czy potrzebuję programisty?
            <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /></svg>
          </summary>
          <p class="px-5 pb-5 text-gray-600">Nie. Cały interfejs jest po polsku i zaprojektowany dla nie-technicznych właścicieli sklepów. Nic nie instalujesz, nic nie modyfikujesz w sklepie — tylko kopiujesz linki.</p>
        </details>

        <details class="group bg-gray-50 rounded-xl border border-gray-200 transition-all open:bg-white open:shadow-md">
          <summary class="p-5 font-semibold text-gray-900 cursor-pointer flex justify-between items-center">
            Co jeśli mam więcej produktów niż w planie?
            <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /></svg>
          </summary>
          <p class="px-5 pb-5 text-gray-600">Łagodny upgrade prompt — feed dalej działa, a Ty dostajesz powiadomienie z propozycją wyższego planu. Nikogo nie wyłączamy bez ostrzeżenia.</p>
        </details>

        <details class="group bg-gray-50 rounded-xl border border-gray-200 transition-all open:bg-white open:shadow-md">
          <summary class="p-5 font-semibold text-gray-900 cursor-pointer flex justify-between items-center">
            Czy obsługujecie warianty produktów (rozmiary, kolory)?
            <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /></svg>
          </summary>
          <p class="px-5 pb-5 text-gray-600">Tak. Każdy wariant traktowany jest jako osobny produkt z własnym ID, ceną, dostępnością i kategorią. Mapowanie automatyczne, override per wariant w razie potrzeby.</p>
        </details>

        <details class="group bg-gray-50 rounded-xl border border-gray-200 transition-all open:bg-white open:shadow-md">
          <summary class="p-5 font-semibold text-gray-900 cursor-pointer flex justify-between items-center">
            Płatności BLIK, Przelewy24, faktura VAT?
            <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /></svg>
          </summary>
          <p class="px-5 pb-5 text-gray-600">Tak — akceptujemy BLIK, Przelewy24 i karty (przez Stripe). Faktura VAT generuje się automatycznie i trafia mailem po każdej płatności. NIP wpisujesz przy checkoucie.</p>
        </details>

        <details class="group bg-gray-50 rounded-xl border border-gray-200 transition-all open:bg-white open:shadow-md">
          <summary class="p-5 font-semibold text-gray-900 cursor-pointer flex justify-between items-center">
            Jak wygląda anulacja subskrypcji?
            <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /></svg>
          </summary>
          <p class="px-5 pb-5 text-gray-600">Jeden klik w panelu klienta. Bez pytań, bez „dlaczego rezygnujesz", bez prób ratowania. Płatny plan działa do końca okresu rozliczeniowego, potem konto wraca na Free — Twoje feedy zostają.</p>
        </details>

        <details class="group bg-gray-50 rounded-xl border border-gray-200 transition-all open:bg-white open:shadow-md">
          <summary class="p-5 font-semibold text-gray-900 cursor-pointer flex justify-between items-center">
            Czy mogę przejść z DataFeedWatch / Channable?
            <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /></svg>
          </summary>
          <p class="px-5 pb-5 text-gray-600">Tak. Migracja jest darmowa i pomożemy ją przeprowadzić — wystarczy wskazać Twój obecny feed źródłowy. Większość konfiguracji odtworzymy automatycznie. Napisz: kontakt@feedy.pl.</p>
        </details>
      </div>
    </div>
  </section>

  <!-- FOOTER -->
  <footer class="bg-gray-900 text-gray-400 py-16">
    <div class="max-w-7xl mx-auto px-4">
      <div class="grid sm:grid-cols-4 gap-8 mb-12">
        <div class="sm:col-span-2">
          <span class="font-heading text-xl font-extrabold text-white tracking-tight">Feedy</span>
          <p class="mt-3 text-sm text-gray-500 max-w-md">Polska platforma do zarządzania feedami produktowymi dla e-commerce. Generuj feedy XML dla Ceneo, Google Shopping, Allegro i innych porównywarek z jednego panelu.</p>
        </div>
        <div>
          <p class="font-semibold text-gray-300 mb-3">Produkt</p>
          <ul class="space-y-2 text-sm">
            <li><a href="#pricing" class="hover:text-white transition">Cennik</a></li>
            <li><router-link to="/feed-ceneo" class="hover:text-white transition">Feed Ceneo</router-link></li>
            <li><router-link to="/feed-google-shopping" class="hover:text-white transition">Feed Google Shopping</router-link></li>
            <li><router-link to="/feed-allegro" class="hover:text-white transition">Feed Allegro</router-link></li>
            <li><router-link to="/integracja-shoper" class="hover:text-white transition">Integracja Shoper</router-link></li>
            <li><router-link to="/integracja-woocommerce" class="hover:text-white transition">Integracja WooCommerce</router-link></li>
            <li><router-link to="/blog" class="hover:text-white transition">Blog</router-link></li>
            <li><router-link to="/register" class="hover:text-white transition">Załóż konto</router-link></li>
          </ul>
        </div>
        <div>
          <p class="font-semibold text-gray-300 mb-3">Informacje prawne</p>
          <ul class="space-y-2 text-sm">
            <li><router-link to="/regulamin" class="hover:text-white transition">Regulamin</router-link></li>
            <li><router-link to="/polityka-prywatnosci" class="hover:text-white transition">Polityka prywatności</router-link></li>
            <li><router-link to="/polityka-cookies" class="hover:text-white transition">Polityka cookies</router-link></li>
            <li><a href="mailto:kontakt@feedy.pl" class="hover:text-white transition">kontakt@feedy.pl</a></li>
          </ul>
        </div>
      </div>
      <div class="border-t border-gray-800 pt-8 flex flex-col sm:flex-row justify-between items-center gap-4">
        <p class="text-sm">© 2026 Feedy — Artur Dylik. NIP: 7282905430. Wszelkie prawa zastrzeżone.</p>
        <p class="text-sm">kontakt@feedy.pl</p>
      </div>
    </div>
  </footer>

  <!-- STICKY MOBILE CTA -->
  <div class="fixed bottom-0 left-0 right-0 z-40 sm:hidden bg-white border-t border-gray-200 shadow-2xl px-4 py-3">
    <router-link
      to="/register"
      class="flex items-center justify-center gap-2 w-full py-3 text-sm font-bold rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 transition"
    >
      Zacznij za darmo — 30 sekund
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" /></svg>
    </router-link>
  </div>
</template>
