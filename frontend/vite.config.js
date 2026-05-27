import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) }
  },
  server: {
    port: 5173,
    // 仅开发环境生效，生产构建不使用 proxy
    proxy: {
      '/api': {
        target: 'http://localhost:8002',
        changeOrigin: true
      }
    }
  }
})
