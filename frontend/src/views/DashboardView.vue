<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Hash, MessageSquareText, SmilePlus, Users } from '@lucide/vue'
import type { ChartConfiguration } from 'chart.js'

import ChartPanel from '../components/ChartPanel.vue'
import ErrorBanner from '../components/ErrorBanner.vue'
import LoadingState from '../components/LoadingState.vue'
import StatCard from '../components/StatCard.vue'
import { useAnalyticsStore } from '../stores/analytics'

const analytics = useAnalyticsStore()

onMounted(() => analytics.fetchAll())

const sentimentTotal = computed(
  () => analytics.sentiments.positive + analytics.sentiments.neutral + analytics.sentiments.negative,
)

const sentimentChart = computed<ChartConfiguration>(() => ({
  type: 'doughnut',
  data: {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [
      {
        data: [
          analytics.sentiments.positive,
          analytics.sentiments.neutral,
          analytics.sentiments.negative,
        ],
        backgroundColor: ['#27d6a2', '#78a6ff', '#ff6b8a'],
        borderWidth: 0,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { labels: { color: '#d9e4f2' } } },
  },
}))
</script>

<template>
  <section class="page-stack">
    <div class="page-header">
      <div>
        <p class="eyebrow">Vue globale</p>
        <h1>Dashboard social analytics</h1>
      </div>
      <span class="health-pill">API BigQuery ready</span>
    </div>

    <ErrorBanner v-if="analytics.error" title="Analytics indisponibles" :message="analytics.error" />

    <div class="stats-grid">
      <StatCard label="Posts ingérés" :value="analytics.summary.total_posts" tone="cyan" :icon="MessageSquareText" />
      <StatCard label="Auteurs uniques" :value="analytics.summary.total_authors" tone="green" :icon="Users" />
      <StatCard label="Sentiments classés" :value="sentimentTotal" tone="rose" :icon="SmilePlus" />
      <StatCard label="Keywords suivis" :value="analytics.keywords.length" tone="amber" :icon="Hash" />
    </div>

    <LoadingState v-if="analytics.loading" label="Chargement du dashboard..." />

    <div class="dashboard-grid">
      <section class="panel">
        <header class="panel-header">
          <h2>Top keywords</h2>
        </header>
        <div class="keyword-list">
          <div v-for="keyword in analytics.keywords.slice(0, 8)" :key="keyword.keyword" class="keyword-row">
            <span>{{ keyword.keyword }}</span>
            <strong>{{ keyword.count }}</strong>
          </div>
          <p v-if="!analytics.loading && !analytics.keywords.length" class="empty-state">
            Aucune donnée disponible
          </p>
        </div>
      </section>

      <ChartPanel title="Répartition des sentiments" :config="sentimentChart" />
    </div>
  </section>
</template>
