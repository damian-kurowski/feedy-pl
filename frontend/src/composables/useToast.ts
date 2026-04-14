import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'info' | 'warning'

export interface ToastAction {
  label: string
  handler: () => void | Promise<void>
}

export interface Toast {
  id: number
  type: ToastType
  message: string
  duration: number
  action?: ToastAction
}

const toasts = ref<Toast[]>([])
let nextId = 1
const timers = new Map<number, ReturnType<typeof setTimeout>>()

function dismiss(id: number) {
  const t = timers.get(id)
  if (t) {
    clearTimeout(t)
    timers.delete(id)
  }
  toasts.value = toasts.value.filter((x) => x.id !== id)
}

function show(type: ToastType, message: string, opts: { duration?: number; action?: ToastAction } = {}) {
  const id = nextId++
  const duration = opts.duration ?? (type === 'error' ? 6000 : 4000)
  const toast: Toast = { id, type, message, duration, action: opts.action }
  toasts.value.push(toast)
  if (duration > 0) {
    const timer = setTimeout(() => dismiss(id), duration)
    timers.set(id, timer)
  }
  return id
}

export function useToast() {
  return {
    toasts,
    dismiss,
    success: (message: string, opts?: { duration?: number; action?: ToastAction }) => show('success', message, opts),
    error: (message: string, opts?: { duration?: number; action?: ToastAction }) => show('error', message, opts),
    info: (message: string, opts?: { duration?: number; action?: ToastAction }) => show('info', message, opts),
    warning: (message: string, opts?: { duration?: number; action?: ToastAction }) => show('warning', message, opts),
  }
}

/** Extract a user-friendly error message from an Axios/API error. */
export function getApiError(e: any, fallback = 'Coś poszło nie tak. Spróbuj ponownie.'): string {
  if (!e) return fallback
  const detail = e?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((d: any) => d?.msg || String(d)).join(' · ')
  return e?.message || fallback
}
