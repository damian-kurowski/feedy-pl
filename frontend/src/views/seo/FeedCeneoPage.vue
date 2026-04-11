<template>
  <div class="min-h-screen bg-white">
    <section class="bg-gradient-to-br from-indigo-600 to-indigo-800 text-white py-20">
      <div class="max-w-4xl mx-auto px-4">
        <h1 class="font-heading text-4xl sm:text-5xl font-extrabold leading-tight">Feed Ceneo — generuj plik XML dla Ceneo.pl</h1>
        <p class="mt-6 text-lg text-indigo-100 max-w-2xl">Automatycznie twórz i aktualizuj feed produktowy dla Ceneo. Feedy pobiera produkty z Twojego sklepu, mapuje pola i generuje gotowy XML zgodny z wymaganiami Ceneo.</p>
        <div class="mt-8 flex gap-3">
          <router-link to="/register" class="px-8 py-3 bg-white text-indigo-700 font-semibold rounded-xl hover:bg-indigo-50 transition">Zacznij za darmo</router-link>
        </div>
      </div>
    </section>

    <section class="py-16 max-w-4xl mx-auto px-4">
      <h2 class="font-heading text-2xl font-bold text-gray-900 mb-6">Wymagania feedu Ceneo — pełna specyfikacja</h2>
      <p class="text-gray-600 mb-6">Feed XML dla Ceneo musi zawierać określone pola. Feedy automatycznie mapuje dane z Twojego sklepu do wymaganego formatu.</p>
      <div class="overflow-x-auto">
        <table class="w-full text-sm border border-gray-200 rounded-lg">
          <thead class="bg-gray-50"><tr>
            <th class="text-left px-4 py-3 font-medium">Pole</th>
            <th class="text-left px-4 py-3 font-medium">Wymagane</th>
            <th class="text-left px-4 py-3 font-medium">Opis</th>
          </tr></thead>
          <tbody class="divide-y">
            <tr><td class="px-4 py-3 font-mono text-sm">id</td><td class="px-4 py-3 text-green-600 font-medium">Tak</td><td class="px-4 py-3 text-gray-600">Unikalny identyfikator produktu</td></tr>
            <tr><td class="px-4 py-3 font-mono text-sm">url</td><td class="px-4 py-3 text-green-600 font-medium">Tak</td><td class="px-4 py-3 text-gray-600">Link do strony produktu w sklepie</td></tr>
            <tr><td class="px-4 py-3 font-mono text-sm">price</td><td class="px-4 py-3 text-green-600 font-medium">Tak</td><td class="px-4 py-3 text-gray-600">Cena brutto (bez waluty, np. 49.99)</td></tr>
            <tr><td class="px-4 py-3 font-mono text-sm">avail</td><td class="px-4 py-3 text-green-600 font-medium">Tak</td><td class="px-4 py-3 text-gray-600">Dostępność: 1 (dostępny), 3, 7, 14, 99 (na zamówienie)</td></tr>
            <tr><td class="px-4 py-3 font-mono text-sm">name</td><td class="px-4 py-3 text-green-600 font-medium">Tak</td><td class="px-4 py-3 text-gray-600">Pełna nazwa produktu</td></tr>
            <tr><td class="px-4 py-3 font-mono text-sm">cat</td><td class="px-4 py-3 text-green-600 font-medium">Tak</td><td class="px-4 py-3 text-gray-600">Kategoria produktu</td></tr>
            <tr><td class="px-4 py-3 font-mono text-sm">desc</td><td class="px-4 py-3 text-green-600 font-medium">Tak</td><td class="px-4 py-3 text-gray-600">Opis produktu</td></tr>
            <tr><td class="px-4 py-3 font-mono text-sm">imgs</td><td class="px-4 py-3 text-gray-400">Zalecane</td><td class="px-4 py-3 text-gray-600">Zdjęcie główne produktu</td></tr>
            <tr><td class="px-4 py-3 font-mono text-sm">producer</td><td class="px-4 py-3 text-gray-400">Zalecane</td><td class="px-4 py-3 text-gray-600">Marka / producent</td></tr>
            <tr><td class="px-4 py-3 font-mono text-sm">code (EAN)</td><td class="px-4 py-3 text-gray-400">Zalecane</td><td class="px-4 py-3 text-gray-600">Kod EAN — pomaga dopasować do karty produktu</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="py-16 bg-gray-50">
      <div class="max-w-4xl mx-auto px-4">
        <h2 class="font-heading text-2xl font-bold text-gray-900 mb-6">Jak dodać produkty do Ceneo przez Feedy?</h2>
        <ol class="space-y-6">
          <li class="flex gap-4"><span class="shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">1</span><div><h3 class="font-semibold text-gray-900">Wklej link do XML ze sklepu</h3><p class="text-gray-600 mt-1">Skopiuj URL eksportu produktów z panelu Shoper, WooCommerce, PrestaShop lub innej platformy.</p></div></li>
          <li class="flex gap-4"><span class="shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">2</span><div><h3 class="font-semibold text-gray-900">Utwórz feed wyjściowy — Ceneo</h3><p class="text-gray-600 mt-1">Wybierz szablon Ceneo. Feedy automatycznie zmapuje pola z Twojego XML do formatu wymaganego przez Ceneo.</p></div></li>
          <li class="flex gap-4"><span class="shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">3</span><div><h3 class="font-semibold text-gray-900">Skopiuj link i wklej w panelu Ceneo</h3><p class="text-gray-600 mt-1">Feedy generuje link XML, który wklejasz w panelu Ceneo. Feed odświeża się automatycznie co 1h, 6h lub 24h.</p></div></li>
        </ol>
        <div class="mt-10"><router-link to="/register" class="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition">Zacznij za darmo — bez karty kredytowej</router-link></div>
      </div>
    </section>

    <section class="py-16 max-w-4xl mx-auto px-4">
      <h2 class="font-heading text-2xl font-bold text-gray-900 mb-6">Najczęstsze problemy z feedem Ceneo</h2>
      <div class="space-y-4">
        <div class="border rounded-xl p-5"><h3 class="font-semibold text-gray-900">Ceneo odrzuca oferty</h3><p class="text-gray-600 mt-2">Najczęstszy powód to brak wymaganych pól (id, url, price) lub nieprawidłowy format ceny. Feedy automatycznie waliduje feed przed wysłaniem i pokazuje dokładnie które pola brakują.</p></div>
        <div class="border rounded-xl p-5"><h3 class="font-semibold text-gray-900">Brak kodu EAN</h3><p class="text-gray-600 mt-2">Produkty bez EAN mogą nie być dopasowane do kart produktów na Ceneo. Feedy wyświetla pokrycie EAN i ostrzega o brakujących kodach.</p></div>
        <div class="border rounded-xl p-5"><h3 class="font-semibold text-gray-900">Nieaktualne ceny</h3><p class="text-gray-600 mt-2">Ustaw automatyczne odświeżanie feedu co 1 godzinę. Feedy pobierze aktualne dane z Twojego sklepu i zaktualizuje XML.</p></div>
      </div>
    </section>
  </div>
</template>
