<script setup lang="ts">
defineProps<{
  label?: string
}>()
</script>

<template>
  <div class="loading-state" role="status" aria-live="polite">
    <span class="spinner" aria-hidden="true"></span>
    <span>{{ label ?? 'Chargement...' }}</span>
  </div>
</template>
