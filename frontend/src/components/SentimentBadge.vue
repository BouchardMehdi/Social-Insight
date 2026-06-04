<script setup lang="ts">
import type { Sentiment } from '../types/social'

defineProps<{ sentiment: Sentiment }>()
</script>

<template>
  <span class="sentiment-badge" :class="`sentiment-${sentiment}`">{{ sentiment }}</span>
</template>
