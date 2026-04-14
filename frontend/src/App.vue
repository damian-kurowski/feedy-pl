<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import CookieConsent from './components/CookieConsent.vue'
import ToastContainer from './components/ToastContainer.vue'

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
      <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div class="flex justify-between h-14 items-center gap-2">
          <div class="flex items-center gap-3 sm:gap-7 min-w-0">
            <router-link to="/dashboard" class="font-heading text-lg font-extrabold tracking-tight text-indigo-600 shrink-0">Feedy</router-link>
            <router-link to="/dashboard" class="text-[13px] font-medium text-gray-500 hover:text-gray-900 transition-colors">Dashboard</router-link>
            <router-link to="/oferty" class="text-[13px] font-medium text-gray-500 hover:text-gray-900 transition-colors hidden sm:inline">Oferty</router-link>
          </div>
          <div class="flex items-center gap-2 sm:gap-4 shrink-0">
            <span class="hidden md:inline text-[13px] text-gray-400 truncate max-w-[180px]">{{ auth.user?.email }}</span>
            <span
              v-if="auth.user?.plan"
              class="inline-flex items-center px-2 sm:px-2.5 py-0.5 rounded-md text-[10px] sm:text-[11px] font-semibold tracking-wide uppercase bg-indigo-600 text-white"
            >
              {{ auth.user.plan.name }}
            </span>
            <router-link
              to="/organization"
              class="hidden sm:inline text-[13px] text-gray-500 hover:text-gray-900 transition-colors"
            >
              Organizacja
            </router-link>
            <router-link
              to="/organization"
              class="sm:hidden text-gray-500 hover:text-gray-900"
              title="Organizacja"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" /></svg>
            </router-link>
            <button
              @click="handleLogout"
              class="text-[13px] text-gray-400 hover:text-red-600 transition-colors cursor-pointer"
              title="Wyloguj"
            >
              <span class="hidden sm:inline">Wyloguj</span>
              <svg class="sm:hidden w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" /></svg>
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
              Zarejestruj się
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <router-view />
    <CookieConsent />
    <ToastContainer />
  </div>
</template>
