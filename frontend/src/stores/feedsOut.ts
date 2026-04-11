import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/client'

export interface FeedOut {
  id: number
  feed_in_id: number
  name: string
  type: string
  template: string | null
  active: boolean
  link_out: string
  rules: any[] | null
  category_mapping: Record<string, string> | null
  created_at: string
}

export interface StructureElement {
  id?: number
  sort_key: number
  custom_element: boolean
  path_in: string | null
  constant_value?: string | null
  level_out: number
  path_out: string
  parent_path_out: string | null
  element_name_out: string
  is_leaf: boolean
  attribute: boolean
  condition: 'always' | 'if_not_empty'
}

export const useFeedsOutStore = defineStore('feedsOut', () => {
  const feeds = ref<FeedOut[]>([])
  const validationCache = ref<Record<number, { score: number; label: string; timestamp: number }>>({})

  async function getQualityScore(id: number): Promise<{ score: number; label: string } | null> {
    const cached = validationCache.value[id]
    if (cached && Date.now() - cached.timestamp < 5 * 60 * 1000) {
      return { score: cached.score, label: cached.label }
    }
    try {
      const { data } = await api.get(`/feeds-out/${id}/validate`)
      const result = { score: data.quality_score, label: data.quality_label }
      validationCache.value[id] = { ...result, timestamp: Date.now() }
      return result
    } catch {
      return null
    }
  }

  async function fetchFeeds() {
    const { data } = await api.get('/feeds-out')
    feeds.value = data
  }

  async function createFeed(body: { feed_in_id: number; name: string; type: string; template?: string }) {
    const { data } = await api.post('/feeds-out', body)
    feeds.value.unshift(data)
    return data
  }

  async function updateFeed(id: number, body: Partial<FeedOut>) {
    const { data } = await api.put(`/feeds-out/${id}`, body)
    const idx = feeds.value.findIndex((f) => f.id === id)
    if (idx !== -1) feeds.value[idx] = data
    return data as FeedOut
  }

  async function deleteFeed(id: number) {
    await api.delete(`/feeds-out/${id}`)
    feeds.value = feeds.value.filter((f) => f.id !== id)
  }

  async function getStructure(id: number): Promise<StructureElement[]> {
    const { data } = await api.get(`/feeds-out/${id}/structure`)
    return data
  }

  async function updateStructure(id: number, structure: StructureElement[]): Promise<StructureElement[]> {
    const { data } = await api.put(`/feeds-out/${id}/structure`, structure)
    return data
  }

  async function generateFeed(id: number) {
    const { data } = await api.post(`/feeds-out/${id}/generate`)
    return data
  }

  async function getFeedProducts(feedOutId: number, search: string = ''): Promise<any[]> {
    const params = search ? { search } : {}
    const { data } = await api.get(`/feeds-out/${feedOutId}/products`, { params })
    return data
  }

  async function upsertOverride(feedOutId: number, productId: number, body: { field_overrides: Record<string, string>; excluded: boolean }) {
    const { data } = await api.put(`/feeds-out/${feedOutId}/products/${productId}/override`, body)
    return data
  }

  async function deleteOverride(feedOutId: number, productId: number) {
    await api.delete(`/feeds-out/${feedOutId}/products/${productId}/override`)
  }

  async function getPlatformInfo(platform: string) {
    const { data } = await api.get(`/feeds-out/platform-info/${platform}`)
    return data
  }

  async function getPlatforms() {
    const { data } = await api.get('/feeds-out/platforms')
    return data
  }

  async function getGoogleCategories(q: string): Promise<string[]> {
    const { data } = await api.get('/feeds-out/google-categories', { params: { q } })
    return data.categories
  }

  return { feeds, fetchFeeds, createFeed, updateFeed, deleteFeed, getStructure, updateStructure, generateFeed, validationCache, getQualityScore, getFeedProducts, upsertOverride, deleteOverride, getPlatformInfo, getPlatforms, getGoogleCategories }
})
