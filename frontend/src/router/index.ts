import { createRouter, createWebHistory } from 'vue-router'

import AnalyticsView from '../views/AnalyticsView.vue'
import DashboardView from '../views/DashboardView.vue'
import NewPostView from '../views/NewPostView.vue'
import PostDetailView from '../views/PostDetailView.vue'
import PostsView from '../views/PostsView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import WorkspacesView from '../views/WorkspacesView.vue'
import { useAuthStore } from '../stores/auth'
import { pinia } from '../stores'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: LoginView, meta: { publicOnly: true } },
    { path: '/register', name: 'register', component: RegisterView, meta: { publicOnly: true } },
    { path: '/', name: 'dashboard', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/posts', name: 'posts', component: PostsView, meta: { requiresAuth: true } },
    { path: '/posts/:id', name: 'post-detail', component: PostDetailView, meta: { requiresAuth: true } },
    { path: '/analytics', name: 'analytics', component: AnalyticsView, meta: { requiresAuth: true } },
    { path: '/new-post', name: 'new-post', component: NewPostView, meta: { requiresAuth: true } },
    { path: '/workspaces', name: 'workspaces', component: WorkspacesView, meta: { requiresAuth: true } },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore(pinia)
  await auth.initialize()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.publicOnly && auth.isAuthenticated) return { name: 'dashboard' }
})

export default router
