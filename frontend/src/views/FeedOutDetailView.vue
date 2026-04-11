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
    mappingError.value = e.response?.data?.detail || 'Błąd zapisu mapowania kategorii'
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
  filter_include: 'Pokaż tylko produkty z kategorii',
  modify_prefix: 'Dodaj prefix do pola',
  modify_replace: 'Zamień tekst w polu',
  description_template: 'Szablon opisu',
}

function ruleDescription(rule: any): string {
  switch (rule.type) {
    case 'filter_no_image': return 'Ukryj produkty bez zdjęcia'
    case 'filter_no_price': return 'Ukryj produkty bez ceny'
    case 'filter_exclude': return `Ukryj produkty gdzie ${rule.field} zawiera "${rule.value}"`
    case 'filter_include': return `Pokaż tylko produkty gdzie ${rule.field} zawiera "${rule.value}"`
    case 'modify_prefix': return `Dodaj prefix "${rule.value}" do pola ${rule.field}`
    case 'modify_replace': return `Zamień "${rule.value}" na "${rule.new_value}" w polu ${rule.field}`
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
    rulesError.value = e.response?.data?.detail || 'Błąd zapisu reguł'
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
  <div class="max-w-5xl mx-auto py-10 px-4">
    <div v-if="!feedOut" class="text-gray-500">Ładowanie...</div>

    <template v-else>
      <!-- Header -->
      <div class="mb-8">
        <router-link to="/dashboard" class="text-xs text-gray-400 hover:text-indigo-600 transition-colors mb-3 inline-flex items-center gap-1">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" /></svg>
          Dashboard
        </router-link>
        <div class="flex items-center gap-3 mt-2">
          <h1 class="font-heading text-2xl font-bold text-gray-900">{{ feedOut.name }}</h1>
          <span class="px-2.5 py-1 text-xs font-semibold bg-indigo-100 text-indigo-700 rounded-full uppercase tracking-wide">
            {{ feedOut.type }}
          </span>
        </div>
      </div>

      <!-- Feed URL — always visible at top -->
      <div class="mb-8 p-5 bg-gradient-to-r from-indigo-50 to-white rounded-2xl border border-indigo-100 flex items-center gap-4">
        <div class="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center shrink-0">
          <svg class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.86-2.54a4.5 4.5 0 00-1.242-7.244l-4.5-4.5a4.5 4.5 0 00-6.364 6.364L4.343 8.05" /></svg>
        </div>
        <code class="flex-1 text-sm text-gray-700 break-all truncate">{{ feedUrl }}</code>
        <button
          type="button"
          class="shrink-0 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer"
          @click="copyLink"
        >
          {{ copied ? 'Skopiowano!' : 'Kopiuj link' }}
        </button>
        <a
          :href="feedUrl"
          target="_blank"
          class="shrink-0 border border-gray-200 hover:border-gray-300 text-gray-600 text-sm font-medium rounded-xl px-4 py-2 transition cursor-pointer"
        >
          Podgląd
        </a>
        <a
          :href="feedUrl + '?download=1'"
          class="shrink-0 border border-gray-200 hover:border-gray-300 text-gray-600 text-sm font-medium rounded-xl px-4 py-2 transition cursor-pointer flex items-center gap-1.5"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" /></svg>
          Pobierz XML
        </a>
      </div>

      <!-- Quality Score section -->
      <section class="mb-8">
        <div class="bg-white border border-gray-200 rounded-2xl p-6">
        <div class="flex items-center justify-between mb-5">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
              <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" /></svg>
            </div>
            <h2 class="font-heading text-lg font-bold text-gray-900">Jakość feedu</h2>
          </div>
          <button
            type="button"
            :disabled="validating"
            class="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer"
            @click="validateFeed"
          >
            {{ validating ? 'Sprawdzanie...' : validation ? 'Sprawdź ponownie' : 'Sprawdź jakość feedu' }}
          </button>
        </div>

        <div v-if="validation">
          <QualityScore
            :score="validation.quality_score"
            :label="validation.quality_label"
            :breakdown="validation.quality_breakdown"
            :summary="validation.summary"
          />

          <div v-if="validation.field_coverage?.length" class="mt-4 bg-white border border-gray-200 rounded-2xl p-6">
            <h3 class="text-sm font-medium text-gray-700 mb-3">Pokrycie pól</h3>
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

          <div v-if="validation.issues?.length" class="mt-4 bg-white border border-gray-200 rounded-2xl p-6">
            <h3 class="text-sm font-medium text-gray-700 mb-3">Problemy</h3>
            <ValidationIssues :issues="validation.issues" />
          </div>
        </div>

        <div v-else-if="!validating" class="text-sm text-gray-400 bg-gray-50 border border-gray-200 rounded-2xl p-6 text-center">
          Kliknij "Sprawdź jakość feedu" aby zobaczyć wynik walidacji.
        </div>
        </div>
      </section>

      <!-- Mapping section -->
      <section class="mb-8">
        <div class="bg-white border border-gray-200 rounded-2xl p-6">
        <div class="flex items-center justify-between mb-5">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
              <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0112 18.375m9.75-12.75c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125m19.5 0v1.5c0 .621-.504 1.125-1.125 1.125M2.25 5.625v1.5c0 .621.504 1.125 1.125 1.125m0 0h17.25m-17.25 0h7.5c.621 0 1.125.504 1.125 1.125M3.375 8.25c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m17.25-3.75h-7.5c-.621 0-1.125.504-1.125 1.125m8.625-1.125c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M12 10.875v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125M10.875 12c-.621 0-1.125.504-1.125 1.125M12 10.875c-.621 0-1.125.504-1.125 1.125m0 1.5v-1.5m0 0c0-.621.504-1.125 1.125-1.125m0 1.5c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m0 1.5v-1.5m0 0c0-.621.504-1.125 1.125-1.125" /></svg>
            </div>
            <div>
              <h2 class="font-heading text-lg font-bold text-gray-900">Mapowanie pól</h2>
              <p class="text-sm text-gray-500">Przypisz pola z XML źródłowego do pól wymaganych przez porównywarkę</p>
            </div>
          </div>
        </div>

        <div v-if="saveError" class="mb-3 p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm">
          {{ saveError }}
        </div>
        <div v-if="saveSuccess" class="mb-3 p-3 bg-green-50 border border-green-200 text-green-700 rounded-xl text-sm">
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
          class="mt-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer"
          @click="saveStructure"
        >
          {{ saving ? 'Zapisywanie...' : 'Zapisz mapowanie' }}
        </button>
        </div>
      </section>

      <!-- Rules section -->
      <section class="mb-8">
        <div class="bg-white border border-gray-200 rounded-2xl p-6">
        <div class="flex items-center justify-between mb-5">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
              <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 01-.659 1.591l-5.432 5.432a2.25 2.25 0 00-.659 1.591v2.927a2.25 2.25 0 01-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 00-.659-1.591L3.659 7.409A2.25 2.25 0 013 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0112 3z" /></svg>
            </div>
            <h2 class="font-heading text-lg font-bold text-gray-900">
              Reguły filtrowania
              <span v-if="rules.length" class="text-sm font-normal text-gray-500">({{ rules.length }})</span>
            </h2>
          </div>
        </div>

        <div v-if="rulesError" class="mb-3 p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm">
          {{ rulesError }}
        </div>
        <div v-if="rulesSuccess" class="mb-3 p-3 bg-green-50 border border-green-200 text-green-700 rounded-xl text-sm">
          Reguły zapisane pomyślnie.
        </div>

        <div class="bg-gray-50 border border-gray-200 rounded-2xl p-6 space-y-2">
          <!-- Existing rules -->
          <div
            v-for="(rule, index) in rules"
            :key="index"
            class="flex items-center justify-between bg-white border border-gray-200 rounded-xl px-4 py-3"
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
            Brak reguł filtrowania.
          </div>

          <!-- Pending rule input -->
          <div v-if="pendingRuleType" class="mt-3 p-4 bg-white border border-indigo-200 rounded-xl space-y-3">
            <div class="text-sm font-medium text-gray-700">{{ ruleTypeLabels[pendingRuleType] }}</div>

            <template v-if="pendingRuleType === 'filter_exclude' || pendingRuleType === 'filter_include'">
              <input
                v-model="pendingRuleInput"
                type="text"
                placeholder="Wpisz wartość kategorii..."
                class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              />
            </template>

            <template v-if="pendingRuleType === 'modify_prefix'">
              <input
                v-model="pendingRuleInput"
                type="text"
                placeholder="Nazwa pola (np. title)"
                class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              />
              <input
                v-model="pendingRuleInput2"
                type="text"
                placeholder="Prefix do dodania (np. PROMO: )"
                class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              />
            </template>

            <template v-if="pendingRuleType === 'modify_replace'">
              <input
                v-model="pendingRuleInput"
                type="text"
                placeholder="Nazwa pola (np. title)"
                class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              />
              <input
                v-model="pendingRuleInput2"
                type="text"
                placeholder="Tekst do znalezienia"
                class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              />
              <input
                v-model="pendingRuleInput3"
                type="text"
                placeholder="Zamień na..."
                class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
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
                class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium rounded-xl px-3 py-1.5 transition cursor-pointer"
                @click="confirmPendingRule"
              >
                Dodaj
              </button>
              <button
                type="button"
                class="bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-medium rounded-xl px-3 py-1.5 transition cursor-pointer"
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
              class="border border-gray-200 hover:border-gray-300 text-gray-600 text-sm font-medium rounded-xl px-4 py-2 transition cursor-pointer"
              @click="showRuleMenu = !showRuleMenu"
            >
              + Dodaj regułę
            </button>
            <div
              v-if="showRuleMenu"
              class="absolute left-0 mt-1 w-72 bg-white border border-gray-200 rounded-xl shadow-lg z-10 overflow-hidden"
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
          class="mt-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer"
          @click="saveRules"
        >
          {{ savingRules ? 'Zapisywanie...' : 'Zapisz reguły' }}
        </button>
        </div>
      </section>

      <!-- Title Optimization section -->
      <section class="mb-8">
        <div class="bg-white rounded-2xl border border-gray-200 p-6">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
            <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" /></svg>
          </div>
          <div>
            <h2 class="font-heading text-lg font-bold text-gray-900">Optymalizacja tytułów</h2>
            <p class="text-sm text-gray-500">Automatycznie ulepsz tytuły produktów -- dodaj marke, wyczysc formatowanie.</p>
          </div>
        </div>

        <button @click="previewOptimization" :disabled="optimizing" class="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/20 disabled:opacity-50 cursor-pointer">
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

          <button @click="applyOptimization" class="mt-3 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer">
            Zastosuj optymalizację do feedu
          </button>
        </div>
        </div>
      </section>

      <!-- AI Rewrite section -->
      <section class="mb-8">
        <div class="bg-white rounded-2xl border border-gray-200 p-6">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
            <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg>
          </div>
          <h2 class="font-heading text-lg font-bold text-gray-900">AI Opisy</h2>
        </div>
        <AiRewriteSection :feed-out-id="feedId" />
        </div>
      </section>

      <!-- Category Mapping section -->
      <section class="mb-8">
        <div class="bg-white border border-gray-200 rounded-2xl p-6">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
            <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" /></svg>
          </div>
          <div>
            <h2 class="font-heading text-lg font-bold text-gray-900">Mapowanie kategorii</h2>
            <p class="text-sm text-gray-500">Przypisz kategorie ze swojego sklepu do kategorii platformy docelowej</p>
          </div>
        </div>

        <div v-if="mappingError" class="mb-3 p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm">
          {{ mappingError }}
        </div>
        <div v-if="mappingSuccess" class="mb-3 p-3 bg-green-50 border border-green-200 text-green-700 rounded-xl text-sm">
          Mapowanie kategorii zapisane pomyślnie.
        </div>

        <div class="bg-gray-50 border border-gray-200 rounded-2xl p-6 space-y-3">
          <!-- Existing mappings -->
          <div
            v-for="(ceneoCategory, sourceCategory) in categoryMapping"
            :key="sourceCategory"
            class="bg-white border border-gray-200 rounded-xl px-4 py-4 space-y-2"
          >
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-gray-700">{{ sourceCategory }}</span>
              <button
                type="button"
                class="text-red-500 hover:text-red-700 text-sm font-medium cursor-pointer"
                @click="removeCategoryRow(sourceCategory as string)"
              >
                Usuń
              </button>
            </div>
            <div class="flex items-center gap-2">
              <select
                :value="categoryMapping[sourceCategory as string]"
                @change="categoryMapping[sourceCategory as string] = ($event.target as HTMLSelectElement).value"
                class="flex-1 px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
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
                class="shrink-0 border border-gray-200 hover:border-gray-300 text-gray-600 text-sm font-medium rounded-xl px-4 py-2 transition cursor-pointer"
                :disabled="loadingSuggestions[sourceCategory as string]"
                @click="fetchCeneoSuggestions(sourceCategory as string)"
              >
                {{ loadingSuggestions[sourceCategory as string] ? '...' : 'Sugeruj' }}
              </button>
            </div>
          </div>

          <div v-if="Object.keys(categoryMapping).length === 0" class="text-sm text-gray-400 py-2">
            Brak mapowania kategorii. Dodaj kategorie ze swojego sklepu poniżej.
          </div>

          <!-- Add new category row -->
          <div class="flex items-center gap-2 mt-3">
            <input
              v-model="newSourceCategory"
              type="text"
              placeholder="Nazwa kategorii ze sklepu..."
              class="flex-1 px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              @keyup.enter="addCategoryRow"
            />
            <button
              type="button"
              class="border border-gray-200 hover:border-gray-300 text-gray-600 text-sm font-medium rounded-xl px-4 py-2 transition cursor-pointer"
              @click="addCategoryRow"
            >
              + Dodaj
            </button>
          </div>

          <!-- Auto-suggest all button -->
          <div v-if="Object.keys(categoryMapping).length > 0" class="mt-2">
            <button
              type="button"
              class="border border-gray-200 hover:border-gray-300 text-indigo-600 text-sm font-medium rounded-xl px-4 py-2 transition cursor-pointer"
              @click="autoSuggestAll"
            >
              Automatyczne sugestie dla wszystkich
            </button>
          </div>
        </div>

        <button
          type="button"
          :disabled="savingMapping"
          class="mt-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer"
          @click="saveCategoryMapping"
        >
          {{ savingMapping ? 'Zapisywanie...' : 'Zapisz mapowanie kategorii' }}
        </button>
        </div>
      </section>

      <!-- Products section -->
      <section class="mb-8">
        <div class="bg-white border border-gray-200 rounded-2xl p-6">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
            <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" /></svg>
          </div>
          <h2 class="font-heading text-lg font-bold text-gray-900">Produkty</h2>
        </div>
        <FeedOutProducts :feed-out-id="feedId" />
        </div>
      </section>

      <!-- Link section -->
      <section class="mb-8">
        <div class="bg-white border border-gray-200 rounded-2xl p-6">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
            <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.86-2.54a4.5 4.5 0 00-1.242-7.244l-4.5-4.5a4.5 4.5 0 00-6.364 6.364L4.343 8.05" /></svg>
          </div>
          <h2 class="font-heading text-lg font-bold text-gray-900">Link do feeda</h2>
        </div>

        <div class="mb-4 p-4 bg-gradient-to-r from-indigo-50 to-white border border-indigo-100 rounded-xl text-sm text-indigo-800">
          Wklej ten link w panelu porównywarki (Ceneo, Google Merchant Center) jako źródło feeda produktowego.
        </div>

        <div class="flex items-center gap-3">
          <code class="flex-1 text-sm text-gray-800 break-all">{{ feedUrl }}</code>
          <button
            type="button"
            class="shrink-0 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer"
            @click="copyLink"
          >
            {{ copied ? 'Skopiowano!' : 'Kopiuj' }}
          </button>
          <a
            :href="feedUrl"
            target="_blank"
            class="shrink-0 border border-gray-200 hover:border-gray-300 text-gray-600 text-sm font-medium rounded-xl px-4 py-2 transition cursor-pointer"
          >
            Podgląd XML
          </a>
        </div>
        </div>
      </section>

      <!-- XML Preview section -->
      <section class="mb-8">
        <div class="bg-white rounded-2xl border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-5">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
              <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" /></svg>
            </div>
            <h2 class="font-heading text-lg font-bold text-gray-900">Podgląd XML</h2>
          </div>
          <button @click="loadPreview" :disabled="loadingPreview" class="text-sm text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer">
            {{ loadingPreview ? 'Ładowanie...' : showPreview ? 'Odśwież' : 'Pokaż podgląd' }}
          </button>
        </div>
        <pre v-if="showPreview" class="bg-gray-50 p-4 rounded-lg text-xs font-mono overflow-x-auto max-h-96 overflow-y-auto whitespace-pre-wrap">{{ xmlPreview }}</pre>
        </div>
      </section>
    </template>
  </div>
</template>
