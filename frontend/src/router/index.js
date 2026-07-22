import { createRouter, createWebHashHistory } from 'vue-router'
import { loadSession } from '../utils/session'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: 'OfferPilot - 登录', requiresAuth: false }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('../views/Layout.vue'),
    redirect: '/upload',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'upload',
        name: 'Upload',
        component: () => import('../views/UploadView.vue'),
        meta: { title: 'OfferPilot - 简历解析与匹配', requiresAuth: true }
      },
      {
        path: 'interview',
        name: 'Interview',
        component: () => import('../views/Interview.vue'),
        meta: { title: 'OfferPilot - AI 模拟面试', requiresAuth: true }
      },
      {
        path: 'report',
        name: 'Report',
        component: () => import('../views/ReportView.vue'),
        meta: { title: 'OfferPilot - 求职分析报告', requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const session = loadSession()
  const isLoggedIn = !!session.token

  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
  } else if (to.path === '/login' && isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

// 全局标题更新
router.afterEach((to) => {
  document.title = to.meta.title || 'OfferPilot'
})

export default router