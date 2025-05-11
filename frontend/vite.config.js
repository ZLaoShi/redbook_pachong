import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    // 监听所有网络接口，这样可以通过远程IP访问
    host: '0.0.0.0',
    port: 5173,
    // 设置代理
    proxy: {
      '/api': {
        target: 'http://192.168.96.211:8000',
        changeOrigin: true
      }
    }
  }
})