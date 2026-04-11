<template>
  <div class="min-h-screen bg-white">
    <section class="bg-gradient-to-br from-indigo-600 to-indigo-800 text-white py-20">
      <div class="max-w-4xl mx-auto px-4">
        <h1 class="font-heading text-4xl sm:text-5xl font-extrabold leading-tight">Feed Google Shopping — Google Merchant Center</h1>
        <p class="mt-6 text-lg text-indigo-100 max-w-2xl">Generuj feed XML/Atom dla Google Merchant Center. Automatyczne mapowanie pól, walidacja i odświeżanie. Twoje produkty w Google Shopping w kilka minut.</p>
        <div class="mt-8"><router-link to="/register" class="px-8 py-3 bg-white text-indigo-700 font-semibold rounded-xl hover:bg-indigo-50 transition">Zacznij za darmo</router-link></div>
      </div>
    </section>

    <section class="py-16 max-w-4xl mx-auto px-4">
      <h2 class="font-heading text-2xl font-bold text-gray-900 mb-6">Wymagania feedu Google Merchant Center</h2>
      <p class="text-gray-600 mb-6">Google Shopping wymaga feedu w formacie Atom XML z namespace g:. Feedy generuje feed zgodny ze specyfikacją Google automatycznie.</p>
      <div class="overflow-x-auto">
        <table class="w-full text-sm border border-gray-200 rounded-lg">
          <thead class="bg-gray-50"><tr><th class="text-left px-4 py-3 font-medium">Pole</th><th class="text-left px-4 py-3 font-medium">Wymagane</th><th class="text-left px-4 py-3 font-medium">Opis</th></tr></thead>
          <tbody class="divide-y">
            <tr><td class="px-4 py-3 font-mono">g:id</td><td class="px-4 py-3 text-green-600 font-medium">Tak</td><td class="px-4 py-3 text-gray-600">Unikalny identyfikator, max 50 znaków</td></tr>
            <tr><td class="px-4 py-3 font-mono">title</td><td class="px-4 py-3 text-green-600 font-medium">Tak</td><td class="px-4 py-3 text-gray-600">Tytuł produktu, max 150 znaków</td></tr>
            <tr><td class="px-4 py-3 font-mono">description</td><td class="px-4 py-3 text-green-600 font-medium">Tak</td><td class="px-4 py-3 text-gray-600">Opis, max 5000 znaków, bez HTML</td></tr>
            <tr><td class="px-4 py-3 font-mono">link</td><td class="px-4 py-3 text-green-600 font-medium">Tak</td><td class="px-4 py-3 text-gray-600">URL strony produktu</td></tr>
            <tr><td class="px-4 py-3 font-mono">g:image_link</td><td class="px-4 py-3 text-green-600 font-medium">Tak</td><td class="px-4 py-3 text-gray-600">URL zdjęcia, min 100x100 px</td></tr>
            <tr><td class="px-4 py-3 font-mono">g:price</td><td class="px-4 py-3 text-green-600 font-medium">Tak</td><td class="px-4 py-3 text-gray-600">Cena Z walutą: 29.99 PLN</td></tr>
            <tr><td class="px-4 py-3 font-mono">g:availability</td><td class="px-4 py-3 text-green-600 font-medium">Tak</td><td class="px-4 py-3 text-gray-600">in_stock, out_of_stock, preorder</td></tr>
            <tr><td class="px-4 py-3 font-mono">g:brand / g:gtin</td><td class="px-4 py-3 text-green-600 font-medium">Tak</td><td class="px-4 py-3 text-gray-600">Marka lub kod EAN — co najmniej jedno</td></tr>
            <tr><td class="px-4 py-3 font-mono">g:google_product_category</td><td class="px-4 py-3 text-gray-400">Zalecane</td><td class="px-4 py-3 text-gray-600">Kategoria z taksonomii Google</td></tr>
            <tr><td class="px-4 py-3 font-mono">g:gtin (EAN)</td><td class="px-4 py-3 text-gray-400">Zalecane</td><td class="px-4 py-3 text-gray-600">Produkty z EAN mają ~40% więcej wyświetleń</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="py-16 bg-gray-50">
      <div class="max-w-4xl mx-auto px-4">
        <h2 class="font-heading text-2xl font-bold text-gray-900 mb-6">Jak stworzyć feed Google Shopping?</h2>
        <ol class="space-y-6">
          <li class="flex gap-4"><span class="shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">1</span><div><h3 class="font-semibold text-gray-900">Dodaj feed źródłowy z Twojego sklepu</h3><p class="text-gray-600 mt-1">Feedy obsługuje XML z Shoper, WooCommerce, PrestaShop, Magento i Shopify.</p></div></li>
          <li class="flex gap-4"><span class="shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">2</span><div><h3 class="font-semibold text-gray-900">Wybierz szablon Google Merchant Center</h3><p class="text-gray-600 mt-1">Automatyczne mapowanie pól do formatu Atom z namespace g:.</p></div></li>
          <li class="flex gap-4"><span class="shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">3</span><div><h3 class="font-semibold text-gray-900">Wklej link w Google Merchant Center</h3><p class="text-gray-600 mt-1">Skopiuj URL feedu i dodaj jako źródło w GMC. Auto-refresh co 1h/6h/24h.</p></div></li>
        </ol>
        <div class="mt-10"><router-link to="/register" class="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition">Zacznij za darmo</router-link></div>
      </div>
    </section>
  </div>
</template>
