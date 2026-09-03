<script setup lang="ts">
import { computed } from 'vue'
import { BarChart3, Building2, FileText, LayoutDashboard, LogOut, PlusCircle } from '@lucide/vue'
import { useRoute } from 'vue-router'

import ToastContainer from './components/ToastContainer.vue'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const auth = useAuthStore()
const isPublicPage = computed(() => Boolean(route.meta.publicOnly))

function selectWorkspace(event: Event) {
  auth.selectWorkspace((event.target as HTMLSelectElement).value)
}

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/posts', label: 'Posts', icon: FileText },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/new-post', label: 'Nouveau post', icon: PlusCircle },
  { to: '/workspaces', label: 'Espaces', icon: Building2 },
]
</script>

<template>
  <RouterView v-if="isPublicPage" />

  <div v-else class="app-shell">
    <aside class="sidebar">
      <RouterLink to="/" class="brand">
        <img class="brand-logo" src="/social-insight-logo.png" alt="Social Insight" />
        <span class="brand-copy" aria-hidden="true">
          <strong>Social Insight</strong>
          <small>Data Intelligence</small>
        </span>
      </RouterLink>

      <label class="workspace-switcher">
        <span>Espace actif</span>
        <select
          :value="auth.activeWorkspaceId"
          @change="selectWorkspace"
        >
          <option v-for="workspace in auth.workspaces" :key="workspace.id" :value="workspace.id">
            {{ workspace.name }}
          </option>
        </select>
      </label>

      <nav class="nav-list" aria-label="Navigation principale">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="nav-link">
          <component :is="item.icon" :size="18" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div class="account-panel">
        <span>
          <strong>{{ auth.user?.display_name }}</strong>
          <small>{{ auth.user?.email }}</small>
        </span>
        <button class="icon-button" title="Se déconnecter" @click="auth.logout">
          <LogOut :size="17" />
        </button>
      </div>
    </aside>

    <main class="main-panel">
      <RouterView :key="`${route.fullPath}-${auth.activeWorkspaceId}`" />
    </main>

    <ToastContainer />
  </div>
</template>
