import { expect, type Page, test } from '@playwright/test'

async function login(page: Page) {
  await page.goto('/login')
  await page.getByLabel('Adresse e-mail').fill('demo@social-insight.local')
  await page.getByLabel('Mot de passe').fill('demo-social-insight')
  await page.getByRole('button', { name: 'Se connecter' }).click()
  await expect(page).toHaveURL('/')
  await expect(page.getByRole('heading', { name: 'Dashboard social analytics' })).toBeVisible()
}

test('redirects an anonymous visitor and authenticates the demo account', async ({ page }) => {
  await page.goto('/posts')
  await expect(page).toHaveURL(/\/login\?redirect=/)

  await page.getByLabel('Adresse e-mail').fill('demo@social-insight.local')
  await page.getByLabel('Mot de passe').fill('demo-social-insight')
  await page.getByRole('button', { name: 'Se connecter' }).click()

  await expect(page).toHaveURL('/posts')
  await expect(page.getByRole('heading', { name: 'Posts ingérés' })).toBeVisible()
})

test('creates a post and displays its asynchronous NLP result', async ({ page }) => {
  await login(page)
  await page.getByRole('link', { name: 'Nouveau post' }).click()

  await page.getByLabel('Plateforme').selectOption('linkedin')
  await page.getByLabel('Auteur').fill(`e2e-${Date.now()}`)
  await page
    .getByLabel('Contenu')
    .fill('Une excellente expérience, rapide, fiable et vraiment utile pour notre équipe.')
  await page.getByRole('button', { name: 'Créer' }).click()

  await expect(page.getByText('Post enregistré, analyse en arrière-plan.')).toBeVisible()
  await expect(page.locator('.analysis-result')).toContainText('positive')
  await expect(page.locator('.analysis-result')).toContainText('spacy-rules-fr-en-v2')
})
