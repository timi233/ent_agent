const express = require('express');
const { createServer } = require('vite');
const history = require('connect-history-api-fallback');
const { createProxyMiddleware } = require('http-proxy-middleware');

async function startServer() {
  const app = express();

  // 使用 connect-history-api-fallback 中间件，但排除API路由
  // 只有非API请求才使用history模式
  app.use((req, res, next) => {
    // 如果请求路径以 /api 开头，跳过 history 中间件
    if (req.path.startsWith('/api')) {
      next();
    } else {
      // 对非API请求应用history中间件
      history({
        verbose: true,
        disableDotRule: true
      })(req, res, next);
    }
  });

  // 配置代理中间件，将 /api/api/* 请求转发到后端服务
  // 前端请求 /api/api/v1/...，代理需要将其转换为 http://localhost:9003/api/v1/...
  app.use('/api/api', createProxyMiddleware({
    target: 'http://localhost:9003',
    changeOrigin: true,
    pathRewrite: {
      '^/api/api': '/api' // 重写 /api/api/v1/* 为 /api/v1/*
    },
    onProxyReq: (proxyReq, req, res) => {
      console.log('Proxying request:', req.method, req.url);
    },
    onProxyRes: (proxyRes, req, res) => {
      console.log('Received response from backend:', proxyRes.statusCode, req.url);
    }
  }));

  // 创建 Vite 服务器
  const vite = await createServer({
    server: { middlewareMode: true },
  });
  app.use(vite.middlewares);

  app.listen(9002, () => {
    console.log('前端服务器运行在 http://localhost:9002');
  });
}

startServer();