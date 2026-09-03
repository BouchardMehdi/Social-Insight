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
    async waitForAnalysis(postId: string, workspaceId: string) {
      for (let attempt = 0; attempt < 75; attempt += 1) {
        if (attempt > 0) await new Promise((resolve) => window.setTimeout(resolve, 400))
        const post = await getPost(postId, workspaceId)
        this.replacePost(post)
        if (post.analysis_status === 'completed' || post.analysis_status === 'failed') {
          return post
        }
      }
      throw new Error("L’analyse prend plus de temps que prévu. Le suivi continuera dans Posts.")
    },
    async refreshPending() {
      const pending = this.items.filter(
        (post) => post.analysis_status === 'pending' || post.analysis_status === 'processing',
      )
      await Promise.all(
        pending.map(async (post) => {
          try {
            this.replacePost(await getPost(post.id, post.workspace_id))
          } catch {
            // A workspace switch can make an old polling request inaccessible.
          }
        }),
      )
    },
    async refreshSelectedAnalysis() {
      const post = this.selected
      if (!post || !['pending', 'processing'].includes(post.analysis_status)) return
      try {
        this.replacePost(await getPost(post.id, post.workspace_id))
      } catch {
        // The regular detail error flow handles inaccessible posts.
      }
    },
    replacePost(post: Post) {
      const index = this.items.findIndex((item) => item.id === post.id)
      if (index >= 0) this.items[index] = post
      if (this.selected?.id === post.id) this.selected = post
    },
  },
})
