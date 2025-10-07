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

// 首先提供构建后的静态文件
app.use(express.static(path.join(__dirname, 'dist')));

// 然后提供public目录的静态文件（如果请求的资源在dist中找不到）
app.use(express.static(path.join(__dirname, 'public')));

// 处理SPA路由 - 对于任何非API的GET请求，返回构建后的index.html
app.get('*', (req, res) => {
  if (!req.path.startsWith('/api')) {
    // 尝试发送构建后的index.html，如果不存在则发送public目录的
    const indexPath = path.join(__dirname, 'dist', 'index.html');
    require('fs').access(indexPath, require('fs').constants.F_OK, (err) => {
      if (err) {
        // 如果dist/index.html不存在，回退到public/index.html
        res.sendFile(path.join(__dirname, 'public', 'index.html'));
      } else {
        res.sendFile(indexPath);
      }
    });
  } else {
    // 这个路由不应该被触发，因为/api已经由代理处理
    res.status(404).send('Not Found');
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`前端服务器运行在 http://localhost:${PORT}`);
});