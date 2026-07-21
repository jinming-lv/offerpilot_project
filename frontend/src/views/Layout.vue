<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '80px' : '260px'" class="layout-aside">
      <div class="aside-header">
        <div class="aside-logo" @click="router.push('/')">
          <div class="logo-icon-mini">
            <svg viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="22" stroke="url(#logoGrad2)" stroke-width="2" />
              <path d="M24 10 L32 22 L27 22 L27 34 L21 34 L21 22 L16 22 Z" fill="url(#logoGrad2)" />
            </svg>
            <defs>
              <linearGradient id="logoGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#00d4ff" />
                <stop offset="100%" stop-color="#00e5a0" />
              </linearGradient>
            </defs>
          </div>
          <transition name="fade">
            <span v-show="!isCollapse" class="aside-title">OfferPilot</span>
          </transition>
        </div>
        <el-button
          class="collapse-btn"
          :icon="isCollapse ? Expand : Fold"
          text
          @click="isCollapse = !isCollapse"
        />
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="true"
        router
        class="side-menu"
      >
        <el-menu-item index="/upload">
          <el-icon class="menu-icon"><Document /></el-icon>
          <template #title>
            <span class="menu-title">简历解析与匹配</span>
          </template>
        </el-menu-item>
        <el-menu-item index="/interview">
          <el-icon class="menu-icon"><ChatLineRound /></el-icon>
          <template #title>
            <span class="menu-title">AI 模拟面试</span>
          </template>
        </el-menu-item>
        <el-menu-item index="/report">
          <el-icon class="menu-icon"><PieChart /></el-icon>
          <template #title>
            <span class="menu-title">求职分析报告</span>
          </template>
        </el-menu-item>
      </el-menu>

      <!-- 侧边栏底部用户信息 -->
      <div class="aside-footer">
        <div class="user-info">
          <el-avatar :size="32" :icon="UserFilled" class="user-avatar" />
          <transition name="fade">
            <div v-show="!isCollapse" class="user-detail">
              <span class="user-name">求职者</span>
              <span class="user-role">Pro 会员</span>
            </div>
          </transition>
        </div>
      </div>
    </el-aside>

    <!-- 主内容区域 -->
    <el-container class="main-container">
      <!-- 顶部状态栏 -->
      <el-header class="main-header" height="56px">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag size="small" type="success" effect="plain" class="status-tag">
            <span class="status-dot" />
            Agent 运行中
          </el-tag>
          <el-button
            text
            circle
            class="header-icon-btn"
            @click="handleLogout"
          >
            <el-icon><SwitchButton /></el-icon>
          </el-button>
        </div>
      </el-header>

      <!-- 主内容 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="slide-up" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Document,
  ChatLineRound,
  PieChart,
  Expand,
  Fold,
  UserFilled,
  SwitchButton
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const isCollapse = ref(false)

const activeMenu = computed(() => {
  if (route.path.startsWith('/report')) return '/report'
  if (route.path.startsWith('/interview')) return '/interview'
  return '/upload'
})

const currentPageTitle = computed(() => {
  const map = {
    '/upload': '简历解析与匹配',
    '/interview': 'AI 模拟面试',
    '/report': '求职分析报告'
  }
  return map[activeMenu.value] || '首页'
})

function handleLogout() {
  ElMessage.success('已安全退出')
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;
}

/* === 侧边栏 === */
.layout-aside {
  background: var(--glass-bg);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border-right: 1px solid var(--border-glass);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  position: relative;
}
.layout-aside::after {
  content: '';
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 1px;
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(0, 212, 255, 0.3) 50%,
    transparent 100%
  );
}

/* 侧边栏头部 */
.aside-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 16px;
  height: 72px;
  border-bottom: 1px solid var(--border-glass);
}
.aside-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  overflow: hidden;
  flex: 1;
}
.logo-icon-mini {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  filter: drop-shadow(0 0 12px rgba(0, 212, 255, 0.5));
}
.logo-icon-mini svg {
  width: 100%;
  height: 100%;
}
.aside-title {
  font-size: 20px;
  font-weight: 800;
  white-space: nowrap;
  background: var(--gradient-accent);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 1px;
}
.collapse-btn {
  color: var(--text-secondary);
  flex-shrink: 0;
}
.collapse-btn:hover {
  color: var(--accent-cyan);
  background: rgba(0, 212, 255, 0.1);
}

/* 侧边栏菜单 */
.side-menu {
  flex: 1;
  border-right: none;
  background: transparent;
  padding: 12px 8px;
}
.side-menu :deep(.el-menu-item) {
  border-radius: var(--radius-sm);
  margin-bottom: 4px;
  height: 48px;
  line-height: 48px;
  color: var(--text-secondary);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}
.side-menu :deep(.el-menu-item::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  background: var(--gradient-accent);
  border-radius: 0 3px 3px 0;
  transition: height 0.3s ease;
}
.side-menu :deep(.el-menu-item:hover) {
  background: rgba(0, 212, 255, 0.08);
  color: var(--accent-cyan);
}
.side-menu :deep(.el-menu-item:hover::before) {
  height: 60%;
}
.side-menu :deep(.el-menu-item.is-active) {
  background: rgba(0, 212, 255, 0.12);
  color: var(--accent-cyan);
  font-weight: 600;
}
.side-menu :deep(.el-menu-item.is-active::before) {
  height: 70%;
}
.menu-icon {
  font-size: 20px;
  margin-right: 4px;
}
.menu-title {
  font-size: 14px;
  letter-spacing: 1px;
}

/* 侧边栏底部 */
.aside-footer {
  padding: 16px;
  border-top: 1px solid var(--border-glass);
}
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  overflow: hidden;
}
.user-avatar {
  flex-shrink: 0;
  background: var(--gradient-accent);
  color: #0a1628;
}
.user-detail {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}
.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
}
.user-role {
  font-size: 11px;
  color: var(--accent-teal);
  white-space: nowrap;
}

/* === 主容器 === */
.main-container {
  flex-direction: column;
  background: transparent;
}

/* 顶部状态栏 */
.main-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-glass);
}
.header-left :deep(.el-breadcrumb__inner) {
  color: var(--text-secondary);
  font-size: 13px;
}
.header-left :deep(.el-breadcrumb__inner.is-link:hover) {
  color: var(--accent-cyan);
}
.header-left :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: var(--text-primary);
  font-weight: 500;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.status-tag {
  background: rgba(0, 229, 160, 0.1) !important;
  border-color: rgba(0, 229, 160, 0.3) !important;
  color: var(--accent-teal) !important;
  font-size: 12px;
}
.status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent-teal);
  margin-right: 6px;
  animation: statusPulse 2s ease-in-out infinite;
}
@keyframes statusPulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 4px var(--accent-teal); }
  50% { opacity: 0.5; box-shadow: 0 0 10px var(--accent-teal); }
}
.header-icon-btn {
  color: var(--text-secondary);
}
.header-icon-btn:hover {
  color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

/* 主内容 */
.main-content {
  padding: 24px;
  overflow-y: auto;
  height: calc(100vh - 56px);
  background: transparent;
}
</style>