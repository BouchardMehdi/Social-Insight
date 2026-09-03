<script setup lang="ts">
import { reactive, ref } from 'vue'
import { LogIn } from '@lucide/vue'
import { useRoute, useRouter } from 'vue-router'

import { getApiErrorMessage } from '../api/errors'
import ErrorBanner from '../components/ErrorBanner.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const error = ref('')
const form = reactive({ email: '', password: '' })
const showDemoCredentials =
  import.meta.env.DEV || import.meta.env.VITE_SHOW_DEMO_CREDENTIALS === 'true'

async function submit() {
  error.value = ''
  try {
    await auth.login(form)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    await router.push(redirect)
  } catch (caughtError) {
    error.value = getApiErrorMessage(caughtError, 'Connexion impossible')
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-card">
      <img class="auth-logo" src="/social-insight-logo.png" alt="Social Insight" />
      <div>
        <p class="eyebrow">Bienvenue</p>
        <h1>Connexion</h1>
        <p class="auth-intro">Retrouvez les analyses de votre espace de travail.</p>
      </div>

      <ErrorBanner v-if="error" title="Connexion impossible" :message="error" />

      <form class="auth-form" @submit.prevent="submit">
        <label>
          Adresse e-mail
          <input v-model="form.email" required type="email" autocomplete="email" />
        </label>
        <label>
          Mot de passe
          <input
            v-model="form.password"
            required
            type="password"
            autocomplete="current-password"
          />
        </label>
        <button class="primary-button" type="submit" :disabled="auth.loading">
          <LogIn :size="17" />
          <span>{{ auth.loading ? 'Connexion...' : 'Se connecter' }}</span>
        </button>
      </form>

      <p class="auth-switch">
        Pas encore de compte ? <RouterLink to="/register">Créer un compte</RouterLink>
      </p>
      <p v-if="showDemoCredentials" class="demo-hint">
        Démo locale : <strong>demo@social-insight.local</strong> / <strong>demo-social-insight</strong>
      </p>
    </section>
  </main>
</template>
