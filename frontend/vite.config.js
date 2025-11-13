import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // ⭐ ВАЖНО: мини-ап обслуживается по /webapp
  base: "/webapp/",

  server: {
    port: 5173,        // фиксируем порт, как у тебя было
    strictPort: true   // если порт занят — выдаем ошибку
  }
})
