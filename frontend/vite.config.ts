import { defineConfig } from 'vite'


// https://vite.dev/config/
export default defineConfig({
  server: {
    proxy: {
      '/fix': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
