<script setup lang="ts">
defineProps<{
  rows?: number
  variant?: 'card' | 'list' | 'stat'
}>()
</script>

<template>
  <div v-if="variant === 'stat'" class="bg-gray-50 border border-gray-100 rounded-2xl p-5 animate-pulse">
    <div class="h-3 w-16 bg-gray-200 rounded mb-3"></div>
    <div class="h-7 w-24 bg-gray-200 rounded"></div>
  </div>

  <div v-else-if="variant === 'list'" class="bg-gray-50 border border-gray-100 rounded-2xl p-5 animate-pulse flex items-center gap-4">
    <div class="w-12 h-12 bg-gray-200 rounded-xl shrink-0"></div>
    <div class="flex-1 space-y-2">
      <div class="h-3 w-1/3 bg-gray-200 rounded"></div>
      <div class="h-2.5 w-2/3 bg-gray-200 rounded"></div>
    </div>
  </div>

  <div v-else class="bg-gray-50 border border-gray-100 rounded-2xl p-5 animate-pulse">
    <div class="h-4 w-1/3 bg-gray-200 rounded mb-4"></div>
    <div v-for="i in (rows || 3)" :key="i" class="h-3 bg-gray-200 rounded mb-2"
      :style="{ width: `${100 - (i * 8)}%` }"></div>
  </div>
</template>
