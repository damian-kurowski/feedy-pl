<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useFeedsOutStore, type FeedOut, type StructureElement } from '../stores/feedsOut'
import { useFeedsInStore } from '../stores/feedsIn'
import MappingTable from '../components/MappingTable.vue'
import QualityScore from '../components/QualityScore.vue'
import ValidationIssues from '../components/ValidationIssues.vue'
import FeedOutProducts from '../components/FeedOutProducts.vue'
import EanCoverage from '../components/EanCoverage.vue'
import DescriptionTemplateRule from '../components/DescriptionTemplateRule.vue'
import AiRewriteSection from '../components/AiRewriteSection.vue'
import api from '../api/client'

const route = useRoute()
const feedsOutStore = useFeedsOutStore()
const feedsInStore = useFeedsInStore()

const feedId = Number(route.params.id)

const feedOut = ref<FeedOut | null>(null)
const structure = ref<StructureElement[]>([])
const sampleProduct = ref<Record<string, any> | null>(null)
const saving = ref(false)
const copied = ref(false)
const saveError = ref('')
const saveSuccess = ref(false)

// XML Preview
const xmlPreview = ref('')
const showPreview = ref(false)
const loadingPreview = ref(false)

async function loadPreview() {
  if (!feedOut.value) return
  loadingPreview.value = true
  try {
    const url = `/feed/${feedOut.value.link_out}.xml`
    const response = await fetch(url)
    const text = await response.text()
    // Show first 5000 chars
    xmlPreview.value = text.substring(0, 5000)
    if (text.length > 5000) xmlPreview.value += '\n... (obcięto do 5000 znaków)'
    showPreview.value = true
  } catch {
    xmlPreview.value = 'Błąd ładowania podglądu'
    showPreview.value = true
  } finally {
    loadingPreview.value = false
  }
}

// Validation
const validation = ref<any>(null)
const validating = ref(false)

async function validateFeed() {
  if (!feedOut.value) return
  validating.value = true
  try {
    const { data } = await api.get(`/feeds-out/${feedOut.value.id}/validate`)
    validation.value = data
  } catch {
    validation.value = null
  } finally {
    validating.value = false
  }
}

// Category Mapping
const categoryMapping = ref<Record<string, string>>({})
const savingMapping = ref(false)
const mappingError = ref('')
const mappingSuccess = ref(false)
const newSourceCategory = ref('')
const ceneoCategorySuggestions = ref<Record<string, string[]>>({})
const loadingSuggestions = ref<Record<string, boolean>>({})

async function fetchCeneoSuggestions(sourceCategory: string) {
  loadingSuggestions.value[sourceCategory] = true
  try {
    let categories: string[]
    if (feedOut.value && (feedOut.value.type === 'gmc' || feedOut.value.type === 'facebook')) {
      categories = await feedsOutStore.getGoogleCategories(sourceCategory)
    } else {
      const { data } = await api.get('/feeds-out/ceneo-categories', { params: { q: sourceCategory } })
      categories = data.categories
    }
    ceneoCategorySuggestions.value[sourceCategory] = categories
    if (!categoryMapping.value[sourceCategory] && categories.length > 0) {
      categoryMapping.value[sourceCategory] = categories[0]
    }
  } catch {
    ceneoCategorySuggestions.value[sourceCategory] = []
  } finally {
    loadingSuggestions.value[sourceCategory] = false
  }
}

function addCategoryRow() {
  const name = newSourceCategory.value.trim()
  if (!name || name in categoryMapping.value) return
  categoryMapping.value[name] = ''
  newSourceCategory.value = ''
  fetchCeneoSuggestions(name)
}

function removeCategoryRow(sourceCategory: string) {
  delete categoryMapping.value[sourceCategory]
}

async function saveCategoryMapping() {
  savingMapping.value = true
  mappingError.value = ''
  mappingSuccess.value = false
  try {
    const mapping = Object.keys(categoryMapping.value).length > 0 ? { ...categoryMapping.value } : null
    const updated = await feedsOutStore.updateFeed(feedId, { category_mapping: mapping } as any)
    feedOut.value = updated
    mappingSuccess.value = true
    setTimeout(() => (mappingSuccess.value = false), 3000)
  } catch (e: any) {
    mappingError.value = e.response?.data?.detail || 'Blad zapisu mapowania kategorii'
  } finally {
    savingMapping.value = false
  }
}

async function autoSuggestAll() {
  for (const sourceCategory of Object.keys(categoryMapping.value)) {
    await fetchCeneoSuggestions(sourceCategory)
  }
}

// Rules
const rules = ref<any[]>([])
const savingRules = ref(false)
const rulesError = ref('')
const rulesSuccess = ref(false)
const showRuleMenu = ref(false)
const pendingRuleType = ref<string | null>(null)
const pendingRuleInput = ref('')
const pendingRuleInput2 = ref('')
const pendingRuleInput3 = ref('')

const ruleTypeLabels: Record<string, string> = {
  filter_no_image: 'Ukryj produkty bez zdjęcia',
  filter_no_price: 'Ukryj produkty bez ceny',
  filter_exclude: 'Ukryj produkty z kategorii',
  filter_include: 'Pokaz tylko produkty z kategorii',
  modify_prefix: 'Dodaj prefix do pola',
  modify_replace: 'Zamien tekst w polu',
  description_template: 'Szablon opisu',
}

function ruleDescription(rule: any): string {
  switch (rule.type) {
    case 'filter_no_image': return 'Ukryj produkty bez zdjęcia'
    case 'filter_no_price': return 'Ukryj produkty bez ceny'
    case 'filter_exclude': return `Ukryj produkty gdzie ${rule.field} zawiera "${rule.value}"`
    case 'filter_include': return `Pokaz tylko produkty gdzie ${rule.field} zawiera "${rule.value}"`
    case 'modify_prefix': return `Dodaj prefix "${rule.value}" do pola ${rule.field}`
    case 'modify_replace': return `Zamien "${rule.value}" na "${rule.new_value}" w polu ${rule.field}`
    case 'optimize_titles': return 'Automatyczna optymalizacja tytułów'
    case 'description_template': return `Szablon opisu: "${(rule.template || '').substring(0, 50)}..." -> ${rule.field || 'desc'}`
    default: return JSON.stringify(rule)
  }
}

function selectRuleType(type: string) {
  showRuleMenu.value = false
  if (type === 'filter_no_image' || type === 'filter_no_price') {
    rules.value.push({ type })
    pendingRuleType.value = null
  } else {
    pendingRuleType.value = type
    pendingRuleInput.value = ''
    pendingRuleInput2.value = ''
    pendingRuleInput3.value = ''
  }
}

function confirmPendingRule() {
  if (!pendingRuleType.value) return
  const type = pendingRuleType.value
  if (type === 'filter_exclude' || type === 'filter_include') {
    rules.value.push({ type, field: 'g:product_type', value: pendingRuleInput.value })
  } else if (type === 'modify_prefix') {
    rules.value.push({ type, field: pendingRuleInput.value, value: pendingRuleInput2.value })
  } else if (type === 'modify_replace') {
    rules.value.push({ type, field: pendingRuleInput.value, value: pendingRuleInput2.value, new_value: pendingRuleInput3.value })
  }
  pendingRuleType.value = null
  pendingRuleInput.value = ''
  pendingRuleInput2.value = ''
  pendingRuleInput3.value = ''
}

function cancelPendingRule() {
  pendingRuleType.value = null
  pendingRuleInput.value = ''
  pendingRuleInput2.value = ''
}

function removeRule(index: number) {
  rules.value.splice(index, 1)
}

async function saveRules() {
  savingRules.value = true
  rulesError.value = ''
  rulesSuccess.value = false
  try {
    const updated = await feedsOutStore.updateFeed(feedId, { rules: rules.value.length > 0 ? rules.value : null })
    feedOut.value = updated
    rulesSuccess.value = true
    setTimeout(() => (rulesSuccess.value = false), 3000)
  } catch (e: any) {
    rulesError.value = e.response?.data?.detail || 'Blad zapisu regul'
  } finally {
    savingRules.value = false
  }
}

// Title optimization
const optimizing = ref(false)
const titleComparisons = ref<any[]>([])

async function previewOptimization() {
  if (!feedOut.value) return
  optimizing.value = true
  try {
    const { data } = await api.post(`/feeds-out/${feedOut.value.id}/optimize-titles`)
    titleComparisons.value = data.comparisons
  } catch { }
  finally { optimizing.value = false }
}

async function applyOptimization() {
  if (!feedOut.value) return
  const currentRules = rules.value || []
  if (!currentRules.find((r: any) => r.type === 'optimize_titles')) {
    currentRules.push({ type: 'optimize_titles' })
    rules.value = currentRules
    await feedsOutStore.updateFeed(feedOut.value.id, { rules: currentRules })
    rulesSuccess.value = true
    setTimeout(() => rulesSuccess.value = false, 3000)
  }
}

const feedUrl = computed(() => {
  if (!feedOut.value) return ''
  return `${window.location.origin}/feed/${feedOut.value.link_out}.xml`
})

function addRow() {
  structure.value.push({
    sort_key: structure.value.length,
    custom_element: true,
    path_in: null,
    constant_value: null,
    level_out: 1,
    path_out: '',
    parent_path_out: null,
    element_name_out: '',
    is_leaf: true,
    attribute: false,
    condition: 'always',
  })
}

function removeRow(index: number) {
  structure.value.splice(index, 1)
}

async function saveStructure() {
  saving.value = true
  saveError.value = ''
  saveSuccess.value = false
  try {
    structure.value = await feedsOutStore.updateStructure(feedId, structure.value)
    saveSuccess.value = true
    setTimeout(() => (saveSuccess.value = false), 3000)
  } catch (e: any) {
    saveError.value = e.response?.data?.detail || 'Błąd zapisu mapowania'
  } finally {
    saving.value = false
  }
}

async function copyLink() {
  try {
    await navigator.clipboard.writeText(feedUrl.value)
    copied.value = true
    setTimeout(() => (copied.value = false), 2000)
  } catch {
    // fallback: silently fail
  }
}

onMounted(async () => {
  // Load feed out details
  await feedsOutStore.fetchFeeds()
  feedOut.value = feedsOutStore.feeds.find((f) => f.id === feedId) || null

  if (!feedOut.value) return

  // Load rules
  rules.value = feedOut.value.rules ? [...feedOut.value.rules] : []

  // Load category mapping
  categoryMapping.value = feedOut.value.category_mapping ? { ...feedOut.value.category_mapping } : {}

  // Load structure
  structure.value = (await feedsOutStore.getStructure(feedId)).map((s) => ({
    ...s,
    condition: s.condition || 'always',
    constant_value: s.constant_value ?? null,
  }))

  // Load sample product from feed-in for preview
  try {
    const products = await feedsInStore.getProducts(feedOut.value.feed_in_id)
    if (products.length > 0) {
      sampleProduct.value = products[0].product_value as Record<string, any>
    }
  } catch {
    // No products available for preview
  }
})
</script>

<template>
  <div class="max-w-4xl mx-auto py-10 px-4">
    <div v-if="!feedOut" class="text-gray-500">Ładowanie...</div>

    <template v-else>
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center gap-3 mb-1">
          <h1 class="text-2xl font-bold text-gray-900">{{ feedOut.name }}</h1>
          <span class="px-2 py-0.5 text-xs font-medium bg-indigo-100 text-indigo-700 rounded-full uppercase">
            {{ feedOut.type }}
          </span>
        </div>
        <router-link to="/dashboard" class="text-sm text-gray-500 hover:text-gray-700">&larr; Powrót do dashboardu</router-link>
      </div>

      <!-- Feed URL — always visible at top -->
      <div class="mb-6 p-4 bg-indigo-50 border border-indigo-200 rounded-xl flex items-center gap-3">
        <span class="text-sm font-medium text-indigo-700 shrink-0">Link XML:</span>
        <code class="flex-1 text-sm text-indigo-900 break-all truncate">{{ feedUrl }}</code>
        <button
          type="button"
          class="shrink-0 py-1.5 px-4 text-sm bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg cursor-pointer transition-colors"
          @click="copyLink"
        >
          {{ copied ? 'Skopiowano!' : 'Kopiuj link' }}
        </button>
        <a
          :href="feedUrl"
          target="_blank"
          class="shrink-0 py-1.5 px-4 text-sm bg-white border border-indigo-200 hover:bg-indigo-50 text-indigo-700 font-medium rounded-lg"
        >
          Podgląd
        </a>
      </div>

      <!-- Quality Score section -->
      <section class="mb-10">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-800">Jakosc feedu</h2>
          <button
            type="button"
            :disabled="validating"
            class="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 disabled:opacity-50 text-white font-medium rounded-md text-sm cursor-pointer"
            @click="validateFeed"
          >
            {{ validating ? 'Sprawdzanie...' : validation ? 'Sprawdz ponownie' : 'Sprawdz jakosc feedu' }}
          </button>
        </div>

        <div v-if="validation">
          <QualityScore
            :score="validation.quality_score"
            :label="validation.quality_label"
            :breakdown="validation.quality_breakdown"
            :summary="validation.summary"
          />

          <div v-if="validation.field_coverage?.length" class="mt-4 bg-white border rounded-lg p-4">
            <h3 class="text-sm font-medium text-gray-700 mb-3">Pokrycie pol</h3>
            <div class="space-y-1.5">
              <div v-for="field in validation.field_coverage" :key="field.field" class="flex items-center gap-2 text-xs">
                <span class="w-40 truncate" :class="field.required ? 'text-gray-700 font-medium' : 'text-gray-500'">
                  {{ field.field }}
                  <span v-if="field.required" class="text-red-400">*</span>
                </span>
                <div class="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full"
                    :class="field.percent === 100 ? 'bg-green-500' : field.percent > 0 ? 'bg-yellow-400' : 'bg-red-300'"
                    :style="{ width: field.percent + '%' }"
                  />
                </div>
                <span class="w-16 text-right text-gray-500">{{ field.filled }}/{{ field.total }}</span>
              </div>
            </div>
          </div>

          <EanCoverage
            v-if="validation.field_coverage?.length && validation.issues?.length"
            :field-coverage="validation.field_coverage"
            :issues="validation.issues"
            class="mt-4"
          />

          <div v-if="validation.issues?.length" class="mt-4 bg-white border rounded-lg p-4">
            <h3 class="text-sm font-medium text-gray-700 mb-3">Problemy</h3>
            <ValidationIssues :issues="validation.issues" />
          </div>
        </div>

        <div v-else-if="!validating" class="text-sm text-gray-400 bg-gray-50 border rounded-lg p-6 text-center">
          Kliknij "Sprawdz jakosc feedu" aby zobaczyc wynik walidacji.
        </div>
      </section>

      <!-- Mapping section -->
      <section class="mb-10">
        <h2 class="text-lg font-semibold text-gray-800 mb-1">Mapowanie pól</h2>
        <p class="text-sm text-gray-500 mb-4">Przypisz pola z XML źródłowego do pól wymaganych przez porównywarkę</p>

        <div v-if="saveError" class="mb-3 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
          {{ saveError }}
        </div>
        <div v-if="saveSuccess" class="mb-3 p-3 bg-green-50 border border-green-200 text-green-700 rounded-md text-sm">
          Mapowanie zapisane pomyślnie.
        </div>

        <MappingTable
          :rows="structure"
          :sample-product="sampleProduct"
          @remove="removeRow"
          @add="addRow"
        />

        <button
          type="button"
          :disabled="saving"
          class="mt-4 py-2 px-6 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 cursor-pointer"
          @click="saveStructure"
        >
          {{ saving ? 'Zapisywanie...' : 'Zapisz mapowanie' }}
        </button>
      </section>

      <!-- Rules section -->
      <section class="mb-10">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">
          Reguły filtrowania
          <span v-if="rules.length" class="text-sm font-normal text-gray-500">({{ rules.length }})</span>
        </h2>

        <div v-if="rulesError" class="mb-3 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
          {{ rulesError }}
        </div>
        <div v-if="rulesSuccess" class="mb-3 p-3 bg-green-50 border border-green-200 text-green-700 rounded-md text-sm">
          Reguły zapisane pomyślnie.
        </div>

        <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-2">
          <!-- Existing rules -->
          <div
            v-for="(rule, index) in rules"
            :key="index"
            class="flex items-center justify-between bg-white border border-gray-200 rounded-md px-3 py-2"
          >
            <span class="text-sm text-gray-700">{{ ruleDescription(rule) }}</span>
            <button
              type="button"
              class="text-red-500 hover:text-red-700 text-sm font-medium cursor-pointer"
              @click="removeRule(index)"
            >
              Usuń
            </button>
          </div>

          <div v-if="rules.length === 0" class="text-sm text-gray-400 py-2">
            Brak regul filtrowania.
          </div>

          <!-- Pending rule input -->
          <div v-if="pendingRuleType" class="mt-3 p-3 bg-white border border-indigo-200 rounded-md space-y-2">
            <div class="text-sm font-medium text-gray-700">{{ ruleTypeLabels[pendingRuleType] }}</div>

            <template v-if="pendingRuleType === 'filter_exclude' || pendingRuleType === 'filter_include'">
              <input
                v-model="pendingRuleInput"
                type="text"
                placeholder="Wpisz wartość kategorii..."
                class="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </template>

            <template v-if="pendingRuleType === 'modify_prefix'">
              <input
                v-model="pendingRuleInput"
                type="text"
                placeholder="Nazwa pola (np. title)"
                class="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <input
                v-model="pendingRuleInput2"
                type="text"
                placeholder="Prefix do dodania (np. PROMO: )"
                class="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </template>

            <template v-if="pendingRuleType === 'modify_replace'">
              <input
                v-model="pendingRuleInput"
                type="text"
                placeholder="Nazwa pola (np. title)"
                class="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <input
                v-model="pendingRuleInput2"
                type="text"
                placeholder="Tekst do znalezienia"
                class="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <input
                v-model="pendingRuleInput3"
                type="text"
                placeholder="Zamien na..."
                class="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </template>

            <template v-if="pendingRuleType === 'description_template'">
              <DescriptionTemplateRule
                :sample-product="sampleProduct"
                @confirm="(rule: any) => { rules.push(rule); pendingRuleType = null }"
                @cancel="cancelPendingRule"
              />
            </template>

            <div class="flex gap-2">
              <button
                type="button"
                class="py-1 px-3 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700 cursor-pointer"
                @click="confirmPendingRule"
              >
                Dodaj
              </button>
              <button
                type="button"
                class="py-1 px-3 text-sm bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 cursor-pointer"
                @click="cancelPendingRule"
              >
                Anuluj
              </button>
            </div>
          </div>

          <!-- Add rule dropdown -->
          <div class="relative mt-3">
            <button
              type="button"
              class="py-1.5 px-4 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 font-medium text-gray-700 cursor-pointer"
              @click="showRuleMenu = !showRuleMenu"
            >
              + Dodaj regule
            </button>
            <div
              v-if="showRuleMenu"
              class="absolute left-0 mt-1 w-72 bg-white border border-gray-200 rounded-md shadow-lg z-10"
            >
              <button
                v-for="(label, type) in ruleTypeLabels"
                :key="type"
                type="button"
                class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer"
                @click="selectRuleType(type)"
              >
                {{ label }}
              </button>
            </div>
          </div>
        </div>

        <button
          type="button"
          :disabled="savingRules"
          class="mt-4 py-2 px-6 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 cursor-pointer"
          @click="saveRules"
        >
          {{ savingRules ? 'Zapisywanie...' : 'Zapisz reguly' }}
        </button>
      </section>

      <!-- Title Optimization section -->
      <section class="mb-10 bg-white rounded-lg shadow-sm border p-5">
        <h2 class="text-lg font-semibold mb-3">Optymalizacja tytułów</h2>
        <p class="text-sm text-gray-500 mb-4">Automatycznie ulepsz tytuły produktów — dodaj markę, wyczyść formatowanie.</p>

        <button @click="previewOptimization" :disabled="optimizing" class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50 cursor-pointer">
          {{ optimizing ? 'Analizuję...' : 'Podgląd optymalizacji' }}
        </button>

        <div v-if="titleComparisons.length" class="mt-4 space-y-2">
          <div v-for="(comp, i) in titleComparisons" :key="i" class="p-3 rounded-lg" :class="comp.changed ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-50'">
            <p class="text-xs text-gray-400">Oryginał:</p>
            <p class="text-sm">{{ comp.original }}</p>
            <p v-if="comp.changed" class="text-xs text-green-600 mt-1">Zoptymalizowany:</p>
            <p v-if="comp.changed" class="text-sm font-medium text-green-800">{{ comp.optimized }}</p>
            <p v-else class="text-xs text-gray-400 mt-1">Bez zmian</p>
          </div>

          <button @click="applyOptimization" class="mt-3 px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 cursor-pointer">
            Zastosuj optymalizację do feedu
          </button>
        </div>
      </section>

      <!-- AI Rewrite section -->
      <section class="mb-10 bg-white rounded-lg shadow-sm border p-5">
        <h2 class="text-lg font-semibold mb-3">AI Opisy</h2>
        <AiRewriteSection :feed-out-id="feedId" />
      </section>

      <!-- Category Mapping section -->
      <section class="mb-10">
        <h2 class="text-lg font-semibold text-gray-800 mb-1">Mapowanie kategorii</h2>
        <p class="text-sm text-gray-500 mb-4">Przypisz kategorie ze swojego sklepu do kategorii platformy docelowej</p>

        <div v-if="mappingError" class="mb-3 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
          {{ mappingError }}
        </div>
        <div v-if="mappingSuccess" class="mb-3 p-3 bg-green-50 border border-green-200 text-green-700 rounded-md text-sm">
          Mapowanie kategorii zapisane pomyslnie.
        </div>

        <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-3">
          <!-- Existing mappings -->
          <div
            v-for="(ceneoCategory, sourceCategory) in categoryMapping"
            :key="sourceCategory"
            class="bg-white border border-gray-200 rounded-md px-3 py-3 space-y-2"
          >
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-gray-700">{{ sourceCategory }}</span>
              <button
                type="button"
                class="text-red-500 hover:text-red-700 text-sm font-medium cursor-pointer"
                @click="removeCategoryRow(sourceCategory as string)"
              >
                Usun
              </button>
            </div>
            <div class="flex items-center gap-2">
              <select
                :value="categoryMapping[sourceCategory as string]"
                @change="categoryMapping[sourceCategory as string] = ($event.target as HTMLSelectElement).value"
                class="flex-1 border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">-- Wybierz kategorie Ceneo --</option>
                <option
                  v-for="suggestion in (ceneoCategorySuggestions[sourceCategory as string] || [])"
                  :key="suggestion"
                  :value="suggestion"
                >
                  {{ suggestion }}
                </option>
              </select>
              <button
                type="button"
                class="shrink-0 py-1.5 px-3 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 font-medium text-gray-700 cursor-pointer"
                :disabled="loadingSuggestions[sourceCategory as string]"
                @click="fetchCeneoSuggestions(sourceCategory as string)"
              >
                {{ loadingSuggestions[sourceCategory as string] ? '...' : 'Sugeruj' }}
              </button>
            </div>
          </div>

          <div v-if="Object.keys(categoryMapping).length === 0" class="text-sm text-gray-400 py-2">
            Brak mapowania kategorii. Dodaj kategorie ze swojego sklepu ponizej.
          </div>

          <!-- Add new category row -->
          <div class="flex items-center gap-2 mt-3">
            <input
              v-model="newSourceCategory"
              type="text"
              placeholder="Nazwa kategorii ze sklepu..."
              class="flex-1 border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              @keyup.enter="addCategoryRow"
            />
            <button
              type="button"
              class="py-1.5 px-4 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 font-medium text-gray-700 cursor-pointer"
              @click="addCategoryRow"
            >
              + Dodaj
            </button>
          </div>

          <!-- Auto-suggest all button -->
          <div v-if="Object.keys(categoryMapping).length > 0" class="mt-2">
            <button
              type="button"
              class="py-1.5 px-4 text-sm bg-white border border-indigo-300 rounded-md hover:bg-indigo-50 font-medium text-indigo-600 cursor-pointer"
              @click="autoSuggestAll"
            >
              Automatyczne sugestie dla wszystkich
            </button>
          </div>
        </div>

        <button
          type="button"
          :disabled="savingMapping"
          class="mt-4 py-2 px-6 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 cursor-pointer"
          @click="saveCategoryMapping"
        >
          {{ savingMapping ? 'Zapisywanie...' : 'Zapisz mapowanie kategorii' }}
        </button>
      </section>

      <!-- Products section -->
      <section class="mb-10">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Produkty</h2>
        <FeedOutProducts :feed-out-id="feedId" />
      </section>

      <!-- Link section -->
      <section>
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Link do feeda</h2>

        <div class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md text-sm text-blue-800">
          Wklej ten link w panelu porównywarki (Ceneo, Google Merchant Center) jako źródło feeda produktowego.
        </div>

        <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div class="flex items-center gap-3">
            <code class="flex-1 text-sm text-gray-800 break-all">{{ feedUrl }}</code>
            <button
              type="button"
              class="shrink-0 py-1.5 px-4 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 font-medium text-gray-700 cursor-pointer"
              @click="copyLink"
            >
              {{ copied ? 'Skopiowano!' : 'Kopiuj' }}
            </button>
            <a
              :href="feedUrl"
              target="_blank"
              class="shrink-0 py-1.5 px-4 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 font-medium text-indigo-600"
            >
              Podgląd XML
            </a>
          </div>
        </div>
      </section>

      <!-- XML Preview section -->
      <div class="bg-white rounded-lg shadow-sm border p-4 mt-6">
        <div class="flex items-center justify-between mb-3">
          <h2 class="font-semibold">Podgląd XML</h2>
          <button @click="loadPreview" :disabled="loadingPreview" class="text-sm text-indigo-600 hover:text-indigo-800">
            {{ loadingPreview ? 'Ładowanie...' : showPreview ? 'Odśwież' : 'Pokaż podgląd' }}
          </button>
        </div>
        <pre v-if="showPreview" class="bg-gray-50 p-4 rounded-lg text-xs font-mono overflow-x-auto max-h-96 overflow-y-auto whitespace-pre-wrap">{{ xmlPreview }}</pre>
      </div>
    </template>
  </div>
</template>
