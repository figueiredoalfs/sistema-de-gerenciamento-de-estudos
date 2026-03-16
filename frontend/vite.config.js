import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/tasks': 'http://localhost:8000',
      '/metas': 'http://localhost:8000',
      '/onboarding': 'http://localhost:8000',
      '/desempenho': 'http://localhost:8000',
      '/bateria': 'http://localhost:8000',
      '/baterias': 'http://localhost:8000',
      '/questoes': 'http://localhost:8000',
      '/admin': 'http://localhost:8000',
      '/task-conteudo': 'http://localhost:8000',
      '/task-videos': 'http://localhost:8000',
    },
  },
})
