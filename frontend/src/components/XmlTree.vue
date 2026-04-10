<script setup lang="ts">
import type { XmlElement } from '../stores/feedsIn'

defineProps<{
  tree: XmlElement[]
  selected?: string
}>()

const emit = defineEmits<{
  select: [path: string]
}>()

function truncate(val: string, max = 60) {
  return val.length > max ? val.slice(0, max) + '...' : val
}
</script>

<template>
  <div class="text-sm font-mono">
    <div
      v-for="el in tree"
      :key="el.path"
      class="py-1 px-2 rounded cursor-pointer hover:bg-gray-50"
      :class="{ 'bg-indigo-100': el.path === selected }"
      :style="{ paddingLeft: (el.level - 1) * 20 + 8 + 'px' }"
      @click="emit('select', el.path)"
    >
      <span
        v-if="el.attribute"
        class="text-purple-600"
      >@{{ el.element_name }}</span>
      <span
        v-else-if="el.is_leaf"
        class="text-green-700"
      >{{ el.element_name }}</span>
      <span
        v-else
        class="text-blue-700 font-bold"
      >{{ el.element_name }}</span>
      <span v-if="el.value" class="text-gray-500 ml-1">= {{ truncate(el.value) }}</span>
    </div>
  </div>
</template>
