<script setup lang="ts">
import { CheckCircle2, Info, TriangleAlert, X } from '@lucide/vue'

import { useToastsStore } from '../stores/toasts'

const toasts = useToastsStore()

const icons = {
  success: CheckCircle2,
  error: TriangleAlert,
  info: Info,
}
</script>

<template>
  <div class="toast-stack" aria-live="polite" aria-relevant="additions removals">
    <article v-for="toast in toasts.items" :key="toast.id" class="toast" :class="`toast-${toast.tone}`">
      <component :is="icons[toast.tone]" :size="18" />
      <div>
        <strong>{{ toast.title }}</strong>
        <p v-if="toast.message">{{ toast.message }}</p>
      </div>
      <button class="toast-close" type="button" @click="toasts.remove(toast.id)" aria-label="Fermer">
        <X :size="16" />
      </button>
    </article>
  </div>
</template>
