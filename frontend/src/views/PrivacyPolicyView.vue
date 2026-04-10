<template>
  <div class="min-h-screen bg-white py-16 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">Polityka prywatności</h1>
      <p class="text-sm text-gray-500 mb-10">Ostatnia aktualizacja: 10 kwietnia 2026</p>

      <!-- 1. Administrator -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">1. Administrator danych osobowych</h2>
        <p class="text-gray-700 leading-relaxed">
          Administratorem Twoich danych osobowych jest:
        </p>
        <ul class="mt-3 list-none space-y-1 text-gray-700">
          <li><strong>Firma:</strong> Artur Dylik</li>
          <li><strong>Forma prawna:</strong> Indywidualna działalność gospodarcza</li>
          <li><strong>Adres:</strong> Bedońska 28, 95-020 Janówka</li>
          <li><strong>NIP:</strong> 7282905430</li>
          <li><strong>REGON:</strong> 543472610</li>
          <li><strong>Email kontaktowy:</strong> kontakt@feedy.pl</li>
        </ul>
      </section>

      <!-- 2. Jakie dane zbieramy -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">2. Jakie dane zbieramy</h2>
        <p class="text-gray-700 leading-relaxed mb-3">
          W ramach korzystania z usługi Feedy zbieramy następujące dane:
        </p>
        <ul class="list-disc pl-6 space-y-2 text-gray-700">
          <li><strong>Adres email</strong> — podawany podczas rejestracji i używany do logowania oraz komunikacji.</li>
          <li><strong>Hasło</strong> — przechowywane wyłącznie w postaci zaszyfrowanego skrótu (hash). Nie mamy dostępu do Twojego hasła w formie jawnej.</li>
          <li><strong>Adres IP</strong> — rejestrowany automatycznie w logach serwera w celach bezpieczeństwa i diagnostyki.</li>
          <li><strong>Dane produktów z plików XML</strong> — adresy URL do plików XML oraz dane produktowe (nazwy, ceny, opisy, zdjęcia itp.) pobierane z tych plików w celu generowania feedów wyjściowych.</li>
          <li><strong>Dane billingowe</strong> — informacje o płatnościach i subskrypcjach przetwarzane za pośrednictwem Stripe.</li>
        </ul>
      </section>

      <!-- 3. Cel przetwarzania -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">3. Cel przetwarzania danych</h2>
        <ul class="list-disc pl-6 space-y-2 text-gray-700">
          <li><strong>Świadczenie usługi</strong> — rejestracja konta, parsowanie plików XML, generowanie feedów wyjściowych, udostępnianie linków do feedów.</li>
          <li><strong>Autoryzacja i bezpieczeństwo</strong> — weryfikacja tożsamości użytkownika, ochrona przed nieautoryzowanym dostępem.</li>
          <li><strong>Komunikacja</strong> — wysyłanie powiadomień związanych z usługą (np. zmiany w regulaminie, informacje o koncie).</li>
          <li><strong>Marketing</strong> — wyłącznie za wyraźną zgodą użytkownika (np. newsletter z informacjami o nowych funkcjach).</li>
          <li><strong>Rozliczenia</strong> — obsługa płatności, fakturowanie, rozpatrywanie reklamacji.</li>
        </ul>
      </section>

      <!-- 4. Podstawa prawna -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">4. Podstawa prawna przetwarzania</h2>
        <p class="text-gray-700 leading-relaxed mb-3">
          Dane osobowe przetwarzamy na podstawie art. 6 ust. 1 Rozporządzenia Parlamentu Europejskiego i Rady (UE) 2016/679 (RODO):
        </p>
        <ul class="list-disc pl-6 space-y-2 text-gray-700">
          <li><strong>Art. 6 ust. 1 lit. b) RODO</strong> — przetwarzanie jest niezbędne do wykonania umowy (świadczenie usługi Feedy na podstawie regulaminu).</li>
          <li><strong>Art. 6 ust. 1 lit. f) RODO</strong> — przetwarzanie jest niezbędne do celów wynikających z prawnie uzasadnionych interesów administratora (bezpieczeństwo, diagnostyka, ochrona przed nadużyciami).</li>
          <li><strong>Art. 6 ust. 1 lit. a) RODO</strong> — przetwarzanie na podstawie zgody użytkownika (marketing, newsletter).</li>
          <li><strong>Art. 6 ust. 1 lit. c) RODO</strong> — przetwarzanie jest niezbędne do wypełnienia obowiązku prawnego ciążącego na administratorze (przechowywanie danych billingowych zgodnie z przepisami podatkowymi).</li>
        </ul>
      </section>

      <!-- 5. Odbiorcy danych -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">5. Odbiorcy danych</h2>
        <p class="text-gray-700 leading-relaxed mb-3">
          Twoje dane mogą być przekazywane następującym kategoriom odbiorców:
        </p>
        <ul class="list-disc pl-6 space-y-2 text-gray-700">
          <li><strong>Stripe, Inc.</strong> — operator płatności. Dane niezbędne do realizacji płatności (email, dane karty) są przetwarzane bezpośrednio przez Stripe zgodnie z ich polityką prywatności.</li>
          <li><strong>Dostawca usług hostingowych</strong> — serwery, na których przechowywane są dane usługi.</li>
          <li><strong>Dostawca usług SMTP</strong> — do wysyłania wiadomości email (powiadomienia, resetowanie hasła).</li>
        </ul>
        <p class="text-gray-700 mt-3">
          Nie sprzedajemy Twoich danych osobowych podmiotom trzecim. Dane mogą być również udostępnione organom państwowym, jeśli wynika to z obowiązujących przepisów prawa.
        </p>
      </section>

      <!-- 6. Okres przechowywania -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">6. Okres przechowywania danych</h2>
        <ul class="list-disc pl-6 space-y-2 text-gray-700">
          <li><strong>Dane konta</strong> (email, hasło, dane produktów) — przechowywane przez cały okres posiadania konta. Po usunięciu konta dane są trwale usuwane w ciągu 30 dni.</li>
          <li><strong>Dane billingowe</strong> — przechowywane przez okres 5 lat od końca roku kalendarzowego, w którym dokonano płatności, zgodnie z przepisami prawa podatkowego.</li>
          <li><strong>Logi serwera</strong> (adresy IP) — przechowywane przez okres 90 dni, a następnie automatycznie usuwane.</li>
          <li><strong>Dane przetwarzane na podstawie zgody</strong> — do momentu wycofania zgody.</li>
        </ul>
      </section>

      <!-- 7. Prawa użytkownika -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">7. Prawa użytkownika</h2>
        <p class="text-gray-700 leading-relaxed mb-3">
          Zgodnie z RODO przysługują Ci następujące prawa:
        </p>
        <ul class="list-disc pl-6 space-y-2 text-gray-700">
          <li><strong>Prawo dostępu</strong> — masz prawo uzyskać informację, czy przetwarzamy Twoje dane, oraz otrzymać ich kopię.</li>
          <li><strong>Prawo do sprostowania</strong> — możesz żądać poprawienia nieprawidłowych lub uzupełnienia niekompletnych danych.</li>
          <li><strong>Prawo do usunięcia</strong> ("prawo do bycia zapomnianym") — możesz żądać usunięcia swoich danych. Możesz również samodzielnie usunąć konto w ustawieniach.</li>
          <li><strong>Prawo do przenoszenia danych</strong> — masz prawo otrzymać swoje dane w ustrukturyzowanym formacie (np. JSON).</li>
          <li><strong>Prawo do sprzeciwu</strong> — możesz sprzeciwić się przetwarzaniu danych opartemu na uzasadnionym interesie administratora.</li>
          <li><strong>Prawo do ograniczenia przetwarzania</strong> — możesz żądać ograniczenia przetwarzania danych w określonych sytuacjach.</li>
          <li><strong>Prawo do wycofania zgody</strong> — w przypadku przetwarzania opartego na zgodzie, możesz ją wycofać w dowolnym momencie.</li>
          <li><strong>Prawo do skargi</strong> — masz prawo złożyć skargę do Prezesa Urzędu Ochrony Danych Osobowych (UODO), ul. Stawki 2, 00-193 Warszawa, <a href="https://uodo.gov.pl" class="text-indigo-600 underline" target="_blank" rel="noopener">uodo.gov.pl</a>.</li>
        </ul>
        <p class="text-gray-700 mt-3">
          W celu realizacji swoich praw skontaktuj się z nami pod adresem: <strong>kontakt@feedy.pl</strong>.
        </p>
      </section>

      <!-- 8. Pliki cookies -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">8. Pliki cookies i localStorage</h2>
        <p class="text-gray-700 leading-relaxed mb-3">
          Usługa Feedy korzysta z mechanizmu localStorage przeglądarki w celu przechowywania danych niezbędnych do prawidłowego działania aplikacji:
        </p>
        <ul class="list-disc pl-6 space-y-2 text-gray-700">
          <li><strong>access_token</strong> — token autoryzacyjny umożliwiający korzystanie z usługi bez ponownego logowania (niezbędny).</li>
          <li><strong>refresh_token</strong> — token służący do automatycznego odświeżania sesji (niezbędny).</li>
          <li><strong>onboarding_done</strong> — zapamiętanie ukończenia procesu wdrożenia (funkcjonalny).</li>
          <li><strong>cookies_accepted</strong> — zapamiętanie wyrażenia zgody na politykę cookies (niezbędny).</li>
        </ul>
        <p class="text-gray-700 mt-3">
          Szczegółowe informacje znajdziesz w naszej
          <router-link to="/polityka-cookies" class="text-indigo-600 underline">polityce cookies</router-link>.
        </p>
      </section>

      <!-- 9. Kontakt -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">9. Kontakt w sprawie danych osobowych</h2>
        <p class="text-gray-700 leading-relaxed">
          We wszystkich sprawach dotyczących ochrony danych osobowych możesz skontaktować się z nami:
        </p>
        <ul class="mt-3 list-none space-y-1 text-gray-700">
          <li><strong>Email:</strong> kontakt@feedy.pl</li>
          <li><strong>Adres korespondencyjny:</strong> Artur Dylik, Bedońska 28, 95-020 Janówka</li>
        </ul>
        <p class="text-gray-700 mt-3">
          Odpowiadamy na zapytania w ciągu 30 dni od ich otrzymania, zgodnie z art. 12 ust. 3 RODO.
        </p>
      </section>

      <!-- 10. Zmiany -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">10. Zmiany polityki prywatności</h2>
        <p class="text-gray-700 leading-relaxed">
          Zastrzegamy sobie prawo do wprowadzania zmian w niniejszej polityce prywatności. O istotnych zmianach poinformujemy użytkowników drogą mailową lub poprzez komunikat w aplikacji, z co najmniej 14-dniowym wyprzedzeniem. Korzystanie z usługi po wejściu zmian w życie oznacza ich akceptację.
        </p>
      </section>

      <div class="border-t border-gray-200 pt-6 text-sm text-gray-500">
        <p>Niniejsza polityka prywatności obowiązuje od dnia 10 kwietnia 2026 roku.</p>
      </div>
    </div>
  </div>
</template>
