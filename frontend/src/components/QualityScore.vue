<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  score: number
  label: string
  breakdown: {
    required_fields_score: number
    recommended_fields_score: number
    format_compliance_score: number
  }
  summary: { errors: number; warnings: number; info: number }
}>()

const colorClass = computed(() => {
  if (props.score >= 90) return { text: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200' }
  if (props.score >= 70) return { text: 'text-yellow-600', bg: 'bg-yellow-50', border: 'border-yellow-200' }
  if (props.score >= 50) return { text: 'text-orange-600', bg: 'bg-orange-50', border: 'border-orange-200' }
  return { text: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200' }
})
</script>

<template>
  <div :class="[colorClass.bg, colorClass.border]" class="border rounded-lg p-5">
    <div class="flex items-center gap-6">
      <div class="w-20 h-20 rounded-full flex items-center justify-center border-4 shrink-0" :class="[colorClass.border]">
        <span class="text-2xl font-bold" :class="colorClass.text">{{ score }}%</span>
      </div>
      <div class="flex-1">
        <h3 class="text-lg font-semibold" :class="colorClass.text">{{ label }}</h3>
        <p class="text-sm text-gray-600 mt-1">
          {{ summary.errors }} błędów
          <span class="mx-1">|</span>
          {{ summary.warnings }} ostrzeżeń
          <span v-if="summary.info > 0" class="mx-1">|</span>
          <span v-if="summary.info > 0">{{ summary.info }} informacji</span>
        </p>
        <div class="mt-3 space-y-1.5">
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <span class="w-32">Pola wymagane</span>
            <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-indigo-500 rounded-full" :style="{ width: breakdown.required_fields_score + '%' }" />
            </div>
            <span class="w-8 text-right">{{ breakdown.required_fields_score }}%</span>
          </div>
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <span class="w-32">Pola zalecane</span>
            <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-indigo-300 rounded-full" :style="{ width: breakdown.recommended_fields_score + '%' }" />
            </div>
            <span class="w-8 text-right">{{ breakdown.recommended_fields_score }}%</span>
          </div>
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <span class="w-32">Zgodnosc formatu</span>
            <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-green-500 rounded-full" :style="{ width: breakdown.format_compliance_score + '%' }" />
            </div>
            <span class="w-8 text-right">{{ breakdown.format_compliance_score }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
