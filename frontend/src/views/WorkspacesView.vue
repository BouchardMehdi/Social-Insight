<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { Building2, Plus, UserPlus } from '@lucide/vue'

import { addWorkspaceMember, getWorkspaceMembers } from '../api/auth'
import { getApiErrorMessage } from '../api/errors'
import ErrorBanner from '../components/ErrorBanner.vue'
import { useAuthStore } from '../stores/auth'
import { useToastsStore } from '../stores/toasts'
import type { WorkspaceMember } from '../types/social'

const auth = useAuthStore()
const toasts = useToastsStore()
const name = ref('')
const loading = ref(false)
const error = ref('')
const members = ref<WorkspaceMember[]>([])
const membersLoading = ref(false)
const memberForm = reactive({ email: '', role: 'member' as 'admin' | 'member' })
const canManageMembers = computed(
  () => auth.activeWorkspace?.role === 'owner' || auth.activeWorkspace?.role === 'admin',
)

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const workspace = await auth.addWorkspace(name.value)
    name.value = ''
    toasts.success('Espace créé', `${workspace.name} est maintenant votre espace actif.`)
  } catch (caughtError) {
    error.value = getApiErrorMessage(caughtError, "Impossible de créer l’espace")
  } finally {
    loading.value = false
  }
}

async function fetchMembers() {
  if (!auth.activeWorkspaceId) return
  membersLoading.value = true
  try {
    members.value = await getWorkspaceMembers(auth.activeWorkspaceId)
  } catch (caughtError) {
    error.value = getApiErrorMessage(caughtError, 'Impossible de charger les membres')
  } finally {
    membersLoading.value = false
  }
}

async function submitMember() {
  if (!auth.activeWorkspaceId) return
  loading.value = true
  error.value = ''
  try {
    const member = await addWorkspaceMember(
      auth.activeWorkspaceId,
      memberForm.email,
      memberForm.role,
    )
    members.value.push(member)
    memberForm.email = ''
    memberForm.role = 'member'
    toasts.success('Membre ajouté', `${member.display_name} a rejoint cet espace.`)
  } catch (caughtError) {
    error.value = getApiErrorMessage(caughtError, "Impossible d’ajouter ce membre")
  } finally {
    loading.value = false
  }
}

onMounted(fetchMembers)
watch(() => auth.activeWorkspaceId, fetchMembers)
</script>

<template>
  <section class="page-stack">
    <div class="page-header">
      <div>
        <p class="eyebrow">Organisation</p>
        <h1>Espaces de travail</h1>
      </div>
    </div>

    <ErrorBanner v-if="error" title="Action impossible" :message="error" />

    <div class="workspace-grid">
      <button
        v-for="workspace in auth.workspaces"
        :key="workspace.id"
        class="workspace-card"
        :class="{ active: workspace.id === auth.activeWorkspaceId }"
        @click="auth.selectWorkspace(workspace.id)"
      >
        <Building2 :size="22" />
        <span>
          <strong>{{ workspace.name }}</strong>
          <small>{{ workspace.role }}</small>
        </span>
      </button>
    </div>

    <form class="panel workspace-form" @submit.prevent="submit">
      <div>
        <h2>Créer un espace</h2>
        <p>Un nouvel environnement isolé pour une marque, un client ou une équipe.</p>
      </div>
      <input v-model="name" required minlength="2" placeholder="Nom de l’espace" />
      <button class="primary-button" type="submit" :disabled="loading">
        <Plus :size="17" />
        <span>{{ loading ? 'Création...' : 'Créer' }}</span>
      </button>
    </form>

    <section class="panel members-panel">
      <header class="panel-header">
        <div>
          <h2>Membres de {{ auth.activeWorkspace?.name }}</h2>
          <p>Les nouveaux membres doivent déjà posséder un compte Social Insight.</p>
        </div>
      </header>

      <p v-if="membersLoading" class="empty-state">Chargement des membres...</p>
      <div v-else class="member-list">
        <div v-for="member in members" :key="member.user_id" class="member-row">
          <span>
            <strong>{{ member.display_name }}</strong>
            <small>{{ member.email }}</small>
          </span>
          <span class="role-pill">{{ member.role }}</span>
        </div>
      </div>

      <form v-if="canManageMembers" class="member-form" @submit.prevent="submitMember">
        <label>
          Adresse e-mail
          <input v-model="memberForm.email" required type="email" placeholder="membre@example.com" />
        </label>
        <label>
          Rôle
          <select v-model="memberForm.role">
            <option value="member">Membre</option>
            <option v-if="auth.activeWorkspace?.role === 'owner'" value="admin">Administrateur</option>
          </select>
        </label>
        <button class="primary-button" type="submit" :disabled="loading">
          <UserPlus :size="17" />
          <span>Ajouter</span>
        </button>
      </form>
    </section>
  </section>
</template>
