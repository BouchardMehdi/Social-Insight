import { defineStore } from 'pinia'

import { getApiErrorMessage } from '../api/errors'
import { createPost, getPost, listPosts, type PostQuery } from '../api/socialInsight'
import type { Post, PostCreatePayload } from '../types/social'

export const usePostsStore = defineStore('posts', {
  state: () => ({
    items: [] as Post[],
    selected: null as Post | null,
    total: 0,
    limit: 10,
    offset: 0,
    loading: false,
    detailLoading: false,
    error: '',
    detailError: '',
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
        this.error = getApiErrorMessage(error, 'Impossible de charger les posts')
      } finally {
        this.loading = false
      }
    },
    async fetchPost(id: string) {
      this.detailLoading = true
      this.detailError = ''
      this.selected = null
      try {
        this.selected = await getPost(id)
      } catch (error) {
        this.detailError = getApiErrorMessage(error, 'Impossible de charger le post')
      } finally {
        this.detailLoading = false
      }
    },
    async create(payload: PostCreatePayload) {
      try {
        const post = await createPost(payload)
        this.items = [post, ...this.items]
        this.total += 1
        return post
      } catch (error) {
        throw new Error(getApiErrorMessage(error, 'Impossible de creer le post'))
      }
    },
  },
})
