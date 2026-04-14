<script setup lang="ts">
const tiers = [
  { range: '1 produkt', price: 'Darmo 3 miesiące', subPrice: 'potem 10 zł/mies.', highlight: false },
  { range: '2–5 produktów', price: '25 zł', subPrice: 'miesięcznie', highlight: true },
  { range: '6–25 produktów', price: '50 zł', subPrice: 'miesięcznie', highlight: false },
  { range: '26–100 produktów', price: '100 zł', subPrice: 'miesięcznie', highlight: false },
  { range: '101–500 produktów', price: '250 zł', subPrice: 'miesięcznie', highlight: false },
  { range: 'Powyżej 500', price: 'Kontakt', subPrice: 'mailowy', highlight: false },
]

const blogBenefits = [
  'Każda oferta dostaje własny landing page z H1, galerią, CTA i SEO',
  'Link wyjściowy z rel="ugc sponsored nofollow noopener"',
  'Pełna kontrola nad tytułem, slug, meta tagami, indeksowalnością',
  'Lokalizacja + cena lub „do wyceny indywidualnej"',
  'Galeria do 10 zdjęć z upscalingiem',
]
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <section class="bg-gradient-to-br from-indigo-600 to-indigo-800 text-white py-12 sm:py-16">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h1 class="font-heading text-3xl sm:text-5xl font-extrabold">Strony ofert produktów</h1>
        <p class="mt-4 text-base sm:text-xl text-indigo-100">Publikuj swoje produkty i usługi na feedy.pl — własny landing z SEO, CTA i lokalizacją.</p>
      </div>
    </section>

    <div class="max-w-5xl mx-auto px-3 sm:px-4 py-10 sm:py-16">
      <div class="mb-10 text-center">
        <h2 class="font-heading text-xl sm:text-2xl font-bold text-gray-900 mb-2">Pakiety cenowe</h2>
        <p class="text-sm text-gray-500">Wybierz pakiet dopasowany do liczby ofert. Bez zobowiązań.</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
        <div
          v-for="tier in tiers"
          :key="tier.range"
          class="bg-white border rounded-2xl p-6 transition-all hover:shadow-lg"
          :class="tier.highlight ? 'border-indigo-500 ring-2 ring-indigo-100 shadow-md' : 'border-gray-200'"
        >
          <div v-if="tier.highlight" class="inline-block text-[10px] font-semibold uppercase tracking-wide bg-indigo-600 text-white px-2 py-0.5 rounded-full mb-3">Popularne</div>
          <p class="text-sm font-medium text-gray-500 mb-2">{{ tier.range }}</p>
          <p class="font-heading text-2xl sm:text-3xl font-extrabold text-gray-900">{{ tier.price }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ tier.subPrice }}</p>
        </div>
      </div>

      <div class="mt-10 bg-white border border-gray-200 rounded-2xl p-6 sm:p-8">
        <h3 class="font-heading text-lg font-bold text-gray-900 mb-2">Wpis blogowy</h3>
        <p class="text-sm text-gray-600">
          <strong class="text-gray-900">1 wpis blogowy gratis przez 1 miesiąc</strong> do każdego aktywnego pakietu.
          Powyżej — <strong class="text-gray-900">20 zł/mies. za każdy dodatkowy wpis</strong>, jeśli ma pozostać opublikowany.
        </p>
      </div>

      <div class="mt-10 bg-white border border-gray-200 rounded-2xl p-6 sm:p-8">
        <h3 class="font-heading text-lg font-bold text-gray-900 mb-4">Co dostajesz w pakiecie</h3>
        <ul class="space-y-2">
          <li v-for="b in blogBenefits" :key="b" class="flex items-start gap-2 text-sm text-gray-700">
            <svg class="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
            {{ b }}
          </li>
        </ul>
      </div>

      <div class="mt-10 text-center">
        <router-link to="/oferty"
          class="inline-block bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl px-7 py-3 transition-all hover:shadow-lg hover:shadow-indigo-500/20">
          Przejdź do moich ofert
        </router-link>
        <p class="text-xs text-gray-400 mt-3">Pierwsza oferta darmo przez 3 miesiące</p>
      </div>
    </div>
  </div>
</template>
