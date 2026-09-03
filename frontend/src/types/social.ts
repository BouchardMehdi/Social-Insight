export type Sentiment = 'positive' | 'neutral' | 'negative'

export interface Post {
  id: string
  workspace_id: string
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

export type WorkspaceRole = 'owner' | 'admin' | 'member'

export interface User {
  id: string
  email: string
  display_name: string
  created_at: string
}

export interface Workspace {
  id: string
  name: string
  role: WorkspaceRole
  created_at: string
}

export interface WorkspaceMember {
  user_id: string
  email: string
  display_name: string
  role: WorkspaceRole
  joined_at: string
}

export interface AuthSession {
  user: User
  workspaces: Workspace[]
  active_workspace_id: string
}

export interface AuthResponse extends AuthSession {
  access_token: string
  token_type: 'bearer'
  expires_in: number
}

export interface RegisterPayload {
  email: string
  password: string
  display_name: string
  workspace_name?: string
}

export interface LoginPayload {
  email: string
  password: string
}
