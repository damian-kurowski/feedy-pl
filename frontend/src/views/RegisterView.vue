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
const consent = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(email.value, password.value)
    router.push('/dashboard')
  } catch (e: any) {
    const data = e.response?.data
    if (data?.email) {
      error.value = data.email.join(' ')
    } else if (data?.password) {
      error.value = data.password.join(' ')
    } else {
      error.value = data?.detail || 'Nie udało się utworzyć konta'
    }
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
        <p class="mt-2 text-sm text-gray-400">Zaloz darmowe konto</p>
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
            <label for="password" class="block text-[13px] font-medium text-gray-600 mb-1.5">Haslo (min. 6 znakow)</label>
            <input
              id="password" v-model="password" type="password" required minlength="6"
              class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
            />
          </div>

          <label class="flex items-start gap-2.5 text-[13px] text-gray-500 pt-1">
            <input v-model="consent" type="checkbox" required class="mt-0.5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500/20" />
            <span>Akceptuje <router-link to="/regulamin" class="text-indigo-600 hover:underline">regulamin</router-link>
            oraz <router-link to="/polityka-prywatnosci" class="text-indigo-600 hover:underline">polityke prywatnosci</router-link>.</span>
          </label>

          <button
            type="submit" :disabled="loading || !consent"
            class="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl transition-all hover:shadow-lg hover:shadow-indigo-500/20 cursor-pointer"
          >
            {{ loading ? 'Rejestracja...' : 'Zacznij za darmo' }}
          </button>
        </form>
      </div>

      <div class="mt-6 text-center space-y-2">
        <p class="text-[12px] text-gray-400 flex items-center justify-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
          Darmowy plan: 100 produktow, 1 feed wyjsciowy
        </p>
        <p class="text-[13px] text-gray-400">
          Masz juz konto?
          <router-link to="/login" class="text-indigo-600 hover:text-indigo-500 font-semibold transition-colors">Zaloguj sie</router-link>
        </p>
      </div>
    </div>
  </div>
</template>
