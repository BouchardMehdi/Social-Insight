<script setup lang="ts">
import { reactive, ref } from 'vue'
import { UserPlus } from '@lucide/vue'
import { useRouter } from 'vue-router'

import { getApiErrorMessage } from '../api/errors'
import ErrorBanner from '../components/ErrorBanner.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const error = ref('')
const form = reactive({
  display_name: '',
  email: '',
  password: '',
  workspace_name: '',
})

async function submit() {
  error.value = ''
  try {
    await auth.register(form)
    await router.push('/')
  } catch (caughtError) {
    error.value = getApiErrorMessage(caughtError, 'Création du compte impossible')
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-card">
      <img class="auth-logo" src="/social-insight-logo.png" alt="Social Insight" />
      <div>
        <p class="eyebrow">Nouvel espace</p>
        <h1>Créer un compte</h1>
        <p class="auth-intro">Vos publications et statistiques resteront isolées dans votre espace.</p>
      </div>

      <ErrorBanner v-if="error" title="Inscription impossible" :message="error" />

      <form class="auth-form" @submit.prevent="submit">
        <label>
          Nom affiché
          <input v-model="form.display_name" required minlength="2" autocomplete="name" />
        </label>
        <label>
          Adresse e-mail
          <input v-model="form.email" required type="email" autocomplete="email" />
        </label>
        <label>
          Nom de l’espace
          <input v-model="form.workspace_name" required minlength="2" />
        </label>
        <label>
          Mot de passe
          <input
            v-model="form.password"
            required
            minlength="8"
            type="password"
            autocomplete="new-password"
          />
        </label>
        <button class="primary-button" type="submit" :disabled="auth.loading">
          <UserPlus :size="17" />
          <span>{{ auth.loading ? 'Création...' : 'Créer mon espace' }}</span>
        </button>
      </form>

      <p class="auth-switch">
        Déjà inscrit ? <RouterLink to="/login">Se connecter</RouterLink>
      </p>
    </section>
  </main>
</template>
