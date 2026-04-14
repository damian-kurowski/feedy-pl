<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import api from '../api/client'
import { useToast, getApiError } from '../composables/useToast'

const props = defineProps<{ feedId: number }>()
const toast = useToast()

interface InvalidItem {
  id: number
  product_name: string
  ean: string
  reason: string
  fixed: string | null
}
interface Report {
  total_products: number
  with_ean: number
  valid_ean: number
  invalid_ean: number
  missing_ean: number
  ean_coverage_pct: number
  ean_validity_pct: number
  invalid_items: InvalidItem[]
}

const report = ref<Report | null>(null)
const loading = ref(false)
const showInvalid = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get(`/feeds-in/${props.feedId}/ean-report`)
    report.value = data
  } catch (e) {
    toast.error(getApiError(e, 'Nie udało się załadować raportu EAN'))
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => props.feedId, load)

function coverageColor(pct: number) {
  if (pct >= 90) return 'text-green-600'
  if (pct >= 70) return 'text-amber-600'
  return 'text-red-600'
}

function copyEan(ean: string) {
  void navigator.clipboard.writeText(ean)
  toast.success('Skopiowano EAN')
}
</script>

<template>
  <section class="bg-white border border-gray-200 rounded-2xl p-6">
    <div class="flex items-center gap-3 mb-5">
      <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
        <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 013.75 9.375v-4.5zM3.75 14.625c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 013.75 19.125v-4.5zM13.5 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 0113.5 9.375v-4.5z"/>
        </svg>
      </div>
      <div class="flex-1">
        <h2 class="font-heading text-lg font-bold text-gray-900">Pokrycie EAN / GTIN</h2>
        <p class="text-xs text-gray-500">Walidacja kodów kreskowych — EAN-8/12/13/14 z sumą kontrolną</p>
      </div>
      <button v-if="report" type="button" @click="load"
        class="text-xs text-gray-500 hover:text-indigo-600 cursor-pointer">Odśwież</button>
    </div>

    <div v-if="loading && !report" class="text-sm text-gray-400">Ładowanie...</div>

    <template v-else-if="report">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        <div class="bg-gray-50 rounded-xl p-4 text-center">
          <p class="text-2xl font-extrabold text-gray-900">{{ report.total_products }}</p>
          <p class="text-[10px] uppercase font-semibold text-gray-500 mt-1 tracking-wider">Produktów</p>
        </div>
        <div class="bg-gray-50 rounded-xl p-4 text-center">
          <p class="text-2xl font-extrabold" :class="coverageColor(report.ean_coverage_pct)">{{ report.ean_coverage_pct }}%</p>
          <p class="text-[10px] uppercase font-semibold text-gray-500 mt-1 tracking-wider">Pokrycie EAN</p>
        </div>
        <div class="bg-gray-50 rounded-xl p-4 text-center">
          <p class="text-2xl font-extrabold" :class="coverageColor(report.ean_validity_pct)">{{ report.ean_validity_pct }}%</p>
          <p class="text-[10px] uppercase font-semibold text-gray-500 mt-1 tracking-wider">Ważne EAN</p>
        </div>
        <div class="bg-gray-50 rounded-xl p-4 text-center">
          <p class="text-2xl font-extrabold" :class="report.invalid_ean > 0 ? 'text-red-600' : 'text-green-600'">{{ report.invalid_ean }}</p>
          <p class="text-[10px] uppercase font-semibold text-gray-500 mt-1 tracking-wider">Błędne</p>
        </div>
      </div>

      <div v-if="report.missing_ean > 0" class="mb-3 p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800">
        ⚠ <strong>{{ report.missing_ean }}</strong> produktów nie ma kodu EAN. Produkty bez EAN trudniej dopasować do kart produktów na Ceneo i Google Shopping.
      </div>

      <div v-if="report.invalid_ean > 0">
        <button type="button" @click="showInvalid = !showInvalid"
          class="text-xs font-semibold text-red-600 hover:text-red-800 cursor-pointer">
          {{ showInvalid ? 'Ukryj' : 'Pokaż' }} {{ report.invalid_ean }} produktów z błędnym EAN
        </button>
        <div v-if="showInvalid" class="mt-3 max-h-80 overflow-y-auto border border-gray-200 rounded-xl">
          <table class="w-full text-xs">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="text-left p-2 font-semibold text-gray-600">Produkt</th>
                <th class="text-left p-2 font-semibold text-gray-600">EAN</th>
                <th class="text-left p-2 font-semibold text-gray-600">Problem</th>
                <th class="text-left p-2 font-semibold text-gray-600">Sugestia</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="item in report.invalid_items" :key="item.id">
                <td class="p-2 text-gray-900 max-w-[220px] truncate">{{ item.product_name }}</td>
                <td class="p-2 font-mono text-gray-700">
                  <button type="button" @click="copyEan(item.ean)" class="hover:text-indigo-600 cursor-pointer" title="Kopiuj">{{ item.ean }}</button>
                </td>
                <td class="p-2 text-red-600">{{ item.reason }}</td>
                <td class="p-2 text-gray-500">
                  <code v-if="item.fixed" class="font-mono text-green-600">{{ item.fixed }}</code>
                  <span v-else class="text-gray-400">—</span>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-if="report.invalid_items.length === 200" class="text-[11px] text-gray-400 p-2 text-center">
            (pokazano pierwsze 200 z {{ report.invalid_ean }})
          </p>
        </div>
      </div>

      <div v-else class="text-xs text-green-600 font-medium">
        ✓ Wszystkie EAN-y są poprawne
      </div>
    </template>
  </section>
</template>
