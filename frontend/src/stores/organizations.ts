import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/client'

export interface OrgPlan {
  id: number
  name: string
  max_products: number | null
  max_feeds_out: number | null
  price_pln: number
}

export interface Org {
  id: number
  name: string
  plan: OrgPlan
  brand_name: string | null
  brand_color: string | null
  brand_logo_url: string | null
  custom_domain: string | null
}

export interface OrgMember {
  id: number
  user_id: number
  email: string
  role: string
}

export const useOrganizationsStore = defineStore('organizations', () => {
  const orgs = ref<Org[]>([])
  const currentOrg = ref<Org | null>(null)

  async function fetchOrgs() {
    const { data } = await api.get('/organizations')
    orgs.value = data
    if (data.length > 0 && !currentOrg.value) {
      currentOrg.value = data[0]
    }
  }

  async function createOrg(name: string): Promise<Org> {
    const { data } = await api.post('/organizations', { name })
    orgs.value.push(data)
    currentOrg.value = data
    return data
  }

  async function fetchMembers(orgId: number): Promise<OrgMember[]> {
    const { data } = await api.get(`/organizations/${orgId}/members`)
    return data
  }

  async function inviteMember(orgId: number, email: string, role: string = 'member'): Promise<OrgMember> {
    const { data } = await api.post(`/organizations/${orgId}/invite`, { email, role })
    return data
  }

  async function removeMember(orgId: number, memberId: number): Promise<void> {
    await api.delete(`/organizations/${orgId}/members/${memberId}`)
  }

  async function updateOrg(orgId: number, payload: Partial<Org>): Promise<Org> {
    const { data } = await api.put(`/organizations/${orgId}`, payload)
    const idx = orgs.value.findIndex((o) => o.id === orgId)
    if (idx !== -1) {
      orgs.value[idx] = data
    }
    if (currentOrg.value?.id === orgId) {
      currentOrg.value = data
    }
    return data
  }

  return { orgs, currentOrg, fetchOrgs, createOrg, updateOrg, fetchMembers, inviteMember, removeMember }
})
