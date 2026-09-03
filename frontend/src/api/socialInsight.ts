import api from './client'
import type {
  ActivityPoint,
  AnalyzeResponse,
  Post,
  PostCreatePayload,
  PostListResponse,
  Sentiment,
  SentimentDistribution,
  SummaryStats,
  TopKeyword,
} from '../types/social'

export interface PostQuery {
  platform?: string
  sentiment?: Sentiment | ''
  keyword?: string
  limit?: number
  offset?: number
}

export async function analyzeText(text: string): Promise<AnalyzeResponse> {
  const { data } = await api.post<AnalyzeResponse>('/analyze', { text })
  return data
}

export async function createPost(payload: PostCreatePayload): Promise<Post> {
  const { data } = await api.post<Post>('/posts', payload)
  return data
}

export async function getPost(id: string, workspaceId?: string): Promise<Post> {
  const { data } = await api.get<Post>(`/posts/${id}`, {
    headers: workspaceId ? { 'X-Workspace-ID': workspaceId } : undefined,
  })
  return data
}

export async function listPosts(params: PostQuery): Promise<PostListResponse> {
  const { data } = await api.get<PostListResponse>('/posts', { params })
  return data
}

export async function getSummary(): Promise<SummaryStats> {
  const { data } = await api.get<SummaryStats>('/stats/summary')
  return data
}

export async function getTopKeywords(limit = 10): Promise<TopKeyword[]> {
  const { data } = await api.get<TopKeyword[]>('/stats/top-keywords', { params: { limit } })
  return data
}

export async function getSentiments(): Promise<SentimentDistribution> {
  const { data } = await api.get<SentimentDistribution>('/stats/sentiments')
  return data
}

export async function getActivity(limit = 30): Promise<ActivityPoint[]> {
  const { data } = await api.get<ActivityPoint[]>('/stats/activity', { params: { limit } })
  return data
}
