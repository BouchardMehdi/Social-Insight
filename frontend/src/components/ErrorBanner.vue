<script setup lang="ts">
import { AlertCircle } from '@lucide/vue'

defineProps<{
  title?: string
  message: string
}>()
</script>

<template>
  <section class="error-banner" role="alert">
    <AlertCircle :size="18" />
    <div>
      <strong>{{ title ?? 'Erreur' }}</strong>
      <p>{{ message }}</p>
    </div>
  </section>
</template>
