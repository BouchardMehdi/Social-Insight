<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  label: string
  value: string | number
  tone: 'cyan' | 'green' | 'amber' | 'rose'
  icon: Component
}>()
</script>

<template>
  <article class="stat-card" :class="`tone-${tone}`">
    <div>
      <span class="stat-label">{{ label }}</span>
      <strong>{{ value }}</strong>
    </div>
    <component :is="icon" :size="22" aria-hidden="true" />
  </article>
</template>
