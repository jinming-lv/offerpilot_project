import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],

  server: {
    port: 5173,

    // Vite 代理：解决跨域 CORS 问题
    // 前端 /api/* 请求 → 转发到后端 http://127.0.0.1:8000/api/*
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,           // 修改请求头 origin，避免后端 CORS 校验
        secure: false,               // 允许自签名 HTTPS 证书（开发环境）
        ws: true,                    // 支持 WebSocket 代理（预留）

        // 代理事件钩子（调试用，可在终端查看转发日志）
        configure: (proxy) => {
          proxy.on('error', (err) => {
            console.error('[Vite Proxy Error]', err.message)
          })
          proxy.on('proxyReq', (proxyReq, req) => {
            console.log(`[Vite Proxy] ${req.method} ${req.url} → ${proxyReq.path}`)
          })
          proxy.on('proxyRes', (proxyRes, req) => {
            console.log(`[Vite Proxy] ${req.method} ${req.url} ← ${proxyRes.statusCode}`)
          })
        },
      },
    },
  },
})