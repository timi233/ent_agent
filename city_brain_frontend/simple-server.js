const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = 9002;

// 代理API请求到后端
app.use('/api', createProxyMiddleware({
  target: 'http://localhost:9003',
  changeOrigin: true,
  pathRewrite: {
    '^/api/api': '/api' // /api/api/v1/... 转发为 /api/v1/...
  }
}));

// 提供构建后的静态文件
app.use(express.static(path.join(__dirname, 'dist')));

// 对于其他请求，尝试从public目录提供文件（处理Vite开发模式）
app.use(express.static(path.join(__dirname, 'public')));

// 处理SPA路由
app.get('*', (req, res) => {
  // 优先使用构建后的index.html，否则使用public目录的
  const indexPath = path.join(__dirname, 'dist', 'index.html');
  const publicIndexPath = path.join(__dirname, 'public', 'index.html');
  
  // 如果存在构建后的版本，使用它；否则使用public目录的
  if (require('fs').existsSync(indexPath)) {
    res.sendFile(indexPath);
  } else {
    res.sendFile(publicIndexPath);
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`前端服务器运行在 http://localhost:${PORT}`);
});