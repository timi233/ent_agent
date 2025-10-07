const express = require('express');
const path = require('path');
const fs = require('fs');

// 创建Express应用
const app = express();
const PORT = 9002;

// 静态文件服务，仅服务dist目录
app.use(express.static(path.join(__dirname, 'dist')));

// 根路径返回构建后的index.html
app.get('/', (req, res) => {
    const indexPath = path.join(__dirname, 'dist', 'index.html');
    
    if (fs.existsSync(indexPath)) {
        res.sendFile(indexPath);
    } else {
        res.status(500).send('Index file not found');
    }
});

// 其他路径也返回index.html以支持SPA
app.get(/.*/, (req, res) => {
    const indexPath = path.join(__dirname, 'dist', 'index.html');
    
    if (fs.existsSync(indexPath)) {
        res.sendFile(indexPath);
    } else {
        res.status(500).send('Index file not found');
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`测试服务器运行在 http://localhost:${PORT}`);
});