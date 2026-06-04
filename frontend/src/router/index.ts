import { createRouter, createWebHistory } from 'vue-router'

import AnalyticsView from '../views/AnalyticsView.vue'
import DashboardView from '../views/DashboardView.vue'
import NewPostView from '../views/NewPostView.vue'
import PostsView from '../views/PostsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: DashboardView },
    { path: '/posts', name: 'posts', component: PostsView },
    { path: '/analytics', name: 'analytics', component: AnalyticsView },
    { path: '/new-post', name: 'new-post', component: NewPostView },
  ],
})

export default router
