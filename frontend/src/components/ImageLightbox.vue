<script setup lang="ts">
defineProps<{
  images: string[]
  show: boolean
}>()

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
      role="dialog"
      aria-modal="true"
      aria-label="Galeria zdjęć produktu"
      tabindex="-1"
      @click.self="emit('close')"
      @keydown.esc="emit('close')"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 p-4 max-h-[80vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-3">
          <h3 class="text-sm font-medium text-gray-700">Zdjęcia produktu ({{ images.length }})</h3>
          <button type="button" class="text-gray-400 hover:text-gray-600 cursor-pointer" aria-label="Zamknij galerię" @click="emit('close')">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div v-for="(img, idx) in images" :key="idx">
            <img :src="img" :alt="`Zdjęcie ${idx + 1}`" class="w-full h-auto rounded border border-gray-200" loading="lazy" />
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
