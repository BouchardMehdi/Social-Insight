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
const tracking = ref(false)
const created = ref(false)
const error = ref('')
const analysis = ref<AnalyzeResponse | null>(null)
const analysisStatus = ref<'idle' | 'pending' | 'processing' | 'completed' | 'failed'>('idle')
const analysisError = ref('')

async function previewAnalysis() {
  if (!form.content.trim()) return
  analyzing.value = true
  error.value = ''
  try {
    analysis.value = await analyzeText(form.content)
    analysisStatus.value = 'completed'
    analysisError.value = ''
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
  analysisError.value = ''
  try {
    const post = await posts.create(form)
    analysis.value = null
    analysisStatus.value = post.analysis_status
    form.author = ''
    form.content = ''
    created.value = true
    toasts.info('Post enregistré', `L’analyse du post ${post.platform} continue en arrière-plan.`)
    void trackAnalysis(post.id, post.workspace_id)
  } catch (caughtError) {
    error.value = getApiErrorMessage(caughtError, 'Impossible de créer le post')
    toasts.error('Création impossible', error.value)
  } finally {
    loading.value = false
  }
}

async function trackAnalysis(postId: string, workspaceId: string) {
  tracking.value = true
  try {
    const post = await posts.waitForAnalysis(postId, workspaceId)
    analysisStatus.value = post.analysis_status
    if (post.analysis_status === 'failed') {
      analysisError.value = post.analysis_error ?? 'Le moteur NLP a rencontré une erreur.'
      toasts.error('Analyse échouée', analysisError.value)
      return
    }
    analysis.value = {
      language: post.language,
      language_confidence: post.language_confidence,
      sentiment: post.sentiment,
      sentiment_confidence: post.sentiment_confidence,
      keywords: post.keywords,
      model_version: post.model_version,
      analysis_status: post.analysis_status,
    }
    toasts.success('Analyse terminée', 'Les résultats NLP sont maintenant disponibles.')
  } catch (caughtError) {
    analysisError.value = getApiErrorMessage(caughtError, "Impossible de suivre l’analyse")
    toasts.error('Suivi interrompu', analysisError.value)
  } finally {
    tracking.value = false
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
          <button
            class="secondary-button"
            type="button"
            :disabled="analyzing || loading || tracking"
            @click="previewAnalysis"
          >
            <Sparkles :size="16" />
            <span>{{ analyzing ? 'Analyse...' : 'Analyser' }}</span>
          </button>
          <button class="primary-button" type="submit" :disabled="loading || tracking">
            <Send :size="16" />
            <span>{{ loading ? 'Envoi...' : 'Créer' }}</span>
          </button>
        </div>
        <p v-if="created" class="success-text">Post enregistré, analyse en arrière-plan.</p>
      </form>

      <section class="panel analysis-panel">
        <header class="panel-header">
          <h2>Résultat NLP</h2>
        </header>
        <div
          v-if="analysisStatus === 'pending' || analysisStatus === 'processing' || tracking"
          class="analysis-progress"
        >
          <span class="spinner"></span>
          <div>
            <strong>Analyse {{ analysisStatus === 'processing' ? 'en cours' : 'en attente' }}</strong>
            <p>Vous pouvez continuer à utiliser l’application.</p>
          </div>
        </div>
        <ErrorBanner
          v-else-if="analysisStatus === 'failed'"
          title="Analyse échouée"
          :message="analysisError"
        />
        <div v-else-if="analysis" class="analysis-result">
          <div>
            <span class="stat-label">Langue</span>
            <strong>{{ analysis.language }} · {{ Math.round(analysis.language_confidence * 100) }} %</strong>
          </div>
          <div>
            <span class="stat-label">Sentiment</span>
            <SentimentBadge
              :sentiment="analysis.sentiment"
              :confidence="analysis.sentiment_confidence"
            />
          </div>
          <div>
            <span class="stat-label">Modèle</span>
            <strong>{{ analysis.model_version }}</strong>
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
