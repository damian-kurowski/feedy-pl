<template>
  <div class="min-h-screen bg-white">
    <article class="max-w-3xl mx-auto px-4 py-16">
      <div class="mb-10">
        <router-link to="/blog" class="text-sm text-indigo-600 hover:text-indigo-800 mb-4 inline-block">&larr; Wróć do bloga</router-link>
        <div class="flex items-center gap-2 text-xs text-gray-400 mb-4">
          <span>11 kwietnia 2026</span><span>·</span><span>6 min czytania</span>
        </div>
        <h1 class="font-heading text-3xl sm:text-4xl font-extrabold text-gray-900 leading-tight">Ceneo odrzuca oferty — jak naprawić feed?</h1>
        <p class="mt-4 text-lg text-gray-600">Najczęstsze przyczyny odrzuceń i jak je zdiagnozować oraz naprawić.</p>
      </div>
      <div class="prose prose-gray max-w-none">
        <h2 class="font-heading">Dlaczego Ceneo odrzuca oferty?</h2>
        <p>Ceneo waliduje każdą ofertę w feedzie XML. Jeśli produkt nie spełnia wymagań, zostaje odrzucony i nie pojawia się w wynikach porównywania cen. Oto najczęstsze przyczyny:</p>

        <h3>1. Brak wymaganego pola</h3>
        <p>Feed musi zawierać pola: <strong>id, url, price, avail, name, cat, desc</strong>. Brak któregokolwiek = odrzucenie.</p>
        <p><strong>Jak naprawić:</strong> Sprawdź feed walidatorem. W Feedy — kliknij "Sprawdź jakość feedu" na stronie feedu wyjściowego. Zobaczysz dokładnie które produkty i pola brakują.</p>

        <h3>2. Nieprawidłowy format ceny</h3>
        <p>Ceneo oczekuje ceny jako liczby <strong>bez waluty</strong>: <code>49.99</code>, nie <code>49.99 PLN</code> ani <code>49,99</code>.</p>
        <p><strong>Jak naprawić:</strong> Feedy automatycznie formatuje cenę — usuwa walutę i zamienia przecinek na kropkę.</p>

        <h3>3. Brak lub nieprawidłowy kod EAN</h3>
        <p>Choć EAN nie jest stricte wymagany, produkty bez EAN mogą nie być dopasowane do kart produktów. Nieprawidłowy EAN (zły checksum) też powoduje problemy.</p>
        <p><strong>Jak naprawić:</strong> Feedy pokazuje pokrycie EAN i waliduje checksum EAN-13. Zobaczysz które produkty mają błędne kody.</p>

        <h3>4. Cena niezgodna ze stroną produktu</h3>
        <p>Ceneo crawluje strony produktów i porównuje cenę z feedu z ceną na stronie. Rozbieżność = zawieszenie oferty.</p>
        <p><strong>Jak naprawić:</strong> Ustaw automatyczne odświeżanie feedu co 1 godzinę w Feedy.</p>

        <h3>5. Niedostępne zdjęcia</h3>
        <p>Jeśli URL zdjęcia zwraca błąd 404, Ceneo może odrzucić ofertę.</p>
        <p><strong>Jak naprawić:</strong> Sprawdź czy wszystkie URL-e zdjęć są dostępne. W Feedy — podgląd zdjęć pokazuje które się nie ładują.</p>

        <h2 class="font-heading">Jak zdiagnozować problem?</h2>
        <ol>
          <li>Zaloguj się do panelu Ceneo dla sprzedawców</li>
          <li>Sprawdź raport z ostatniego pobrania feedu</li>
          <li>Ceneo pokaże listę odrzuconych ofert z przyczyną</li>
        </ol>
        <p>Alternatywnie — użyj <a href="https://feedy.pl" class="text-indigo-600 font-semibold">walidatora Feedy</a>, który sprawdza feed <strong>zanim wyślesz go do Ceneo</strong>. Dzięki temu naprawisz błędy przed odrzuceniem.</p>

        <h2 class="font-heading">Podsumowanie</h2>
        <p>Większość odrzuceń na Ceneo wynika z brakujących pól, złego formatu ceny lub nieaktualnych danych. Walidacja feedu przed wysłaniem eliminuje 90% problemów.</p>
        <p class="mt-6"><router-link to="/register" class="inline-flex items-center px-6 py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition">Waliduj swój feed za darmo w Feedy</router-link></p>
      </div>
    </article>
  </div>
</template>
