const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');
const fs = require('fs');

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

// 处理SPA路由 - 返回构建后的index.html
app.get('*', (req, res) => {
  if (req.path.startsWith('/api')) {
    // 这个不应该被触发，因为/api已经被代理处理
    res.status(404).send('Not Found');
  } else {
    // 返回构建后的index.html
    const indexPath = path.join(__dirname, 'dist', 'index.html');
    if (fs.existsSync(indexPath)) {
      res.sendFile(indexPath);
    } else {
      console.error('构建后的index.html文件不存在');
      res.status(500).send('Server Error: index.html not found');
    }
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`前端服务器运行在 http://localhost:${PORT}`);
});