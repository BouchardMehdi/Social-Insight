export type Sentiment = 'positive' | 'neutral' | 'negative'

export interface Post {
  id: string
  platform: string
  author: string
  content: string
  language: string
  sentiment: Sentiment
  keywords: string[]
  created_at: string
  inserted_at: string
}

export interface PostCreatePayload {
  platform: string
  author: string
  content: string
}

export interface PostListResponse {
  items: Post[]
  total: number
  limit: number
  offset: number
}

export interface AnalyzeResponse {
  language: string
  sentiment: Sentiment
  keywords: string[]
}

export interface TopKeyword {
  keyword: string
  count: number
}

export interface SentimentDistribution {
  positive: number
  neutral: number
  negative: number
}

export interface ActivityPoint {
  date: string
  count: number
}

export interface SummaryStats {
  total_posts: number
  total_authors: number
}
