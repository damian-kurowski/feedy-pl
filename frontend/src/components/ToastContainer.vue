<script setup lang="ts">
import { useToast } from '../composables/useToast'

const { toasts, dismiss } = useToast()

function colorFor(type: string) {
  switch (type) {
    case 'success': return 'border-green-200 bg-green-50 text-green-900'
    case 'error':   return 'border-red-200 bg-red-50 text-red-900'
    case 'warning': return 'border-amber-200 bg-amber-50 text-amber-900'
    default:        return 'border-indigo-200 bg-indigo-50 text-indigo-900'
  }
}

function iconColorFor(type: string) {
  switch (type) {
    case 'success': return 'text-green-600'
    case 'error':   return 'text-red-600'
    case 'warning': return 'text-amber-600'
    default:        return 'text-indigo-600'
  }
}

async function runAction(toastId: number, handler: () => void | Promise<void>) {
  try {
    await handler()
  } finally {
    dismiss(toastId)
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed top-4 right-4 z-[100] flex flex-col gap-2 max-w-sm pointer-events-none"
      role="region"
      aria-label="Powiadomienia"
      aria-live="polite"
    >
      <TransitionGroup name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="pointer-events-auto flex items-start gap-3 px-4 py-3 rounded-xl border shadow-lg backdrop-blur-sm"
          :class="colorFor(t.type)"
          role="status"
        >
          <svg v-if="t.type === 'success'" class="w-5 h-5 shrink-0" :class="iconColorFor(t.type)" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
          <svg v-else-if="t.type === 'error'" class="w-5 h-5 shrink-0" :class="iconColorFor(t.type)" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>
          <svg v-else-if="t.type === 'warning'" class="w-5 h-5 shrink-0" :class="iconColorFor(t.type)" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>
          <svg v-else class="w-5 h-5 shrink-0" :class="iconColorFor(t.type)" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" /></svg>

          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium leading-snug">{{ t.message }}</p>
            <button
              v-if="t.action"
              type="button"
              class="mt-1 text-xs font-semibold underline hover:no-underline cursor-pointer"
              @click="runAction(t.id, t.action.handler)"
            >
              {{ t.action.label }}
            </button>
          </div>

          <button
            type="button"
            class="text-gray-400 hover:text-gray-700 shrink-0 cursor-pointer"
            aria-label="Zamknij powiadomienie"
            @click="dismiss(t.id)"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active, .toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(20px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
