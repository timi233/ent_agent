const { createServer } = require('vite');
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');
const fs = require('fs');

async function startServer() {
  const app = express();
  
  // 代理API请求到后端
  app.use('/api', createProxyMiddleware({
    target: 'http://localhost:9003',
    changeOrigin: true,
    pathRewrite: {
      '^/api/api': '/api' // /api/api/v1/... 转发为 /api/v1/...
    }
  }));

  // 创建 Vite 预览服务器
  const vite = await createServer({
    server: { middlewareMode: true },
    appType: 'custom'
  });
  
  // 使用 Vite 的 HTML 服务中间件
  app.use(vite.middlewares);

  app.listen(9002, '0.0.0.0', () => {
    console.log('前端服务器运行在 http://localhost:9002');
  });
}

startServer().catch(err => {
  console.error('服务器启动失败:', err);
});