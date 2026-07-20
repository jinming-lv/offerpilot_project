<template>
  <div class="login-container">
    <!-- 背景粒子动画 -->
    <div class="bg-particles">
      <div
        v-for="i in 30"
        :key="i"
        class="particle"
        :style="getParticleStyle(i)"
      />
    </div>

    <!-- 左侧品牌区域 -->
    <div class="login-brand">
      <div class="brand-logo">
        <div class="logo-icon">
          <svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#00d4ff" />
                <stop offset="100%" stop-color="#00e5a0" />
              </linearGradient>
            </defs>
            <circle cx="40" cy="40" r="36" stroke="url(#logoGrad)" stroke-width="2.5" />
            <path d="M40 16 L52 36 L44 36 L44 56 L36 56 L36 36 L28 36 Z" fill="url(#logoGrad)" />
            <circle cx="40" cy="40" r="6" fill="#0a1628" stroke="url(#logoGrad)" stroke-width="2" />
          </svg>
        </div>
        <h1 class="brand-title">Offer<span class="highlight">Pilot</span></h1>
      </div>
      <p class="brand-desc">基于多智能体架构的 AI 求职导航平台</p>
      <div class="brand-features">
        <div class="feature-item">
          <span class="feature-icon">📄</span>
          <span>智能简历解析与岗位匹配</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">🎙️</span>
          <span>AI 多轮模拟面试与点评</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">📊</span>
          <span>多维能力画像与学习规划</span>
        </div>
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="login-form-panel">
      <div class="form-card tech-card">
        <h2 class="form-title">欢迎回来</h2>
        <p class="form-subtitle">登录您的 OfferPilot 账号继续求职之旅</p>

        <el-form
          ref="formRef"
          :model="loginForm"
          :rules="rules"
          class="login-form"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入账号"
              size="large"
              :prefix-icon="User"
              class="custom-input"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
              class="custom-input"
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="glow-btn login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <span class="footer-link">还没有账号？<a href="javascript:void(0)">立即注册</a></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' }
  ]
}

// 背景粒子随机样式
function getParticleStyle(i) {
  const size = 2 + Math.random() * 4
  const left = Math.random() * 100
  const delay = Math.random() * 8
  const duration = 6 + Math.random() * 10
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    opacity: 0.3 + Math.random() * 0.5
  }
}

// 登录处理
function handleLogin() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    loading.value = true

    // 模拟登录延迟
    setTimeout(() => {
      loading.value = false
      ElMessage({
        message: '登录成功！欢迎使用 OfferPilot 🚀',
        type: 'success',
        duration: 2000
      })
      router.push('/')
    }, 1200)
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--gradient-hero);
  position: relative;
}

/* === 背景粒子 === */
.bg-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}
.particle {
  position: absolute;
  bottom: -10px;
  background: var(--accent-cyan);
  border-radius: 50%;
  animation: floatUp linear infinite;
}
@keyframes floatUp {
  0% {
    transform: translateY(0) scale(1);
    opacity: 0;
  }
  10% {
    opacity: 0.8;
  }
  90% {
    opacity: 0.1;
  }
  100% {
    transform: translateY(-100vh) scale(0.3);
    opacity: 0;
  }
}

/* === 左侧品牌区域 === */
.login-brand {
  flex: 0 0 45%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 60px;
  position: relative;
  z-index: 1;
}
.brand-logo {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}
.logo-icon {
  width: 72px;
  height: 72px;
  filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.4));
  animation: pulseGlow 3s ease-in-out infinite;
}
.logo-icon svg {
  width: 100%;
  height: 100%;
}
@keyframes pulseGlow {
  0%, 100% { filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.4)); }
  50% { filter: drop-shadow(0 0 35px rgba(0, 212, 255, 0.7)); }
}
.brand-title {
  font-size: 48px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: 2px;
}
.brand-title .highlight {
  background: var(--gradient-accent);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.brand-desc {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 40px;
  letter-spacing: 1px;
}
.brand-features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  color: var(--text-secondary);
  padding: 12px 20px;
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  transition: all 0.3s ease;
}
.feature-item:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.3);
  color: var(--text-primary);
  transform: translateX(6px);
}
.feature-icon {
  font-size: 22px;
}

/* === 右侧表单 === */
.login-form-panel {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px;
  position: relative;
  z-index: 1;
}
.form-card {
  width: 100%;
  max-width: 440px;
  padding: 48px 40px;
}
.form-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.form-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 36px;
}
.login-form {
  margin-top: 8px;
}
.custom-input :deep(.el-input__wrapper) {
  background: rgba(10, 22, 40, 0.8);
  border: 1px solid var(--border-glass);
  box-shadow: none;
  border-radius: var(--radius-sm);
}
.custom-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(0, 212, 255, 0.4);
}
.custom-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--accent-cyan);
  box-shadow: 0 0 0 1px rgba(0, 212, 255, 0.25);
}
.custom-input :deep(.el-input__inner) {
  color: var(--text-primary);
}
.custom-input :deep(.el-input__prefix) {
  color: var(--text-secondary);
}
.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  letter-spacing: 4px;
  border-radius: var(--radius-sm);
  margin-top: 8px;
}
.form-footer {
  text-align: center;
  margin-top: 20px;
}
.footer-link {
  font-size: 13px;
  color: var(--text-secondary);
}
.footer-link a {
  color: var(--accent-cyan);
  text-decoration: none;
  margin-left: 4px;
}
.footer-link a:hover {
  text-decoration: underline;
}

/* 响应式 */
@media (max-width: 768px) {
  .login-brand {
    display: none;
  }
  .login-form-panel {
    flex: 1;
    padding: 30px 20px;
  }
  .form-card {
    padding: 32px 24px;
  }
}
</style>