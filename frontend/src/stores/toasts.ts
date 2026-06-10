import { defineStore } from 'pinia'

export type ToastTone = 'success' | 'error' | 'info'

export interface ToastMessage {
  id: string
  title: string
  message?: string
  tone: ToastTone
}

export const useToastsStore = defineStore('toasts', {
  state: () => ({
    items: [] as ToastMessage[],
  }),
  actions: {
    push(toast: Omit<ToastMessage, 'id'>) {
      const id = crypto.randomUUID()
      this.items.push({ ...toast, id })
      window.setTimeout(() => this.remove(id), 4500)
    },
    success(title: string, message?: string) {
      this.push({ title, message, tone: 'success' })
    },
    error(title: string, message?: string) {
      this.push({ title, message, tone: 'error' })
    },
    info(title: string, message?: string) {
      this.push({ title, message, tone: 'info' })
    },
    remove(id: string) {
      this.items = this.items.filter((toast) => toast.id !== id)
    },
  },
})
