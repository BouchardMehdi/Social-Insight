import { defineStore } from 'pinia'

import { createPost, listPosts, type PostQuery } from '../api/socialInsight'
import type { Post, PostCreatePayload } from '../types/social'

export const usePostsStore = defineStore('posts', {
  state: () => ({
    items: [] as Post[],
    total: 0,
    limit: 10,
    offset: 0,
    loading: false,
    error: '',
  }),
  actions: {
    async fetchPosts(query: PostQuery = {}) {
      this.loading = true
      this.error = ''
      try {
        const response = await listPosts({
          limit: this.limit,
          offset: this.offset,
          ...query,
        })
        this.items = response.items
        this.total = response.total
        this.limit = response.limit
        this.offset = response.offset
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Impossible de charger les posts'
      } finally {
        this.loading = false
      }
    },
    async create(payload: PostCreatePayload) {
      const post = await createPost(payload)
      this.items = [post, ...this.items]
      this.total += 1
      return post
    },
  },
})
