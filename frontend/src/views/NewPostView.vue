<script setup lang="ts">
import { reactive, ref } from 'vue'
import { Send, Sparkles } from '@lucide/vue'

import { getApiErrorMessage } from '../api/errors'
import { analyzeText } from '../api/socialInsight'
import ErrorBanner from '../components/ErrorBanner.vue'
import SentimentBadge from '../components/SentimentBadge.vue'
import { usePostsStore } from '../stores/posts'
import { useToastsStore } from '../stores/toasts'
import type { AnalyzeResponse } from '../types/social'

const posts = usePostsStore()
const toasts = useToastsStore()
const form = reactive({
  platform: 'twitter',
  author: '',
  content: '',
})
const loading = ref(false)
const analyzing = ref(false)
const created = ref(false)
const error = ref('')
const analysis = ref<AnalyzeResponse | null>(null)

async function previewAnalysis() {
  if (!form.content.trim()) return
  analyzing.value = true
  error.value = ''
  try {
    analysis.value = await analyzeText(form.content)
    toasts.info('Analyse terminée', 'Le contenu a été analysé sans insertion.')
  } catch (caughtError) {
    error.value = getApiErrorMessage(caughtError, "Impossible d'analyser le texte")
    toasts.error('Analyse impossible', error.value)
  } finally {
    analyzing.value = false
  }
}

async function submitPost() {
  loading.value = true
  created.value = false
  error.value = ''
  try {
    const post = await posts.create(form)
    analysis.value = {
      language: post.language,
      sentiment: post.sentiment,
      keywords: post.keywords,
    }
    form.author = ''
    form.content = ''
    created.value = true
    toasts.success('Post créé', `Le post ${post.platform} a été analysé et enregistré.`)
  } catch (caughtError) {
    error.value = getApiErrorMessage(caughtError, 'Impossible de créer le post')
    toasts.error('Création impossible', error.value)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="page-stack">
    <div class="page-header">
      <div>
        <p class="eyebrow">Ingestion</p>
        <h1>Nouveau post</h1>
      </div>
    </div>

    <ErrorBanner v-if="error" title="Action impossible" :message="error" />

    <div class="form-grid">
      <form class="panel form-panel" @submit.prevent="submitPost">
        <label>
          Plateforme
          <select v-model="form.platform">
            <option value="twitter">Twitter</option>
            <option value="linkedin">LinkedIn</option>
            <option value="reddit">Reddit</option>
            <option value="instagram">Instagram</option>
          </select>
        </label>
        <label>
          Auteur
          <input v-model="form.author" required type="text" placeholder="mehdi" />
        </label>
        <label>
          Contenu
          <textarea
            v-model="form.content"
            required
            rows="8"
            placeholder="L'intelligence artificielle transforme les entreprises."
          ></textarea>
        </label>
        <div class="button-row">
          <button class="secondary-button" type="button" :disabled="analyzing || loading" @click="previewAnalysis">
            <Sparkles :size="16" />
            <span>{{ analyzing ? 'Analyse...' : 'Analyser' }}</span>
          </button>
          <button class="primary-button" type="submit" :disabled="loading">
            <Send :size="16" />
            <span>{{ loading ? 'Envoi...' : 'Créer' }}</span>
          </button>
        </div>
        <p v-if="created" class="success-text">Post créé et analysé.</p>
      </form>

      <section class="panel analysis-panel">
        <header class="panel-header">
          <h2>Résultat NLP</h2>
        </header>
        <div v-if="analysis" class="analysis-result">
          <div>
            <span class="stat-label">Langue</span>
            <strong>{{ analysis.language }}</strong>
          </div>
          <div>
            <span class="stat-label">Sentiment</span>
            <SentimentBadge :sentiment="analysis.sentiment" />
          </div>
          <div class="keyword-cloud">
            <span v-for="keyword in analysis.keywords" :key="keyword">{{ keyword }}</span>
          </div>
        </div>
        <p v-else class="empty-state">Analyse disponible après prévisualisation ou création</p>
      </section>
    </div>
  </section>
</template>
