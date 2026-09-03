import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    clearMocks: true,
    restoreMocks: true,
    include: ['tests/unit/**/*.spec.ts'],
  },
})
