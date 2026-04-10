<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import CookieConsent from './components/CookieConsent.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

onMounted(async () => {
  if (auth.token) {
    try {
      await auth.fetchUser()
    } catch {
      auth.logout()
    }
  }
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Logged-in nav -->
    <nav v-if="auth.isLoggedIn" class="bg-white/80 backdrop-blur-lg border-b border-gray-200/60 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-14 items-center">
          <div class="flex items-center gap-7">
            <router-link to="/dashboard" class="font-heading text-lg font-extrabold tracking-tight text-indigo-600">Feedy</router-link>
            <router-link to="/dashboard" class="text-[13px] font-medium text-gray-500 hover:text-gray-900 transition-colors">Dashboard</router-link>
          </div>
          <div class="flex items-center gap-4">
            <span class="text-[13px] text-gray-400">{{ auth.user?.email }}</span>
            <span
              v-if="auth.user?.plan"
              class="inline-flex items-center px-2.5 py-0.5 rounded-md text-[11px] font-semibold tracking-wide uppercase bg-indigo-600 text-white"
            >
              {{ auth.user.plan.name }}
            </span>
            <router-link
              to="/organization"
              class="text-[13px] text-gray-500 hover:text-gray-900 transition-colors"
            >
              Organizacja
            </router-link>
            <button
              @click="handleLogout"
              class="text-[13px] text-gray-400 hover:text-red-600 transition-colors cursor-pointer"
            >
              Wyloguj
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Landing page nav (not logged in) -->
    <nav v-else-if="route.name === 'landing'" class="absolute top-0 left-0 right-0 z-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16 items-center">
          <router-link to="/" class="font-heading text-lg font-extrabold tracking-tight text-white">Feedy</router-link>
          <div class="flex items-center gap-4">
            <router-link
              to="/login"
              class="text-[13px] font-medium text-white/80 hover:text-white transition-colors"
            >
              Zaloguj
            </router-link>
            <router-link
              to="/register"
              class="text-[13px] font-semibold px-5 py-2 rounded-lg bg-white text-indigo-700 hover:bg-indigo-50 transition-all shadow-sm"
            >
              Zarejestruj sie
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <router-view />
    <CookieConsent />
  </div>
</template>
