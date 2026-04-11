<template>
  <div class="min-h-screen bg-white py-16 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">Polityka cookies</h1>
      <p class="text-sm text-gray-500 mb-10">Ostatnia aktualizacja: 11 kwietnia 2026</p>

      <!-- 1. Czym są cookies -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">1. Czym są pliki cookies i localStorage</h2>
        <p class="text-gray-700 leading-relaxed">
          Pliki cookies to małe pliki tekstowe zapisywane na urządzeniu użytkownika przez przeglądarkę internetową. localStorage to mechanizm przeglądarki umożliwiający przechowywanie danych lokalnie na urządzeniu użytkownika. Oba mechanizmy służą do zapamiętywania informacji niezbędnych do prawidłowego działania stron internetowych i aplikacji.
        </p>
      </section>

      <!-- 2. Jakie cookies używamy -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">2. Jakie dane przechowujemy lokalnie</h2>
        <p class="text-gray-700 leading-relaxed mb-4">
          Usługa Feedy korzysta z mechanizmu localStorage przeglądarki. Poniżej przedstawiamy pełną listę przechowywanych danych:
        </p>

        <h3 class="text-lg font-medium text-gray-900 mb-2">Niezbędne (wymagane do działania usługi)</h3>
        <div class="overflow-x-auto mb-6">
          <table class="w-full text-sm text-left border border-gray-200 rounded-lg">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 font-medium text-gray-700 border-b">Nazwa</th>
                <th class="px-4 py-3 font-medium text-gray-700 border-b">Typ</th>
                <th class="px-4 py-3 font-medium text-gray-700 border-b">Cel</th>
                <th class="px-4 py-3 font-medium text-gray-700 border-b">Czas życia</th>
              </tr>
            </thead>
            <tbody>
              <tr class="border-b border-gray-100">
                <td class="px-4 py-3 font-mono text-gray-900">access_token</td>
                <td class="px-4 py-3 text-gray-600">localStorage</td>
                <td class="px-4 py-3 text-gray-600">Token autoryzacyjny umożliwiający korzystanie z usługi po zalogowaniu. Bez niego nie jest możliwe korzystanie z konta.</td>
                <td class="px-4 py-3 text-gray-600">Do wylogowania</td>
              </tr>
              <tr class="border-b border-gray-100">
                <td class="px-4 py-3 font-mono text-gray-900">refresh_token</td>
                <td class="px-4 py-3 text-gray-600">localStorage</td>
                <td class="px-4 py-3 text-gray-600">Token służący do automatycznego odświeżania sesji, aby użytkownik nie musiał logować się ponownie po wygaśnięciu access_token.</td>
                <td class="px-4 py-3 text-gray-600">Do wylogowania</td>
              </tr>
              <tr>
                <td class="px-4 py-3 font-mono text-gray-900">cookie_consent</td>
                <td class="px-4 py-3 text-gray-600">localStorage</td>
                <td class="px-4 py-3 text-gray-600">Zapamiętanie wyborów użytkownika dotyczących plików cookie (niezbędne, analityczne). Zawiera datę wyrażenia zgody.</td>
                <td class="px-4 py-3 text-gray-600">Bezterminowo</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h3 class="text-lg font-medium text-gray-900 mb-2">Funkcjonalne (ułatwiające korzystanie z usługi)</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-sm text-left border border-gray-200 rounded-lg">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 font-medium text-gray-700 border-b">Nazwa</th>
                <th class="px-4 py-3 font-medium text-gray-700 border-b">Typ</th>
                <th class="px-4 py-3 font-medium text-gray-700 border-b">Cel</th>
                <th class="px-4 py-3 font-medium text-gray-700 border-b">Czas życia</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="px-4 py-3 font-mono text-gray-900">onboarding_done</td>
                <td class="px-4 py-3 text-gray-600">localStorage</td>
                <td class="px-4 py-3 text-gray-600">Zapamiętanie, że użytkownik ukończył proces wdrożenia (onboarding), aby nie wyświetlać go ponownie.</td>
                <td class="px-4 py-3 text-gray-600">Bezterminowo</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- 3. Cookies analityczne -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">3. Cookies analityczne (opcjonalne)</h2>
        <p class="text-gray-700 leading-relaxed mb-4">
          Za Twoją zgodą korzystamy z Google Analytics 4 w celu analizy ruchu na stronie i ulepszania usługi. Cookies analityczne są <strong>ładowane wyłącznie po wyrażeniu zgody</strong> za pośrednictwem bannera cookie.
        </p>
        <div class="overflow-x-auto mb-4">
          <table class="w-full text-sm text-left border border-gray-200 rounded-lg">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 font-medium text-gray-700 border-b">Nazwa</th>
                <th class="px-4 py-3 font-medium text-gray-700 border-b">Dostawca</th>
                <th class="px-4 py-3 font-medium text-gray-700 border-b">Cel</th>
                <th class="px-4 py-3 font-medium text-gray-700 border-b">Czas życia</th>
              </tr>
            </thead>
            <tbody>
              <tr class="border-b border-gray-100">
                <td class="px-4 py-3 font-mono text-gray-900">_ga</td>
                <td class="px-4 py-3 text-gray-600">Google</td>
                <td class="px-4 py-3 text-gray-600">Rozróżnianie użytkowników w Google Analytics.</td>
                <td class="px-4 py-3 text-gray-600">2 lata</td>
              </tr>
              <tr>
                <td class="px-4 py-3 font-mono text-gray-900">_ga_FXG667NT02</td>
                <td class="px-4 py-3 text-gray-600">Google</td>
                <td class="px-4 py-3 text-gray-600">Utrzymanie stanu sesji w Google Analytics 4.</td>
                <td class="px-4 py-3 text-gray-600">2 lata</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="text-gray-700 leading-relaxed">
          Dane zbierane przez Google Analytics są <strong>anonimizowane</strong> (anonymize_ip). Nie łączymy danych analitycznych z danymi osobowymi. Usługa Feedy <strong>nie używa</strong> plików cookies marketingowych, reklamowych ani śledzących (Facebook Pixel itp.). Nie udostępniamy danych z przeglądarki użytkownika podmiotom trzecim w celach reklamowych.
        </p>
      </section>

      <!-- 3a. Zarządzanie zgodą -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">4. Zarządzanie zgodą na cookies</h2>
        <p class="text-gray-700 leading-relaxed mb-3">
          Przy pierwszej wizycie wyświetlamy baner z możliwością:
        </p>
        <ul class="list-disc pl-6 space-y-2 text-gray-700">
          <li><strong>Akceptacji wszystkich</strong> — cookies niezbędne + analityczne (Google Analytics).</li>
          <li><strong>Odrzucenia opcjonalnych</strong> — tylko cookies niezbędne, bez Google Analytics.</li>
          <li><strong>Ustawień</strong> — indywidualny wybór kategorii cookies.</li>
        </ul>
        <p class="text-gray-700 mt-3">
          Swoją zgodę możesz zmienić w dowolnym momencie, usuwając klucz <code>cookie_consent</code> z localStorage przeglądarki (Narzędzia deweloperskie → Aplikacja → Local Storage → feedy.pl) — przy następnej wizycie baner wyświetli się ponownie.
        </p>
      </section>

      <!-- 4. Zarządzanie cookies -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">5. Jak zarządzać danymi przechowywanymi lokalnie</h2>
        <p class="text-gray-700 leading-relaxed mb-3">
          Możesz zarządzać danymi przechowywanymi w localStorage za pomocą ustawień przeglądarki:
        </p>
        <ul class="list-disc pl-6 space-y-2 text-gray-700">
          <li><strong>Google Chrome:</strong> Ustawienia &rarr; Prywatność i bezpieczeństwo &rarr; Pliki cookie i dane witryn &rarr; Wyświetl wszystkie dane witryn.</li>
          <li><strong>Mozilla Firefox:</strong> Ustawienia &rarr; Prywatność i bezpieczeństwo &rarr; Ciasteczka i dane stron &rarr; Zarządzaj danymi.</li>
          <li><strong>Microsoft Edge:</strong> Ustawienia &rarr; Prywatność, wyszukiwanie i usługi &rarr; Pliki cookie i uprawnienia witryn.</li>
          <li><strong>Safari:</strong> Preferencje &rarr; Prywatność &rarr; Zarządzaj danymi stron.</li>
        </ul>
        <p class="text-gray-700 mt-3">
          Usunięcie danych localStorage spowoduje wylogowanie z usługi Feedy i konieczność ponownego zalogowania.
        </p>
      </section>

      <!-- 5. Kontakt -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">6. Kontakt</h2>
        <p class="text-gray-700 leading-relaxed">
          W razie pytań dotyczących polityki cookies skontaktuj się z nami:
        </p>
        <ul class="mt-3 list-none space-y-1 text-gray-700">
          <li><strong>Email:</strong> kontakt@feedy.pl</li>
          <li><strong>Adres:</strong> Artur Dylik, Bedońska 28, 95-020 Janówka</li>
        </ul>
      </section>

      <div class="border-t border-gray-200 pt-6 text-sm text-gray-500">
        <p>Niniejsza polityka cookies obowiązuje od dnia 11 kwietnia 2026 roku.</p>
      </div>
    </div>
  </div>
</template>
