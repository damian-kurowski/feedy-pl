<template>
  <div class="min-h-screen bg-white">
    <article class="max-w-3xl mx-auto px-4 py-16">
      <div class="mb-10">
        <router-link to="/blog" class="text-sm text-indigo-600 hover:text-indigo-800 mb-4 inline-block">&larr; Wróć do bloga</router-link>
        <div class="flex items-center gap-2 text-xs text-gray-400 mb-4">
          <span>11 kwietnia 2026</span>
          <span>·</span>
          <span>10 min czytania</span>
        </div>
        <h1 class="font-heading text-3xl sm:text-4xl font-extrabold text-gray-900 leading-tight">Jak dodać produkty do Ceneo — kompletny poradnik 2026</h1>
        <p class="mt-4 text-lg text-gray-600">Krok po kroku: jak stworzyć feed XML dla Ceneo, jakie pola są wymagane, jak uniknąć odrzucenia ofert i jak automatycznie aktualizować dane produktowe.</p>
      </div>

      <div class="prose prose-gray max-w-none">
        <h2 class="font-heading">Czym jest feed produktowy Ceneo?</h2>
        <p>Feed produktowy Ceneo to plik XML zawierający informacje o produktach z Twojego sklepu internetowego. Ceneo pobiera ten plik i wyświetla Twoje oferty w wynikach porównywania cen. Dzięki temu potencjalni klienci mogą znaleźć Twoje produkty, porównać ceny i przejść bezpośrednio do Twojego sklepu.</p>
        <p>Feed XML jest standardowym formatem wymiany danych między sklepem a porównywarką. Aktualizuje się automatycznie — Ceneo pobiera nową wersję pliku co kilka godzin, dzięki czemu ceny i dostępność produktów są zawsze aktualne.</p>

        <h2 class="font-heading">Wymagane pola w feedzie Ceneo</h2>
        <p>Feed Ceneo musi zawierać określone pola dla każdego produktu. Brak wymaganych pól to najczęstsza przyczyna odrzucenia ofert.</p>

        <h3>Pola obowiązkowe</h3>
        <ul>
          <li><strong>id</strong> — unikalny identyfikator produktu w Twoim sklepie</li>
          <li><strong>url</strong> — bezpośredni link do strony produktu</li>
          <li><strong>price</strong> — cena brutto w formacie numerycznym, <strong>bez waluty</strong> (np. 49.99, NIE 49.99 PLN)</li>
          <li><strong>avail</strong> — dostępność jako kod: 1 (dostępny), 3 (3 dni), 7 (7 dni), 14 (14 dni), 99 (na zamówienie)</li>
          <li><strong>name</strong> — pełna nazwa produktu z marką i kluczowymi cechami</li>
          <li><strong>cat</strong> — kategoria produktu z Twojego sklepu</li>
          <li><strong>desc</strong> — opis produktu</li>
        </ul>

        <h3>Pola zalecane (zwiększają widoczność)</h3>
        <ul>
          <li><strong>producer</strong> — marka / producent</li>
          <li><strong>code (EAN)</strong> — kod kreskowy EAN-13. Produkty z EAN są automatycznie dopasowywane do kart produktów na Ceneo, co znacząco zwiększa widoczność</li>
          <li><strong>imgs</strong> — zdjęcie główne produktu</li>
          <li><strong>old_price</strong> — cena przed obniżką (wyświetla przekreśloną cenę)</li>
          <li><strong>shipping</strong> — koszt dostawy</li>
        </ul>

        <h2 class="font-heading">Przykład poprawnego feedu XML Ceneo</h2>
        <pre class="bg-gray-50 rounded-xl p-4 text-sm overflow-x-auto"><code>&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;offers&gt;
  &lt;o id="123" url="https://twojsklep.pl/produkt/123"
     price="49.99" avail="1"&gt;
    &lt;name&gt;Koszulka polo męska bawełniana - rozmiar L&lt;/name&gt;
    &lt;cat&gt;Odzież &gt; Koszulki&lt;/cat&gt;
    &lt;desc&gt;Wysokiej jakości koszulka polo z 100% bawełny...&lt;/desc&gt;
    &lt;imgs&gt;
      &lt;main url="https://twojsklep.pl/img/koszulka.jpg"/&gt;
    &lt;/imgs&gt;
    &lt;attrs&gt;
      &lt;a name="Producent"&gt;PoloBrand&lt;/a&gt;
      &lt;a name="EAN"&gt;5901234123457&lt;/a&gt;
    &lt;/attrs&gt;
  &lt;/o&gt;
&lt;/offers&gt;</code></pre>

        <h2 class="font-heading">Krok po kroku: jak dodać produkty do Ceneo</h2>

        <h3>Krok 1: Znajdź link do eksportu XML w swoim sklepie</h3>
        <p>Każda platforma e-commerce generuje feed XML inaczej:</p>
        <ul>
          <li><strong>Shoper:</strong> Panel administracyjny → Integracje → Eksport danych → skopiuj link CeneoV2</li>
          <li><strong>WooCommerce:</strong> Zainstaluj wtyczkę Product Feed PRO lub CTX Feed → wygeneruj feed Ceneo → skopiuj URL</li>
          <li><strong>PrestaShop:</strong> Moduły → Feed produktowy → skonfiguruj i skopiuj link</li>
          <li><strong>Magento:</strong> Rozszerzenia → Product Feed → eksportuj jako Ceneo XML</li>
        </ul>

        <h3>Krok 2: Zweryfikuj feed przed wysłaniem</h3>
        <p>Zanim wyślesz feed do Ceneo, sprawdź go pod kątem błędów. Najczęstsze problemy:</p>
        <ul>
          <li>Brak wymaganego pola (id, url, price)</li>
          <li>Cena z walutą (np. "49.99 PLN" zamiast "49.99")</li>
          <li>Nieprawidłowy kod dostępności</li>
          <li>Zdjęcie niedostępne (błąd 404)</li>
        </ul>
        <p><strong>Narzędzie Feedy automatycznie waliduje feed</strong> i pokazuje dokładnie które produkty i pola wymagają poprawy, wraz z Quality Score (wskaźnikiem jakości).</p>

        <h3>Krok 3: Wyślij feed do Ceneo</h3>
        <p>W panelu Ceneo dla sprzedawców (partner.ceneo.pl):</p>
        <ol>
          <li>Zaloguj się na swoje konto sprzedawcy</li>
          <li>Przejdź do ustawień feedu</li>
          <li>Wklej URL feedu XML</li>
          <li>Ustaw częstotliwość pobierania (zalecamy co 4-6 godzin)</li>
          <li>Zapisz i poczekaj na pierwsze pobranie</li>
        </ol>

        <h3>Krok 4: Monitoruj i optymalizuj</h3>
        <p>Po wysłaniu feedu regularnie sprawdzaj:</p>
        <ul>
          <li>Ile produktów zostało zaakceptowanych vs odrzuconych</li>
          <li>Czy ceny i dostępność są aktualne</li>
          <li>Czy produkty z EAN są prawidłowo dopasowane do kart produktów</li>
        </ul>

        <h2 class="font-heading">Najczęstsze błędy i jak ich uniknąć</h2>

        <h3>1. Cena z walutą</h3>
        <p><strong>Błąd:</strong> <code>price="49.99 PLN"</code></p>
        <p><strong>Poprawnie:</strong> <code>price="49.99"</code></p>
        <p>Ceneo oczekuje ceny jako czystej liczby, bez symbolu waluty.</p>

        <h3>2. Brak kodu EAN</h3>
        <p>Produkty bez kodu EAN mogą nie zostać dopasowane do istniejących kart produktów na Ceneo. To oznacza, że Twoja oferta może być widoczna jako osobna pozycja zamiast w porównaniu cen z innymi sklepami.</p>
        <p><strong>Rozwiązanie:</strong> Dodaj kody EAN do produktów. Jeśli nie masz EAN, skontaktuj się z producentem lub dystrybutorem.</p>

        <h3>3. Nieaktualny feed</h3>
        <p>Jeśli feed nie odświeża się automatycznie, ceny i dostępność będą nieaktualne. Ceneo może zawiesić oferty z dużą rozbieżnością cenową.</p>
        <p><strong>Rozwiązanie:</strong> Ustaw automatyczne odświeżanie feedu. W Feedy możesz ustawić refresh co 1h, 6h lub 24h.</p>

        <h2 class="font-heading">Jak Feedy ułatwia zarządzanie feedem Ceneo?</h2>
        <p><a href="https://feedy.pl" class="text-indigo-600 font-semibold">Feedy</a> to polskie narzędzie do zarządzania feedami produktowymi. Oto jak pomaga z feedem Ceneo:</p>
        <ul>
          <li><strong>Automatyczne mapowanie pól</strong> — wklej link do XML ze sklepu, Feedy rozpozna format i zmapuje pola do wymagań Ceneo</li>
          <li><strong>Walidacja przed wysłaniem</strong> — Quality Score pokazuje jakość feedu i listę błędów do naprawienia</li>
          <li><strong>Auto-refresh</strong> — feed odświeża się automatycznie co 1h, 6h lub 24h</li>
          <li><strong>Edycja per produkt</strong> — zmień tytuł, cenę lub opis konkretnego produktu bez modyfikacji źródła</li>
          <li><strong>Mapowanie kategorii</strong> — zmapuj kategorie ze sklepu na kategorie Ceneo</li>
        </ul>
        <p class="mt-6"><router-link to="/register" class="inline-flex items-center px-6 py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition">Zacznij za darmo — 200 produktów, bez karty kredytowej</router-link></p>

        <h2 class="font-heading">Podsumowanie</h2>
        <p>Dodanie produktów do Ceneo wymaga poprawnego feedu XML z wymaganymi polami. Kluczowe elementy to: prawidłowy format ceny (bez waluty), kody EAN, aktualne zdjęcia i regularne odświeżanie feedu. Narzędzia takie jak Feedy automatyzują cały proces i pomagają uniknąć najczęstszych błędów.</p>
      </div>
    </article>
  </div>
</template>
