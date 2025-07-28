import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  base: '/',  // ✅ base path for production
  plugins: [vue()],
  server: {
    port: 5173,
    historyApiFallback: true  // ✅ fallback for local dev
  }
})