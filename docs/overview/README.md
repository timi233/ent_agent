# 城市大脑企业信息处理系统前端

这是一个基于Vue 3和Vite构建的前端应用，为城市大脑企业信息处理系统提供用户友好的聊天界面。

## 功能特性

- 对话式交互界面
- 企业信息查询
- 实时响应显示
- 响应式设计
- 与后端API集成

## 技术栈

- Vue 3
- Vite
- Element Plus
- Axios
- Vue Router

## 项目结构

```
city_brain_frontend/
├── public/              # 静态资源
├── src/                 # 源代码
│   ├── assets/          # 静态资源
│   ├── components/      # 组件
│   ├── router/          # 路由配置
│   ├── styles/          # 样式文件
│   ├── utils/           # 工具函数
│   ├── views/           # 页面视图
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── package.json         # 项目配置
└── vite.config.js       # Vite配置
```

## 开发指南

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run start
```

默认访问地址: http://localhost:9002

### 构建生产版本

```bash
npm run build
```

## 代理配置

前端通过Vite代理将API请求转发到后端服务：

```
/api -> http://localhost:9003
```

确保后端服务在运行时监听9003端口。