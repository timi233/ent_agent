import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    component: () => import('@views/dashboard/DashboardView.vue'),
    meta: { title: '企业信息查询' }
  },
  {
    path: '/insights',
    component: () => import('@views/insights/InsightsView.vue'),
    meta: { title: '商机洞察' }
  },
  {
    path: '/operations',
    component: () => import('@views/operations/OperationsView.vue'),
    meta: { title: '工单管理' }
  },
  {
    path: '/planning',
    component: () => import('@views/planning/PlanningView.vue'),
    meta: { title: '行业分析' }
  },
  {
    path: '/:pathMatch(.*)*',
    component: () => import('@views/NotFoundView.vue'),
    meta: { title: '页面不存在' }
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})

// 移除权限检查 - 后端无鉴权系统
// router.beforeEach((to, _from, next) => {
//   next()
// })
