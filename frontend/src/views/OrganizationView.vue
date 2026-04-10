<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useOrganizationsStore, type OrgMember } from '../stores/organizations'
import { useAuthStore } from '../stores/auth'

const orgStore = useOrganizationsStore()
const authStore = useAuthStore()

const members = ref<OrgMember[]>([])
const newOrgName = ref('')
const inviteEmail = ref('')
const inviteRole = ref('member')
const error = ref('')
const success = ref('')
const loading = ref(false)

// Branding
const brandName = ref('')
const brandColor = ref('#4F46E5')
const brandLogoUrl = ref('')

onMounted(async () => {
  await orgStore.fetchOrgs()
  if (orgStore.currentOrg) {
    await loadMembers()
    loadBrandingFromOrg()
  }
})

function loadBrandingFromOrg() {
  if (!orgStore.currentOrg) return
  brandName.value = orgStore.currentOrg.brand_name || ''
  brandColor.value = orgStore.currentOrg.brand_color || '#4F46E5'
  brandLogoUrl.value = orgStore.currentOrg.brand_logo_url || ''
}

async function loadMembers() {
  if (!orgStore.currentOrg) return
  try {
    members.value = await orgStore.fetchMembers(orgStore.currentOrg.id)
  } catch {
    // user may not have permission
    members.value = []
  }
}

async function handleCreateOrg() {
  if (!newOrgName.value.trim()) return
  error.value = ''
  try {
    await orgStore.createOrg(newOrgName.value.trim())
    newOrgName.value = ''
    await loadMembers()
    success.value = 'Organizacja utworzona'
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Nie udalo sie utworzyc organizacji'
  }
}

async function selectOrg(orgId: number) {
  const org = orgStore.orgs.find((o) => o.id === orgId)
  if (org) {
    orgStore.currentOrg = org
    await loadMembers()
    loadBrandingFromOrg()
  }
}

async function handleInvite() {
  if (!orgStore.currentOrg || !inviteEmail.value.trim()) return
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    await orgStore.inviteMember(orgStore.currentOrg.id, inviteEmail.value.trim(), inviteRole.value)
    inviteEmail.value = ''
    inviteRole.value = 'member'
    success.value = 'Zaproszenie wyslane'
    await loadMembers()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Nie udalo sie zaprosic uzytkownika'
  } finally {
    loading.value = false
  }
}

async function handleRemove(memberId: number) {
  if (!orgStore.currentOrg) return
  error.value = ''
  success.value = ''
  try {
    await orgStore.removeMember(orgStore.currentOrg.id, memberId)
    success.value = 'Czlonek usuniety'
    await loadMembers()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Nie udalo sie usunac czlonka'
  }
}

async function saveBranding() {
  if (!orgStore.currentOrg) return
  error.value = ''
  success.value = ''
  try {
    await orgStore.updateOrg(orgStore.currentOrg.id, {
      brand_name: brandName.value || undefined,
      brand_color: brandColor.value || undefined,
      brand_logo_url: brandLogoUrl.value || undefined,
    } as any)
    success.value = 'Branding zapisany'
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Nie udalo sie zapisac brandingu'
  }
}

function currentUserRole(): string | null {
  const m = members.value.find((m) => m.user_id === authStore.user?.id)
  return m?.role ?? null
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Organizacja</h1>

    <!-- Alerts -->
    <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
      {{ error }}
    </div>
    <div v-if="success" class="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm">
      {{ success }}
    </div>

    <!-- Create new org -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Utworz nowa organizacje</h2>
      <form @submit.prevent="handleCreateOrg" class="flex gap-3">
        <input
          v-model="newOrgName"
          type="text"
          placeholder="Nazwa organizacji"
          class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
        />
        <button
          type="submit"
          class="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition cursor-pointer"
        >
          Utworz
        </button>
      </form>
    </div>

    <!-- Org selector -->
    <div v-if="orgStore.orgs.length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Twoje organizacje</h2>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="org in orgStore.orgs"
          :key="org.id"
          @click="selectOrg(org.id)"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition cursor-pointer',
            orgStore.currentOrg?.id === org.id
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
          ]"
        >
          {{ org.name }}
        </button>
      </div>
    </div>

    <!-- Current org details -->
    <div v-if="orgStore.currentOrg" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-800">{{ orgStore.currentOrg.name }}</h2>
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
          {{ orgStore.currentOrg.plan.name }}
        </span>
      </div>

      <!-- Members list -->
      <h3 class="text-sm font-semibold text-gray-700 mb-3">Czlonkowie</h3>
      <div v-if="members.length === 0" class="text-sm text-gray-500">Brak dostepnych czlonkow.</div>
      <ul class="divide-y divide-gray-100">
        <li v-for="member in members" :key="member.id" class="flex items-center justify-between py-3">
          <div>
            <span class="text-sm text-gray-900">{{ member.email }}</span>
            <span
              class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
              :class="{
                'bg-yellow-100 text-yellow-800': member.role === 'owner',
                'bg-blue-100 text-blue-800': member.role === 'admin',
                'bg-gray-100 text-gray-600': member.role === 'member',
              }"
            >
              {{ member.role }}
            </span>
          </div>
          <button
            v-if="currentUserRole() === 'owner' && member.user_id !== authStore.user?.id"
            @click="handleRemove(member.id)"
            class="text-sm text-red-600 hover:text-red-800 cursor-pointer"
          >
            Usun
          </button>
        </li>
      </ul>

      <!-- Invite form -->
      <div v-if="currentUserRole() === 'owner' || currentUserRole() === 'admin'" class="mt-6 pt-4 border-t border-gray-100">
        <h3 class="text-sm font-semibold text-gray-700 mb-3">Zapros nowego czlonka</h3>
        <form @submit.prevent="handleInvite" class="flex gap-3 items-end">
          <div class="flex-1">
            <label class="block text-xs text-gray-500 mb-1">Email</label>
            <input
              v-model="inviteEmail"
              type="email"
              placeholder="user@example.com"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Rola</label>
            <select
              v-model="inviteRole"
              class="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            >
              <option value="member">member</option>
              <option value="admin">admin</option>
            </select>
          </div>
          <button
            type="submit"
            :disabled="loading"
            class="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition cursor-pointer disabled:opacity-50"
          >
            Zapros
          </button>
        </form>
      </div>
    </div>

    <!-- Branding / White-label -->
    <div v-if="orgStore.currentOrg && (currentUserRole() === 'owner' || currentUserRole() === 'admin')" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-2">White-label / Branding</h2>
      <p class="text-sm text-gray-500 mb-4">Dostosuj wyglad panelu dla Twoich klientow.</p>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nazwa firmy</label>
          <input v-model="brandName" type="text" placeholder="np. Moja Agencja"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Kolor glowny</label>
          <div class="flex items-center gap-3">
            <input v-model="brandColor" type="color" class="w-12 h-10 border rounded cursor-pointer" />
            <input v-model="brandColor" type="text" placeholder="#4F46E5"
              class="border border-gray-300 rounded-lg px-3 py-2 w-32 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">URL logo</label>
          <input v-model="brandLogoUrl" type="url" placeholder="https://..."
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
        </div>
        <button @click="saveBranding"
          class="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition cursor-pointer">
          Zapisz branding
        </button>
      </div>

      <!-- Preview -->
      <div v-if="brandName || brandLogoUrl" class="mt-6 p-4 rounded-lg border" :style="{ borderColor: brandColor }">
        <p class="text-sm text-gray-500 mb-2">Podglad:</p>
        <div class="flex items-center gap-3">
          <img v-if="brandLogoUrl" :src="brandLogoUrl" class="h-8" alt="Logo" />
          <span class="text-xl font-bold" :style="{ color: brandColor }">{{ brandName || 'Feedy' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
