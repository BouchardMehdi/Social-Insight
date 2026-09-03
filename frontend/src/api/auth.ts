import api from './client'
import type {
  AuthResponse,
  AuthSession,
  LoginPayload,
  RegisterPayload,
  Workspace,
  WorkspaceMember,
} from '../types/social'

export async function registerAccount(payload: RegisterPayload): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>('/auth/register', payload)
  return data
}

export async function loginAccount(payload: LoginPayload): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>('/auth/login', payload)
  return data
}

export async function getSession(): Promise<AuthSession> {
  const { data } = await api.get<AuthSession>('/auth/me')
  return data
}

export async function createWorkspace(name: string): Promise<Workspace> {
  const { data } = await api.post<Workspace>('/workspaces', { name })
  return data
}

export async function getWorkspaceMembers(workspaceId: string): Promise<WorkspaceMember[]> {
  const { data } = await api.get<WorkspaceMember[]>(`/workspaces/${workspaceId}/members`)
  return data
}

export async function addWorkspaceMember(
  workspaceId: string,
  email: string,
  role: 'admin' | 'member',
): Promise<WorkspaceMember> {
  const { data } = await api.post<WorkspaceMember>(`/workspaces/${workspaceId}/members`, {
    email,
    role,
  })
  return data
}
