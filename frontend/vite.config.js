import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/watchdog_automation/',
  server: {
    port: 3000
  },
  build: {
    outDir: 'dist'
  }
})

