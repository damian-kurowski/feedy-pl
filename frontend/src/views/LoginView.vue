<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Nieprawidłowy email lub hasło'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4 bg-gray-50">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <router-link to="/" class="font-heading text-2xl font-extrabold tracking-tight text-indigo-600">Feedy</router-link>
        <p class="mt-2 text-sm text-gray-400">Zaloguj się na swoje konto</p>
      </div>

      <div class="bg-white rounded-2xl shadow-sm border border-gray-200/60 p-7">
        <div v-if="error" class="mb-5 p-3 bg-red-50 border border-red-100 text-red-600 rounded-xl text-sm">
          {{ error }}
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label for="email" class="block text-[13px] font-medium text-gray-600 mb-1.5">Email</label>
            <input
              id="email" v-model="email" type="email" required
              placeholder="ty@twojsklep.pl"
              class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
            />
          </div>
          <div>
            <label for="password" class="block text-[13px] font-medium text-gray-600 mb-1.5">Hasło</label>
            <input
              id="password" v-model="password" type="password" required
              class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
            />
          </div>
          <button
            type="submit" :disabled="loading"
            class="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer"
          >
            {{ loading ? 'Logowanie...' : 'Zaloguj się' }}
          </button>
        </form>

        <p class="mt-4 text-center">
          <router-link to="/forgot-password" class="text-[13px] text-gray-400 hover:text-indigo-600 transition-colors">Nie pamiętam hasła</router-link>
        </p>
      </div>

      <p class="mt-6 text-center text-[13px] text-gray-400">
        Nie masz konta?
        <router-link to="/register" class="text-indigo-600 hover:text-indigo-500 font-semibold transition-colors">Zarejestruj się</router-link>
      </p>
    </div>
  </div>
</template>
