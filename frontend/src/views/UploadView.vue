<template>
  <div class="upload-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">
        <el-icon class="title-icon"><Document /></el-icon>
        简历解析与岗位匹配
      </h2>
      <p class="page-desc">上传您的简历并输入目标岗位 JD，OfferPilot Agent 将为您深度解析匹配度</p>
    </div>

    <div class="upload-grid">
      <!-- 左侧：简历上传区 -->
      <div class="tech-card upload-panel">
        <div class="panel-header">
          <span class="panel-step">Step 1</span>
          <h3>📄 上传简历</h3>
        </div>
        <p class="panel-hint">支持 PDF / Word（.docx）格式，文件大小不超过 10MB</p>

        <el-upload
          ref="uploadRef"
          class="resume-uploader"
          drag
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          accept=".pdf,.docx"
          show-file-list="false"
        >
          <div class="upload-placeholder">
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">
              <span class="upload-primary">将简历文件拖拽到此处</span>
              <span class="upload-secondary">或 <em>点击选择文件</em></span>
            </div>
            <div class="upload-hint">仅支持 .pdf / .doc / .docx 格式</div>
          </div>
        </el-upload>

        <transition name="slide-up">
          <div v-if="uploadedFile" class="file-preview">
            <div class="preview-card">
              <el-icon class="preview-icon"><DocumentChecked /></el-icon>
              <div class="preview-info">
                <span class="preview-name">{{ uploadedFile.name }}</span>
                <span class="preview-size">{{ formatFileSize(uploadedFile.size) }}</span>
              </div>
              <div class="preview-actions">
                <el-tag type="success" size="small" effect="plain">就绪</el-tag>
                <el-button
                  type="danger"
                  size="small"
                  text
                  circle
                  class="preview-delete-btn"
                  @click="handleFileRemove"
                >
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </transition>
      </div>

      <!-- 右侧：岗位 JD 输入区 -->
      <div class="tech-card jd-panel">
        <div class="panel-header">
          <span class="panel-step">Step 2</span>
          <h3>🎯 输入岗位 JD</h3>
        </div>
        <p class="panel-hint">粘贴或输入您心仪岗位的职位描述，系统将进行智能匹配分析</p>

        <el-input
          v-model="jdText"
          type="textarea"
          class="jd-textarea"
          :rows="12"
          placeholder="请在此粘贴目标岗位的 JD（职位描述）&#10;&#10;示例：&#10;岗位名称：数据分析师&#10;岗位职责：&#10;1. 构建数据分析体系，输出分析报告&#10;2. 通过数据驱动业务决策&#10;任职要求：&#10;1. 本科及以上学历，2年以上数据分析经验&#10;2. 熟练掌握 SQL、Python（Pandas/NumPy）&#10;3. 熟悉常见统计学模型和数据分析方法"
        />

        <div class="jd-stats" v-if="jdText.length > 0">
          <span class="stat-item">
            <el-icon><Document /></el-icon>
            已输入 {{ jdText.length }} 字符
          </span>
          <span class="stat-item">
            <el-icon><MagicStick /></el-icon>
            预估解析关键词：{{ estimatedKeywords }} 个
          </span>
        </div>
      </div>
    </div>

    <!-- 分析按钮 -->
    <div class="action-bar">
      <el-button
        type="primary"
        size="large"
        class="glow-btn analyze-btn"
        :loading="analyzing"
        :disabled="!uploadedFile || !jdText.trim()"
        @click="startAnalysis"
      >
        <el-icon v-if="!analyzing"><MagicStick /></el-icon>
        {{ analyzing ? 'Agent 正在深度解析中...' : '开始智能分析' }}
      </el-button>
    </div>

    <!-- 全屏分析 Loading 遮罩 -->
    <transition name="fade">
      <div v-if="analyzing" class="analysis-overlay">
        <div class="overlay-content">
          <div class="loading-sphere">
            <div class="sphere-ring" />
            <div class="sphere-ring" />
            <div class="sphere-ring" />
            <div class="sphere-core">
              <el-icon class="core-icon"><MagicStick /></el-icon>
            </div>
          </div>
          <h3 class="loading-title">OfferPilot Agent 正在深度解析</h3>
          <p class="loading-desc">您的简历与岗位匹配度...</p>
          <div class="loading-steps">
            <div class="step" :class="{ active: analysisStep >= 1, done: analysisStep > 1 }">
              <span class="step-dot" /> 简历解析
            </div>
            <div class="step" :class="{ active: analysisStep >= 2, done: analysisStep > 2 }">
              <span class="step-dot" /> JD 关键词提取
            </div>
            <div class="step" :class="{ active: analysisStep >= 3, done: analysisStep > 3 }">
              <span class="step-dot" /> 多维能力匹配
            </div>
            <div class="step" :class="{ active: analysisStep >= 4 }">
              <span class="step-dot" /> 生成分析报告
            </div>
          </div>
          <el-progress
            :percentage="analysisProgress"
            :stroke-width="4"
            class="loading-progress"
            :show-text="false"
            color="var(--gradient-accent)"
          />
        </div>
      </div>
    </transition>

    <!-- 分析结果（Mock JSON） -->
    <transition name="slide-up">
      <div v-if="analysisResult" class="result-panel tech-card">
        <div class="result-header">
          <h3>📋 分析结果预览</h3>
          <el-button type="primary" class="glow-btn" size="small" @click="goToReport">
            查看完整报告 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        <pre class="result-json">{{ JSON.stringify(analysisResult, null, 2) }}</pre>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Document,
  UploadFilled,
  DocumentChecked,
  MagicStick,
  ArrowRight,
  Close
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { analyzeMatch, uploadResume } from '../api/offerpilot'
import { saveSession } from '../utils/session'
import { handleApiError } from '../utils/request'

const router = useRouter()

// 文件上传
const uploadRef = ref(null)
const fileList = ref([])
const uploadedFile = ref(null)
const parsedResume = ref(null)

// JD 文本
const jdText = ref('')

// 分析状态
const analyzing = ref(false)
const analysisProgress = ref(0)
const analysisStep = ref(0)
const analysisResult = ref(null)

const resumeSummary = computed(() => {
  const basic = parsedResume.value?.basic_info || {}
  const skills = parsedResume.value?.skills || []

  return {
    name: basic.name || '待解析',
    education: [basic.education, basic.major].filter(Boolean).join(' · ') || '待解析',
    experience: parsedResume.value?.experience?.length ? `${parsedResume.value.experience.length} 段经历` : '待解析',
    skills: skills.length ? skills.slice(0, 5) : ['Python', 'MySQL', 'Django', 'Linux', 'Git'],
  }
})

// 预估关键词数量
const estimatedKeywords = computed(() => {
  if (!jdText.value.trim()) return 0
  // 简单按空格和标点分词估算
  const words = jdText.value.split(/[\s,，。；;、\n]+/).filter(Boolean)
  return words.length
})

// 格式化文件大小
function formatFileSize(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  return `${size.toFixed(1)} ${units[i]}`
}

// 文件变化
function handleFileChange(file) {
  uploadedFile.value = file.raw
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 文件移除
function handleFileRemove() {
  uploadedFile.value = null
  parsedResume.value = null
  analysisResult.value = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 格式化文件大小（用于 file.raw.size）
function formatFileSizeRaw(file) {
  return formatFileSize(file?.size || 0)
}

// 开始分析
async function startAnalysis() {
  if (!uploadedFile.value || !jdText.value.trim()) {
    ElMessage.warning('请先上传简历并输入岗位 JD')
    return
  }

  analyzing.value = true
  analysisProgress.value = 0
  analysisStep.value = 0
  analysisResult.value = null
  document.body.classList.add('hide-global-loading') // 👉 [新增] 开启分析时屏蔽全局 Loading

  try {
    analysisStep.value = 1
    analysisProgress.value = 20

    const resumeResponse = await uploadResume(uploadedFile.value, { showLoading: false })
    parsedResume.value = resumeResponse.data
    saveSession({
      resumeId: resumeResponse.resume_id,
      resumeData: resumeResponse.data,
      fileName: uploadedFile.value.name,
      jobText: jdText.value,
      interviewRecords: [],
      interviewSummary: null,
      interviewSummaryRaw: '',
      learningPlan: null,
    })

    analysisStep.value = 2
    analysisProgress.value = 45

    const matchResponse = await analyzeMatch({
      resumeId: resumeResponse.resume_id,
      resumeData: resumeResponse.data,
      jobText: jdText.value,
    }, { showLoading: false })

    analysisStep.value = 3
    analysisProgress.value = 80

    analysisResult.value = matchResponse.data
    saveSession({
      matchResult: matchResponse.data,
      jobText: jdText.value,
    })

    analysisStep.value = 4
    analysisProgress.value = 100

    ElMessage.success('分析完成，数据已同步到报告页')
  } catch (error) {
    // 统一错误处理（请求内拦截器已弹出 ElMessage.error，
    // 此处确保用户能感知到分析流程中断）
    handleApiError(error, '匹配分析')
    analysisStep.value = 0
    analysisProgress.value = 0
  } finally {
    analyzing.value = false
    document.body.classList.remove('hide-global-loading')
  }
}

// 前往报告页
function goToReport() {
  router.push('/report')
}
</script>

<style scoped>
<style scoped>
:host {
  /* 升级为更鲜艳的荧光色 */
  --accent-cyan-bright: #00ffff;
  --accent-teal-bright: #00ffca;
  --text-secondary-bright: #a0aec0;
  /* 定义发光效果 */
  --glow-cyan: 0 0 15px rgba(0, 255, 255, 0.5);
  --glow-teal: 0 0 15px rgba(0, 255, 202, 0.4);
}

/* 关键帧动画：卡片轻微浮动 */
@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-4px); }
  100% { transform: translateY(0px); }
}

/* 关键帧动画：分析按钮呼吸发光 */
@keyframes btnGlow {
  0%, 100% { box-shadow: 0 0 10px rgba(0, 212, 255, 0.5); }
  50% { box-shadow: 0 0 25px rgba(0, 212, 255, 0.8); }
}

/* 关键帧动画：Step 标签流光 */
@keyframes stepShine {
  0% { background-position: 0% 50%; }
  100% { background-position: 100% 50%; }
}
.upload-view {
  max-width: 1200px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  padding: 20px;
}

/* 页面标题 */
.page-header {
  margin-bottom: 32px; /* 稍微增加底部留白 */
}
.page-title {
  font-size: 28px; /* 从 22px 放大到 28px */
  font-weight: 800; /* 加粗 */
  letter-spacing: 1px; /* 增加呼吸感 */
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-primary);
  margin-bottom: 12px;
}
.title-icon {
  color: var(--accent-cyan);
  font-size: 28px;
  filter: drop-shadow(0 0 8px rgba(0, 255, 255, 0.6));
}
.page-desc {
  color: var(--text-secondary);
  font-size: 15px; /* 从 14px 放大到 15px */
  margin-left: 40px;
  letter-spacing: 0.5px;
}

/* 双栏布局 */
.upload-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 28px;
}

/* 面板标题 */
.panel-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.panel-header h3 {
  font-size: 18px; /* 从 16px 放大到 18px */
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}
.panel-step {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 54px; /* 稍微加宽 */
  height: 26px; /* 稍微加高 */
  /* 升级为更亮的渐变并增加流光背景尺寸 */
  background: linear-gradient(135deg, #00d4ff, #00ffca, #00d4ff);
  background-size: 200% 200%;
  animation: stepShine 3s linear infinite;
  color: #0a1628;
  font-size: 12px;
  font-weight: 800; /* 加粗 */
  border-radius: 13px;
  letter-spacing: 0.5px;
  /* 增加发光 */
  box-shadow: var(--glow-cyan);
}
.panel-hint {
  font-size: 13px; /* 从 12px 放大到 13px，提升可读性 */
  color: var(--text-secondary);
  margin-bottom: 16px;
}

/* 上传组件 */
.resume-uploader :deep(.el-upload) {
  width: 100%;
}
/* 修改：上传拖拽区基础样式 */
.resume-uploader :deep(.el-upload-dragger) {
  background: rgba(0, 212, 255, 0.02);
  border: 2px dashed var(--border-glass);
  border-radius: var(--radius-md);
  padding: 36px 24px;
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
}

/* 修改：上传拖拽区悬停效果，改为荧光蓝边框和内发光 */
.resume-uploader :deep(.el-upload-dragger:hover) {
  border-color: var(--accent-cyan-bright);
  background: rgba(0, 212, 255, 0.08);
  box-shadow: inset 0 0 15px rgba(0, 255, 255, 0.1);
}

/* 修改：上传图标增加悬停时的动画 */
.resume-uploader :deep(.el-upload-dragger:hover .upload-icon) {
  animation: float 1.5s ease-in-out infinite;
  color: var(--accent-cyan-bright);
  opacity: 1;
}
.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.upload-icon {
  font-size: 44px;
  color: var(--accent-cyan);
  opacity: 0.7;
}
.upload-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.upload-primary {
  font-size: 16px; /* 从 15px 放大 */
  font-weight: 500;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}
.upload-secondary {
  font-size: 14px; /* 从 13px 放大 */
  color: var(--text-secondary);
}
.upload-secondary em {
  color: var(--accent-cyan);
  font-style: normal;
  cursor: pointer;
}
.upload-hint {
  font-size: 11px;
  color: var(--text-secondary);
  opacity: 0.7;
}

/* 文件预览 */
.file-preview {
  margin-top: 16px;
}
.preview-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  /* 升级：纯色背景改为更亮的渐变内阴影 */
  background: rgba(0, 229, 160, 0.03);
  box-shadow: inset 0 0 10px rgba(0, 255, 202, 0.1);
  /* 升级：荧光绿边框 */
  border: 1px solid rgba(0, 255, 202, 0.4);
  border-radius: var(--radius-sm);
  /* 整体加个外发光 */
  box-shadow: 0 0 15px rgba(0, 255, 202, 0.15);
}
.preview-icon {
  font-size: 28px;
  color: var(--accent-teal-bright);
  filter: drop-shadow(0 0 5px rgba(0, 255, 202, 0.5));
}
.preview-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.preview-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}
.preview-size {
  font-size: 11px;
  color: var(--text-secondary);
}

/* Mock 解析摘要 */
.mock-summary {
  margin-top: 12px;
  padding: 16px;
  background: rgba(15, 39, 68, 0.4);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-glass);
}
.summary-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 0;
}
.summary-label {
  font-size: 12px;
  color: var(--text-secondary);
  min-width: 60px;
}
.summary-value {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}
.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.skill-tags :deep(.el-tag) {
  background: rgba(0, 212, 255, 0.1) !important;
  border-color: rgba(0, 212, 255, 0.25) !important;
  color: var(--accent-cyan) !important;
}
.preview-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.preview-delete-btn {
  color: var(--text-secondary);
  transition: all 0.3s ease;
}
.preview-delete-btn:hover {
  color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}
/* JD 输入区 */
.jd-textarea :deep(.el-textarea__inner) {
  background: rgba(10, 22, 40, 0.6);
  border: 1px solid var(--border-glass);
  color: var(--text-primary);
  font-size: 14px; /* 从 13px 放大到 14px */
  line-height: 1.8; /* 保持行高，让长文本呼吸更顺畅 */
  border-radius: var(--radius-md);
  resize: none;
  font-family: inherit; /* 继承外层的现代字体 */
}
.jd-textarea :deep(.el-textarea__inner:hover) {
  border-color: rgba(0, 212, 255, 0.5);
}
.jd-textarea :deep(.el-textarea__inner:focus) {
  border-color: var(--accent-cyan-bright);
  /* 升级：聚焦时增加外发光，更有掌控感 */
  box-shadow: var(--glow-cyan);
  background: rgba(10, 22, 40, 0.8); /* 聚焦时背景更实，利于阅读 */
}
.jd-textarea :deep(.el-textarea__inner::placeholder) {
  color: var(--text-secondary);
  opacity: 0.5;
}
.jd-stats {
  margin-top: 12px;
  display: flex;
  gap: 24px;
}
.stat-item {
  font-size: 12px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 分析按钮 */
.action-bar {
  text-align: center;
  margin-bottom: 28px;
}
/* 分析按钮 */
.analyze-btn {
  width: 320px; /* 从 280px 稍微加宽，更有分量 */
  height: 52px; /* 从 48px 加高 */
  font-size: 18px; /* 从 16px 放大 */
  font-weight: 600;
  letter-spacing: 4px; /* 显著增加按钮文字间距，高级感来源 */
  border-radius: var(--radius-sm);
}
/* 全屏分析遮罩 */
.analysis-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 22, 40, 0.92);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.overlay-content {
  text-align: center;
  max-width: 500px;
}
.loading-sphere {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto 32px;
}
.sphere-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid transparent;
  border-top-color: var(--accent-cyan);
  animation: ringSpin 2s linear infinite;
}
.sphere-ring:nth-child(2) {
  inset: 10px;
  border-top-color: var(--accent-teal);
  animation-duration: 2.5s;
  animation-direction: reverse;
}
.sphere-ring:nth-child(3) {
  inset: 20px;
  border-top-color: var(--accent-purple);
  animation-duration: 3s;
}
@keyframes ringSpin {
  to { transform: rotate(360deg); }
}
.sphere-core {
  position: absolute;
  inset: 28px;
  border-radius: 50%;
  background: rgba(0, 212, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: corePulse 2s ease-in-out infinite;
}
@keyframes corePulse {
  0%, 100% { transform: scale(1); box-shadow: 0 0 20px rgba(0, 212, 255, 0.3); }
  50% { transform: scale(1.1); box-shadow: 0 0 35px rgba(0, 212, 255, 0.6); }
}
.core-icon {
  font-size: 24px;
  color: var(--accent-cyan);
}
.loading-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.loading-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 28px;
}
.loading-steps {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.loading-steps .step {
  font-size: 12px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}
.loading-steps .step .step-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}
.loading-steps .step.active {
  color: var(--accent-cyan);
}
.loading-steps .step.active .step-dot {
  background: var(--accent-cyan);
  box-shadow: 0 0 8px rgba(0, 212, 255, 0.6);
  animation: stepPulse 1s ease-in-out infinite;
}
.loading-steps .step.done {
  color: var(--accent-teal);
}
.loading-steps .step.done .step-dot {
  background: var(--accent-teal);
}
@keyframes stepPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.3); }
}
.loading-progress {
  width: 80%;
  margin: 0 auto;
}
.loading-progress :deep(.el-progress-bar__outer) {
  background: rgba(255, 255, 255, 0.08);
}

/* 分析结果 */
.result-panel {
  margin-top: 8px;
}
.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.result-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}
.result-json {
  background: rgba(10, 22, 40, 0.8);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  padding: 16px 20px;
  color: var(--accent-teal);
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.7;
  overflow-x: auto;
  max-height: 480px;
  overflow-y: auto;
}

/* 响应式 */
@media (max-width: 900px) {
  .upload-grid {
    grid-template-columns: 1fr;
  }
}
</style>
<style>
body.hide-global-loading .el-loading-mask.is-fullscreen {
  display: none !important;
  opacity: 0 !important;
  z-index: -1 !important;
}
</style>