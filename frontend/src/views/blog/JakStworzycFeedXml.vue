<template>
  <div class="min-h-screen bg-white">
    <article class="max-w-3xl mx-auto px-4 py-16">
      <div class="mb-10">
        <router-link to="/blog" class="text-sm text-indigo-600 hover:text-indigo-800 mb-4 inline-block">&larr; Wróć do bloga</router-link>
        <div class="flex items-center gap-2 text-xs text-gray-400 mb-4">
          <span>11 kwietnia 2026</span><span>·</span><span>8 min czytania</span>
        </div>
        <h1 class="font-heading text-3xl sm:text-4xl font-extrabold text-gray-900 leading-tight">Jak stworzyć feed XML dla sklepu internetowego</h1>
        <p class="mt-4 text-lg text-gray-600">Czym jest feed produktowy, jakie formaty istnieją i jak wybrać odpowiedni dla Twojej porównywarki.</p>
      </div>
      <div class="prose prose-gray max-w-none">
        <h2 class="font-heading">Czym jest feed produktowy?</h2>
        <p>Feed produktowy (ang. product feed) to ustrukturyzowany plik zawierający informacje o produktach z Twojego sklepu internetowego. Najczęściej ma format XML lub CSV. Porównywarki cen (Ceneo, Google Shopping, Skąpiec) i marketplace'y (Allegro, Facebook) pobierają ten plik, aby wyświetlać Twoje produkty w swoich wynikach.</p>
        <p>Feed jest mostem między Twoim sklepem a platformami sprzedażowymi. Im lepiej przygotowany feed, tym więcej klientów znajdzie Twoje produkty.</p>

        <h2 class="font-heading">Formaty feedów XML — który wybrać?</h2>
        <p>Każda platforma ma własny format feedu. Oto najważniejsze:</p>

        <h3>Ceneo XML</h3>
        <p>Format z elementami <code>&lt;o&gt;</code> (oferta) i atrybutami: id, url, price, avail. Cena <strong>bez waluty</strong>. Używany przez Ceneo.pl — największą porównywarkę cen w Polsce.</p>

        <h3>Google Merchant Center (Atom XML)</h3>
        <p>Format Atom z namespace <code>g:</code>. Cena <strong>z walutą</strong> (np. "29.99 PLN"). Wymagany przez Google Shopping. Meta/Facebook też akceptuje ten format.</p>

        <h3>Skąpiec XML</h3>
        <p>Format z elementami <code>&lt;offer&gt;</code> i child elementami (id, name, url, price). Podobny do Ceneo ale z inną strukturą. Cena bez waluty.</p>

        <h3>Allegro</h3>
        <p>Allegro używa REST API, nie tradycyjnych feedów XML. Jednak feedy XML są przydatne do przygotowania danych przed importem przez integrację.</p>

        <h2 class="font-heading">Jak stworzyć feed XML?</h2>
        <h3>Opcja 1: Eksport z platformy e-commerce</h3>
        <p>Większość platform (Shoper, WooCommerce, PrestaShop, Magento, Shopify) ma wbudowany eksport XML lub oferuje wtyczki do generowania feedów. To najszybszy sposób.</p>

        <h3>Opcja 2: Narzędzie do zarządzania feedami</h3>
        <p>Narzędzia takie jak <a href="https://feedy.pl" class="text-indigo-600 font-semibold">Feedy</a> pobierają XML z Twojego sklepu i automatycznie transformują go do formatu wymaganego przez różne porównywarki. Jedno źródło danych — wiele formatów wyjściowych.</p>

        <h3>Opcja 3: Ręczne tworzenie XML</h3>
        <p>Dla małych sklepów z kilkoma produktami można stworzyć XML ręcznie. Nie jest to jednak zalecane dla większej liczby produktów — zbyt czasochłonne i podatne na błędy.</p>

        <h2 class="font-heading">Podsumowanie</h2>
        <p>Feed produktowy XML to fundament sprzedaży przez porównywarki cen. Wybierz format odpowiedni dla platformy docelowej, zadbaj o wymagane pola i regularnie aktualizuj dane. Narzędzia takie jak Feedy automatyzują cały proces.</p>
        <p class="mt-6"><router-link to="/register" class="inline-flex items-center px-6 py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition">Wypróbuj Feedy za darmo</router-link></p>
      </div>
    </article>
  </div>
</template>
