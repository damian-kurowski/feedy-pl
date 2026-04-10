<template>
  <div class="min-h-screen bg-white py-16 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">Regulamin usługi Feedy</h1>
      <p class="text-sm text-gray-500 mb-10">Ostatnia aktualizacja: 10 kwietnia 2026</p>

      <!-- 1. Postanowienia ogólne -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">1. Postanowienia ogólne</h2>
        <ol class="list-decimal pl-6 space-y-2 text-gray-700">
          <li>Niniejszy regulamin określa zasady korzystania z usługi Feedy, dostępnej pod adresem feedy.pl (dalej: "Usługa").</li>
          <li>
            Usługodawcą jest:
            <ul class="list-none mt-2 space-y-1 ml-0">
              <li><strong>Firma:</strong> Artur Dylik</li>
              <li><strong>Forma prawna:</strong> Indywidualna działalność gospodarcza</li>
              <li><strong>Adres:</strong> Bedońska 28, 95-020 Janówka</li>
              <li><strong>NIP:</strong> 7282905430</li>
              <li><strong>REGON:</strong> 543472610</li>
              <li><strong>Email:</strong> kontakt@feedy.pl</li>
            </ul>
          </li>
          <li>
            Feedy to usługa SaaS (Software as a Service) umożliwiająca zarządzanie feedami produktowymi XML dla e-commerce. Użytkownik podaje URL do pliku XML ze swojego sklepu internetowego, system parsuje dane produktowe i generuje feedy wyjściowe w formatach wymaganych przez porównywarki cenowe i platformy reklamowe.
          </li>
          <li>
            Definicje:
            <ul class="list-disc pl-6 mt-2 space-y-1">
              <li><strong>Użytkownik</strong> — osoba fizyczna, prawna lub jednostka organizacyjna korzystająca z Usługi.</li>
              <li><strong>Konto</strong> — indywidualne konto Użytkownika w systemie Feedy.</li>
              <li><strong>Feed wejściowy</strong> — plik XML ze sklepu Użytkownika, podany jako URL.</li>
              <li><strong>Feed wyjściowy</strong> — plik XML wygenerowany przez Feedy w formacie docelowej platformy.</li>
              <li><strong>Plan</strong> — wybrany przez Użytkownika wariant usługi określający limity i funkcjonalności.</li>
            </ul>
          </li>
        </ol>
      </section>

      <!-- 2. Warunki korzystania -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">2. Warunki korzystania z usługi</h2>
        <ol class="list-decimal pl-6 space-y-2 text-gray-700">
          <li>Korzystanie z Usługi wymaga rejestracji konta poprzez podanie adresu email i hasła.</li>
          <li>Użytkownik musi mieć ukończone 18 lat lub posiadać zgodę opiekuna prawnego.</li>
          <li>Użytkownik jest odpowiedzialny za zachowanie poufności danych logowania do swojego konta.</li>
          <li>Jedno konto może być używane wyłącznie przez jednego Użytkownika, chyba że Użytkownik korzysta z funkcji organizacji umożliwiającej dostęp wielu osobom.</li>
          <li>Rejestracja oznacza akceptację niniejszego regulaminu oraz polityki prywatności.</li>
        </ol>
      </section>

      <!-- 3. Zakres usługi -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">3. Zakres usługi</h2>
        <p class="text-gray-700 mb-3">W ramach Usługi Feedy zapewnia:</p>
        <ul class="list-disc pl-6 space-y-2 text-gray-700">
          <li>Parsowanie plików XML z produktami na podstawie podanego przez Użytkownika adresu URL.</li>
          <li>Generowanie feedów wyjściowych w formatach: Ceneo, Google Merchant Center, Skapiec, Nokaut, Okazje.info i inne.</li>
          <li>Automatyczne odświeżanie feedów wyjściowych zgodnie z ustawionym interwałem (1h, 6h, 24h).</li>
          <li>Gotowe szablony mapowania pól dla popularnych platform.</li>
          <li>Możliwość ręcznego mapowania i konfiguracji pól feedu wyjściowego.</li>
          <li>Udostępnianie publicznego linku do wygenerowanego feedu XML.</li>
          <li>Reguły filtrowania i modyfikacji produktów w feedach wyjściowych.</li>
        </ul>
      </section>

      <!-- 4. Plany i płatności -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">4. Plany i płatności</h2>
        <ol class="list-decimal pl-6 space-y-2 text-gray-700">
          <li>
            Usługa dostępna jest w następujących planach:
            <ul class="list-disc pl-6 mt-2 space-y-1">
              <li><strong>Free</strong> — 0 zł/mies., do 200 produktów, 1 feed wyjściowy.</li>
              <li><strong>Starter</strong> — 29 zł/mies., do 1 000 produktów, 3 feedy wyjściowe.</li>
              <li><strong>Pro</strong> — 59 zł/mies., do 5 000 produktów, 10 feedów wyjściowych.</li>
              <li><strong>Business</strong> — 99 zł/mies., do 20 000 produktów, bez limitu feedów wyjściowych.</li>
            </ul>
          </li>
          <li>Płatności realizowane są za pośrednictwem operatora Stripe, Inc. Usługodawca nie przechowuje danych kart płatniczych.</li>
          <li>Płatność pobierana jest z góry za każdy okres rozliczeniowy (miesiąc).</li>
          <li>Na życzenie Użytkownika wystawiamy fakturę VAT.</li>
          <li>Użytkownik będący konsumentem ma prawo do odstąpienia od umowy w ciągu 14 dni od dnia zawarcia umowy (zakupu planu płatnego), bez podania przyczyny. Zwrot środków następuje w ciągu 14 dni na ten sam środek płatności.</li>
          <li>Prawo do odstąpienia nie przysługuje, jeśli Użytkownik wyraził zgodę na rozpoczęcie świadczenia usługi przed upływem terminu do odstąpienia i został o tym poinformowany.</li>
        </ol>
      </section>

      <!-- 5. Prawa i obowiązki użytkownika -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">5. Prawa i obowiązki Użytkownika</h2>
        <ol class="list-decimal pl-6 space-y-2 text-gray-700">
          <li>Użytkownik zobowiązuje się do korzystania z Usługi zgodnie z obowiązującym prawem i niniejszym regulaminem.</li>
          <li>Zabronione jest przesyłanie treści nielegalnych, naruszających prawa osób trzecich lub zawierających złośliwe oprogramowanie.</li>
          <li>Zabronione jest nadużywanie API usługi, w tym generowanie sztucznego ruchu, próby obejścia limitów planu lub ataki na infrastrukturę.</li>
          <li>Użytkownik ponosi pełną odpowiedzialność za treść swoich feedów produktowych oraz za posiadanie praw do publikacji danych produktów.</li>
          <li>Użytkownik ma prawo do eksportu swoich danych w dowolnym momencie.</li>
        </ol>
      </section>

      <!-- 6. Prawa i obowiązki usługodawcy -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">6. Prawa i obowiązki Usługodawcy</h2>
        <ol class="list-decimal pl-6 space-y-2 text-gray-700">
          <li>Usługodawca dołoży starań, aby zapewnić dostępność usługi na poziomie 99% w skali miesiąca (SLA).</li>
          <li>Usługodawca zastrzega sobie prawo do planowanych przerw technicznych (maintenance windows), o których poinformuje Użytkowników z co najmniej 24-godzinnym wyprzedzeniem.</li>
          <li>Usługodawca ma prawo do wprowadzania zmian w funkcjonalności Usługi, w tym dodawania nowych funkcji i modyfikacji istniejących.</li>
          <li>Usługodawca ma prawo do zablokowania lub usunięcia konta Użytkownika, który narusza regulamin, po uprzednim ostrzeżeniu.</li>
          <li>W przypadku istotnych zmian w regulaminie Usługodawca poinformuje Użytkowników z co najmniej 14-dniowym wyprzedzeniem.</li>
        </ol>
      </section>

      <!-- 7. Odpowiedzialność -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">7. Odpowiedzialność</h2>
        <ol class="list-decimal pl-6 space-y-2 text-gray-700">
          <li>Usługodawca nie ponosi odpowiedzialności za treść feedów produktowych przesyłanych i generowanych przez Użytkownika.</li>
          <li>Usługodawca nie ponosi odpowiedzialności za błędy lub nieprawidłowości w działaniu platform docelowych (porównywarki cenowe, Google Merchant Center itp.), w tym za odrzucenie feedów przez te platformy.</li>
          <li>Usługodawca nie ponosi odpowiedzialności za straty wynikające z niedostępności źródłowego pliku XML Użytkownika.</li>
          <li>Odpowiedzialność Usługodawcy wobec Użytkownika niebędącego konsumentem jest ograniczona do wysokości opłat uiszczonych przez Użytkownika w okresie ostatnich 3 miesięcy.</li>
          <li>Usługodawca nie ponosi odpowiedzialności za przerwy w działaniu Usługi wynikające z siły wyższej.</li>
        </ol>
      </section>

      <!-- 8. Własność intelektualna -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">8. Własność intelektualna</h2>
        <ol class="list-decimal pl-6 space-y-2 text-gray-700">
          <li>Usługa Feedy, w tym jej kod źródłowy, interfejs graficzny, szablony feedów i dokumentacja, stanowią własność intelektualną Usługodawcy i są chronione prawem autorskim.</li>
          <li>Użytkownik zachowuje pełne prawa do swoich danych produktowych przesłanych do systemu.</li>
          <li>Usługodawca nie nabywa żadnych praw do danych produktowych Użytkownika. Dane te są przetwarzane wyłącznie w celu świadczenia Usługi.</li>
          <li>Zabronione jest kopiowanie, modyfikowanie lub rozpowszechnianie elementów Usługi bez pisemnej zgody Usługodawcy.</li>
        </ol>
      </section>

      <!-- 9. Rozwiązanie umowy -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">9. Rozwiązanie umowy</h2>
        <ol class="list-decimal pl-6 space-y-2 text-gray-700">
          <li>Użytkownik może w dowolnym momencie usunąć swoje konto w ustawieniach aplikacji lub wysyłając żądanie na adres kontakt@feedy.pl.</li>
          <li>Po usunięciu konta wszystkie dane Użytkownika (w tym feedy, konfiguracje i dane produktowe) zostaną trwale usunięte w ciągu 30 dni.</li>
          <li>W przypadku planu płatnego rezygnacja jest skuteczna na koniec bieżącego okresu rozliczeniowego. Środki za niewykorzystany okres nie podlegają zwrotowi, z zastrzeżeniem prawa do odstąpienia opisanego w punkcie 4.</li>
          <li>Usługodawca może rozwiązać umowę ze skutkiem natychmiastowym w przypadku rażącego naruszenia regulaminu przez Użytkownika.</li>
        </ol>
      </section>

      <!-- 10. Reklamacje -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">10. Reklamacje</h2>
        <ol class="list-decimal pl-6 space-y-2 text-gray-700">
          <li>Reklamacje można składać drogą elektroniczną na adres: <strong>kontakt@feedy.pl</strong>.</li>
          <li>Reklamacja powinna zawierać: adres email konta, opis problemu oraz oczekiwany sposób rozwiązania.</li>
          <li>Usługodawca rozpatrzy reklamację w ciągu 14 dni od jej otrzymania i poinformuje Użytkownika o wyniku drogą mailową.</li>
          <li>Użytkownik będący konsumentem może skorzystać z pozasądowych sposobów rozpatrywania reklamacji, w tym z platformy ODR pod adresem <a href="https://ec.europa.eu/consumers/odr" class="text-indigo-600 underline" target="_blank" rel="noopener">https://ec.europa.eu/consumers/odr</a>.</li>
        </ol>
      </section>

      <!-- 11. Postanowienia końcowe -->
      <section class="mb-10">
        <h2 class="text-xl font-semibold text-gray-900 mb-3">11. Postanowienia końcowe</h2>
        <ol class="list-decimal pl-6 space-y-2 text-gray-700">
          <li>W sprawach nieuregulowanych niniejszym regulaminem zastosowanie mają przepisy prawa polskiego, w szczególności Kodeksu cywilnego, ustawy o prawach konsumenta oraz RODO.</li>
          <li>Ewentualne spory pomiędzy Usługodawcą a Użytkownikiem niebędącym konsumentem rozstrzygane będą przez sąd właściwy dla siedziby Usługodawcy.</li>
          <li>W przypadku Użytkowników będących konsumentami właściwość sądu ustalana jest zgodnie z przepisami ogólnymi.</li>
          <li>Jeżeli którekolwiek z postanowień niniejszego regulaminu zostanie uznane za nieważne, pozostałe postanowienia pozostają w mocy.</li>
          <li>Niniejszy regulamin wchodzi w życie z dniem 10 kwietnia 2026 roku.</li>
        </ol>
      </section>

      <div class="border-t border-gray-200 pt-6 text-sm text-gray-500">
        <p>Niniejszy regulamin obowiązuje od dnia 10 kwietnia 2026 roku.</p>
      </div>
    </div>
  </div>
</template>
