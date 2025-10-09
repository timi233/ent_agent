import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import path from 'node:path'

export default defineConfig({
  plugins: [vue(), vueJsx()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@views': path.resolve(__dirname, 'src/views'),
      '@stores': path.resolve(__dirname, 'src/stores'),
      '@utils': path.resolve(__dirname, 'src/utils'),
      '@composables': path.resolve(__dirname, 'src/composables'),
      '@services': path.resolve(__dirname, 'src/services')
    }
  },
  server: {
    port: 9002,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:9003',
        changeOrigin: true,
        secure: false
      }
    }
  },
  preview: {
    port: 5002,
    strictPort: true
  }
})
