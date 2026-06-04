<script setup lang="ts">
import { computed, onMounted } from 'vue'
import type { ChartConfiguration } from 'chart.js'

import ChartPanel from '../components/ChartPanel.vue'
import { useAnalyticsStore } from '../stores/analytics'

const analytics = useAnalyticsStore()

onMounted(() => analytics.fetchAll())

const activityChart = computed<ChartConfiguration>(() => ({
  type: 'line',
  data: {
    labels: analytics.activity.map((point) => point.date),
    datasets: [
      {
        label: 'Posts',
        data: analytics.activity.map((point) => point.count),
        borderColor: '#35d3ff',
        backgroundColor: 'rgba(53, 211, 255, 0.18)',
        fill: true,
        tension: 0.35,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { ticks: { color: '#9fb1c7' }, grid: { color: 'rgba(255,255,255,0.06)' } },
      y: { ticks: { color: '#9fb1c7' }, grid: { color: 'rgba(255,255,255,0.06)' } },
    },
    plugins: { legend: { labels: { color: '#d9e4f2' } } },
  },
}))

const keywordChart = computed<ChartConfiguration>(() => ({
  type: 'bar',
  data: {
    labels: analytics.keywords.map((keyword) => keyword.keyword),
    datasets: [
      {
        label: 'Occurrences',
        data: analytics.keywords.map((keyword) => keyword.count),
        backgroundColor: '#f5b85b',
        borderRadius: 6,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { ticks: { color: '#9fb1c7' }, grid: { display: false } },
      y: { ticks: { color: '#9fb1c7' }, grid: { color: 'rgba(255,255,255,0.06)' } },
    },
    plugins: { legend: { labels: { color: '#d9e4f2' } } },
  },
}))

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
        <p class="eyebrow">BigQuery SQL</p>
        <h1>Analytics</h1>
      </div>
    </div>

    <div class="analytics-grid">
      <ChartPanel title="Activité quotidienne" :config="activityChart" />
      <ChartPanel title="Top keywords" :config="keywordChart" />
      <ChartPanel title="Sentiments" :config="sentimentChart" />
    </div>
  </section>
</template>
