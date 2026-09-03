import { defineStore } from 'pinia'

import { createWorkspace, getSession, loginAccount, registerAccount } from '../api/auth'
import type {
  AuthResponse,
  LoginPayload,
  RegisterPayload,
  User,
  Workspace,
} from '../types/social'

const TOKEN_KEY = 'social-insight-token'
const WORKSPACE_KEY = 'social-insight-workspace'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) ?? '',
    user: null as User | null,
    workspaces: [] as Workspace[],
    activeWorkspaceId: localStorage.getItem(WORKSPACE_KEY) ?? '',
    initialized: false,
    loading: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token && state.user),
    activeWorkspace: (state) =>
      state.workspaces.find((workspace) => workspace.id === state.activeWorkspaceId) ?? null,
  },
  actions: {
    async initialize() {
      if (this.initialized) return
      if (!this.token) {
        this.initialized = true
        return
      }
      try {
        const session = await getSession()
        this.user = session.user
        this.workspaces = session.workspaces
        const storedIsValid = this.workspaces.some(
          (workspace) => workspace.id === this.activeWorkspaceId,
        )
        this.selectWorkspace(storedIsValid ? this.activeWorkspaceId : session.active_workspace_id)
      } catch {
        this.clearSession()
      } finally {
        this.initialized = true
      }
    },
    async login(payload: LoginPayload) {
      this.loading = true
      try {
        this.applyAuthResponse(await loginAccount(payload))
      } finally {
        this.loading = false
      }
    },
    async register(payload: RegisterPayload) {
      this.loading = true
      try {
        this.applyAuthResponse(await registerAccount(payload))
      } finally {
        this.loading = false
      }
    },
    async addWorkspace(name: string) {
      const workspace = await createWorkspace(name)
      this.workspaces.push(workspace)
      this.selectWorkspace(workspace.id)
      return workspace
    },
    selectWorkspace(workspaceId: string) {
      if (!this.workspaces.some((workspace) => workspace.id === workspaceId)) return
      this.activeWorkspaceId = workspaceId
      localStorage.setItem(WORKSPACE_KEY, workspaceId)
    },
    logout() {
      this.clearSession()
      window.location.assign('/login')
    },
    applyAuthResponse(response: AuthResponse) {
      this.token = response.access_token
      this.user = response.user
      this.workspaces = response.workspaces
      this.initialized = true
      localStorage.setItem(TOKEN_KEY, response.access_token)
      this.selectWorkspace(response.active_workspace_id)
    },
    clearSession() {
      this.token = ''
      this.user = null
      this.workspaces = []
      this.activeWorkspaceId = ''
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(WORKSPACE_KEY)
    },
  },
})
