<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api/client'

const router = useRouter()
const auth = useAuthStore()

async function selectPlan(planId: number) {
  if (!auth.isLoggedIn) {
    router.push('/register')
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
    alert(e.response?.data?.detail || 'Brak konfiguracji platnosci')
  }
}
</script>

<template>
  <!-- HERO -->
  <section class="bg-gradient-to-br from-indigo-600 to-indigo-800 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32 text-center">
      <h1 class="font-heading text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.1]">
        Zarządzaj feedami produktowymi<br class="hidden sm:inline" /> z jednego miejsca
      </h1>
      <p class="mt-6 max-w-2xl mx-auto text-lg sm:text-xl text-indigo-100/90 leading-relaxed">
        Pobieraj XML z dowolnego sklepu, transformuj i generuj feedy dla Ceneo, Google Merchant Center, Allegro i innych porównywarek.
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
      <p class="mt-5 text-[13px] text-indigo-200/60">Bez karty kredytowej. 200 produktów za darmo, na zawsze.</p>
    </div>
  </section>

  <!-- SOCIAL PROOF BAR — logos -->
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
              Walidacja feedu zanim wyślesz do porównywarki
            </li>
            <li class="flex gap-3 text-gray-600">
              <svg class="w-6 h-6 text-green-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Automatyczne odświeżanie co 1h / 6h / 24h
            </li>
            <li class="flex gap-3 text-gray-600">
              <svg class="w-6 h-6 text-green-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Ceneo, GMC, Allegro, Skapiec — jeden panel
            </li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- HOW IT WORKS — 3 steps, big numbers -->
  <section class="py-24 bg-gray-50">
    <div class="max-w-7xl mx-auto px-4">
      <p class="text-center text-sm font-bold text-indigo-600 uppercase tracking-wider mb-3">Jak to dziala</p>
      <h2 class="font-heading text-3xl sm:text-4xl font-bold text-center text-gray-900 mb-4">Trzy kroki do gotowego feeda</h2>
      <p class="text-center text-gray-500 text-lg mb-16 max-w-2xl mx-auto">Konfiguracja zajmuje mniej niż 5 minut. Bez kodowania, bez pomocy programisty.</p>

      <div class="grid md:grid-cols-3 gap-8">
        <div class="relative bg-white rounded-2xl p-8 shadow-sm border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
          <span class="absolute -top-5 -left-3 text-8xl font-black text-indigo-100 select-none">1</span>
          <div class="relative">
            <div class="w-14 h-14 rounded-2xl bg-indigo-600 text-white flex items-center justify-center mb-5">
              <svg class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244" /></svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-2">Wklej link do XML</h3>
            <p class="text-gray-500">Skopiuj URL feeda z panelu sklepu. System automatycznie pobierze i przeanalizuje wszystkie produkty.</p>
          </div>
        </div>

        <div class="relative bg-white rounded-2xl p-8 shadow-sm border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
          <span class="absolute -top-5 -left-3 text-8xl font-black text-indigo-100 select-none">2</span>
          <div class="relative">
            <div class="w-14 h-14 rounded-2xl bg-indigo-600 text-white flex items-center justify-center mb-5">
              <svg class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-2">Wybierz porownywark</h3>
            <p class="text-gray-500">Ceneo, Google Merchant, Allegro — kliknij szablon i pola zmapuja sie automatycznie. Zero konfiguracji.</p>
          </div>
        </div>

        <div class="relative bg-white rounded-2xl p-8 shadow-sm border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
          <span class="absolute -top-5 -left-3 text-8xl font-black text-indigo-100 select-none">3</span>
          <div class="relative">
            <div class="w-14 h-14 rounded-2xl bg-indigo-600 text-white flex items-center justify-center mb-5">
              <svg class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 0 1-1.043 3.296 3.745 3.745 0 0 1-3.296 1.043A3.745 3.745 0 0 1 12 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 0 1-3.296-1.043 3.745 3.745 0 0 1-1.043-3.296A3.745 3.745 0 0 1 3 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 0 1 1.043-3.296 3.746 3.746 0 0 1 3.296-1.043A3.746 3.746 0 0 1 12 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 0 1 3.296 1.043 3.746 3.746 0 0 1 1.043 3.296A3.745 3.745 0 0 1 21 12Z" /></svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-2">Gotowy link XML</h3>
            <p class="text-gray-500">Skopiuj link i wklej w panelu porównywarki. Feed odświeża się automatycznie.</p>
          </div>
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
          <p class="text-gray-500 text-sm">Wklej URL — system rozpozna strukture i wyciagnie produkty automatycznie.</p>
        </div>

        <div class="group p-8 rounded-2xl border border-gray-100 hover:border-indigo-200 hover:bg-indigo-50/50 transition-all duration-300">
          <div class="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25a2.25 2.25 0 0 1-2.25-2.25v-2.25Z" /></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">Szablony Ceneo, GMC, Allegro</h3>
          <p class="text-gray-500 text-sm">Gotowe mapowania pol. Kliknij szablon — feed generuje sie w sekundzie.</p>
        </div>

        <div class="group p-8 rounded-2xl border border-gray-100 hover:border-indigo-200 hover:bg-indigo-50/50 transition-all duration-300">
          <div class="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182M2.985 19.644l3.181-3.182" /></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">Auto-refresh co 1h / 6h / 24h</h3>
          <p class="text-gray-500 text-sm">Feedy same sie odswiezaja. Ceny i dostepnosc zawsze aktualne.</p>
        </div>

        <div class="group p-8 rounded-2xl border border-gray-100 hover:border-indigo-200 hover:bg-indigo-50/50 transition-all duration-300">
          <div class="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 0 1-.659 1.591l-5.432 5.432a2.25 2.25 0 0 0-.659 1.591v2.927a2.25 2.25 0 0 1-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 0 0-.659-1.591L3.659 7.409A2.25 2.25 0 0 1 3 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0 1 12 3Z" /></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">Reguly filtrowania i modyfikacji</h3>
          <p class="text-gray-500 text-sm">Ukryj produkty bez zdjec, zmien tytuly, filtruj kategorie. If/then rules.</p>
        </div>

        <div class="group p-8 rounded-2xl border border-gray-100 hover:border-indigo-200 hover:bg-indigo-50/50 transition-all duration-300">
          <div class="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" /></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">Walidacja przed wyslaniem</h3>
          <p class="text-gray-500 text-sm">Sprawdz czy feed przejdzie w Ceneo/GMC zanim wyślesz. Zero odrzucen.</p>
        </div>

        <div class="group p-8 rounded-2xl border border-gray-100 hover:border-indigo-200 hover:bg-indigo-50/50 transition-all duration-300">
          <div class="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 0 0-2.455 2.456Z" /></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">AI optymalizacja tytulow</h3>
          <p class="text-gray-500 text-sm">Automatycznie ulepsz tytuly produktow — dodaj marke, wyczysc formatowanie.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- COMPARISON TABLE — us vs competitors -->
  <section class="py-24 bg-gray-50">
    <div class="max-w-4xl mx-auto px-4">
      <p class="text-center text-sm font-bold text-indigo-600 uppercase tracking-wider mb-3">Porownanie</p>
      <h2 class="font-heading text-3xl sm:text-4xl font-bold text-center text-gray-900 mb-12">Dlaczego Feedy, a nie inne narzedzia?</h2>

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
              <td class="p-4 text-gray-700">Cena (1000 produktow)</td>
              <td class="p-4 text-center font-bold text-indigo-600 bg-indigo-50/50">29 zl/mies.</td>
              <td class="p-4 text-center text-gray-500">~280 zl/mies.</td>
              <td class="p-4 text-center text-gray-500">~260 zl/mies.</td>
            </tr>
            <tr>
              <td class="p-4 text-gray-700">Liczba porównywarek w cenie</td>
              <td class="p-4 text-center font-bold text-indigo-600 bg-indigo-50/50">Bez limitu</td>
              <td class="p-4 text-center text-gray-500">1 kanal</td>
              <td class="p-4 text-center text-gray-500">1 kanal</td>
            </tr>
            <tr>
              <td class="p-4 text-gray-700">Ceneo + Skapiec + Allegro</td>
              <td class="p-4 text-center bg-indigo-50/50"><svg class="w-5 h-5 mx-auto text-green-500" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg></td>
              <td class="p-4 text-center"><svg class="w-5 h-5 mx-auto text-green-500" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg></td>
              <td class="p-4 text-center text-gray-400">Czesciowo</td>
            </tr>
            <tr>
              <td class="p-4 text-gray-700">Interfejs po polsku</td>
              <td class="p-4 text-center bg-indigo-50/50"><svg class="w-5 h-5 mx-auto text-green-500" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg></td>
              <td class="p-4 text-center text-gray-400">Angielski</td>
              <td class="p-4 text-center text-gray-400">Angielski</td>
            </tr>
            <tr>
              <td class="p-4 text-gray-700">Darmowy plan</td>
              <td class="p-4 text-center bg-indigo-50/50"><svg class="w-5 h-5 mx-auto text-green-500" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg></td>
              <td class="p-4 text-center"><svg class="w-5 h-5 mx-auto text-red-400" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" /></svg></td>
              <td class="p-4 text-center"><svg class="w-5 h-5 mx-auto text-red-400" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" /></svg></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- TESTIMONIALS -->
  <section class="py-24 bg-white">
    <div class="max-w-7xl mx-auto px-4">
      <p class="text-center text-sm font-bold text-indigo-600 uppercase tracking-wider mb-3">Opinie</p>
      <h2 class="font-heading text-3xl sm:text-4xl font-bold text-center text-gray-900 mb-12">Zaufali nam wlasciciele sklepow</h2>

      <div class="grid md:grid-cols-3 gap-8">
        <div class="bg-gradient-to-br from-gray-50 to-white rounded-2xl p-8 border border-gray-100 shadow-sm">
          <div class="flex gap-1 mb-4">
            <svg v-for="i in 5" :key="i" class="w-5 h-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
          </div>
          <p class="text-gray-600 leading-relaxed">"Wreszcie moge zarzadzac feedami bez recznej edycji XML. Konfiguracja trwala 5 minut, a wczesniej poswiecalem na to pol dnia."</p>
          <div class="mt-6 flex items-center gap-3">
            <div class="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-bold text-lg">M</div>
            <div>
              <p class="font-semibold text-gray-900">Marek K.</p>
              <p class="text-sm text-gray-500">Wlasciciel sklepu na Shoperze</p>
            </div>
          </div>
        </div>

        <div class="bg-gradient-to-br from-gray-50 to-white rounded-2xl p-8 border border-gray-100 shadow-sm">
          <div class="flex gap-1 mb-4">
            <svg v-for="i in 5" :key="i" class="w-5 h-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
          </div>
          <p class="text-gray-600 leading-relaxed">"Automatyczne odswiezanie feedow oszczedza mi godziny tygodniowo. Zarzadzam 3 sklepami i 8 feedami z jednego panelu."</p>
          <div class="mt-6 flex items-center gap-3">
            <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center text-green-600 font-bold text-lg">A</div>
            <div>
              <p class="font-semibold text-gray-900">Anna W.</p>
              <p class="text-sm text-gray-500">E-commerce manager, 3 sklepy</p>
            </div>
          </div>
        </div>

        <div class="bg-gradient-to-br from-gray-50 to-white rounded-2xl p-8 border border-gray-100 shadow-sm">
          <div class="flex gap-1 mb-4">
            <svg v-for="i in 5" :key="i" class="w-5 h-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
          </div>
          <p class="text-gray-600 leading-relaxed">"Jedno narzedzie do Ceneo, Google i Allegro. Wczesniej placilem 200 zl za DataFeedWatch — teraz mam lepsze narzedzie za 59 zl."</p>
          <div class="mt-6 flex items-center gap-3">
            <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center text-purple-600 font-bold text-lg">P</div>
            <div>
              <p class="font-semibold text-gray-900">Pawel D.</p>
              <p class="text-sm text-gray-500">Agencja e-commerce, 12 klientow</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- PRICING -->
  <section id="pricing" class="py-24 bg-gray-50">
    <div class="max-w-7xl mx-auto px-4">
      <p class="text-center text-sm font-bold text-indigo-600 uppercase tracking-wider mb-3">Cennik</p>
      <h2 class="font-heading text-3xl sm:text-4xl font-bold text-center text-gray-900 mb-4">Prosty cennik, bez ukrytych kosztow</h2>
      <p class="text-center text-gray-500 text-lg mb-16 max-w-2xl mx-auto">Wszystkie porównywarki w cenie. Bez limitu kanalow. Bez dodatkowych oplat.</p>

      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
        <!-- Free -->
        <div class="bg-white rounded-2xl border border-gray-200 p-8 flex flex-col hover:shadow-lg transition-shadow">
          <h3 class="text-lg font-bold text-gray-900">Free</h3>
          <p class="mt-4 flex items-baseline gap-1">
            <span class="text-5xl font-extrabold text-gray-900">0 zl</span>
            <span class="text-gray-500">/mies.</span>
          </p>
          <p class="mt-2 text-sm text-gray-500">Na zawsze, bez karty kredytowej</p>
          <ul class="mt-8 space-y-3 text-sm text-gray-600 flex-1">
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              200 produktow
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              1 feed wyjsciowy
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Wszystkie szablony
            </li>
          </ul>
          <button @click="selectPlan(1)" class="mt-8 w-full py-3 rounded-xl border-2 border-gray-200 text-gray-700 font-semibold hover:border-indigo-300 hover:text-indigo-600 transition cursor-pointer">
            Zacznij za darmo
          </button>
        </div>

        <!-- Starter -->
        <div class="bg-white rounded-2xl border border-gray-200 p-8 flex flex-col hover:shadow-lg transition-shadow">
          <h3 class="text-lg font-bold text-gray-900">Starter</h3>
          <p class="mt-4 flex items-baseline gap-1">
            <span class="text-5xl font-extrabold text-gray-900">29 zl</span>
            <span class="text-gray-500">/mies.</span>
          </p>
          <p class="mt-2 text-sm text-gray-500">Dla malych sklepow</p>
          <ul class="mt-8 space-y-3 text-sm text-gray-600 flex-1">
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              1 000 produktow
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              3 feedy wyjsciowe
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Auto-refresh
            </li>
          </ul>
          <button @click="selectPlan(2)" class="mt-8 w-full py-3 rounded-xl border-2 border-indigo-200 text-indigo-600 font-semibold hover:bg-indigo-50 transition cursor-pointer">
            Wybierz plan
          </button>
        </div>

        <!-- Pro -->
        <div class="relative bg-white rounded-2xl border-2 border-indigo-600 p-8 flex flex-col shadow-xl shadow-indigo-100">
          <div class="absolute -top-4 left-1/2 -translate-x-1/2">
            <span class="inline-block px-4 py-1.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-bold rounded-full uppercase tracking-wider shadow-lg">Najpopularniejszy</span>
          </div>
          <h3 class="text-lg font-bold text-gray-900">Pro</h3>
          <p class="mt-4 flex items-baseline gap-1">
            <span class="text-5xl font-extrabold text-gray-900">59 zl</span>
            <span class="text-gray-500">/mies.</span>
          </p>
          <p class="mt-2 text-sm text-gray-500">Dla rozwijajacych sie sklepow</p>
          <ul class="mt-8 space-y-3 text-sm text-gray-600 flex-1">
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              5 000 produktow
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              10 feedow wyjsciowych
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Reguly + optymalizacja AI
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Walidacja feedow
            </li>
          </ul>
          <button @click="selectPlan(3)" class="mt-8 w-full py-3 rounded-xl bg-indigo-600 text-white font-bold hover:bg-indigo-700 shadow-lg shadow-indigo-200 transition cursor-pointer">
            Wybierz plan
          </button>
        </div>

        <!-- Business -->
        <div class="bg-white rounded-2xl border border-gray-200 p-8 flex flex-col hover:shadow-lg transition-shadow">
          <h3 class="text-lg font-bold text-gray-900">Business</h3>
          <p class="mt-4 flex items-baseline gap-1">
            <span class="text-5xl font-extrabold text-gray-900">99 zl</span>
            <span class="text-gray-500">/mies.</span>
          </p>
          <p class="mt-2 text-sm text-gray-500">Dla agencji i duzych sklepow</p>
          <ul class="mt-8 space-y-3 text-sm text-gray-600 flex-1">
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              20 000 produktow
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Bez limitu feedow
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              White-label branding
            </li>
            <li class="flex items-center gap-2">
              <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
              Multi-user / organizacje
            </li>
          </ul>
          <button @click="selectPlan(4)" class="mt-8 w-full py-3 rounded-xl border-2 border-indigo-200 text-indigo-600 font-semibold hover:bg-indigo-50 transition cursor-pointer">
            Wybierz plan
          </button>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA -->
  <section class="py-24 bg-gradient-to-br from-indigo-600 to-indigo-800 text-white">
    <div class="max-w-4xl mx-auto px-4 text-center">
      <h2 class="font-heading text-3xl sm:text-4xl font-extrabold mb-6">Gotowy na lepsze feedy?</h2>
      <p class="text-xl text-indigo-100 mb-10 max-w-2xl mx-auto">Dolacz do setek sklepow, ktore juz oszczedzaja czas i pieniadze dzieki Feedy.</p>
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
            Czy Feedy dziala z moim sklepem?
            <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /></svg>
          </summary>
          <p class="px-5 pb-5 text-gray-600">Feedy dziala z kazdym sklepem, ktory generuje XML z produktami — Shoper, WooCommerce, PrestaShop, Magento, Shopify i inne. Wystarczy wkleic link do XML.</p>
        </details>
        <details class="group bg-gray-50 rounded-xl border border-gray-200 transition-all open:bg-white open:shadow-md">
          <summary class="p-5 font-semibold text-gray-900 cursor-pointer flex justify-between items-center">
            Jak szybko feed sie odswieza?
            <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /></svg>
          </summary>
          <p class="px-5 pb-5 text-gray-600">Mozesz ustawic automatyczne odswiezanie co 1, 6 lub 24 godziny. Feed jest zawsze aktualny — ceny i dostepnosc synchronizuja sie automatycznie.</p>
        </details>
        <details class="group bg-gray-50 rounded-xl border border-gray-200 transition-all open:bg-white open:shadow-md">
          <summary class="p-5 font-semibold text-gray-900 cursor-pointer flex justify-between items-center">
            Czy moge przetestowac za darmo?
            <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /></svg>
          </summary>
          <p class="px-5 pb-5 text-gray-600">Tak! Plan Free pozwala na 200 produktow i 1 feed wyjsciowy — bez karty kredytowej, bez limitu czasowego. Mozesz uzywac tak dlugo jak chcesz.</p>
        </details>
        <details class="group bg-gray-50 rounded-xl border border-gray-200 transition-all open:bg-white open:shadow-md">
          <summary class="p-5 font-semibold text-gray-900 cursor-pointer flex justify-between items-center">
            Ile kosztuje obsluga wielu porównywarek?
            <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /></svg>
          </summary>
          <p class="px-5 pb-5 text-gray-600">Nic dodatkowego! W przeciwienstwie do konkurencji, u nas wszystkie porównywarki sa w cenie planu. Nie doliczamy za dodatkowe kanaly.</p>
        </details>
      </div>
    </div>
  </section>

  <!-- FOOTER -->
  <footer class="bg-gray-900 text-gray-400 py-16">
    <div class="max-w-7xl mx-auto px-4">
      <div class="grid sm:grid-cols-3 gap-8 mb-12">
        <div>
          <span class="font-heading text-xl font-extrabold text-white tracking-tight">Feedy</span>
          <p class="mt-3 text-sm text-gray-500">Platforma do zarzadzania feedami produktowymi dla e-commerce.</p>
        </div>
        <div>
          <p class="font-semibold text-gray-300 mb-3">Produkt</p>
          <ul class="space-y-2 text-sm">
            <li><a href="#pricing" class="hover:text-white transition">Cennik</a></li>
            <li><router-link to="/register" class="hover:text-white transition">Zaloz konto</router-link></li>
            <li><router-link to="/login" class="hover:text-white transition">Zaloguj sie</router-link></li>
          </ul>
        </div>
        <div>
          <p class="font-semibold text-gray-300 mb-3">Informacje prawne</p>
          <ul class="space-y-2 text-sm">
            <li><router-link to="/regulamin" class="hover:text-white transition">Regulamin</router-link></li>
            <li><router-link to="/polityka-prywatnosci" class="hover:text-white transition">Polityka prywatnosci</router-link></li>
            <li><router-link to="/polityka-cookies" class="hover:text-white transition">Polityka cookies</router-link></li>
          </ul>
        </div>
      </div>
      <div class="border-t border-gray-800 pt-8 flex flex-col sm:flex-row justify-between items-center gap-4">
        <p class="text-sm">&copy; 2026 Feedy — Artur Dylik. NIP: 7282905430. Wszelkie prawa zastrzezone.</p>
        <p class="text-sm">kontakt@feedy.pl</p>
      </div>
    </div>
  </footer>
</template>
