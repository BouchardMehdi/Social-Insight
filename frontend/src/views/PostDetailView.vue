<script setup lang="ts">
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { ArrowLeft, CalendarDays, Cpu, Gauge, Hash, Languages, UserRound } from '@lucide/vue'
import { useRoute } from 'vue-router'

import ErrorBanner from '../components/ErrorBanner.vue'
import LoadingState from '../components/LoadingState.vue'
import SentimentBadge from '../components/SentimentBadge.vue'
import { usePostsStore } from '../stores/posts'

const route = useRoute()
const posts = usePostsStore()

const postId = computed(() => String(route.params.id))
let pollingTimer: number | undefined

function loadPost() {
  posts.fetchPost(postId.value)
}

onMounted(() => {
  loadPost()
  pollingTimer = window.setInterval(() => posts.refreshSelectedAnalysis(), 1500)
})
onUnmounted(() => window.clearInterval(pollingTimer))
watch(postId, loadPost)
</script>

<template>
  <section class="page-stack">
    <div class="page-header">
      <div>
        <p class="eyebrow">Détail</p>
        <h1>Publication analysée</h1>
      </div>
      <RouterLink class="secondary-button" to="/posts">
        <ArrowLeft :size="16" />
        <span>Retour</span>
      </RouterLink>
    </div>

    <LoadingState v-if="posts.detailLoading" label="Chargement du post..." />
    <ErrorBanner v-else-if="posts.detailError" title="Post introuvable" :message="posts.detailError" />

    <article v-else-if="posts.selected" class="panel post-detail">
      <header class="post-detail-header">
        <div>
          <p class="eyebrow">{{ posts.selected.platform }}</p>
          <h2>{{ posts.selected.author }}</h2>
        </div>
        <SentimentBadge
          v-if="posts.selected.analysis_status === 'completed'"
          :sentiment="posts.selected.sentiment"
          :confidence="posts.selected.sentiment_confidence"
        />
        <span
          v-else
          class="analysis-status-pill"
          :class="`status-${posts.selected.analysis_status}`"
        >
          {{ posts.selected.analysis_status }}
        </span>
      </header>

      <p class="post-content">{{ posts.selected.content }}</p>

      <dl class="metadata-grid">
        <div>
          <dt><UserRound :size="16" /> Auteur</dt>
          <dd>{{ posts.selected.author }}</dd>
        </div>
        <div>
          <dt><CalendarDays :size="16" /> Date</dt>
          <dd>{{ new Date(posts.selected.created_at).toLocaleString('fr-FR') }}</dd>
        </div>
        <div v-if="posts.selected.analysis_status === 'completed'">
          <dt><Languages :size="16" /> Langue</dt>
          <dd>
            {{ posts.selected.language }} · {{ Math.round(posts.selected.language_confidence * 100) }} %
          </dd>
        </div>
        <div v-if="posts.selected.analysis_status === 'completed'">
          <dt><Gauge :size="16" /> Confiance sentiment</dt>
          <dd>{{ Math.round(posts.selected.sentiment_confidence * 100) }} %</dd>
        </div>
        <div v-if="posts.selected.analysis_status === 'completed'">
          <dt><Cpu :size="16" /> Modèle</dt>
          <dd>{{ posts.selected.model_version }}</dd>
        </div>
        <div>
          <dt><Hash :size="16" /> Statut</dt>
          <dd class="analysis-status" :class="`status-${posts.selected.analysis_status}`">
            {{ posts.selected.analysis_status }}
          </dd>
        </div>
      </dl>

      <ErrorBanner
        v-if="posts.selected.analysis_status === 'failed'"
        title="Analyse échouée"
        :message="posts.selected.analysis_error ?? 'Le moteur NLP a rencontré une erreur.'"
      />

      <section v-if="posts.selected.analysis_status === 'completed'">
        <h2>Keywords</h2>
        <div class="keyword-cloud">
          <span v-for="keyword in posts.selected.keywords" :key="keyword">{{ keyword }}</span>
        </div>
      </section>
    </article>
  </section>
</template>
