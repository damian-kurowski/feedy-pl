<template>
  <div class="min-h-screen bg-white">
    <section class="bg-gradient-to-br from-indigo-600 to-indigo-800 text-white py-16">
      <div class="max-w-4xl mx-auto px-4">
        <h1 class="font-heading text-4xl font-extrabold">Blog Feedy</h1>
        <p class="mt-3 text-lg text-indigo-100">Poradniki, instrukcje i nowości ze świata feedów produktowych</p>
      </div>
    </section>

    <div class="max-w-4xl mx-auto px-4 py-16">
      <div class="space-y-8">
        <router-link to="/blog/jak-dodac-produkty-do-ceneo" class="block group">
          <article class="border border-gray-200 rounded-2xl p-6 hover:border-indigo-200 hover:shadow-md transition-all">
            <div class="flex items-center gap-2 text-xs text-gray-400 mb-3">
              <span>11 kwietnia 2026</span>
              <span>·</span>
              <span>10 min czytania</span>
              <span>·</span>
              <span class="bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full font-medium">Ceneo</span>
            </div>
            <h2 class="font-heading text-xl font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">Jak dodać produkty do Ceneo — kompletny poradnik 2026</h2>
            <p class="mt-2 text-gray-600 text-sm leading-relaxed">Krok po kroku: jak stworzyć feed XML dla Ceneo, jakie pola są wymagane, jak uniknąć odrzucenia ofert i jak automatycznie aktualizować dane produktowe.</p>
          </article>
        </router-link>

        <router-link to="/blog/jak-stworzyc-feed-xml" class="block group">
          <article class="border border-gray-200 rounded-2xl p-6 hover:border-indigo-200 hover:shadow-md transition-all">
            <div class="flex items-center gap-2 text-xs text-gray-400 mb-3">
              <span>11 kwietnia 2026</span>
              <span>·</span>
              <span>8 min czytania</span>
              <span>·</span>
              <span class="bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">Poradnik</span>
            </div>
            <h2 class="font-heading text-xl font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">Jak stworzyć feed XML dla sklepu internetowego</h2>
            <p class="mt-2 text-gray-600 text-sm leading-relaxed">Czym jest feed produktowy, jakie formaty XML istnieją, jak wybrać odpowiedni dla Ceneo, Google Shopping i Allegro.</p>
          </article>
        </router-link>

        <router-link to="/blog/ceneo-odrzuca-oferty" class="block group">
          <article class="border border-gray-200 rounded-2xl p-6 hover:border-indigo-200 hover:shadow-md transition-all">
            <div class="flex items-center gap-2 text-xs text-gray-400 mb-3">
              <span>11 kwietnia 2026</span>
              <span>·</span>
              <span>6 min czytania</span>
              <span>·</span>
              <span class="bg-red-100 text-red-700 px-2 py-0.5 rounded-full font-medium">Troubleshooting</span>
            </div>
            <h2 class="font-heading text-xl font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">Ceneo odrzuca oferty — jak naprawić feed?</h2>
            <p class="mt-2 text-gray-600 text-sm leading-relaxed">Najczęstsze przyczyny odrzuceń: brak wymaganych pól, zły format ceny, nieprawidłowy EAN. Jak je zdiagnozować i naprawić.</p>
          </article>
        </router-link>
      </div>
    </div>
  </div>
</template>
