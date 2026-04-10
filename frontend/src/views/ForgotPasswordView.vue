<script setup lang="ts">
import { ref } from 'vue'
import api from '../api/client'

const email = ref('')
const success = ref(false)
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await api.post('/auth/forgot-password', { email: email.value })
    success.value = true
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Wystąpił błąd. Spróbuj ponownie.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="bg-white rounded-lg shadow-md w-full max-w-md p-8">
      <h1 class="text-2xl font-bold text-center text-gray-900 mb-8">Resetuj hasło</h1>

      <div v-if="success" class="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-md text-sm">
        Sprawdź swoją skrzynkę email.
      </div>

      <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
        {{ error }}
      </div>

      <form v-if="!success" @submit.prevent="handleSubmit" class="space-y-5">
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-2 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 cursor-pointer"
        >
          {{ loading ? 'Wysyłanie...' : 'Wyślij link do resetowania' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-gray-600">
        <router-link to="/login" class="text-indigo-600 hover:text-indigo-500 font-medium">Wróć do logowania</router-link>
      </p>
    </div>
  </div>
</template>
