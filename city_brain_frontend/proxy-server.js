const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();

// 配置代理中间件，将 /api/api/* 请求转发到后端服务
// 前端请求 /api/api/v1/...，代理需要将其转换为 http://localhost:9003/api/v1/...
app.use('/api/api', createProxyMiddleware({
  target: 'http://localhost:9003',
  changeOrigin: true,
  pathRewrite: {
    '^/api/api': '/api' // 重写 /api/api/v1/* 为 /api/v1/*
  }
}));

// 为其他所有请求提供静态文件服务
app.use(express.static('dist'));

app.listen(9002, () => {
  console.log('前端代理服务器运行在 http://localhost:9002');
});