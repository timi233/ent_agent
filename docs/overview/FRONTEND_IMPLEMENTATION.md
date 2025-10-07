# 前端技术实现方案

## 📋 概述

本文档详细描述了城市大脑企业信息处理系统前端的技术实现方案，包括Vue3应用架构、组件设计、状态管理和用户界面实现。

## 🏗️ 前端架构设计

### 技术栈
- **框架**: Vue 3.3+ (Composition API)
- **语言**: TypeScript 5.0+
- **构建工具**: Vite 4.0+
- **UI组件库**: Element Plus 2.3+
- **状态管理**: Pinia 2.1+
- **路由**: Vue Router 4.2+
- **HTTP客户端**: Axios 1.4+
- **图表库**: ECharts 5.4+
- **地图**: 高德地图 API

### 项目结构
```
city_brain_frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── main.ts                 # 应用入口
│   ├── App.vue                 # 根组件
│   ├── assets/                 # 静态资源
│   │   ├── images/
│   │   ├── icons/
│   │   └── styles/
│   ├── components/             # 通用组件
│   │   ├── common/
│   │   ├── charts/
│   │   └── forms/
│   ├── views/                  # 页面组件
│   │   ├── enterprise/
│   │   ├── dashboard/
│   │   └── data-quality/
│   ├── router/                 # 路由配置
│   │   └── index.ts
│   ├── stores/                 # 状态管理
│   │   ├── enterprise.ts
│   │   ├── user.ts
│   │   └── app.ts
│   ├── services/               # API服务
│   │   ├── api.ts
│   │   ├── enterprise.ts
│   │   └── ai.ts
│   ├── types/                  # 类型定义
│   │   ├── enterprise.ts
│   │   ├── api.ts
│   │   └── common.ts
│   ├── utils/                  # 工具函数
│   │   ├── request.ts
│   │   ├── format.ts
│   │   └── validation.ts
│   ├── composables/            # 组合式函数
│   │   ├── useEnterprise.ts
│   │   └── useDataQuality.ts
│   └── styles/                 # 样式文件
│       ├── index.scss
│       ├── variables.scss
│       └── mixins.scss
├── package.json
├── vite.config.ts
├── tsconfig.json
└── tailwind.config.js
```

## 🚀 应用配置

### 主应用入口 (src/main.ts)
```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

import App from './App.vue'
import router from './router'
import { setupGlobalComponents } from './components'
import { setupGlobalDirectives } from './directives'
import './styles/index.scss'

const app = createApp(App)

// 状态管理
const pinia = createPinia()
app.use(pinia)

// 路由
app.use(router)

// UI组件库
app.use(ElementPlus, {
  size: 'default',
  zIndex: 3000,
})

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 全局组件
setupGlobalComponents(app)

// 全局指令
setupGlobalDirectives(app)

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('Global error:', err, info)
  // 可以集成错误监控服务
}

app.mount('#app')
```

### Vite 配置 (vite.config.ts)
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
      imports: [
        'vue',
        'vue-router',
        'pinia',
        {
          '@/utils/request': ['request'],
          '@/utils/format': ['formatCurrency', 'formatDate'],
        }
      ],
      dts: true,
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: true,
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 9002,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:9003',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
  },
  build: {
    target: 'es2015',
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: '[ext]/[name]-[hash].[ext]',
      },
    },
  },
})
```

## 📊 类型定义

### 企业类型定义 (src/types/enterprise.ts)
```typescript
export interface Enterprise {
  id: number;
  name: string;
  unifiedSocialCreditCode?: string;
  enterpriseType: EnterpriseType;
  status: EnterpriseStatus;
  registrationCapital?: number;
  establishmentDate?: string;
  businessScope?: string;
  legalRepresentative?: string;
  contactPhone?: string;
  contactEmail?: string;
  website?: string;
  employeeCount?: number;
  annualRevenue?: number;
  dataSource: DataSource;
  importBatch?: string;
  confidenceScore?: number;
  verifiedAt?: string;
  addresses?: EnterpriseAddress[];
  industries?: Industry[];
  relationships?: EnterpriseRelationship[];
  createdAt: string;
  updatedAt: string;
}

export enum EnterpriseType {
  CUSTOMER = 'customer',
  CHAIN_LEADER = 'chain_leader',
  SUPPLIER = 'supplier',
  OTHER = 'other',
}

export enum EnterpriseStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  MERGED = 'merged',
  DISSOLVED = 'dissolved',
}

export enum DataSource {
  MANUAL = 'manual',
  WEB_SEARCH = 'web_search',
  API = 'api',
  IMPORT = 'import',
}

export interface EnterpriseAddress {
  id: number;
  enterpriseId: number;
  addressType: AddressType;
  province?: string;
  city?: string;
  district?: string;
  street?: string;
  detailedAddress?: string;
  postalCode?: string;
  longitude?: number;
  latitude?: number;
  dataSource: DataSource;
  confidenceScore?: number;
  verifiedAt?: string;
  isPrimary: boolean;
  createdAt: string;
  updatedAt: string;
}

export enum AddressType {
  REGISTERED = 'registered',
  OFFICE = 'office',
  FACTORY = 'factory',
  BRANCH = 'branch',
}

export interface EnterpriseSearchParams {
  query?: string;
  enterpriseType?: EnterpriseType;
  status?: EnterpriseStatus;
  city?: string;
  industry?: string;
  dataSource?: DataSource;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface EnterpriseCreateRequest {
  name: string;
  enterpriseType: EnterpriseType;
  unifiedSocialCreditCode?: string;
  registrationCapital?: number;
  establishmentDate?: string;
  businessScope?: string;
  legalRepresentative?: string;
  contactPhone?: string;
  contactEmail?: string;
  website?: string;
  employeeCount?: number;
  annualRevenue?: number;
  address?: {
    addressType: AddressType;
    province?: string;
    city?: string;
    district?: string;
    detailedAddress?: string;
    isPrimary: boolean;
  };
}

export interface EnterpriseUpdateRequest extends Partial<EnterpriseCreateRequest> {
  id: number;
}
```

## 🔧 API服务封装

### 基础API服务 (src/services/api.ts)
```typescript
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useUserStore } from '@/stores/user';
import router from '@/router';

// 响应数据接口
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
  success: boolean;
}

// 分页响应接口
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:9003',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // 请求拦截器
    this.api.interceptors.request.use(
      (config) => {
        // 添加认证token
        const userStore = useUserStore();
        const token = userStore.token;
        
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // 添加请求ID用于追踪
        config.headers['X-Request-ID'] = this.generateRequestId();

        // 显示加载状态
        if (config.showLoading !== false) {
          // 可以在这里显示全局loading
        }

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.api.interceptors.response.use(
      (response: AxiosResponse<ApiResponse>) => {
        const { data } = response;

        // 隐藏加载状态
        // hideLoading();

        // 检查业务状态码
        if (data.success === false) {
          ElMessage.error(data.message || '请求失败');
          return Promise.reject(new Error(data.message));
        }

        return response;
      },
      (error: AxiosError<ApiResponse>) => {
        // 隐藏加载状态
        // hideLoading();

        // 处理HTTP错误
        if (error.response) {
          const { status, data } = error.response;

          switch (status) {
            case 401:
              ElMessage.error('登录已过期，请重新登录');
              const userStore = useUserStore();
              userStore.logout();
              router.push('/login');
              break;
            case 403:
              ElMessage.error('没有权限访问该资源');
              break;
            case 404:
              ElMessage.error('请求的资源不存在');
              break;
            case 422:
              ElMessage.error(data?.message || '请求参数错误');
              break;
            case 500:
              ElMessage.error('服务器内部错误');
              break;
            default:
              ElMessage.error(data?.message || `请求失败 (${status})`);
          }
        } else if (error.request) {
          ElMessage.error('网络连接失败，请检查网络设置');
        } else {
          ElMessage.error('请求配置错误');
        }

        return Promise.reject(error);
      }
    );
  }

  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  // GET请求
  async get<T = any>(url: string, params?: any, config?: any): Promise<T> {
    const response = await this.api.get<ApiResponse<T>>(url, { params, ...config });
    return response.data.data;
  }

  // POST请求
  async post<T = any>(url: string, data?: any, config?: any): Promise<T> {
    const response = await this.api.post<ApiResponse<T>>(url, data, config);
    return response.data.data;
  }

  // PUT请求
  async put<T = any>(url: string, data?: any, config?: any): Promise<T> {
    const response = await this.api.put<ApiResponse<T>>(url, data, config);
    return response.data.data;
  }

  // PATCH请求
  async patch<T = any>(url: string, data?: any, config?: any): Promise<T> {
    const response = await this.api.patch<ApiResponse<T>>(url, data, config);
    return response.data.data;
  }

  // DELETE请求
  async delete<T = any>(url: string, config?: any): Promise<T> {
    const response = await this.api.delete<ApiResponse<T>>(url, config);
    return response.data.data;
  }

  // 文件上传
  async upload<T = any>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.api.post<ApiResponse<T>>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data.data;
  }

  // 文件下载
  async download(url: string, filename?: string, params?: any): Promise<void> {
    const response = await this.api.get(url, {
      params,
      responseType: 'blob',
    });

    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }
}

export const apiService = new ApiService();
export default apiService;
```

### 企业API服务 (src/services/enterprise.ts)
```typescript
import apiService, { PaginatedResponse } from './api';
import {
  Enterprise,
  EnterpriseSearchParams,
  EnterpriseCreateRequest,
  EnterpriseUpdateRequest,
} from '@/types/enterprise';

export class EnterpriseService {
  // 搜索企业
  async searchEnterprises(params: EnterpriseSearchParams): Promise<PaginatedResponse<Enterprise>> {
    return apiService.get('/api/v1/enterprises/search', params);
  }

  // 获取企业详情
  async getEnterprise(id: number): Promise<Enterprise> {
    return apiService.get(`/api/v1/enterprises/${id}`);
  }

  // 创建企业
  async createEnterprise(data: EnterpriseCreateRequest): Promise<Enterprise> {
    return apiService.post('/api/v1/enterprises', data);
  }

  // 更新企业
  async updateEnterprise(id: number, data: EnterpriseUpdateRequest): Promise<Enterprise> {
    return apiService.put(`/api/v1/enterprises/${id}`, data);
  }

  // 删除企业
  async deleteEnterprise(id: number): Promise<void> {
    return apiService.delete(`/api/v1/enterprises/${id}`);
  }

  // 批量删除企业
  async batchDeleteEnterprises(ids: number[]): Promise<void> {
    return apiService.post('/api/v1/enterprises/batch-delete', { ids });
  }

  // 丰富企业信息
  async enrichEnterprise(id: number): Promise<Enterprise> {
    return apiService.post(`/api/v1/enterprises/${id}/enrich`);
  }

  // 生成企业总结
  async generateSummary(id: number): Promise<string> {
    const result = await apiService.post(`/api/v1/enterprises/${id}/summary`);
    return result.summary;
  }

  // 导出企业数据
  async exportEnterprises(params: EnterpriseSearchParams, format: 'excel' | 'csv' = 'excel'): Promise<void> {
    return apiService.download('/api/v1/enterprises/export', `enterprises.${format}`, { ...params, format });
  }

  // 导入企业数据
  async importEnterprises(file: File, onProgress?: (progress: number) => void): Promise<any> {
    return apiService.upload('/api/v1/enterprises/import', file, onProgress);
  }

  // 获取企业统计信息
  async getStatistics(): Promise<any> {
    return apiService.get('/api/v1/enterprises/statistics');
  }

  // 检查企业名称是否重复
  async checkDuplicateName(name: string, excludeId?: number): Promise<boolean> {
    const result = await apiService.get('/api/v1/enterprises/check-duplicate', { name, excludeId });
    return result.isDuplicate;
  }
}

export const enterpriseService = new EnterpriseService();
export default enterpriseService;
```

## 🏪 状态管理

### 企业状态管理 (src/stores/enterprise.ts)
```typescript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import {
  Enterprise,
  EnterpriseSearchParams,
  EnterpriseCreateRequest,
  EnterpriseUpdateRequest,
} from '@/types/enterprise';
import { enterpriseService } from '@/services/enterprise';
import { PaginatedResponse } from '@/services/api';

export const useEnterpriseStore = defineStore('enterprise', () => {
  // 状态
  const enterprises = ref<Enterprise[]>([]);
  const currentEnterprise = ref<Enterprise | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const searchParams = ref<EnterpriseSearchParams>({});
  const pagination = ref({
    total: 0,
    page: 1,
    pageSize: 20,
    totalPages: 0,
  });

  // 计算属性
  const hasEnterprises = computed(() => enterprises.value.length > 0);
  const isLoading = computed(() => loading.value);
  const totalCount = computed(() => pagination.value.total);

  // 企业类型统计
  const enterpriseTypeStats = computed(() => {
    const stats = {
      customer: 0,
      chain_leader: 0,
      supplier: 0,
      other: 0,
    };

    enterprises.value.forEach(enterprise => {
      stats[enterprise.enterpriseType]++;
    });

    return stats;
  });

  // 操作方法
  const searchEnterprises = async (params: EnterpriseSearchParams) => {
    loading.value = true;
    error.value = null;

    try {
      searchParams.value = { ...params };
      const result: PaginatedResponse<Enterprise> = await enterpriseService.searchEnterprises(params);
      
      enterprises.value = result.items;
      pagination.value = {
        total: result.total,
        page: result.page,
        pageSize: result.pageSize,
        totalPages: result.totalPages,
      };

      return result;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '搜索失败';
      enterprises.value = [];
      pagination.value = { total: 0, page: 1, pageSize: 20, totalPages: 0 };
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getEnterprise = async (id: number) => {
    loading.value = true;
    error.value = null;

    try {
      const enterprise = await enterpriseService.getEnterprise(id);
      currentEnterprise.value = enterprise;
      return enterprise;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取企业信息失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const createEnterprise = async (data: EnterpriseCreateRequest) => {
    loading.value = true;
    error.value = null;

    try {
      const newEnterprise = await enterpriseService.createEnterprise(data);
      enterprises.value.unshift(newEnterprise);
      pagination.value.total++;
      
      ElMessage.success('企业创建成功');
      return newEnterprise;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建企业失败';
      ElMessage.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const updateEnterprise = async (id: number, data: EnterpriseUpdateRequest) => {
    loading.value = true;
    error.value = null;

    try {
      const updatedEnterprise = await enterpriseService.updateEnterprise(id, data);

      // 更新列表中的企业
      const index = enterprises.value.findIndex(e => e.id === id);
      if (index !== -1) {
        enterprises.value[index] = updatedEnterprise;
      }

      // 更新当前企业
      if (currentEnterprise.value?.id === id) {
        currentEnterprise.value = updatedEnterprise;
      }

      ElMessage.success('企业更新成功');
      return updatedEnterprise;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新企业失败';
      ElMessage.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const deleteEnterprise = async (id: number) => {
    loading.value = true;
    error.value = null;

    try {
      await enterpriseService.deleteEnterprise(id);

      // 从列表中移除
      enterprises.value = enterprises.value.filter(e => e.id !== id);
      pagination.value.total--;

      // 清除当前企业
      if (currentEnterprise.value?.id === id) {
        currentEnterprise.value = null;
      }

      ElMessage.success('企业删除成功');
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除企业失败';
      ElMessage.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const batchDeleteEnterprises = async (ids: number[]) => {
    loading.value = true;
    error.value = null;

    try {
      await enterpriseService.batchDeleteEnterprises(ids);

      // 从列表中移除
      enterprises.value = enterprises.value.filter(e => !ids.includes(e.id));
      pagination.value.total -= ids.length;

      ElMessage.success(`成功删除 ${ids.length} 个企业`);
    } catch (err) {
      error.value = err instanceof Error ? err.message : '批量删除失败';
      ElMessage.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const enrichEnterprise = async (id: number) => {
    loading.value = true;
    error.value = null;

    try {
      const enrichedEnterprise = await enterpriseService.enrichEnterprise(id);

      // 更新企业信息
      await updateEnterprise(id, enrichedEnterprise);

      ElMessage.success('企业信息丰富完成');
      return enrichedEnterprise;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '丰富企业信息失败';
      ElMessage.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const generateSummary = async (id: number) => {
    loading.value = true;
    error.value = null;

    try {
      const summary = await enterpriseService.generateSummary(id);
      ElMessage.success('企业总结生成完成');
      return summary;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '生成企业总结失败';
      ElMessage.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const exportEnterprises = async (format: 'excel' | 'csv' = 'excel') => {
    loading.value = true;
    error.value = null;

    try {
      await enterpriseService.exportEnterprises(searchParams.value, format);
      ElMessage.success('导出成功');
    } catch (err) {
      error.value = err instanceof Error ? err.message : '导出失败';
      ElMessage.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const importEnterprises = async (file: File, onProgress?: (progress: number) => void) => {
    loading.value = true;
    error.value = null;

    try {
      const result = await enterpriseService.importEnterprises(file, onProgress);
      
      // 刷新企业列表
      await searchEnterprises(searchParams.value);
      
      ElMessage.success(`导入成功，共导入 ${result.successCount} 个企业`);
      return result;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '导入失败';
      ElMessage.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const clearError = () => {
    error.value = null;
  };

  const resetStore = () => {
    enterprises.value = [];
    currentEnterprise.value = null;
    loading.value = false;
    error.value = null;
    searchParams.value = {};
    pagination.value = { total: 0, page: 1, pageSize: 20, totalPages: 0 };
  };

  return {
    // 状态
    enterprises,
    currentEnterprise,
    loading,
    error,
    searchParams,
    pagination,

    // 计算属性
    hasEnterprises,
    isLoading,
    totalCount,
    enterpriseTypeStats,

    // 操作方法
    searchEnterprises,
    getEnterprise,
    createEnterprise,
    updateEnterprise,
    deleteEnterprise,
    batchDeleteEnterprises,
    enrichEnterprise,
    generateSummary,
    exportEnterprises,
    importEnterprises,
    clearError,
    resetStore,
  };
});
```

## 🎨 核心组件实现

### 企业搜索组件 (src/components/enterprise/EnterpriseSearch.vue)
```vue
<template>
  <div class="enterprise-search">
    <!-- 搜索表单 -->
    <el-card class="search-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">企业信息查询</span>
          <div class="actions">
            <el-button type="primary" @click="showCreateDialog = true">
              <el-icon><Plus /></el-icon>
              新增企业
            </el-button>
            <el-button @click="showImportDialog = true">
              <el-icon><Upload /></el-icon>
              批量导入
            </el-button>
          </div>
        </div>
      </template>

      <el-form :model="searchForm" @submit.prevent="handleSearch" inline class="search-form">
        <el-form-item label="企业名称">
          <el-input
            v-model="searchForm.query"
            placeholder="请输入企业名称或关键词"
            clearable
            style="width: 240px"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="企业类型">
          <el-select v-model="searchForm.enterpriseType" placeholder="请选择" clearable style="width: 150px">
            <el-option label="客户企业" :value="EnterpriseType.CUSTOMER" />
            <el-option label="链主企业" :value="EnterpriseType.CHAIN_LEADER" />
            <el-option label="供应商" :value="EnterpriseType.SUPPLIER" />
            <el-option label="其他" :value="EnterpriseType.OTHER" />
          </el-select>
        </el-form-item>

        <el-form-item label="企业状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable style="width: 120px">
            <el-option label="正常" :value="EnterpriseStatus.ACTIVE" />
            <el-option label="停业" :value="EnterpriseStatus.INACTIVE" />
            <el-option label="合并" :value="EnterpriseStatus.MERGED" />
            <el-option label="注销" :value="EnterpriseStatus.DISSOLVED" />
          </el-select>
        </el-form-item>

        <el-form-item label="所在城市">
          <el-select v-model="searchForm.city" placeholder="请选择" clearable style="width: 120px">
            <el-option
              v-for="city in cities"
              :key="city.value"
              :label="city.label"
              :value="city.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="isLoading">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 搜索结果 -->
    <el-card class="result-card" shadow="never" v-loading="isLoading">
      <template #header>
        <div class="card-header">
          <span class="title">搜索结果 ({{ totalCount }})</span>
          <div class="actions">
            <el-button @click="handleExport('excel')" :disabled="!hasEnterprises">
              <el-icon><Download /></el-icon>
              导出Excel
            </el-button>
            <el-button @click="handleExport('csv')" :disabled="!hasEnterprises">
              <el-icon><Document /></el-icon>
              导出CSV
            </el-button>
            <el-button 
              @click="handleBatchDelete" 
              :disabled="selectedEnterprises.length === 0"
              type="danger"
            >
              <el-icon><Delete /></el-icon>
              批量删除
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        ref="tableRef"
        :data="enterprises"
        stripe
        @selection-change="handleSelectionChange"
        @row-click="handleRowClick"
        style="width: 100%"
        empty-text="暂无数据"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="name" label="企业名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link type="primary" @click="handleViewDetail(row)" :underline="false">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>

        <el-table-column prop="enterpriseType" label="企业类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getEnterpriseTypeTagType(row.enterpriseType)">
              {{ getEnterpriseTypeLabel(row.enterpriseType) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="主要地址" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.addresses && row.addresses.length > 0">
              {{ formatAddress(row.addresses.find(addr => addr.isPrimary) || row.addresses[0]) }}
            </span>
            <span v-else class="text-muted">暂无地址信息</span>
          </template>
        </el-table-column>

        <el-table-column prop="employeeCount" label="员工数量" width="120" align="right">
          <template #default="{ row }">
            <span v-if="row.employeeCount">{{ formatNumber(row.employeeCount) }}人</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="annualRevenue" label="年营收" width="120" align="right">
          <template #default="{ row }">
            <span v-if="row.annualRevenue">{{ formatCurrency(row.annualRevenue) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="dataSource" label="数据来源" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="getDataSourceTagType(row.dataSource)">
              {{ getDataSourceLabel(row.dataSource) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleViewDetail(row)">
              详情
            </el-button>
            <el-button size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-dropdown @command="(command) => handleMoreAction(command, row)">
              <el-button size="small">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="enrich" :disabled="enrichingIds.includes(row.id)">
                    <el-icon><Magic /></el-icon>
                    丰富信息
                  </el-dropdown-item>
                  <el-dropdown-item command="summary">
                    <el-icon><Document /></el-icon>
                    生成总结
                  </el-dropdown-item>
                  <el-dropdown-item command="correct">
                    <el-icon><Tools /></el-icon>
                    修正数据
                  </el-dropdown-item>
                  <el-dropdown-item command="export">
                    <el-icon><Download /></el-icon>
                    导出信息
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided>
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="totalCount > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalCount"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 企业详情对话框 -->
    <EnterpriseDetailDialog
      v-model="showDetailDialog"
      :enterprise-id="selectedEnterpriseId"
      @updated="handleEnterpriseUpdated"
    />

    <!-- 企业创建/编辑对话框 -->
    <EnterpriseFormDialog
      v-model="showCreateDialog"
      :enterprise="editingEnterprise"
      @saved="handleEnterpriseSaved"
    />

    <!-- 导入对话框 -->
    <ImportDialog
      v-model="showImportDialog"
      @imported="handleImported"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  Plus, Search, Refresh, Download, Document, Delete, Upload,
  ArrowDown, Magic, Tools
} from '@element-plus/icons-vue';
import { useEnterpriseStore } from '@/stores/enterprise';
import {
  Enterprise,
  EnterpriseSearchParams,
  EnterpriseType,
  EnterpriseStatus,
  DataSource
} from '@/types/enterprise';
import EnterpriseDetailDialog from './EnterpriseDetailDialog.vue';
import EnterpriseFormDialog from './EnterpriseFormDialog.vue';
import ImportDialog from './ImportDialog.vue';
import { formatCurrency, formatNumber, formatAddress } from '@/utils/format';

// Store
const enterpriseStore = useEnterpriseStore();

// 响应式数据
const searchForm = reactive<EnterpriseSearchParams>({
  query: '',
  enterpriseType: undefined,
  status: undefined,
  city: '',
  page: 1,
  pageSize: 20,
});

const showDetailDialog = ref(false);
const showCreateDialog = ref(false);
const showImportDialog = ref(false);
const selectedEnterpriseId = ref<number | null>(null);
const editingEnterprise = ref<Enterprise | null>(null);
const enrichingIds = ref<number[]>([]);
const selectedEnterprises = ref<Enterprise[]>([]);
const currentPage = ref(1);
const pageSize = ref(20);

// 计算属性
const enterprises = computed(() => enterpriseStore.enterprises);
const totalCount = computed(() => enterpriseStore.totalCount);
const isLoading = computed(() => enterpriseStore.isLoading);
const hasEnterprises = computed(() => enterpriseStore.hasEnterprises);

// 城市选项
const cities = ref([
  { label: '青岛市', value: '青岛市' },
  { label: '市南区', value: '市南区' },
  { label: '市北区', value: '市北区' },
  { label: '李沧区', value: '李沧区' },
  { label: '崂山区', value: '崂山区' },
  { label: '城阳区', value: '城阳区' },
]);

// 方法
const handleSearch = async () => {
  const params = {
    ...searchForm,
    page: currentPage.value,
    pageSize: pageSize.value,
  };
  await enterpriseStore.searchEnterprises(params);
};

const handleReset = () => {
  Object.assign(searchForm, {
    query: '',
    enterpriseType: undefined,
    status: undefined,
    city: '',
  });
  currentPage.value = 1;
  handleSearch();
};

const handleRowClick = (row: Enterprise) => {
  handleViewDetail(row);
};

const handleViewDetail = (enterprise: Enterprise) => {
  selectedEnterpriseId.value = enterprise.id;
  showDetailDialog.value = true;
};

const handleEdit = (enterprise: Enterprise) => {
  editingEnterprise.value = enterprise;
  showCreateDialog.value = true;
};

const handleMoreAction = async (command: string, enterprise: Enterprise) => {
  switch (command) {
    case 'enrich':
      await handleEnrich(enterprise);
      break;
    case 'summary':
      await handleGenerateSummary(enterprise);
      break;
    case 'correct':
      // 处理数据修正
      break;
    case 'export':
      // 导出单个企业信息
      break;
    case 'delete':
      await handleDelete(enterprise);
      break;
  }
};

const handleEnrich = async (enterprise: Enterprise) => {
  enrichingIds.value.push(enterprise.id);
  
  try {
    await enterpriseStore.enrichEnterprise(enterprise.id);
  } finally {
    enrichingIds.value = enrichingIds.value.filter(id => id !== enterprise.id);
  }
};

const handleGenerateSummary = async (enterprise: Enterprise) => {
  try {
    const summary = await enterpriseStore.generateSummary(enterprise.id);
    
    ElMessageBox.alert(summary, `${enterprise.name} - 企业总结`, {
      confirmButtonText: '确定',
      type: 'info',
      customClass: 'enterprise-summary-dialog',
    });
  } catch (error) {
    // 错误已在store中处理
  }
};

const handleDelete = async (enterprise: Enterprise) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除企业 "${enterprise.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    await enterpriseStore.deleteEnterprise(enterprise.id);
    handleSearch();
  } catch (error) {
    // 用户取消删除或删除失败
  }
};

const handleSelectionChange = (selection: Enterprise[]) => {
  selectedEnterprises.value = selection;
};

const handleBatchDelete = async () => {
  if (selectedEnterprises.value.length === 0) {
    ElMessage.warning('请选择要删除的企业');
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedEnterprises.value.length} 个企业吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    const ids = selectedEnterprises.value.map(e => e.id);
    await enterpriseStore.batchDeleteEnterprises(ids);
    selectedEnterprises.value = [];
    handleSearch();
  } catch (error) {
    // 用户取消删除或删除失败
  }
};

const handleExport = async (format: 'excel' | 'csv') => {
  try {
    await enterpriseStore.exportEnterprises(format);
  } catch (error) {
    // 错误已在store中处理
  }
};

const handleSizeChange = (size: number) => {
  pageSize.value = size;
  currentPage.value = 1;
  handleSearch();
};

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
  handleSearch();
};

const handleEnterpriseUpdated = () => {
  handleSearch();
};

const handleEnterpriseSaved = () => {
  showCreateDialog.value = false;
  editingEnterprise.value = null;
  handleSearch();
};

const handleImported = () => {
  showImportDialog.value = false;
  handleSearch();
};

// 辅助方法
const getEnterpriseTypeLabel = (type: EnterpriseType) => {
  const labels = {
    [EnterpriseType.CUSTOMER]: '客户企业',
    [EnterpriseType.CHAIN_LEADER]: '链主企业',
    [EnterpriseType.SUPPLIER]: '供应商',
    [EnterpriseType.OTHER]: '其他',
  };
  return labels[type] || type;
};

const getEnterpriseTypeTagType = (type: EnterpriseType) => {
  const types = {
    [EnterpriseType.CUSTOMER]: 'primary',
    [EnterpriseType.CHAIN_LEADER]: 'success',
    [EnterpriseType.SUPPLIER]: 'warning',
    [EnterpriseType.OTHER]: 'info',
  };
  return types[type] || 'info';
};

const getStatusLabel = (status: EnterpriseStatus) => {
  const labels = {
    [EnterpriseStatus.ACTIVE]: '正常',
    [EnterpriseStatus.INACTIVE]: '停业',
    [EnterpriseStatus.MERGED]: '合并',
    [EnterpriseStatus.DISSOLVED]: '注销',
  };
  return labels[status] || status;
};

const getStatusTagType = (status: EnterpriseStatus) => {
  const types = {
    [EnterpriseStatus.ACTIVE]: 'success',
    [EnterpriseStatus.INACTIVE]: 'warning',
    [EnterpriseStatus.MERGED]: 'info',
    [EnterpriseStatus.DISSOLVED]: 'danger',
  };
  return types[status] || 'info';
};

const getDataSourceLabel = (source: DataSource) => {
  const labels = {
    [DataSource.MANUAL]: '手动',
    [DataSource.WEB_SEARCH]: '搜索',
    [DataSource.API]: 'API',
    [DataSource.IMPORT]: '导入',
  };
  return labels[source] || source;
};

const getDataSourceTagType = (source: DataSource) => {
  const types = {
    [DataSource.MANUAL]: 'primary',
    [DataSource.WEB_SEARCH]: 'success',
    [DataSource.API]: 'warning',
    [DataSource.IMPORT]: 'info',
  };
  return types[source] || 'info';
};

// 生命周期
onMounted(() => {
  handleSearch();
});
</script>

<style scoped lang="scss">
.enterprise-search {
  padding: 20px;
  
  .search-card {
    margin-bottom: 20px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .title {
        font-size: 16px;
        font-weight: 600;
      }
      
      .actions {
        display: flex;
        gap: 10px;
      }
    }
    
    .search-form {
      margin-top: 20px;
    }
  }
  
  .result-card {
    min-height: 400px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .title {
        font-size: 16px;
        font-weight: 600;
      }
      
      .actions {
        display: flex;
        gap: 10px;
      }
    }
  }
  
  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
  
  .text-muted {
    color: var(--el-text-color-placeholder);
  }
}

:deep(.enterprise-summary-dialog) {
  .el-message-box__content {
    max-height: 400px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.6;
  }
}
</style>
```

---

## 🔄 首页并行分块加载（Home.vue）

为提升查询体验，首页对结果展示采用“分块并行加载”策略，使各分块独立渲染与错误管理，不互相阻塞。

### 分块状态结构
- sections.summary：摘要分块状态 { loading: boolean, error: boolean }
- sections.info：企业信息分块状态 { loading: boolean, error: boolean }
- sections.news：新闻资讯分块状态 { loading: boolean, error: boolean }

### 触发与更新
- 查询开始（processCompany）：
  - 将 summary、info、news 三个分块置为 loading: true, error: false
- 响应处理（handleProgressiveUpdate）：
  - 根据返回内容分别结束各分块的 loading
  - 若接口返回错误，则三分块标记为 error: true
- 清空结果（clearResult）：
  - 重置三分块状态为 { loading: false, error: false }

### 模板门控示例
- 企业信息分块：
  - v-if="!sections.info.loading && !sections.info.error" 显示内容
  - v-else-if="sections.info.error" 显示错误（el-empty）
  - v-else 显示骨架（el-skeleton）
- 新闻分块：
  - v-if="!sections.news.loading && !sections.news.error && result.data && result.data.news" 显示内容
  - v-else-if="sections.news.error" 显示错误
  - v-else 显示骨架
- 摘要分块可按同样门控模式扩展（当前实现重点在公司信息与新闻）

### 接口与影响
- 接口保持不变：仍调用 /api/v1/company/process/progressive
- 影响：数据到达即渲染；缺失数据不阻塞其他分块

---

*文档版本：v1.0*
*更新时间：2025年9月26日*