<script setup lang="ts">
import type { Sentiment } from '../types/social'

defineProps<{ sentiment: Sentiment; confidence?: number }>()
</script>

<template>
  <span class="sentiment-badge" :class="`sentiment-${sentiment}`">
    {{ sentiment }}
    <small v-if="confidence !== undefined">{{ Math.round(confidence * 100) }} %</small>
  </span>
</template>
