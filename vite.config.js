import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'app/static/dist',
    emptyOutDir: false,
  },
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/rag': 'http://localhost:8000',
    },
    watch: {
      ignored: ['**/venv/**', '**/.git/**', '**/node_modules/**', '**/app/Storage/**'],
    },
  },
})
