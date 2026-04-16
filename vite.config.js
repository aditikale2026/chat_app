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
      '/rag': 'http://localhost:8000',
      '/ui': 'http://localhost:8000',
    }
  }
})
