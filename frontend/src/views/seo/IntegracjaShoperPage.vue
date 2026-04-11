<template>
  <div class="min-h-screen bg-white">
    <section class="bg-gradient-to-br from-indigo-600 to-indigo-800 text-white py-20">
      <div class="max-w-4xl mx-auto px-4">
        <h1 class="font-heading text-4xl sm:text-5xl font-extrabold leading-tight">Integracja Shoper z porównywarkami cen</h1>
        <p class="mt-6 text-lg text-indigo-100 max-w-2xl">Połącz swój sklep na Shoperze z Ceneo, Google Shopping, Allegro i innymi porównywarkami. Feedy automatycznie pobiera produkty z Shoper i generuje feedy XML.</p>
        <div class="mt-8"><router-link to="/register" class="px-8 py-3 bg-white text-indigo-700 font-semibold rounded-xl hover:bg-indigo-50 transition">Zacznij za darmo</router-link></div>
      </div>
    </section>

    <section class="py-16 max-w-4xl mx-auto px-4">
      <h2 class="font-heading text-2xl font-bold text-gray-900 mb-6">Jak podłączyć Shoper do Feedy?</h2>
      <ol class="space-y-6">
        <li class="flex gap-4"><span class="shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">1</span><div><h3 class="font-semibold text-gray-900">Znajdź link do eksportu XML w panelu Shoper</h3><p class="text-gray-600 mt-1">W panelu administracyjnym Shoper wejdź w <strong>Integracje → Eksport danych</strong>. Skopiuj link do eksportu (np. CeneoV2, GoogleProductSearch).</p></div></li>
        <li class="flex gap-4"><span class="shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">2</span><div><h3 class="font-semibold text-gray-900">Wklej link w Feedy</h3><p class="text-gray-600 mt-1">Utwórz nowy feed źródłowy w Feedy i wklej skopiowany URL. System automatycznie pobierze i przeanalizuje produkty.</p></div></li>
        <li class="flex gap-4"><span class="shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">3</span><div><h3 class="font-semibold text-gray-900">Wybierz porównywarkę i gotowe</h3><p class="text-gray-600 mt-1">Wybierz Ceneo, Google Shopping, Allegro lub inną platformę. Feedy wygeneruje gotowy feed XML.</p></div></li>
      </ol>
    </section>

    <section class="py-16 bg-gray-50">
      <div class="max-w-4xl mx-auto px-4">
        <h2 class="font-heading text-2xl font-bold text-gray-900 mb-6">Obsługiwane formaty eksportu Shoper</h2>
        <div class="grid sm:grid-cols-2 gap-4">
          <div class="bg-white border rounded-xl p-5"><h3 class="font-semibold text-gray-900">CeneoV2</h3><p class="text-gray-600 mt-1">Format XML dla Ceneo.pl — automatycznie rozpoznawany przez Feedy.</p></div>
          <div class="bg-white border rounded-xl p-5"><h3 class="font-semibold text-gray-900">GoogleProductSearch</h3><p class="text-gray-600 mt-1">Feed Atom dla Google Merchant Center — pełna kompatybilność.</p></div>
          <div class="bg-white border rounded-xl p-5"><h3 class="font-semibold text-gray-900">Skąpiec</h3><p class="text-gray-600 mt-1">Format XML dla Skąpiec.pl — parsowanie struktury xmldata/data/item.</p></div>
          <div class="bg-white border rounded-xl p-5"><h3 class="font-semibold text-gray-900">Facebook Catalog</h3><p class="text-gray-600 mt-1">Feed dla Meta Commerce (Facebook/Instagram Shops).</p></div>
        </div>
        <div class="mt-10"><router-link to="/register" class="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition">Połącz swój sklep Shoper z Feedy</router-link></div>
      </div>
    </section>
  </div>
</template>
