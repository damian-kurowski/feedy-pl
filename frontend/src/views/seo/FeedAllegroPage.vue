<template>
  <div class="min-h-screen bg-white">
    <section class="bg-gradient-to-br from-indigo-600 to-indigo-800 text-white py-20">
      <div class="max-w-4xl mx-auto px-4">
        <h1 class="font-heading text-4xl sm:text-5xl font-extrabold leading-tight">Feed Allegro — generuj feed XML dla Allegro</h1>
        <p class="mt-6 text-lg text-indigo-100 max-w-2xl">Automatycznie generuj feed produktowy kompatybilny z Allegro. Mapowanie pól, walidacja i odświeżanie z jednego panelu.</p>
        <div class="mt-8"><router-link to="/register" class="px-8 py-3 bg-white text-indigo-700 font-semibold rounded-xl hover:bg-indigo-50 transition">Zacznij za darmo</router-link></div>
      </div>
    </section>
    <section class="py-16 max-w-4xl mx-auto px-4">
      <h2 class="font-heading text-2xl font-bold text-gray-900 mb-6">Feed XML dla Allegro — wymagania</h2>
      <p class="text-gray-600 mb-4">Allegro wymaga feedu XML z elementami &lt;offer&gt;. Ważne: tytuł max 75 znaków, zdjęcie min 600x400 px.</p>
      <div class="space-y-4">
        <div class="border rounded-xl p-5"><h3 class="font-semibold">Pola wymagane:</h3><p class="text-gray-600 mt-1">id, name (max 75 znaków), description, url, price, category, image, availability</p></div>
        <div class="border rounded-xl p-5"><h3 class="font-semibold">Pola zalecane:</h3><p class="text-gray-600 mt-1">brand, ean, condition (new/used/refurbished)</p></div>
      </div>
      <div class="mt-10"><router-link to="/register" class="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition">Generuj feed Allegro za darmo</router-link></div>
    </section>
  </div>
</template>
