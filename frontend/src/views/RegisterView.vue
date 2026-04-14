<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const consent = ref(false)

// Password strength: 0-4
const passwordStrength = computed(() => {
  const p = password.value
  if (!p) return 0
  let score = 0
  if (p.length >= 8) score++
  if (p.length >= 12) score++
  if (/[A-Z]/.test(p) && /[a-z]/.test(p)) score++
  if (/\d/.test(p)) score++
  if (/[^a-zA-Z0-9]/.test(p)) score++
  return Math.min(score, 4)
})
const strengthLabel = computed(() => ['Bardzo słabe', 'Słabe', 'Średnie', 'Mocne', 'Bardzo mocne'][passwordStrength.value])
const strengthColor = computed(() => ['bg-red-400', 'bg-orange-400', 'bg-amber-400', 'bg-lime-500', 'bg-green-500'][passwordStrength.value])
const strengthTextColor = computed(() => ['text-red-600', 'text-orange-600', 'text-amber-600', 'text-lime-600', 'text-green-600'][passwordStrength.value])

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
        <p class="mt-2 text-sm text-gray-400">Załóż darmowe konto</p>
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
            <label for="password" class="block text-[13px] font-medium text-gray-600 mb-1.5">Hasło (min. 8 znaków)</label>
            <input
              id="password" v-model="password" type="password" required minlength="8"
              class="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
            />
            <div v-if="password" class="mt-2">
              <div class="flex gap-1 mb-1">
                <div v-for="i in 4" :key="i" class="h-1 flex-1 rounded-full transition-colors"
                  :class="i <= passwordStrength ? strengthColor : 'bg-gray-200'"></div>
              </div>
              <p class="text-[11px]" :class="strengthTextColor">{{ strengthLabel }}</p>
            </div>
          </div>

          <label class="flex items-start gap-2.5 text-[13px] text-gray-500 pt-1">
            <input v-model="consent" type="checkbox" required class="mt-0.5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500/20" />
            <span>Akceptuję <router-link to="/regulamin" class="text-indigo-600 hover:underline">regulamin</router-link>
            oraz <router-link to="/polityka-prywatnosci" class="text-indigo-600 hover:underline">politykę prywatności</router-link>.</span>
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
          Darmowy plan: 200 produktów, 1 feed wyjściowy
        </p>
        <p class="text-[13px] text-gray-400">
          Masz już konto?
          <router-link to="/login" class="text-indigo-600 hover:text-indigo-500 font-semibold transition-colors">Zaloguj się</router-link>
        </p>
      </div>
    </div>
  </div>
</template>
