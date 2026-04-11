<template>
  <div class="min-h-screen bg-white">
    <section class="bg-gradient-to-br from-indigo-600 to-indigo-800 text-white py-20">
      <div class="max-w-4xl mx-auto px-4">
        <h1 class="font-heading text-4xl sm:text-5xl font-extrabold leading-tight">WooCommerce — feedy dla porównywarek cen</h1>
        <p class="mt-6 text-lg text-indigo-100 max-w-2xl">Eksportuj produkty z WooCommerce do Ceneo, Google Shopping, Allegro i innych porównywarek. Bez wtyczek — wystarczy link do XML.</p>
        <div class="mt-8"><router-link to="/register" class="px-8 py-3 bg-white text-indigo-700 font-semibold rounded-xl hover:bg-indigo-50 transition">Zacznij za darmo</router-link></div>
      </div>
    </section>
    <section class="py-16 max-w-4xl mx-auto px-4">
      <h2 class="font-heading text-2xl font-bold text-gray-900 mb-6">Jak wyeksportować produkty z WooCommerce?</h2>
      <p class="text-gray-600 mb-6">WooCommerce generuje feed XML produktów przez wtyczkę (np. WooCommerce Product Feed) lub wbudowany eksport. Feedy pobiera ten XML i transformuje go do formatu wymaganego przez porównywarki.</p>
      <div class="space-y-4">
        <div class="border rounded-xl p-5"><h3 class="font-semibold text-gray-900">Opcja 1: Wtyczka Product Feed</h3><p class="text-gray-600 mt-1">Zainstaluj wtyczkę generującą XML (np. Product Feed PRO, CTX Feed). Skopiuj URL feedu i wklej w Feedy.</p></div>
        <div class="border rounded-xl p-5"><h3 class="font-semibold text-gray-900">Opcja 2: WooCommerce REST API</h3><p class="text-gray-600 mt-1">Użyj API WooCommerce do eksportu produktów. Feedy może przetwarzać dowolny format XML.</p></div>
      </div>
      <div class="mt-10"><router-link to="/register" class="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition">Połącz WooCommerce z porównywarkami</router-link></div>
    </section>
  </div>
</template>
