import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: 'OfferPilot - 登录' }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('../views/Layout.vue'),
    redirect: '/upload',
    children: [
      {
        path: 'upload',
        name: 'Upload',
        component: () => import('../views/UploadView.vue'),
        meta: { title: 'OfferPilot - 简历解析与匹配' }
      },
      {
        path: 'interview',
        name: 'Interview',
        component: () => import('../views/Interview.vue'),
        meta: { title: 'OfferPilot - AI 模拟面试' }
      },
      {
        path: 'report',
        name: 'Report',
        component: () => import('../views/ReportView.vue'),
        meta: { title: 'OfferPilot - 求职分析报告' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 全局标题更新
router.afterEach((to) => {
  document.title = to.meta.title || 'OfferPilot'
})

export default router