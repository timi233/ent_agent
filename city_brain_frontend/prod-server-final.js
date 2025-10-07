const express = require('express');
const path = require('path');
const fs = require('fs');
const { createProxyMiddleware } = require('http-proxy-middleware');

// 创建Express应用
const app = express();
const PORT = 9002;

// 代理API请求到后端
app.use('/api', createProxyMiddleware({
  target: 'http://localhost:9003',
  changeOrigin: true,
  pathRewrite: {
    '^/api/api': '/api' // /api/api/v1/... 转发为 /api/v1/...
  },
  // 增加超时设置，因为后端可能需要时间来处理请求
  timeout: 60000, // 60秒超时
  proxyTimeout: 60000, // 代理超时
  onProxyReq: (proxyReq, req, res) => {
    // 增加请求头，允许更长的处理时间
    console.log(`正在代理请求: ${req.method} ${req.url}`);
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log(`收到后端响应: ${proxyRes.statusCode} for ${req.url}`);
  }
}));

// 静态文件服务，服务构建后的dist目录
app.use(express.static(path.join(__dirname, 'dist')));

// 增加超时设置
app.use((req, res, next) => {
  req.setTimeout(60000, () => {
    console.log(`请求超时: ${req.method} ${req.url}`);
  });
  next();
});

// 根路径返回构建后的index.html
app.get('/', (req, res) => {
    const indexPath = path.join(__dirname, 'dist', 'index.html');
    
    if (fs.existsSync(indexPath)) {
        res.sendFile(indexPath);
    } else {
        res.status(500).send('Index file not found');
    }
});

// 其他非API路径也返回index.html以支持SPA
app.get(/^(?!\/api\/).*$/, (req, res) => {
    const indexPath = path.join(__dirname, 'dist', 'index.html');
    
    if (fs.existsSync(indexPath)) {
        res.sendFile(indexPath);
    } else {
        res.status(500).send('Index file not found');
    }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`前端生产服务器运行在 http://localhost:${PORT}`);
});