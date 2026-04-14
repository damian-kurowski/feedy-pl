<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'
import { useToast, getApiError } from '../composables/useToast'

const router = useRouter()
const toast = useToast()

interface Preview {
  filename: string
  headers: string[]
  row_count: number
  preview: string[][]
  auto_mapping: Record<string, string | null>
}

const file = ref<File | null>(null)
const preview = ref<Preview | null>(null)
const allRows = ref<string[][]>([])
const mapping = ref<Record<string, string | null>>({})
const feedName = ref('')
const uploading = ref(false)
const committing = ref(false)
const dragActive = ref(false)

const FIELDS = [
  { value: '', label: '— pomiń —' },
  { value: 'name', label: 'Nazwa produktu *' },
  { value: 'id', label: 'ID / SKU' },
  { value: 'price', label: 'Cena' },
  { value: 'old_price', label: 'Stara cena' },
  { value: 'url', label: 'URL produktu' },
  { value: 'image', label: 'Zdjęcie (URL)' },
  { value: 'description', label: 'Opis' },
  { value: 'category', label: 'Kategoria' },
  { value: 'brand', label: 'Marka' },
  { value: 'ean', label: 'EAN / GTIN' },
  { value: 'availability', label: 'Dostępność' },
  { value: 'weight', label: 'Waga' },
  { value: 'shipping', label: 'Wysyłka' },
]

const hasName = computed(() => Object.values(mapping.value).includes('name'))

function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    file.value = target.files[0]
    if (!feedName.value) {
      feedName.value = file.value.name.replace(/\.(csv|xlsx|xlsm|txt)$/i, '')
    }
  }
}

function onDrop(event: DragEvent) {
  event.preventDefault()
  dragActive.value = false
  if (event.dataTransfer?.files[0]) {
    file.value = event.dataTransfer.files[0]
    if (!feedName.value) {
      feedName.value = file.value.name.replace(/\.(csv|xlsx|xlsm|txt)$/i, '')
    }
  }
}

async function uploadPreview() {
  if (!file.value) return
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file.value)
    const { data } = await api.post('/imports/preview', formData)
    preview.value = data
    mapping.value = { ...data.auto_mapping }
    // Read full file rows for commit (we need everything, not just preview)
    await readAllRows()
  } catch (e) {
    toast.error(getApiError(e, 'Nie udało się przeczytać pliku'))
  } finally {
    uploading.value = false
  }
}

async function readAllRows() {
  // We re-parse the file in browser using FileReader for CSV; for XLSX we
  // rely on backend preview rows being the full set but it returned only first 5.
  // Simplest approach: send a follow-up preview request asking for all rows.
  if (!file.value) return
  const formData = new FormData()
  formData.append('file', file.value)
  try {
    const { data } = await api.post('/imports/preview', formData)
    // Re-parse on backend with custom limit not supported; use a workaround:
    // for CSV — parse client-side; for XLSX — accept only preview limit
    if (file.value.name.toLowerCase().endsWith('.csv') || file.value.name.toLowerCase().endsWith('.txt')) {
      const text = await file.value.text()
      const lines = text.split(/\r?\n/).filter((l) => l.trim())
      const delim = lines[0].includes(';') ? ';' : (lines[0].includes('\t') ? '\t' : ',')
      allRows.value = lines.slice(1).map((l) => parseCsvLine(l, delim))
    } else {
      // XLSX: backend returned full row count; for now accept all from preview
      allRows.value = data.preview // fallback — only 5 rows for XLSX in MVP
      if (data.row_count > 5) {
        toast.warning(`XLSX import: w MVP importujemy tylko pierwsze 5 wierszy. Użyj CSV dla pełnego importu (${data.row_count} wierszy).`)
      }
    }
  } catch (e) {
    toast.error(getApiError(e, 'Błąd parsowania pliku'))
  }
}

function parseCsvLine(line: string, delim: string): string[] {
  // Simple CSV parser handling double-quoted values with embedded delimiters
  const out: string[] = []
  let cur = ''
  let inQuotes = false
  for (let i = 0; i < line.length; i++) {
    const c = line[i]
    if (c === '"') {
      if (inQuotes && line[i + 1] === '"') { cur += '"'; i++ }
      else inQuotes = !inQuotes
    } else if (c === delim && !inQuotes) {
      out.push(cur)
      cur = ''
    } else {
      cur += c
    }
  }
  out.push(cur)
  return out
}

async function commitImport() {
  if (!preview.value) return
  if (!feedName.value.trim()) {
    toast.error('Podaj nazwę feedu')
    return
  }
  if (!hasName.value) {
    toast.error('Wymagane: zmapuj jedną kolumnę jako „Nazwa produktu"')
    return
  }
  committing.value = true
  try {
    const { data } = await api.post('/imports/commit', {
      feed_name: feedName.value.trim(),
      headers: preview.value.headers,
      rows: allRows.value,
      mapping: mapping.value,
    })
    toast.success(`Zaimportowano ${data.products_imported} produktów`)
    router.push(`/feeds-in/${data.feed_in_id}`)
  } catch (e) {
    toast.error(getApiError(e, 'Nie udało się zaimportować pliku'))
  } finally {
    committing.value = false
  }
}

function reset() {
  file.value = null
  preview.value = null
  allRows.value = []
  mapping.value = {}
  feedName.value = ''
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-3 sm:px-4 py-6 sm:py-10">
    <router-link to="/dashboard" class="text-xs text-gray-400 hover:text-indigo-600 mb-3 inline-flex items-center gap-1">
      ← Dashboard
    </router-link>
    <h1 class="font-heading text-2xl font-bold text-gray-900 mb-2">Import produktów z CSV / Excel</h1>
    <p class="text-sm text-gray-500 mb-8">Wgraj plik CSV lub XLSX z produktami. Mapowanie kolumn rozpoznajemy automatycznie.</p>

    <!-- Step 1: file upload -->
    <section v-if="!preview" class="bg-white border border-gray-200 rounded-2xl p-6 sm:p-8">
      <label
        class="block border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition"
        :class="dragActive ? 'border-indigo-400 bg-indigo-50' : 'border-gray-300 hover:border-indigo-300 bg-gray-50'"
        @dragover.prevent="dragActive = true"
        @dragleave.prevent="dragActive = false"
        @drop="onDrop"
      >
        <input type="file" accept=".csv,.xlsx,.xlsm,.txt" class="hidden" @change="onFileChange" />
        <svg class="w-12 h-12 mx-auto text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" /></svg>
        <p class="text-sm font-medium text-gray-700">{{ file ? file.name : 'Przeciągnij plik tutaj lub kliknij' }}</p>
        <p class="text-xs text-gray-400 mt-1">CSV, XLSX · max 10 MB</p>
      </label>

      <div v-if="file" class="mt-6 flex justify-between items-center">
        <button type="button" @click="reset" class="text-sm text-gray-500 hover:text-gray-700 cursor-pointer">Zmień plik</button>
        <button
          type="button"
          @click="uploadPreview"
          :disabled="uploading"
          class="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition cursor-pointer"
        >
          {{ uploading ? 'Analizowanie...' : 'Przeanalizuj plik' }}
        </button>
      </div>

      <div class="mt-8 pt-6 border-t border-gray-100">
        <p class="text-xs text-gray-400 font-semibold uppercase tracking-wider mb-2">Podpowiedzi</p>
        <ul class="text-xs text-gray-500 space-y-1">
          <li>· Pierwsza linia powinna zawierać nazwy kolumn (np. „nazwa", „cena", „url")</li>
          <li>· Obsługujemy separatory: przecinek, średnik, tab</li>
          <li>· Polskie nagłówki rozpoznajemy automatycznie (cena, kategoria, marka, opis...)</li>
          <li>· Wymagana jest kolumna z nazwą produktu</li>
        </ul>
      </div>
    </section>

    <!-- Step 2: mapping + commit -->
    <section v-else class="space-y-6">
      <div class="bg-white border border-gray-200 rounded-2xl p-6">
        <div class="flex items-center justify-between mb-5 flex-wrap gap-3">
          <div>
            <h2 class="font-heading text-lg font-bold text-gray-900">Mapowanie kolumn</h2>
            <p class="text-xs text-gray-500 mt-1">{{ preview.row_count }} wierszy · {{ preview.headers.length }} kolumn</p>
          </div>
          <button type="button" @click="reset" class="text-sm text-gray-500 hover:text-gray-700 cursor-pointer">← Wybierz inny plik</button>
        </div>

        <div class="mb-5">
          <label class="block text-sm font-medium text-gray-700 mb-1">Nazwa nowego feedu *</label>
          <input v-model="feedName" type="text"
            class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
        </div>

        <div class="space-y-2">
          <div v-for="header in preview.headers" :key="header" class="flex items-center gap-3 bg-gray-50 rounded-lg p-3">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-mono text-gray-900 truncate">{{ header }}</p>
              <p v-if="preview.preview[0]?.[preview.headers.indexOf(header)]" class="text-xs text-gray-400 truncate">
                np. „{{ preview.preview[0][preview.headers.indexOf(header)] }}"
              </p>
            </div>
            <svg class="w-4 h-4 text-gray-300 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" /></svg>
            <select
              v-model="mapping[header]"
              class="w-48 sm:w-56 px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
            >
              <option v-for="opt in FIELDS" :key="opt.value" :value="opt.value || null">{{ opt.label }}</option>
            </select>
          </div>
        </div>

        <div v-if="!hasName" class="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800">
          ⚠ Wymagane: zmapuj jedną z kolumn jako „Nazwa produktu"
        </div>

        <div class="mt-6 flex justify-end gap-2">
          <button type="button" @click="reset" class="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-xl cursor-pointer">Anuluj</button>
          <button
            type="button"
            @click="commitImport"
            :disabled="committing || !hasName || !feedName.trim()"
            class="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition cursor-pointer"
          >
            {{ committing ? 'Importowanie...' : `Zaimportuj ${preview.row_count} produktów` }}
          </button>
        </div>
      </div>

      <!-- Preview rows -->
      <div class="bg-white border border-gray-200 rounded-2xl p-6">
        <h3 class="font-heading text-base font-bold text-gray-900 mb-4">Podgląd pierwszych 5 wierszy</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-xs">
            <thead>
              <tr class="border-b border-gray-200">
                <th v-for="h in preview.headers" :key="h" class="text-left p-2 font-semibold text-gray-600">{{ h }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in preview.preview" :key="i" class="border-b border-gray-100">
                <td v-for="(cell, j) in row" :key="j" class="p-2 text-gray-700 max-w-[200px] truncate">{{ cell }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </div>
</template>
