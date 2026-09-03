import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api',
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('social-insight-token')
  const workspaceId = localStorage.getItem('social-insight-workspace')
  if (token) config.headers.Authorization = `Bearer ${token}`
  if (workspaceId && !config.headers['X-Workspace-ID']) {
    config.headers['X-Workspace-ID'] = workspaceId
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !['/login', '/register'].includes(window.location.pathname)) {
      localStorage.removeItem('social-insight-token')
      localStorage.removeItem('social-insight-workspace')
      window.location.assign('/login')
    }
    return Promise.reject(error)
  },
)

export default api
