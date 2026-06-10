import { defineStore } from 'pinia'

import { getApiErrorMessage } from '../api/errors'
import { getActivity, getSentiments, getSummary, getTopKeywords } from '../api/socialInsight'
import type { ActivityPoint, SentimentDistribution, SummaryStats, TopKeyword } from '../types/social'

export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    summary: { total_posts: 0, total_authors: 0 } as SummaryStats,
    keywords: [] as TopKeyword[],
    sentiments: { positive: 0, neutral: 0, negative: 0 } as SentimentDistribution,
    activity: [] as ActivityPoint[],
    loading: false,
    error: '',
  }),
  actions: {
    async fetchAll() {
      this.loading = true
      this.error = ''
      try {
        const [summary, keywords, sentiments, activity] = await Promise.all([
          getSummary(),
          getTopKeywords(10),
          getSentiments(),
          getActivity(30),
        ])
        this.summary = summary
        this.keywords = keywords
        this.sentiments = sentiments
        this.activity = activity
      } catch (error) {
        this.error = getApiErrorMessage(error, 'Impossible de charger les analyses')
      } finally {
        this.loading = false
      }
    },
  },
})
