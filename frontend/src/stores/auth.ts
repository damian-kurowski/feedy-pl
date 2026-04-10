import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/client'

export interface Plan {
  id: number
  name: string
  max_products: number
  max_feeds_out: number
  price_pln: string
}

export interface User {
  id: number
  email: string
  plan: Plan
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))

  const isLoggedIn = computed(() => !!token.value)

  async function register(email: string, password: string) {
    const { data } = await api.post('/auth/register', { email, password })
    token.value = data.access_token
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    await fetchUser()
  }

  async function login(email: string, password: string) {
    const { data } = await api.post('/auth/login', { email, password })
    token.value = data.access_token
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    await fetchUser()
  }

  async function fetchUser() {
    const { data } = await api.get('/auth/me')
    user.value = data
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, token, isLoggedIn, register, login, fetchUser, logout }
})
