<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ fieldCoverage: any[]; issues: any[] }>()
const eanField = computed(() => props.fieldCoverage.find(f => ['g:gtin', 'code', 'ean'].includes(f.field)))
const eanIssues = computed(() => props.issues.filter(i => i.rule && (i.rule.includes('ean') || i.rule.includes('gtin'))))
const show = computed(() => eanField.value != null)
</script>

<template>
  <div v-if="show" class="bg-white border rounded-lg p-4">
    <h3 class="text-sm font-medium text-gray-700 mb-3">Pokrycie EAN/GTIN</h3>
    <div class="flex items-center gap-3 mb-2">
      <div class="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
        <div class="h-full rounded-full" :class="eanField!.percent >= 80 ? 'bg-green-500' : eanField!.percent >= 40 ? 'bg-yellow-400' : 'bg-red-400'" :style="{ width: eanField!.percent + '%' }" />
      </div>
      <span class="text-sm font-medium text-gray-700 w-24 text-right">{{ eanField!.filled }}/{{ eanField!.total }} ({{ eanField!.percent }}%)</span>
    </div>
    <p class="text-xs text-blue-600 bg-blue-50 p-2 rounded mb-3">Produkty z poprawnym kodem EAN maja ok. 40% wiecej wyświetleń na Google Shopping.</p>
    <div v-if="eanIssues.length > 0">
      <p class="text-xs font-medium text-gray-600 mb-1">Błędne kody EAN ({{ eanIssues.length }}):</p>
      <div class="space-y-1 max-h-32 overflow-y-auto">
        <div v-for="(issue, idx) in eanIssues.slice(0, 10)" :key="idx" class="text-xs text-red-600 flex gap-1">
          <span>x</span><span>{{ issue.product_name }} — {{ issue.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
