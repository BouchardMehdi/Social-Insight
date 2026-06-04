<script setup lang="ts">
import { BarChart3, FileText, LayoutDashboard, PlusCircle } from '@lucide/vue'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/posts', label: 'Posts', icon: FileText },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/new-post', label: 'Nouveau post', icon: PlusCircle },
]
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <RouterLink to="/" class="brand">
        <span class="brand-mark">SI</span>
        <span>
          <strong>Social Insight</strong>
          <small>Data Intelligence</small>
        </span>
      </RouterLink>

      <nav class="nav-list" aria-label="Navigation principale">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="nav-link">
          <component :is="item.icon" :size="18" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
    </aside>

    <main class="main-panel">
      <RouterView />
    </main>
  </div>
</template>
