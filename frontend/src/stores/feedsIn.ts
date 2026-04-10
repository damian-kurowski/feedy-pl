import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/client'

export interface FeedIn {
  id: number
  name: string
  source_url: string
  record_path: string | null
  product_name: string | null
  active: boolean
  fetch_status: string
  fetch_error: string | null
  last_fetched_at: string | null
  refresh_interval: number | null
  product_count: number
  created_at: string
}

export interface XmlElement {
  path: string
  parent_path: string | null
  level: number
  element_name: string
  value: string | null
  is_leaf: boolean
  attribute: boolean
}

export interface Product {
  id: number
  product_name: string
  product_value: Record<string, unknown>
  custom_product: boolean
}

export const useFeedsInStore = defineStore('feedsIn', () => {
  const feeds = ref<FeedIn[]>([])

  async function fetchFeeds() {
    const { data } = await api.get('/feeds-in')
    feeds.value = data
  }

  async function createFeed(name: string, sourceUrl: string) {
    const { data } = await api.post('/feeds-in', { name, source_url: sourceUrl })
    feeds.value.unshift(data)
    return data
  }

  async function updateFeed(id: number, updates: Partial<FeedIn>) {
    const { data } = await api.put(`/feeds-in/${id}`, updates)
    const idx = feeds.value.findIndex((f) => f.id === id)
    if (idx !== -1) feeds.value[idx] = data
    return data
  }

  async function deleteFeed(id: number) {
    await api.delete(`/feeds-in/${id}`)
    feeds.value = feeds.value.filter((f) => f.id !== id)
  }

  async function fetchFeedXml(id: number) {
    const { data } = await api.post(`/feeds-in/${id}/fetch`)
    return data
  }

  async function getElements(id: number): Promise<XmlElement[]> {
    const { data } = await api.get(`/feeds-in/${id}/elements`)
    return data
  }

  async function getProducts(id: number): Promise<Product[]> {
    const { data } = await api.get(`/feeds-in/${id}/products`)
    return data
  }

  return { feeds, fetchFeeds, createFeed, updateFeed, deleteFeed, fetchFeedXml, getElements, getProducts }
})
