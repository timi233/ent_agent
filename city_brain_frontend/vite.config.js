import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), vueJsx()],
  server: {
    host: '0.0.0.0',
    port: 9002,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:9003',
        changeOrigin: true,
        rewrite: (path) => {
          // 保持 /api/v1/... 路径不变
          return path
        }
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})