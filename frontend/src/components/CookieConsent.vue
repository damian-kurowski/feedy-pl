<script setup lang="ts">
import { ref, onMounted } from 'vue'

const visible = ref(false)

onMounted(() => {
  if (!localStorage.getItem('cookies_accepted')) {
    visible.value = true
  }
})

function accept() {
  localStorage.setItem('cookies_accepted', '1')
  visible.value = false
}
</script>

<template>
  <div
    v-if="visible"
    class="fixed bottom-0 left-0 right-0 z-50 bg-gray-900 text-white px-4 py-4 sm:px-6"
  >
    <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
      <p class="text-sm text-gray-300 text-center sm:text-left">
        Używamy plików cookie do prawidłowego działania serwisu. Kontynuując, akceptujesz naszą
        <router-link to="/polityka-cookies" class="text-indigo-400 underline hover:text-indigo-300">politykę cookies</router-link>.
      </p>
      <button
        @click="accept"
        class="shrink-0 px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition cursor-pointer"
      >
        Akceptuję
      </button>
    </div>
  </div>
</template>
