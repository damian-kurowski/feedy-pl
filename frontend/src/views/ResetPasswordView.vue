<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/client'

const route = useRoute()
const router = useRouter()

const token = ref((route.query.token as string) || '')
const newPassword = ref('')
const confirmPassword = ref('')
const error = ref('')
const success = ref(false)
const loading = ref(false)

async function handleSubmit() {
  error.value = ''

  if (newPassword.value.length < 6) {
    error.value = 'Hasło musi mieć co najmniej 6 znaków.'
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Hasła nie są identyczne.'
    return
  }

  loading.value = true
  try {
    await api.post('/auth/reset-password', {
      token: token.value,
      new_password: newPassword.value,
    })
    success.value = true
    setTimeout(() => {
      router.push('/login')
    }, 3000)
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Token jest nieprawidłowy lub wygasł.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="bg-white rounded-lg shadow-md w-full max-w-md p-8">
      <h1 class="text-2xl font-bold text-center text-gray-900 mb-8">Ustaw nowe hasło</h1>

      <div v-if="success" class="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-md text-sm">
        Hasło zostało zmienione. Przekierowanie do logowania...
      </div>

      <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
        {{ error }}
      </div>

      <form v-if="!success" @submit.prevent="handleSubmit" class="space-y-5">
        <div>
          <label for="new-password" class="block text-sm font-medium text-gray-700 mb-1">Nowe hasło</label>
          <input
            id="new-password"
            v-model="newPassword"
            type="password"
            required
            minlength="6"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        <div>
          <label for="confirm-password" class="block text-sm font-medium text-gray-700 mb-1">Potwierdź hasło</label>
          <input
            id="confirm-password"
            v-model="confirmPassword"
            type="password"
            required
            minlength="6"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-2 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 cursor-pointer"
        >
          {{ loading ? 'Zapisywanie...' : 'Ustaw nowe hasło' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-gray-600">
        <router-link to="/login" class="text-indigo-600 hover:text-indigo-500 font-medium">Wróć do logowania</router-link>
      </p>
    </div>
  </div>
</template>
