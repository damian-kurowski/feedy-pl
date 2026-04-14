<script setup lang="ts">
import { ref, watch } from 'vue'
import type { FeedEnvelope, FeedEnvelopeCustomField } from '../stores/feedsOut'

const props = defineProps<{
  modelValue: FeedEnvelope | null
  saving?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: FeedEnvelope]
  save: [value: FeedEnvelope]
}>()

const title = ref('')
const description = ref('')
const link = ref('')
const custom = ref<FeedEnvelopeCustomField[]>([])

function loadFromProps() {
  const v = props.modelValue || {}
  title.value = v.title || ''
  description.value = v.description || ''
  link.value = v.link || ''
  custom.value = (v.custom || []).map((c) => ({ tag: c.tag, value: c.value, cdata: !!c.cdata }))
}

loadFromProps()
watch(() => props.modelValue, loadFromProps)

function buildValue(): FeedEnvelope {
  return {
    title: title.value.trim() || undefined,
    description: description.value.trim() || undefined,
    link: link.value.trim() || undefined,
    custom: custom.value
      .filter((c) => c.tag.trim())
      .map((c) => ({ tag: c.tag.trim(), value: c.value, cdata: !!c.cdata })),
  }
}

function addCustom() {
  custom.value.push({ tag: '', value: '', cdata: false })
}

function removeCustom(idx: number) {
  custom.value.splice(idx, 1)
}

function moveCustom(idx: number, dir: -1 | 1) {
  const target = idx + dir
  if (target < 0 || target >= custom.value.length) return
  const arr = custom.value
  ;[arr[idx], arr[target]] = [arr[target], arr[idx]]
}

function handleSave() {
  const value = buildValue()
  emit('update:modelValue', value)
  emit('save', value)
}
</script>

<template>
  <section class="bg-white border border-gray-200 rounded-2xl p-6">
    <div class="flex items-center gap-3 mb-2">
      <div class="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
        <svg class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 9h16.5m-16.5 6.75h16.5" />
        </svg>
      </div>
      <h2 class="font-heading text-lg font-bold text-gray-900">Nagłówek feedu (envelope)</h2>
    </div>
    <p class="text-xs text-gray-500 mb-5">Dane poza produktami — wyświetlają się na szczycie XML, zanim zaczną się produkty. Np. tytuł feedu, opis, link do sklepu, własne tagi.</p>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Tytuł</label>
        <input v-model="title" type="text" placeholder="np. Mój sklep z folią okienną"
          class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Link do sklepu</label>
        <input v-model="link" type="text" placeholder="https://mojsklep.pl"
          class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all" />
      </div>
    </div>

    <div class="mb-5">
      <label class="block text-sm font-medium text-gray-700 mb-1">Opis</label>
      <textarea v-model="description" rows="2" placeholder="Krótki opis feedu/sklepu"
        class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all resize-none"></textarea>
    </div>

    <div class="mb-3">
      <div class="flex items-center justify-between mb-2">
        <label class="text-sm font-medium text-gray-700">Dodatkowe tagi</label>
        <button type="button" @click="addCustom" class="text-xs text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer">+ Dodaj tag</button>
      </div>
      <p class="text-xs text-gray-500 mb-2">Np. <code class="font-mono">generator</code>, <code class="font-mono">version</code>, <code class="font-mono">updated</code>. Zaznacz CDATA jeśli wartość zawiera HTML lub znaki specjalne.</p>

      <div v-if="custom.length === 0" class="text-xs text-gray-400 italic">Brak dodatkowych tagów.</div>

      <div v-for="(c, idx) in custom" :key="idx" class="flex items-start gap-2 mb-2">
        <div class="flex flex-col gap-0.5 shrink-0 pt-1.5">
          <button type="button" @click="moveCustom(idx, -1)" :disabled="idx === 0"
            class="w-5 h-5 flex items-center justify-center text-gray-400 hover:text-indigo-600 disabled:opacity-20 disabled:cursor-not-allowed cursor-pointer">
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 15l7-7 7 7"/></svg>
          </button>
          <button type="button" @click="moveCustom(idx, 1)" :disabled="idx === custom.length - 1"
            class="w-5 h-5 flex items-center justify-center text-gray-400 hover:text-indigo-600 disabled:opacity-20 disabled:cursor-not-allowed cursor-pointer">
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
          </button>
        </div>
        <input v-model="c.tag" type="text" placeholder="tag"
          class="w-1/3 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
        <input v-model="c.value" type="text" placeholder="wartość"
          class="flex-1 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
        <label class="flex items-center gap-1 text-xs text-gray-600 shrink-0 pt-2.5 cursor-pointer select-none">
          <input type="checkbox" v-model="c.cdata" class="w-3.5 h-3.5 rounded border-gray-300" />
          CDATA
        </label>
        <button type="button" @click="removeCustom(idx)"
          class="text-red-400 hover:text-red-600 text-sm cursor-pointer px-2 pt-2" title="Usuń">×</button>
      </div>
    </div>

    <button type="button" @click="handleSave" :disabled="saving"
      class="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl px-5 py-2.5 transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer">
      {{ saving ? 'Zapisywanie...' : 'Zapisz nagłówek' }}
    </button>
  </section>
</template>
