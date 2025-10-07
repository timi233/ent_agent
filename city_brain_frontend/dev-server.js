const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const { createServer: createViteServer } = require('vite');

async function startServer() {
  const app = express();

  // 配置API代理
  app.use('/api/api', createProxyMiddleware({
    target: 'http://localhost:9003',
    changeOrigin: true,
    pathRewrite: {
      '^/api/api': '/api' // 将 /api/api/... 重写为 /api/...
    }
  }));

  // 创建 Vite 服务器
  const vite = await createViteServer({
    server: { middlewareMode: true, host: '0.0.0.0', port: 9002 },
  });
  app.use(vite.middlewares);

  app.listen(9002, () => {
    console.log('开发服务器运行在 http://localhost:9002');
  });
}

startServer();