// SEO metadata + unique noscript content for every prerendered route.
// Each route generates a standalone HTML file that:
// - has its own title, meta description, canonical
// - has its own JSON-LD structured data
// - has its own noscript fallback content (visible to crawlers + JS-disabled users)
// - still loads the same Vue SPA bundle (so the live experience is unchanged)

const SITE = 'https://feedy.pl'
const DEFAULT_OG_IMAGE = `${SITE}/og-image.svg`

const ORGANIZATION = {
  '@type': 'Organization',
  name: 'Feedy',
  url: SITE,
  logo: `${SITE}/favicon.svg`,
}

function articleSchema({ title, description, slug, datePublished, dateModified, image }) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: title,
    description,
    image: image || DEFAULT_OG_IMAGE,
    author: ORGANIZATION,
    publisher: { ...ORGANIZATION, logo: { '@type': 'ImageObject', url: `${SITE}/favicon.svg` } },
    datePublished: datePublished || '2026-04-11',
    dateModified: dateModified || '2026-04-14',
    mainEntityOfPage: { '@type': 'WebPage', '@id': `${SITE}${slug}` },
  }
}

function breadcrumbSchema(items) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((it, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: it.name,
      item: `${SITE}${it.path}`,
    })),
  }
}

function serviceSchema({ name, description, slug, areaServed = 'PL' }) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Service',
    name,
    description,
    provider: ORGANIZATION,
    areaServed,
    serviceType: 'Product feed management',
    url: `${SITE}${slug}`,
  }
}

export const routes = [
  // ───────── Homepage ─────────
  {
    path: '/',
    title: 'Feedy — Zarządzaj feedami produktowymi z jednego miejsca',
    description: 'Generuj feedy XML dla Ceneo, Google Shopping, Allegro, Skąpiec i Facebook Catalog z jednego sklepu. Automatyczne mapowanie, walidacja i odświeżanie. Zacznij za darmo.',
    keywords: 'feed produktowy, feed ceneo, feed xml, google shopping feed, zarządzanie feedami, porównywarka cen, feed allegro, feed skąpiec, generator feedu xml, eksport produktów xml',
    canonical: `${SITE}/`,
    ogTitle: 'Feedy — Zarządzaj feedami produktowymi z jednego miejsca',
    ogDescription: 'Generuj feedy XML dla Ceneo, Google Shopping, Allegro. Automatyczne mapowanie, walidacja i odświeżanie. Zacznij za darmo.',
    jsonLd: [
      {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        name: 'Feedy',
        url: SITE,
        applicationCategory: 'BusinessApplication',
        operatingSystem: 'Web',
        description: 'Narzędzie do zarządzania feedami produktowymi dla e-commerce. Generuj feedy XML dla Ceneo, Google Shopping, Allegro i innych porównywarek.',
        offers: { '@type': 'Offer', price: '0', priceCurrency: 'PLN', description: 'Darmowy plan — 200 produktów, 1 feed wyjściowy' },
        aggregateRating: { '@type': 'AggregateRating', ratingValue: '4.8', ratingCount: '47', bestRating: '5' },
      },
      { '@context': 'https://schema.org', ...ORGANIZATION, description: 'Platforma do zarządzania feedami produktowymi dla e-commerce', contactPoint: { '@type': 'ContactPoint', email: 'kontakt@feedy.pl', contactType: 'customer service', availableLanguage: 'Polish' } },
      {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        mainEntity: [
          { '@type': 'Question', name: 'Czy Feedy działa z moim sklepem?', acceptedAnswer: { '@type': 'Answer', text: 'Feedy działa z każdym sklepem, który generuje XML z produktami — Shoper, WooCommerce, PrestaShop, Magento, Shopify i inne. Wystarczy wkleić link do XML.' } },
          { '@type': 'Question', name: 'Jak szybko feed się odświeża?', acceptedAnswer: { '@type': 'Answer', text: 'Możesz ustawić automatyczne odświeżanie co 1, 6 lub 24 godziny. Feed jest zawsze aktualny — ceny i dostępność synchronizują się automatycznie.' } },
          { '@type': 'Question', name: 'Czy mogę przetestować za darmo?', acceptedAnswer: { '@type': 'Answer', text: 'Tak! Plan Free pozwala na 200 produktów i 1 feed wyjściowy — bez karty kredytowej, bez limitu czasowego.' } },
          { '@type': 'Question', name: 'Ile kosztuje obsługa wielu porównywarek?', acceptedAnswer: { '@type': 'Answer', text: 'Nic dodatkowego! W przeciwieństwie do konkurencji, u nas wszystkie porównywarki są w cenie planu. Nie doliczamy za dodatkowe kanały.' } },
        ],
      },
    ],
    noscript: null, // homepage uses default noscript from index.html
  },

  // ───────── Blog list ─────────
  {
    path: '/blog',
    title: 'Blog Feedy — Poradniki o feedach produktowych XML | Ceneo, Google, Allegro',
    description: 'Praktyczne poradniki o feedach XML: jak skonfigurować feed Ceneo, Google Merchant Center, Allegro. Najczęstsze błędy, walidacja, optymalizacja jakości feedu.',
    keywords: 'blog feedy, poradnik feed xml, blog ceneo, blog google shopping, feed produktowy poradnik',
    canonical: `${SITE}/blog`,
    jsonLd: [
      breadcrumbSchema([{ name: 'Strona główna', path: '/' }, { name: 'Blog', path: '/blog' }]),
      { '@context': 'https://schema.org', '@type': 'Blog', name: 'Blog Feedy', url: `${SITE}/blog`, publisher: ORGANIZATION, inLanguage: 'pl-PL', description: 'Poradniki, instrukcje i nowości ze świata feedów produktowych' },
    ],
    noscript: `
      <h1>Blog Feedy — poradniki o feedach produktowych</h1>
      <p>Praktyczne poradniki dla właścicieli sklepów internetowych: jak stworzyć feed XML, skonfigurować Ceneo, Google Merchant Center i Allegro, jak naprawić odrzucone oferty i jak zwiększyć widoczność produktów w porównywarkach cen.</p>
      <h2>Najnowsze wpisy</h2>
      <ul>
        <li><a href="/blog/jak-dodac-produkty-do-ceneo">Jak dodać produkty do Ceneo — kompletny poradnik 2026</a> — krok po kroku konfiguracja feedu XML dla porównywarki Ceneo, wymagane pola, walidacja i automatyzacja.</li>
        <li><a href="/blog/jak-stworzyc-feed-xml">Jak stworzyć feed XML dla sklepu internetowego</a> — czym jest feed produktowy, jakie formaty istnieją, jak wybrać odpowiedni format dla Ceneo, Google Shopping i Allegro.</li>
        <li><a href="/blog/ceneo-odrzuca-oferty">Ceneo odrzuca oferty — jak naprawić feed?</a> — najczęstsze przyczyny odrzuceń, brak wymaganych pól, zły format ceny, nieprawidłowy EAN.</li>
      </ul>
      <h2>Tematy bloga</h2>
      <ul>
        <li>Feed Ceneo — konfiguracja, wymagane pola, mapowanie kategorii, walidacja</li>
        <li>Google Merchant Center — feed Atom, GTIN, atrybuty Google, optymalizacja</li>
        <li>Allegro — feed produktowy, integracja, mapowanie pól</li>
        <li>Skąpiec, Facebook Catalog, Domodi — pozostałe porównywarki</li>
        <li>Integracje — Shoper, WooCommerce, PrestaShop, Magento, Shopify</li>
        <li>Optymalizacja jakości feedu — opisy, zdjęcia, ceny, dostępność</li>
      </ul>
      <p><a href="/">Wróć na stronę główną</a> · <a href="/feed-ceneo">Feed Ceneo</a> · <a href="/feed-google-shopping">Feed Google Shopping</a> · <a href="/integracja-shoper">Integracja Shoper</a></p>
    `,
  },

  // ───────── Existing static blog articles ─────────
  {
    path: '/blog/jak-dodac-produkty-do-ceneo',
    title: 'Jak dodać produkty do Ceneo — kompletny poradnik 2026 | Feedy',
    description: 'Krok po kroku: jak skonfigurować feed XML dla Ceneo, jakie pola są wymagane, jak uniknąć odrzucenia ofert i automatycznie aktualizować dane produktowe.',
    keywords: 'jak dodać produkty do ceneo, feed ceneo, feed xml ceneo, ceneo wymagane pola, ceneo poradnik, dodawanie produktów ceneo',
    canonical: `${SITE}/blog/jak-dodac-produkty-do-ceneo`,
    ogType: 'article',
    jsonLd: [
      articleSchema({ title: 'Jak dodać produkty do Ceneo — kompletny poradnik 2026', description: 'Krok po kroku: jak skonfigurować feed XML dla Ceneo, jakie pola są wymagane, jak uniknąć odrzucenia ofert.', slug: '/blog/jak-dodac-produkty-do-ceneo' }),
      breadcrumbSchema([{ name: 'Strona główna', path: '/' }, { name: 'Blog', path: '/blog' }, { name: 'Jak dodać produkty do Ceneo', path: '/blog/jak-dodac-produkty-do-ceneo' }]),
    ],
    noscript: `
      <nav><a href="/blog">← Wróć do bloga</a></nav>
      <h1>Jak dodać produkty do Ceneo — kompletny poradnik 2026</h1>
      <p>Krok po kroku: jak stworzyć feed XML dla Ceneo, jakie pola są wymagane, jak uniknąć odrzucenia ofert i jak automatycznie aktualizować dane produktowe.</p>

      <h2>Czym jest feed produktowy Ceneo?</h2>
      <p>Feed produktowy Ceneo to plik XML zawierający informacje o produktach z Twojego sklepu internetowego. Ceneo pobiera ten plik i wyświetla Twoje oferty w wynikach porównywania cen. Feed XML jest standardowym formatem wymiany danych — Ceneo pobiera nową wersję pliku co kilka godzin, dzięki czemu ceny i dostępność produktów są zawsze aktualne.</p>

      <h2>Wymagane pola w feedzie Ceneo</h2>
      <h3>Pola obowiązkowe</h3>
      <ul>
        <li><strong>id</strong> — unikalny identyfikator produktu w Twoim sklepie</li>
        <li><strong>url</strong> — bezpośredni link do strony produktu</li>
        <li><strong>price</strong> — cena brutto w formacie numerycznym, bez waluty (np. 49.99, NIE 49.99 PLN)</li>
        <li><strong>avail</strong> — dostępność jako kod: 1 (dostępny), 3 (3 dni), 7 (7 dni), 14 (14 dni), 99 (na zamówienie)</li>
        <li><strong>name</strong> — pełna nazwa produktu z marką i kluczowymi cechami</li>
        <li><strong>cat</strong> — kategoria produktu z Twojego sklepu</li>
        <li><strong>desc</strong> — opis produktu</li>
      </ul>
      <h3>Pola zalecane (zwiększają widoczność)</h3>
      <ul>
        <li><strong>producer</strong> — marka / producent</li>
        <li><strong>code (EAN)</strong> — kod kreskowy EAN-13. Produkty z EAN są automatycznie dopasowywane do kart produktów na Ceneo</li>
        <li><strong>imgs</strong> — zdjęcie główne produktu</li>
        <li><strong>old_price</strong> — cena przed obniżką (wyświetla przekreśloną cenę)</li>
        <li><strong>shipping</strong> — koszt dostawy</li>
      </ul>

      <h2>Jak wygenerować feed XML automatycznie</h2>
      <p>Zamiast budować feed ręcznie, możesz użyć narzędzia takiego jak Feedy.pl. Wystarczy wkleić link do feedu z Twojego sklepu (Shoper, WooCommerce, PrestaShop, Magento, Shopify), wybrać szablon Ceneo i system automatycznie zmapuje wszystkie pola. Feed jest hostowany pod stałym URL-em, który można wkleić w panelu Ceneo.</p>

      <h2>Najczęstsze błędy</h2>
      <ul>
        <li>Cena z walutą („49.99 PLN") zamiast samej liczby</li>
        <li>Brak EAN — produkty bez kodu trafiają na słabsze pozycje</li>
        <li>Złe kody dostępności (powinno być 1/3/7/14/99)</li>
        <li>Niepoprawnie zakodowane znaki (UTF-8 jest wymagany)</li>
        <li>Zbyt długie nazwy produktów</li>
      </ul>

      <h2>Zobacz też</h2>
      <ul>
        <li><a href="/feed-ceneo">Generator feedu Ceneo — Feedy.pl</a></li>
        <li><a href="/blog/ceneo-odrzuca-oferty">Ceneo odrzuca oferty — jak naprawić feed?</a></li>
        <li><a href="/blog/jak-stworzyc-feed-xml">Jak stworzyć feed XML dla sklepu</a></li>
      </ul>
      <p><a href="/register">Załóż darmowe konto na Feedy.pl</a> i wygeneruj feed Ceneo w 5 minut.</p>
    `,
  },
  {
    path: '/blog/jak-stworzyc-feed-xml',
    title: 'Jak stworzyć feed XML dla sklepu internetowego — poradnik | Feedy',
    description: 'Czym jest feed produktowy, jakie formaty XML istnieją, jak wybrać odpowiedni dla Ceneo, Google Shopping i Allegro. Praktyczny poradnik dla właścicieli sklepów.',
    keywords: 'jak stworzyć feed xml, feed produktowy, formaty feedu xml, feed dla sklepu internetowego, generator feedu',
    canonical: `${SITE}/blog/jak-stworzyc-feed-xml`,
    ogType: 'article',
    jsonLd: [
      articleSchema({ title: 'Jak stworzyć feed XML dla sklepu internetowego', description: 'Czym jest feed produktowy, jakie formaty XML istnieją, jak wybrać odpowiedni dla porównywarek.', slug: '/blog/jak-stworzyc-feed-xml' }),
      breadcrumbSchema([{ name: 'Strona główna', path: '/' }, { name: 'Blog', path: '/blog' }, { name: 'Jak stworzyć feed XML', path: '/blog/jak-stworzyc-feed-xml' }]),
    ],
    noscript: `
      <nav><a href="/blog">← Wróć do bloga</a></nav>
      <h1>Jak stworzyć feed XML dla sklepu internetowego</h1>
      <p>Feed produktowy XML to plik zawierający dane o produktach Twojego sklepu w ustrukturyzowanej formie. Porównywarki cen i marketplace'y (Ceneo, Google Shopping, Allegro) pobierają ten plik i prezentują Twoje oferty użytkownikom.</p>

      <h2>Po co Ci feed XML?</h2>
      <ul>
        <li>Twoje produkty pojawiają się w Ceneo, Google Shopping, Allegro</li>
        <li>Ceny i dostępność synchronizują się automatycznie</li>
        <li>Nie musisz ręcznie dodawać produktów na każdej platformie</li>
        <li>Większa widoczność = więcej kliknięć i sprzedaży</li>
      </ul>

      <h2>Najpopularniejsze formaty</h2>
      <h3>Ceneo XML (offers/o)</h3>
      <p>Format używany przez Ceneo. Root element to <code>&lt;offers&gt;</code>, każdy produkt to <code>&lt;o&gt;</code> z atrybutami id, url, price, avail.</p>
      <h3>Google Merchant Center (Atom)</h3>
      <p>Standard Atom z namespace <code>g:</code>. Wymagane pola: g:id, title, description, link, g:price, g:image_link, g:availability, g:condition.</p>
      <h3>Allegro Product Feed</h3>
      <p>Format zbliżony do Google, ale ze specyficznymi polami: kategorie Allegro, parametry, warunki dostawy.</p>

      <h2>Trzy sposoby na zrobienie feedu</h2>
      <ol>
        <li><strong>Wbudowany w sklep</strong> — Shoper, WooCommerce (z wtyczką), PrestaShop generują feedy natywnie. Problem: tylko ich format, brak elastyczności.</li>
        <li><strong>Pisanie ręczne / skrypt</strong> — pełna kontrola, ale wymaga programisty i utrzymania.</li>
        <li><strong>Narzędzie typu Feedy.pl</strong> — pobiera Twój istniejący XML, transformuje na dowolny format, hostuje pod stałym URL-em. Bez programowania.</li>
      </ol>

      <h2>Zobacz też</h2>
      <ul>
        <li><a href="/blog/jak-dodac-produkty-do-ceneo">Jak dodać produkty do Ceneo</a></li>
        <li><a href="/feed-google-shopping">Feed Google Shopping</a></li>
        <li><a href="/feed-allegro">Feed Allegro</a></li>
        <li><a href="/integracja-shoper">Integracja z Shoperem</a></li>
      </ul>
    `,
  },
  {
    path: '/blog/ceneo-odrzuca-oferty',
    title: 'Ceneo odrzuca oferty — jak naprawić feed XML? | Feedy',
    description: 'Najczęstsze przyczyny odrzuceń ofert na Ceneo: brak wymaganych pól, zły format ceny, nieprawidłowy EAN. Jak je zdiagnozować i szybko naprawić.',
    keywords: 'ceneo odrzuca oferty, ceneo błędy feed, ceneo walidacja, ceneo nieprawidłowe pola, troubleshooting feed ceneo',
    canonical: `${SITE}/blog/ceneo-odrzuca-oferty`,
    ogType: 'article',
    jsonLd: [
      articleSchema({ title: 'Ceneo odrzuca oferty — jak naprawić feed?', description: 'Najczęstsze przyczyny odrzuceń ofert na Ceneo i jak je naprawić.', slug: '/blog/ceneo-odrzuca-oferty' }),
      breadcrumbSchema([{ name: 'Strona główna', path: '/' }, { name: 'Blog', path: '/blog' }, { name: 'Ceneo odrzuca oferty', path: '/blog/ceneo-odrzuca-oferty' }]),
    ],
    noscript: `
      <nav><a href="/blog">← Wróć do bloga</a></nav>
      <h1>Ceneo odrzuca oferty — jak naprawić feed?</h1>
      <p>Sprawdziliśmy najczęstsze powody, dla których Ceneo odrzuca oferty z Twojego feedu, i jak je szybko naprawić bez czekania na pomoc supportu.</p>

      <h2>Top 5 przyczyn odrzuceń</h2>
      <h3>1. Brak wymaganych pól</h3>
      <p>Każda oferta musi mieć: <code>id</code>, <code>url</code>, <code>price</code>, <code>avail</code>, <code>name</code>, <code>cat</code>, <code>desc</code>. Brak któregokolwiek = odrzucenie.</p>
      <h3>2. Zły format ceny</h3>
      <p>Cena to surowa liczba: <code>49.99</code>, NIE <code>49.99 PLN</code>, NIE <code>49,99</code> (Ceneo wymaga kropki). Bez waluty, bez znaków specjalnych.</p>
      <h3>3. Nieprawidłowy EAN</h3>
      <p>EAN-13 powinien mieć dokładnie 13 cyfr i poprawną sumę kontrolną. Złe EAN-y są ignorowane (oferta wchodzi, ale bez dopasowania do karty produktu).</p>
      <h3>4. Niepoprawny kod dostępności</h3>
      <p>Ceneo oczekuje kodu liczbowego: <code>1</code> (dostępny), <code>3</code>, <code>7</code>, <code>14</code> (dni), <code>99</code> (na zamówienie). Wartości typu „in stock" są odrzucane.</p>
      <h3>5. Encoding problems</h3>
      <p>Plik musi być w UTF-8. Polskie znaki zakodowane jako Windows-1250 lub ISO-8859-2 powodują błędy parsowania.</p>

      <h2>Jak szybko zdiagnozować problem?</h2>
      <p>Feedy.pl ma wbudowany Quality Score — automatycznie sprawdza Twój feed pod kątem brakujących pól, niepoprawnych formatów i innych typowych błędów. Otrzymujesz listę problemów z konkretnym produktem i polem.</p>

      <h2>Zobacz też</h2>
      <ul>
        <li><a href="/blog/jak-dodac-produkty-do-ceneo">Jak dodać produkty do Ceneo</a></li>
        <li><a href="/feed-ceneo">Generator feedu Ceneo</a></li>
      </ul>
    `,
  },

  // ───────── SEO landings: feed-ceneo ─────────
  {
    path: '/feed-ceneo',
    title: 'Feed Ceneo XML — generator i automatyzacja w 5 minut | Feedy.pl',
    description: 'Wygeneruj feed XML dla Ceneo z dowolnego sklepu (Shoper, WooCommerce, PrestaShop). Automatyczne mapowanie pól, walidacja i hosting pod stałym URL. Plan darmowy.',
    keywords: 'feed ceneo, generator feed ceneo, feed xml ceneo, ceneo automatyzacja, ceneo integracja, eksport produktów ceneo',
    canonical: `${SITE}/feed-ceneo`,
    jsonLd: [
      serviceSchema({ name: 'Generator feedu Ceneo', description: 'Generowanie i hosting feedów XML dla porównywarki Ceneo z dowolnego sklepu internetowego.', slug: '/feed-ceneo' }),
      breadcrumbSchema([{ name: 'Strona główna', path: '/' }, { name: 'Feed Ceneo', path: '/feed-ceneo' }]),
    ],
    noscript: `
      <h1>Feed Ceneo XML — generator i automatyzacja</h1>
      <p>Feedy.pl pozwala wygenerować feed produktowy dla Ceneo z dowolnego sklepu internetowego — bez programowania, w 5 minut. Wystarczy wkleić link do XML-a Twojego sklepu, wybrać szablon Ceneo i otrzymujesz gotowy feed pod stałym URL-em.</p>

      <h2>Jak to działa</h2>
      <ol>
        <li>Wklej link do XML-a Twojego sklepu (Shoper, WooCommerce, PrestaShop, Magento, Shopify lub dowolny inny)</li>
        <li>Wybierz szablon „Ceneo" — system automatycznie zmapuje pola id, url, price, avail, name, cat, desc, EAN</li>
        <li>Skopiuj wygenerowany URL feedu i wklej w panelu Ceneo</li>
        <li>Feed odświeża się automatycznie co 1, 6 lub 24 godziny</li>
      </ol>

      <h2>Co zawiera nasz feed Ceneo</h2>
      <ul>
        <li>Wszystkie pola wymagane przez Ceneo: id, url, price, avail, name, cat, desc</li>
        <li>Pola zalecane: producer, EAN (code), imgs (zdjęcie główne), old_price, shipping</li>
        <li>Mapowanie kategorii Twojego sklepu → kategorie Ceneo (z autosugestiami)</li>
        <li>Wbudowana walidacja — wykryjemy braki przed wysłaniem do Ceneo</li>
        <li>Quality Score — wskaźnik jakości feedu z konkretnymi rekomendacjami</li>
        <li>Automatyczny format ceny (kropka jako separator dziesiętny)</li>
        <li>Mapowanie kodów dostępności (in stock → 1, out of stock → 99)</li>
      </ul>

      <h2>Dlaczego Feedy.pl, a nie wbudowane narzędzie sklepu?</h2>
      <ul>
        <li>Pełna kontrola nad mapowaniem każdego pola</li>
        <li>Override per produkt — zmień dane konkretnej oferty bez ruszania feedu źródłowego</li>
        <li>Reguły filtrowania — wyklucz produkty bez EAN, bez zdjęć, niezgodne z polityką Ceneo</li>
        <li>AI optymalizacja opisów — przepisanie krótkich/słabych opisów</li>
        <li>Historia zmian (changelog) — zobacz co się zmieniło między aktualizacjami</li>
      </ul>

      <h2>Cennik</h2>
      <ul>
        <li><strong>Free</strong> — 200 produktów, 1 feed Ceneo, na zawsze za darmo</li>
        <li><strong>Starter — 49 zł/mies.</strong> — 1 000 produktów, 3 feedy</li>
        <li><strong>Pro — 149 zł/mies.</strong> — 10 000 produktów, 10 feedów, AI opisy, walidacja</li>
        <li><strong>Business — 349 zł/mies.</strong> — 50 000 produktów, white-label</li>
      </ul>

      <p><a href="/register">Załóż darmowe konto i wygeneruj feed Ceneo</a></p>
      <h2>Zobacz też</h2>
      <p><a href="/blog/jak-dodac-produkty-do-ceneo">Jak dodać produkty do Ceneo (poradnik)</a> · <a href="/blog/ceneo-odrzuca-oferty">Ceneo odrzuca oferty — jak naprawić</a> · <a href="/feed-google-shopping">Feed Google Shopping</a> · <a href="/feed-allegro">Feed Allegro</a></p>
    `,
  },

  // ───────── SEO landings: feed-google-shopping ─────────
  {
    path: '/feed-google-shopping',
    title: 'Feed Google Shopping (Merchant Center) — generator XML | Feedy.pl',
    description: 'Generator feedu dla Google Merchant Center z Twojego sklepu. Format Atom z g: namespace, GTIN, atrybuty Google, automatyczna walidacja. Plan darmowy.',
    keywords: 'feed google shopping, google merchant center, feed gmc, google shopping xml, atom feed google, integracja google shopping',
    canonical: `${SITE}/feed-google-shopping`,
    jsonLd: [
      serviceSchema({ name: 'Generator feedu Google Merchant Center', description: 'Generowanie i hosting feedów Atom XML dla Google Merchant Center.', slug: '/feed-google-shopping' }),
      breadcrumbSchema([{ name: 'Strona główna', path: '/' }, { name: 'Feed Google Shopping', path: '/feed-google-shopping' }]),
    ],
    noscript: `
      <h1>Feed Google Shopping — generator dla Merchant Center</h1>
      <p>Feedy.pl generuje feed produktowy w formacie Atom XML dla Google Merchant Center, zgodny ze wszystkimi wymaganiami Google. Twój sklep pojawi się w wynikach Google Shopping, w karuzelach produktowych i w wyszukiwaniu obrazem.</p>

      <h2>Wymagania Google Merchant Center</h2>
      <ul>
        <li><strong>g:id</strong> — unikalny SKU produktu</li>
        <li><strong>title</strong> — pełna nazwa produktu (max 150 znaków)</li>
        <li><strong>description</strong> — opis (max 5000 znaków)</li>
        <li><strong>link</strong> — URL strony produktu</li>
        <li><strong>g:image_link</strong> — URL głównego zdjęcia (min 100x100 px)</li>
        <li><strong>g:price</strong> — cena z walutą (np. „49.99 PLN")</li>
        <li><strong>g:availability</strong> — „in stock", „out of stock", „preorder"</li>
        <li><strong>g:condition</strong> — „new", „used", „refurbished"</li>
        <li><strong>g:gtin</strong> — kod GTIN/EAN (zalecane dla produktów z markami)</li>
        <li><strong>g:brand</strong> — marka producenta</li>
        <li><strong>g:google_product_category</strong> — kategoria z taksonomii Google</li>
      </ul>

      <h2>Co dostajesz w Feedy.pl</h2>
      <ul>
        <li>Automatyczne mapowanie pól z Twojego źródłowego XML na format GMC</li>
        <li>Wbudowana taksonomia Google (PL, 56+ kategorii)</li>
        <li>Walidator zgodności z polityką Google — wykryje brakujące GTIN, błędne wartości availability/condition</li>
        <li>Quality Score z rekomendacjami</li>
        <li>Auto-refresh feedu (Google rekomenduje codziennie)</li>
        <li>Override per produkt — popraw konkretny produkt bez ruszania pozostałych</li>
        <li>AI optymalizacja tytułów (Google waży tytuły wysoko)</li>
      </ul>

      <h2>Dlaczego warto być w Google Shopping?</h2>
      <ul>
        <li>Karuzele produktowe wyświetlane nad wynikami organicznymi</li>
        <li>Wyszukiwanie obrazem — produkty pojawiają się przy zapytaniach wizualnych</li>
        <li>Free listings — od 2020 darmowa ekspozycja w zakładce Zakupy</li>
        <li>Performance Max kampanie reklamowe — feed jest podstawą</li>
      </ul>

      <p><a href="/register">Załóż darmowe konto i wygeneruj feed GMC</a></p>
      <h2>Zobacz też</h2>
      <p><a href="/feed-ceneo">Feed Ceneo</a> · <a href="/feed-allegro">Feed Allegro</a> · <a href="/integracja-shoper">Integracja Shoper</a> · <a href="/integracja-woocommerce">Integracja WooCommerce</a></p>
    `,
  },

  // ───────── SEO landings: feed-allegro ─────────
  {
    path: '/feed-allegro',
    title: 'Feed Allegro — automatyczny eksport produktów do Allegro | Feedy.pl',
    description: 'Generuj feed produktowy dla Allegro z Shopera, WooCommerce, PrestaShop, Magento. Automatyczne mapowanie kategorii, parametrów i obsługa wariantów. Plan darmowy.',
    keywords: 'feed allegro, allegro xml, allegro automatyzacja, eksport allegro, integracja allegro, allegro produkty xml',
    canonical: `${SITE}/feed-allegro`,
    jsonLd: [
      serviceSchema({ name: 'Generator feedu Allegro', description: 'Eksport produktów ze sklepu internetowego do Allegro przez feed XML.', slug: '/feed-allegro' }),
      breadcrumbSchema([{ name: 'Strona główna', path: '/' }, { name: 'Feed Allegro', path: '/feed-allegro' }]),
    ],
    noscript: `
      <h1>Feed Allegro — eksport produktów do Allegro</h1>
      <p>Feedy.pl pozwala wygenerować feed XML dla Allegro z Twojego sklepu internetowego. Pobieramy istniejący XML (Shoper, WooCommerce, PrestaShop, Magento, Shopify), transformujemy na format Allegro i hostujemy pod stałym URL-em.</p>

      <h2>Jakie pola zawiera feed Allegro</h2>
      <ul>
        <li>id, name, description, url</li>
        <li>price (z mapowaniem do PLN)</li>
        <li>category (mapowanie na kategorie Allegro)</li>
        <li>image — zdjęcie główne</li>
        <li>availability — dostępność</li>
        <li>brand — marka</li>
        <li>ean — kod kreskowy</li>
        <li>condition — stan (domyślnie „new")</li>
      </ul>

      <h2>Funkcje Feedy.pl dla Allegro</h2>
      <ul>
        <li>Automatyczne mapowanie kategorii Twojego sklepu na Allegro</li>
        <li>Reguły filtrowania — wyklucz produkty niezgodne z regulaminem Allegro</li>
        <li>Override per oferta — popraw nazwę, opis lub cenę bez ruszania źródła</li>
        <li>Auto-refresh — feed aktualizuje się automatycznie</li>
        <li>Walidacja — sprawdza wymagane pola przed wysłaniem</li>
      </ul>

      <p><a href="/register">Załóż darmowe konto na Feedy.pl</a></p>
      <h2>Zobacz też</h2>
      <p><a href="/feed-ceneo">Feed Ceneo</a> · <a href="/feed-google-shopping">Feed Google Shopping</a> · <a href="/integracja-shoper">Integracja Shoper</a></p>
    `,
  },

  // ───────── SEO landings: integracja-shoper ─────────
  {
    path: '/integracja-shoper',
    title: 'Integracja Shoper z Ceneo, Google, Allegro przez feed XML | Feedy.pl',
    description: 'Połącz sklep Shoper z porównywarkami: Ceneo, Google Shopping, Allegro, Skąpiec, Facebook. Pobieramy XML z Shopera i generujemy feedy dla każdej platformy.',
    keywords: 'integracja shoper, shoper ceneo, shoper google shopping, shoper allegro, shoper xml, feed shoper',
    canonical: `${SITE}/integracja-shoper`,
    jsonLd: [
      serviceSchema({ name: 'Integracja Shoper z porównywarkami', description: 'Eksport produktów ze sklepu Shoper do Ceneo, Google Shopping, Allegro przez feed XML.', slug: '/integracja-shoper' }),
      breadcrumbSchema([{ name: 'Strona główna', path: '/' }, { name: 'Integracja Shoper', path: '/integracja-shoper' }]),
    ],
    noscript: `
      <h1>Integracja Shoper z porównywarkami przez feed XML</h1>
      <p>Masz sklep na Shoperze i chcesz dodać produkty do Ceneo, Google Shopping, Allegro, Skąpca albo Facebooka? Feedy.pl pobiera feed XML z Twojego sklepu Shoper i generuje feedy dla każdej porównywarki.</p>

      <h2>Jak to działa krok po kroku</h2>
      <ol>
        <li>W panelu Shopera włącz eksport feedu XML (np. CeneoV2, dostępny w sekcji Integracje)</li>
        <li>Skopiuj URL feedu z Shopera (wygląda jak <code>https://twojsklep.shoparena.pl/console/integration/execute/name/CeneoV2</code>)</li>
        <li>Wklej URL w Feedy.pl jako źródło feedu wejściowego</li>
        <li>Wybierz porównywarkę docelową (Ceneo, Google Shopping, Allegro, Skąpiec, Facebook, Domodi)</li>
        <li>Otrzymujesz wygenerowany feed pod stałym URL-em — wklej go w panelu porównywarki</li>
      </ol>

      <h2>Dlaczego Feedy.pl, a nie wbudowane integracje Shopera?</h2>
      <ul>
        <li>Shoper generuje feedy w jednym formacie — Feedy transformuje je na dowolny inny</li>
        <li>Override per produkt — popraw nazwę/opis/cenę konkretnej oferty bez ruszania danych w sklepie</li>
        <li>Walidacja przed wysłaniem — wykryjemy braki przed Ceneo/Google</li>
        <li>Reguły filtrowania — wyklucz produkty bez EAN, bez zdjęć, z określonej kategorii</li>
        <li>AI opisy — przepisanie krótkich lub słabych opisów</li>
        <li>Wszystkie porównywarki w jednym panelu — bez wielu oddzielnych integracji</li>
      </ul>

      <h2>Obsługujemy</h2>
      <ul>
        <li>Feedy CeneoV2, Google Merchant, Allegro, Skąpiec, Facebook Catalog, Domodi z Shopera</li>
        <li>Custom XML — jeśli Shoper generuje nietypowy feed</li>
        <li>Wszystkie kategorie produktowe Shopera</li>
      </ul>

      <p><a href="/register">Załóż darmowe konto i połącz Shopera w 5 minut</a></p>
      <h2>Zobacz też</h2>
      <p><a href="/integracja-woocommerce">Integracja WooCommerce</a> · <a href="/feed-ceneo">Feed Ceneo</a> · <a href="/feed-google-shopping">Feed Google Shopping</a></p>
    `,
  },

  // ───────── SEO landings: integracja-woocommerce ─────────
  {
    path: '/integracja-woocommerce',
    title: 'Integracja WooCommerce z Ceneo, Google, Allegro przez feed XML | Feedy.pl',
    description: 'Połącz sklep WooCommerce z porównywarkami: Ceneo, Google Shopping, Allegro, Skąpiec, Facebook. Bez wtyczek, automatyczne odświeżanie. Plan darmowy.',
    keywords: 'integracja woocommerce, woocommerce ceneo, woocommerce google shopping, woocommerce allegro, woocommerce xml, feed woocommerce',
    canonical: `${SITE}/integracja-woocommerce`,
    jsonLd: [
      serviceSchema({ name: 'Integracja WooCommerce z porównywarkami', description: 'Eksport produktów z WooCommerce do Ceneo, Google Shopping, Allegro przez feed XML.', slug: '/integracja-woocommerce' }),
      breadcrumbSchema([{ name: 'Strona główna', path: '/' }, { name: 'Integracja WooCommerce', path: '/integracja-woocommerce' }]),
    ],
    noscript: `
      <h1>Integracja WooCommerce z porównywarkami</h1>
      <p>Masz sklep na WooCommerce (WordPress) i chcesz wystawiać produkty na Ceneo, Google Shopping, Allegro? Feedy.pl jest najprostszym sposobem — bez instalacji wtyczek, bez modyfikacji motywu.</p>

      <h2>Jak to działa</h2>
      <ol>
        <li>Zainstaluj prostą wtyczkę feed XML w WooCommerce (np. Product Feed PRO, WooCommerce Google Product Feed) lub użyj wbudowanego eksportu</li>
        <li>Skopiuj URL wygenerowanego feedu</li>
        <li>Wklej go w Feedy.pl jako źródło</li>
        <li>Wybierz format docelowy: Ceneo, Google Merchant Center, Allegro, Skąpiec, Facebook</li>
        <li>Otrzymujesz wygenerowany feed pod stałym URL-em do wklejenia w panelu porównywarki</li>
      </ol>

      <h2>Dlaczego nie sama wtyczka WooCommerce?</h2>
      <ul>
        <li>Wtyczki WooCommerce zwykle generują tylko 1-2 formaty</li>
        <li>Brak walidacji błędów przed wysłaniem do porównywarki</li>
        <li>Brak override per produkt</li>
        <li>Brak Quality Score i AI opisów</li>
        <li>Każda dodatkowa wtyczka spowalnia sklep</li>
      </ul>

      <h2>Co zyskujesz w Feedy.pl</h2>
      <ul>
        <li>1 sklep WooCommerce → 6 porównywarek (Ceneo, Google, Allegro, Skąpiec, Facebook, Domodi)</li>
        <li>Jedno miejsce do zarządzania wszystkimi feedami</li>
        <li>Walidacja każdego feedu z konkretnymi błędami i ostrzeżeniami</li>
        <li>Auto-refresh — feedy aktualizują się automatycznie</li>
      </ul>

      <p><a href="/register">Załóż darmowe konto na Feedy.pl</a></p>
      <h2>Zobacz też</h2>
      <p><a href="/integracja-shoper">Integracja Shoper</a> · <a href="/feed-ceneo">Feed Ceneo</a> · <a href="/feed-google-shopping">Feed Google Shopping</a></p>
    `,
  },

  // ───────── Comparison landing ─────────
  {
    path: '/porownanie/feedy-vs-datafeedwatch',
    title: 'Feedy.pl vs DataFeedWatch — porównanie cen i funkcji 2026 | Feedy.pl',
    description: 'Porównanie Feedy.pl i DataFeedWatch: ceny, funkcje, integracje, wsparcie. Sprawdź dlaczego Feedy.pl jest 5x tańsze i ma polski interfejs.',
    keywords: 'feedy vs datafeedwatch, porównanie feedy, datafeedwatch alternatywa, tańszy datafeedwatch, polski datafeedwatch',
    canonical: `${SITE}/porownanie/feedy-vs-datafeedwatch`,
    jsonLd: [
      breadcrumbSchema([{ name: 'Strona główna', path: '/' }, { name: 'Porównania', path: '/porownanie/feedy-vs-datafeedwatch' }, { name: 'Feedy vs DataFeedWatch', path: '/porownanie/feedy-vs-datafeedwatch' }]),
    ],
    noscript: `
      <h1>Feedy.pl vs DataFeedWatch — porównanie 2026</h1>
      <p>Szukasz polskiej alternatywy dla DataFeedWatch? Feedy.pl oferuje te same funkcje, polski interfejs i jest <strong>5x tańszy</strong>.</p>

      <h2>Cennik — porównanie</h2>
      <ul>
        <li>DataFeedWatch — od ~280 zł/mies. (1 000 produktów)</li>
        <li>Feedy.pl — od 49 zł/mies. (1 000 produktów) lub <strong>0 zł</strong> dla 200 produktów na zawsze</li>
      </ul>

      <h2>Funkcje — co dostajesz</h2>
      <ul>
        <li>Pobieranie XML z dowolnego sklepu — ✓ Feedy ✓ DataFeedWatch</li>
        <li>Szablony Ceneo, Google, Allegro, Skąpiec, Facebook, Domodi — ✓ Feedy (w cenie planu) — DataFeedWatch dolicza za kanały</li>
        <li>Reguły filtrowania i transformacji — ✓ obie</li>
        <li>Walidacja feedu — ✓ Feedy z Quality Score — DataFeedWatch ma podstawową</li>
        <li>Polski interfejs — ✓ Feedy — DataFeedWatch tylko EN</li>
        <li>Polski support — ✓ Feedy — DataFeedWatch EN</li>
        <li>AI optymalizacja opisów — ✓ Feedy (Pro plan) — DataFeedWatch nie ma</li>
        <li>Override per produkt — ✓ obie</li>
        <li>Mapowanie kategorii Google PL — ✓ Feedy z autosugestiami</li>
      </ul>

      <h2>Dla kogo Feedy?</h2>
      <ul>
        <li>Polskie sklepy internetowe</li>
        <li>Sprzedawcy startujący z Ceneo (kluczowy kanał w Polsce)</li>
        <li>Sklepy z budżetem do ~500 zł/mies. na narzędzia</li>
        <li>Każdy kto chce polski interfejs i polski support</li>
      </ul>

      <h2>Dla kogo DataFeedWatch?</h2>
      <ul>
        <li>Międzynarodowe sklepy z setkami tysięcy produktów</li>
        <li>Firmy z dużym budżetem i wielojęzycznym zespołem</li>
      </ul>

      <p><a href="/register">Wypróbuj Feedy.pl za darmo</a> — bez karty kredytowej, bez limitu czasowego.</p>
      <h2>Zobacz też</h2>
      <p><a href="/feed-ceneo">Feed Ceneo</a> · <a href="/feed-google-shopping">Feed Google Shopping</a> · <a href="/oferty/cennik">Cennik</a></p>
    `,
  },

  // ───────── Pricing for landing pages product ─────────
  {
    path: '/oferty/cennik',
    title: 'Cennik stron ofert — landing pages dla Twoich produktów | Feedy.pl',
    description: 'Publikuj swoje produkty i usługi na feedy.pl. Pakiety od 1 produktu (darmo 3 mies.) do 500+. Każda oferta ma własny landing z SEO, CTA i lokalizacją.',
    keywords: 'landing pages produktów, strony ofert, cennik feedy, publikacja produktów online, marketplace feedy',
    canonical: `${SITE}/oferty/cennik`,
    jsonLd: [
      breadcrumbSchema([{ name: 'Strona główna', path: '/' }, { name: 'Oferty', path: '/oferty' }, { name: 'Cennik', path: '/oferty/cennik' }]),
      {
        '@context': 'https://schema.org',
        '@type': 'OfferCatalog',
        name: 'Pakiety stron ofert Feedy.pl',
        itemListElement: [
          { '@type': 'Offer', name: '1 produkt', price: '10', priceCurrency: 'PLN', description: 'Darmo 3 miesiące, potem 10 zł/mies.' },
          { '@type': 'Offer', name: '2-5 produktów', price: '25', priceCurrency: 'PLN', description: '25 zł miesięcznie' },
          { '@type': 'Offer', name: '6-25 produktów', price: '50', priceCurrency: 'PLN', description: '50 zł miesięcznie' },
          { '@type': 'Offer', name: '26-100 produktów', price: '100', priceCurrency: 'PLN', description: '100 zł miesięcznie' },
          { '@type': 'Offer', name: '101-500 produktów', price: '250', priceCurrency: 'PLN', description: '250 zł miesięcznie' },
        ],
      },
    ],
    noscript: `
      <h1>Cennik stron ofert na Feedy.pl</h1>
      <p>Publikuj swoje produkty i usługi na feedy.pl — każda oferta dostaje własny landing page z SEO, galerią, lokalizacją i przyciskiem CTA prowadzącym do Twojego sklepu.</p>

      <h2>Pakiety produktów</h2>
      <ul>
        <li><strong>1 produkt</strong> — darmo 3 miesiące, potem 10 zł/mies.</li>
        <li><strong>2-5 produktów</strong> — 25 zł/mies.</li>
        <li><strong>6-25 produktów</strong> — 50 zł/mies.</li>
        <li><strong>26-100 produktów</strong> — 100 zł/mies.</li>
        <li><strong>101-500 produktów</strong> — 250 zł/mies.</li>
        <li><strong>Powyżej 500</strong> — kontakt mailowy</li>
      </ul>

      <h2>Wpis blogowy</h2>
      <p><strong>1 wpis blogowy gratis przez 1 miesiąc</strong> do każdego aktywnego pakietu. Powyżej — 20 zł/mies. za każdy dodatkowy wpis blogowy.</p>

      <h2>Co dostajesz</h2>
      <ul>
        <li>Każda oferta dostaje własny landing page z H1, galerią do 10 zdjęć, CTA i SEO</li>
        <li>Link wyjściowy z rel="ugc sponsored nofollow noopener"</li>
        <li>Pełna kontrola nad tytułem, slug, meta tagami, indeksowalnością</li>
        <li>Lokalizacja + cena lub „do wyceny indywidualnej"</li>
      </ul>

      <p><a href="/register">Załóż konto i dodaj pierwszą ofertę</a></p>
      <h2>Zobacz też</h2>
      <p><a href="/feed-ceneo">Feed Ceneo</a> · <a href="/blog">Blog</a> · <a href="/">Strona główna</a></p>
    `,
  },

  // ───────── noindex pages (auth) ─────────
  {
    path: '/login',
    title: 'Zaloguj się — Feedy.pl',
    description: 'Zaloguj się do Feedy.pl, aby zarządzać feedami produktowymi.',
    canonical: `${SITE}/login`,
    robots: 'noindex, nofollow',
    jsonLd: [],
    noscript: `<h1>Zaloguj się</h1><p><a href="/">Strona główna</a></p>`,
  },
  {
    path: '/register',
    title: 'Załóż konto — Feedy.pl',
    description: 'Załóż darmowe konto Feedy.pl i zarządzaj feedami produktowymi dla Ceneo, Google Shopping i Allegro.',
    canonical: `${SITE}/register`,
    jsonLd: [],
    noscript: `<h1>Załóż darmowe konto na Feedy.pl</h1><p>Zarządzaj feedami produktowymi dla Ceneo, Google Shopping, Allegro w jednym panelu. Plan Free na zawsze, bez karty kredytowej.</p><p><a href="/">Strona główna</a></p>`,
  },
]
