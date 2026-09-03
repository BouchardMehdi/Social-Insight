<script setup lang="ts">
import { onMounted, onUnmounted, reactive } from 'vue'
import { ChevronLeft, ChevronRight, Eye, Search } from '@lucide/vue'

import ErrorBanner from '../components/ErrorBanner.vue'
import LoadingState from '../components/LoadingState.vue'
import SentimentBadge from '../components/SentimentBadge.vue'
import { usePostsStore } from '../stores/posts'
import type { Sentiment } from '../types/social'

const posts = usePostsStore()
const filters = reactive({
  platform: '',
  sentiment: '' as Sentiment | '',
  keyword: '',
})
let pollingTimer: number | undefined

async function fetchPage(offset = posts.offset) {
  posts.offset = offset
  await posts.fetchPosts({
    platform: filters.platform || undefined,
    sentiment: filters.sentiment || undefined,
    keyword: filters.keyword || undefined,
  })
}

onMounted(() => {
  fetchPage(0)
  pollingTimer = window.setInterval(() => posts.refreshPending(), 1500)
})
onUnmounted(() => window.clearInterval(pollingTimer))
</script>

<template>
  <section class="page-stack">
    <div class="page-header">
      <div>
        <p class="eyebrow">Exploration</p>
        <h1>Posts ingérés</h1>
      </div>
    </div>

    <ErrorBanner v-if="posts.error" title="Chargement impossible" :message="posts.error" />

    <form class="toolbar" @submit.prevent="fetchPage(0)">
      <label class="input-with-icon">
        <Search :size="17" />
        <input v-model="filters.keyword" type="search" placeholder="Keyword" />
      </label>
      <input v-model="filters.platform" type="text" placeholder="Plateforme" />
      <select v-model="filters.sentiment">
        <option value="">Tous sentiments</option>
        <option value="positive">Positive</option>
        <option value="neutral">Neutral</option>
        <option value="negative">Negative</option>
      </select>
      <button class="primary-button" type="submit" :disabled="posts.loading">
        <Search :size="16" />
        <span>Filtrer</span>
      </button>
    </form>

    <section class="table-panel">
      <LoadingState v-if="posts.loading" label="Chargement des posts..." />
      <table v-else>
        <thead>
          <tr>
            <th>Auteur</th>
            <th>Plateforme</th>
            <th>Sentiment</th>
            <th>Date</th>
            <th>Contenu</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="post in posts.items" :key="post.id">
            <td>{{ post.author }}</td>
            <td>{{ post.platform }}</td>
            <td>
              <SentimentBadge
                v-if="post.analysis_status === 'completed'"
                :sentiment="post.sentiment"
                :confidence="post.sentiment_confidence"
              />
              <span v-else class="analysis-status-pill" :class="`status-${post.analysis_status}`">
                {{ post.analysis_status }}
              </span>
            </td>
            <td>{{ new Date(post.created_at).toLocaleDateString('fr-FR') }}</td>
            <td class="content-cell">{{ post.content }}</td>
            <td>
              <RouterLink class="icon-button" :to="`/posts/${post.id}`" aria-label="Voir le détail">
                <Eye :size="18" />
              </RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!posts.loading && !posts.items.length" class="empty-state">
        Aucun post ne correspond aux filtres
      </p>
    </section>

    <footer class="pagination-bar">
      <span v-if="posts.total">
        {{ posts.offset + 1 }}-{{ Math.min(posts.offset + posts.limit, posts.total) }} / {{ posts.total }}
      </span>
      <span v-else>0 / 0</span>
      <div>
        <button
          class="icon-button"
          :disabled="posts.loading || posts.offset === 0"
          @click="fetchPage(Math.max(0, posts.offset - posts.limit))"
        >
          <ChevronLeft :size="18" />
        </button>
        <button
          class="icon-button"
          :disabled="posts.loading || posts.offset + posts.limit >= posts.total"
          @click="fetchPage(posts.offset + posts.limit)"
        >
          <ChevronRight :size="18" />
        </button>
      </div>
    </footer>
  </section>
</template>
