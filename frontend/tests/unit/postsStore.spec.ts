import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { getPost, listPosts } from '../../src/api/socialInsight'
import { usePostsStore } from '../../src/stores/posts'
import type { Post } from '../../src/types/social'

vi.mock('../../src/api/socialInsight', () => ({
  createPost: vi.fn(),
  getPost: vi.fn(),
  listPosts: vi.fn(),
}))

const pendingPost: Post = {
  id: 'post-1',
  workspace_id: 'workspace-1',
  platform: 'twitter',
  author: 'ines',
  content: 'Une expérience très utile.',
  language: 'unknown',
  language_confidence: 0,
  sentiment: 'neutral',
  sentiment_confidence: 0,
  keywords: [],
  model_version: 'spacy-rules-fr-en-v2',
  analysis_status: 'pending',
  analysis_error: null,
  created_at: '2026-09-03T10:00:00Z',
  inserted_at: '2026-09-03T10:00:00Z',
}

const completedPost: Post = {
  ...pendingPost,
  language: 'fr',
  language_confidence: 0.98,
  sentiment: 'positive',
  sentiment_confidence: 0.94,
  keywords: ['expérience', 'utile'],
  analysis_status: 'completed',
}

describe('posts store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('loads a paginated list with the active filters', async () => {
    vi.mocked(listPosts).mockResolvedValue({
      items: [completedPost],
      total: 1,
      limit: 10,
      offset: 0,
    })
    const store = usePostsStore()

    await store.fetchPosts({ platform: 'twitter', sentiment: 'positive' })

    expect(listPosts).toHaveBeenCalledWith({
      limit: 10,
      offset: 0,
      platform: 'twitter',
      sentiment: 'positive',
    })
    expect(store.items).toEqual([completedPost])
    expect(store.total).toBe(1)
    expect(store.loading).toBe(false)
  })

  it('polls until an asynchronous NLP analysis is completed', async () => {
    vi.useFakeTimers()
    vi.mocked(getPost)
      .mockResolvedValueOnce(pendingPost)
      .mockResolvedValueOnce(completedPost)
    const store = usePostsStore()
    store.items = [pendingPost]

    const resultPromise = store.waitForAnalysis('post-1', 'workspace-1')
    await vi.advanceTimersByTimeAsync(400)
    const result = await resultPromise

    expect(getPost).toHaveBeenNthCalledWith(1, 'post-1', 'workspace-1')
    expect(getPost).toHaveBeenNthCalledWith(2, 'post-1', 'workspace-1')
    expect(result.analysis_status).toBe('completed')
    expect(store.items[0]).toEqual(completedPost)
  })
})
