<script setup lang="ts">
import { computed, ref } from 'vue'
import type { StructureElement } from '../stores/feedsOut'
import { isImageField } from '../utils/imageExtractor'

const props = defineProps<{
  rows: StructureElement[]
  sampleProduct: Record<string, any> | null
}>()

const emit = defineEmits<{
  remove: [index: number]
  add: []
}>()

const showPreview = ref(false)

const sourceKeys = computed(() => {
  if (!props.sampleProduct) return []
  return Object.keys(props.sampleProduct)
})

/** Unique parent paths for "add as child" dropdown */
const parentPaths = computed(() => {
  const paths = new Set<string>()
  for (const row of props.rows) {
    if (!row.is_leaf || !row.attribute) {
      paths.add(row.path_out || row.element_name_out)
    }
  }
  return Array.from(paths)
})

function resolveValue(row: StructureElement): string {
  if (row.constant_value != null && row.constant_value !== '') return row.constant_value
  if (!row.path_in || !props.sampleProduct) return ''
  const val = props.sampleProduct[row.path_in]
  if (val === undefined || val === null) return ''
  if (typeof val === 'object') return JSON.stringify(val)
  return String(val)
}

function previewValue(row: StructureElement): string {
  const str = resolveValue(row)
  return str.length > 80 ? str.slice(0, 80) + '...' : str
}

function previewImageUrl(pathIn: string | null): string | null {
  if (!pathIn || !props.sampleProduct || !isImageField(pathIn)) return null
  const val = props.sampleProduct[pathIn]
  if (typeof val === 'string' && val.startsWith('http')) return val
  if (typeof val === 'object' && val) {
    const obj = val as Record<string, unknown>
    for (const v of Object.values(obj)) {
      if (typeof v === 'object' && v) {
        const inner = v as Record<string, unknown>
        if (typeof inner['@url'] === 'string') return inner['@url']
      }
      if (typeof v === 'string' && v.startsWith('http')) return v
    }
  }
  return null
}

function isUsingConstant(row: StructureElement): boolean {
  return row.constant_value != null && row.constant_value !== ''
}

function toggleSource(row: StructureElement) {
  if (isUsingConstant(row)) {
    // Switch to source field mode
    row.constant_value = null
  } else {
    // Switch to constant mode
    row.path_in = null
    row.constant_value = ''
  }
}

function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

/** Generate live XML preview from current config + sample product */
const xmlPreview = computed(() => {
  if (!props.rows.length) return '<!-- Brak konfiguracji -->'

  const lines: string[] = []
  lines.push('<?xml version="1.0" encoding="UTF-8"?>')

  // Build a simple sequential render respecting levels
  const indent = (level: number) => '  '.repeat(level)

  // Track open tags for closing
  const openStack: { name: string; level: number }[] = []

  for (const row of props.rows) {
    const name = row.element_name_out || '???'
    const val = resolveValue(row)

    // Check condition
    if (row.condition === 'if_not_empty' && !val) continue

    // Close tags at same or higher level
    while (openStack.length > 0 && openStack[openStack.length - 1].level >= row.level_out) {
      const closing = openStack.pop()!
      lines.push(`${indent(closing.level)}</${closing.name}>`)
    }

    if (row.attribute) {
      // Attributes get attached to parent — show as comment for preview
      lines.push(`${indent(row.level_out)}<!-- @${name}="${escapeXml(val)}" -->`)
    } else if (row.is_leaf) {
      lines.push(`${indent(row.level_out)}<${name}>${escapeXml(val)}</${name}>`)
    } else {
      // Container element — open tag
      lines.push(`${indent(row.level_out)}<${name}>`)
      openStack.push({ name, level: row.level_out })
    }
  }

  // Close remaining open tags
  while (openStack.length > 0) {
    const closing = openStack.pop()!
    lines.push(`${indent(closing.level)}</${closing.name}>`)
  }

  return lines.join('\n')
})
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-semibold text-gray-700 uppercase tracking-wide">Struktura XML</h3>
      <button
        type="button"
        class="text-sm px-3 py-1.5 rounded-md transition-colors cursor-pointer"
        :class="showPreview
          ? 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
        @click="showPreview = !showPreview"
      >
        {{ showPreview ? 'Ukryj podglad XML' : 'Podglad XML' }}
      </button>
    </div>

    <!-- XML Preview Panel -->
    <div
      v-if="showPreview"
      class="border border-indigo-200 rounded-lg bg-indigo-50 p-4 overflow-x-auto"
    >
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs font-medium text-indigo-700 uppercase tracking-wide">Podglad XML (pierwszy produkt)</span>
      </div>
      <pre class="text-xs text-gray-800 font-mono whitespace-pre leading-relaxed">{{ xmlPreview }}</pre>
    </div>

    <!-- Column headers -->
    <div class="hidden md:grid grid-cols-[1fr_1fr_auto_auto_1fr_auto] gap-2 px-3 py-2 text-xs font-medium text-gray-500 uppercase tracking-wide border-b border-gray-200">
      <span>Pole wyjsciowe</span>
      <span>Zrodlo / Stala</span>
      <span>Typ</span>
      <span>Warunek</span>
      <span>Podglad</span>
      <span></span>
    </div>

    <!-- Tree rows -->
    <div class="space-y-0.5">
      <div
        v-for="(row, idx) in rows"
        :key="idx"
        class="group grid grid-cols-1 md:grid-cols-[1fr_1fr_auto_auto_1fr_auto] gap-2 items-center px-3 py-2.5 rounded-lg border border-transparent hover:border-gray-200 hover:bg-gray-50 transition-all"
        :style="{ paddingLeft: `${12 + row.level_out * 24}px` }"
      >
        <!-- Output field name -->
        <div class="flex items-center gap-2">
          <!-- Tree connector visual -->
          <span
            v-if="row.level_out > 0"
            class="text-gray-300 text-xs select-none flex-shrink-0"
            style="font-family: monospace"
          >{{ row.attribute ? ' @' : ' |-' }}</span>
          <span
            v-if="!row.is_leaf && !row.attribute"
            class="text-gray-400 text-xs select-none flex-shrink-0"
            title="Kontener"
          >&#9660;</span>

          <input
            v-if="row.custom_element"
            v-model="row.element_name_out"
            type="text"
            class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="np. nazwa"
          />
          <span v-else class="text-sm font-medium text-gray-900 truncate">
            {{ row.element_name_out }}
          </span>
        </div>

        <!-- Source / Constant toggle -->
        <div class="flex items-center gap-1">
          <button
            type="button"
            class="flex-shrink-0 text-xs px-1.5 py-1 rounded border transition-colors cursor-pointer"
            :class="isUsingConstant(row)
              ? 'bg-amber-50 border-amber-300 text-amber-700'
              : 'bg-gray-50 border-gray-300 text-gray-600'"
            :title="isUsingConstant(row) ? 'Tryb: stala wartosc. Kliknij aby przelaczac na pole zrodlowe.' : 'Tryb: pole zrodlowe. Kliknij aby przelaczac na stala wartosc.'"
            @click="toggleSource(row)"
          >
            {{ isUsingConstant(row) ? 'S' : 'P' }}
          </button>

          <select
            v-if="!isUsingConstant(row)"
            v-model="row.path_in"
            class="w-full px-2 py-1 border border-gray-300 rounded text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option :value="null">-- Wybierz pole --</option>
            <option v-for="key in sourceKeys" :key="key" :value="key">
              {{ key }}
            </option>
          </select>
          <input
            v-else
            v-model="row.constant_value"
            type="text"
            class="w-full px-2 py-1 border border-amber-300 rounded text-sm bg-amber-50 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
            placeholder="Stala wartosc..."
          />
        </div>

        <!-- Type toggle -->
        <button
          type="button"
          class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium transition-colors cursor-pointer"
          :class="row.attribute
            ? 'bg-purple-100 text-purple-800 hover:bg-purple-200'
            : 'bg-blue-100 text-blue-800 hover:bg-blue-200'"
          @click="row.attribute = !row.attribute"
          :title="row.attribute ? 'Atrybut XML. Kliknij aby zmienic na element.' : 'Element XML. Kliknij aby zmienic na atrybut.'"
        >
          {{ row.attribute ? 'atrybut' : 'element' }}
        </button>

        <!-- Condition -->
        <select
          v-model="row.condition"
          class="px-2 py-1 border border-gray-300 rounded text-xs bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          <option value="always">Zawsze</option>
          <option value="if_not_empty">Jesli niepuste</option>
        </select>

        <!-- Preview value -->
        <div class="text-gray-500 truncate text-sm">
          <div v-if="previewImageUrl(row.path_in)" class="flex items-center gap-2">
            <img
              :src="previewImageUrl(row.path_in)!"
              alt="Preview"
              class="w-6 h-6 object-cover rounded border border-gray-200"
            />
            <span class="truncate text-xs">{{ previewValue(row) }}</span>
          </div>
          <span v-else class="text-xs">{{ previewValue(row) }}</span>
        </div>

        <!-- Delete -->
        <button
          type="button"
          class="text-red-400 hover:text-red-600 transition-colors cursor-pointer opacity-0 group-hover:opacity-100"
          title="Usun pole"
          @click="emit('remove', idx)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>

      <!-- Empty state -->
      <div v-if="rows.length === 0" class="px-4 py-8 text-center text-gray-400 border border-dashed border-gray-200 rounded-lg">
        Brak pol. Dodaj pierwsze pole ponizej.
      </div>
    </div>

    <!-- Add field button -->
    <button
      type="button"
      class="mt-2 text-sm text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer"
      @click="emit('add')"
    >
      + Dodaj pole
    </button>
  </div>
</template>
