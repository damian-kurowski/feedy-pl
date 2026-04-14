<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import api from '../api/client'
import { useToast, getApiError } from '../composables/useToast'

interface Notification {
  id: number
  created_at: string
  type: 'alert' | 'recommendation' | 'system' | 'success'
  title: string
  body: string | null
  link: string | null
  read_at: string | null
}

const open = ref(false)
const items = ref<Notification[]>([])
const unreadCount = ref(0)
const loading = ref(false)
const toast = useToast()
let pollTimer: ReturnType<typeof setInterval> | null = null

async function fetchUnreadCount() {
  try {
    const { data } = await api.get('/notifications/unread-count')
    unreadCount.value = data.count || 0
  } catch {}
}

async function fetchList() {
  loading.value = true
  try {
    const { data } = await api.get('/notifications', { params: { limit: 20 } })
    items.value = data
  } catch (e) {
    toast.error(getApiError(e, 'Nie udało się załadować powiadomień'))
  } finally {
    loading.value = false
  }
}

async function toggleOpen() {
  open.value = !open.value
  if (open.value) {
    await fetchList()
  }
}

async function markAsRead(n: Notification) {
  if (n.read_at) return
  try {
    await api.post(`/notifications/${n.id}/read`)
    n.read_at = new Date().toISOString()
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch {}
}

async function markAllRead() {
  try {
    await api.post('/notifications/read-all')
    items.value.forEach((n) => { if (!n.read_at) n.read_at = new Date().toISOString() })
    unreadCount.value = 0
  } catch (e) {
    toast.error(getApiError(e, 'Nie udało się oznaczyć jako przeczytane'))
  }
}

async function dismiss(n: Notification) {
  try {
    await api.delete(`/notifications/${n.id}`)
    items.value = items.value.filter((x) => x.id !== n.id)
    if (!n.read_at) unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch {}
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'przed chwilą'
  if (m < 60) return `${m} min temu`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h} godz. temu`
  const d = Math.floor(h / 24)
  return `${d} dni temu`
}

function colorClass(type: string) {
  switch (type) {
    case 'alert': return 'bg-red-50 border-red-200'
    case 'recommendation': return 'bg-amber-50 border-amber-200'
    case 'success': return 'bg-green-50 border-green-200'
    default: return 'bg-indigo-50 border-indigo-200'
  }
}

function iconColor(type: string) {
  switch (type) {
    case 'alert': return 'text-red-600'
    case 'recommendation': return 'text-amber-600'
    case 'success': return 'text-green-600'
    default: return 'text-indigo-600'
  }
}

function onClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (open.value && !target.closest('[data-notification-root]')) {
    open.value = false
  }
}

onMounted(() => {
  fetchUnreadCount()
  pollTimer = setInterval(fetchUnreadCount, 60000)
  document.addEventListener('click', onClickOutside)
})
onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  document.removeEventListener('click', onClickOutside)
})
</script>

<template>
  <div class="relative" data-notification-root>
    <button
      type="button"
      class="relative p-1.5 text-gray-400 hover:text-gray-700 cursor-pointer"
      :aria-label="`Powiadomienia (${unreadCount} nieprzeczytanych)`"
      @click.stop="toggleOpen"
    >
      <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
      </svg>
      <span
        v-if="unreadCount > 0"
        class="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 px-1 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center"
      >
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>

    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <div
        v-if="open"
        class="absolute right-0 mt-2 w-80 sm:w-96 bg-white border border-gray-200 rounded-2xl shadow-2xl z-50 overflow-hidden origin-top-right"
      >
        <div class="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h3 class="font-heading text-sm font-bold text-gray-900">Powiadomienia</h3>
          <button
            v-if="unreadCount > 0"
            type="button"
            class="text-xs text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer"
            @click="markAllRead"
          >
            Oznacz wszystkie jako przeczytane
          </button>
        </div>

        <div class="max-h-[420px] overflow-y-auto">
          <div v-if="loading" class="p-6 text-center text-sm text-gray-400">Ładowanie...</div>

          <div v-else-if="items.length === 0" class="p-8 text-center">
            <div class="w-12 h-12 mx-auto rounded-xl bg-gray-100 flex items-center justify-center mb-3">
              <svg class="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" /></svg>
            </div>
            <p class="text-sm text-gray-500">Brak powiadomień</p>
          </div>

          <ul v-else class="divide-y divide-gray-100">
            <li
              v-for="n in items"
              :key="n.id"
              class="p-3 sm:p-4 hover:bg-gray-50 transition cursor-pointer relative"
              :class="{ 'bg-indigo-50/30': !n.read_at }"
              @click="markAsRead(n)"
            >
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 rounded-lg shrink-0 border flex items-center justify-center" :class="colorClass(n.type)">
                  <svg v-if="n.type === 'alert'" class="w-4 h-4" :class="iconColor(n.type)" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>
                  <svg v-else-if="n.type === 'success'" class="w-4 h-4" :class="iconColor(n.type)" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                  <svg v-else-if="n.type === 'recommendation'" class="w-4 h-4" :class="iconColor(n.type)" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.354a15.998 15.998 0 01-3 0M9.75 21a9.026 9.026 0 01-1.5-3.272m11.25 0a9.026 9.026 0 01-1.5 3.272M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  <svg v-else class="w-4 h-4" :class="iconColor(n.type)" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between gap-2">
                    <p class="text-sm font-semibold text-gray-900 leading-snug">{{ n.title }}</p>
                    <button type="button" class="text-gray-300 hover:text-gray-600 shrink-0 cursor-pointer" aria-label="Usuń" @click.stop="dismiss(n)">
                      <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                  </div>
                  <p v-if="n.body" class="text-xs text-gray-600 mt-1 leading-snug line-clamp-2">{{ n.body }}</p>
                  <div class="flex items-center gap-2 mt-2 text-[11px] text-gray-400">
                    <span>{{ timeAgo(n.created_at) }}</span>
                    <a v-if="n.link" :href="n.link" class="text-indigo-600 hover:text-indigo-800 font-medium" @click.stop>Otwórz →</a>
                  </div>
                </div>
                <div v-if="!n.read_at" class="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-2 shrink-0"></div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </Transition>
  </div>
</template>
