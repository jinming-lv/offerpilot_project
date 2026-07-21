<template>
  <router-view />
</template>

<script setup>
// App 根组件，仅作为路由容器
</script>

<style>
/* 全局样式重置与科技风主题变量 */
:root {
  --primary-deep-blue: #0a1628;
  --primary-blue: #0f2744;
  --accent-cyan: #00d4ff;
  --accent-teal: #00e5a0;
  --accent-purple: #7c3aed;
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --border-glass: rgba(0, 212, 255, 0.15);
  --card-bg: rgba(15, 39, 68, 0.6);
  --card-bg-hover: rgba(15, 39, 68, 0.85);
  --glass-bg: rgba(10, 22, 40, 0.75);
  --gradient-hero: linear-gradient(135deg, #0a1628 0%, #0f2744 50%, #0c1e38 100%);
  --gradient-accent: linear-gradient(135deg, #00d4ff 0%, #00e5a0 100%);
  --gradient-purple: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
  --shadow-glow: 0 0 20px rgba(0, 212, 255, 0.15);
  --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.3);
  --radius-lg: 16px;
  --radius-md: 12px;
  --radius-sm: 8px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
  background: var(--primary-deep-blue);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  background-image:
    radial-gradient(ellipse at 20% 50%, rgba(0, 212, 255, 0.04) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(0, 229, 160, 0.03) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 80%, rgba(124, 58, 237, 0.04) 0%, transparent 50%);
  background-attachment: fixed;
}

#app {
  height: 100%;
}

/* 覆盖 Element Plus 暗色主题变量 */
.el-container,
.el-header,
.el-aside,
.el-main {
  --el-bg-color: transparent;
  --el-bg-color-overlay: var(--card-bg);
  --el-text-color-primary: var(--text-primary);
  --el-text-color-regular: var(--text-secondary);
  --el-border-color: var(--border-glass);
  --el-border-color-light: var(--border-glass);
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.25);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 212, 255, 0.45);
}

/* 全局过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.35s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(30px);
}
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}

/* 科技感卡片通用样式 */
.tech-card {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-card);
  transition: all 0.3s ease;
}
.tech-card:hover {
  background: var(--card-bg-hover);
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: var(--shadow-glow);
  transform: translateY(-2px);
}

/* 发光按钮 */
.glow-btn {
  background: var(--gradient-accent);
  border: none;
  color: #0a1628;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}
.glow-btn:hover {
  box-shadow: 0 0 25px rgba(0, 212, 255, 0.4), 0 0 50px rgba(0, 229, 160, 0.2);
  transform: translateY(-1px);
}
.glow-btn:active {
  transform: translateY(0);
}

/* 渐变文字 */
.gradient-text {
  background: var(--gradient-accent);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>