/// <reference types="vitest" />
import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    proxy: {
      // Trailing slash matters: Vite matches proxy keys as prefixes, so a bare
      // '/api' also swallows the client-side '/api-docs' route and answers it
      // with the backend's JSON 404. Every backend path is under '/api/v1/'.
      '/api/': {
        target: process.env.VITE_API_URL ?? 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
    exclude: ['**/node_modules/**', '**/e2e/**'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'json-summary', 'lcov'],
      thresholds: {
        lines: 85,
        branches: 85,
        statements: 85,
        functions: 85,
      },
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/**/*.test.{ts,tsx}', 'src/test-setup.ts'],
    },
  },
});
