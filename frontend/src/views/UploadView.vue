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
          :on-remove="handleFileRemove"
          :file-list="fileList"
          accept=".pdf,.docx"
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

        <!-- 文件解析预览（Mock 效果） -->
        <transition name="slide-up">
          <div v-if="uploadedFile" class="file-preview">
            <div class="preview-card">
              <el-icon class="preview-icon"><DocumentChecked /></el-icon>
              <div class="preview-info">
                <span class="preview-name">{{ uploadedFile.name }}</span>
                <span class="preview-size">{{ formatFileSize(uploadedFile.size) }}</span>
              </div>
              <el-tag type="success" size="small" effect="plain">就绪</el-tag>
            </div>
            <!-- Mock 解析结果摘要 -->
            <div class="mock-summary">
              <div class="summary-item">
                <span class="summary-label">姓名</span>
                <span class="summary-value">{{ resumeSummary.name }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">学历</span>
                <span class="summary-value">{{ resumeSummary.education }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">工作经验</span>
                <span class="summary-value">{{ resumeSummary.experience }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">关键技能</span>
                <div class="skill-tags">
                  <el-tag v-for="skill in resumeSummary.skills" :key="skill" size="small" type="info">{{ skill }}</el-tag>
                </div>
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
          placeholder="请在此粘贴目标岗位的 JD（职位描述），例如：&#10;&#10;岗位名称：Python 后端开发工程师&#10;岗位职责：&#10;1. 负责公司核心业务系统的后端开发与维护&#10;2. 参与系统架构设计和技术方案评审&#10;3. 编写高质量的 Python 代码，确保系统稳定高效运行&#10;&#10;任职要求：&#10;1. 计算机相关专业本科及以上学历&#10;2. 3年以上 Python 开发经验，熟悉 Django/Flask 框架&#10;3. 熟悉 MySQL、Redis 等常用数据库&#10;4. 了解 Docker、K8s 容器化技术优先&#10;..."
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
  ArrowRight
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { analyzeMatch, uploadResume } from '../api/offerpilot'
import { saveSession } from '../utils/session'

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
}

// 文件移除
function handleFileRemove() {
  uploadedFile.value = null
  parsedResume.value = null
  analysisResult.value = null
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

  try {
    analysisStep.value = 1
    analysisProgress.value = 20

    const resumeResponse = await uploadResume(uploadedFile.value)
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
    })

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
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || error.message || '分析失败，请检查后端服务是否已启动')
  } finally {
    analyzing.value = false
  }
}

// 前往报告页
function goToReport() {
  router.push('/report')
}
</script>

<style scoped>
.upload-view {
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  margin-bottom: 28px;
}
.page-title {
  font-size: 22px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.title-icon {
  color: var(--accent-cyan);
  font-size: 24px;
}
.page-desc {
  color: var(--text-secondary);
  font-size: 14px;
  margin-left: 34px;
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
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}
.panel-step {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 24px;
  background: var(--gradient-accent);
  color: #0a1628;
  font-size: 11px;
  font-weight: 700;
  border-radius: 12px;
  letter-spacing: 0.5px;
}
.panel-hint {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

/* 上传组件 */
.resume-uploader :deep(.el-upload) {
  width: 100%;
}
.resume-uploader :deep(.el-upload-dragger) {
  background: rgba(0, 212, 255, 0.03);
  border: 2px dashed var(--border-glass);
  border-radius: var(--radius-md);
  padding: 36px 24px;
  transition: all 0.3s ease;
}
.resume-uploader :deep(.el-upload-dragger:hover) {
  border-color: rgba(0, 212, 255, 0.5);
  background: rgba(0, 212, 255, 0.06);
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
  font-size: 15px;
  color: var(--text-primary);
}
.upload-secondary {
  font-size: 13px;
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
  background: rgba(0, 229, 160, 0.06);
  border: 1px solid rgba(0, 229, 160, 0.2);
  border-radius: var(--radius-sm);
}
.preview-icon {
  font-size: 28px;
  color: var(--accent-teal);
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

/* JD 输入区 */
.jd-textarea :deep(.el-textarea__inner) {
  background: rgba(10, 22, 40, 0.6);
  border: 1px solid var(--border-glass);
  color: var(--text-primary);
  font-size: 13px;
  line-height: 1.8;
  border-radius: var(--radius-md);
  resize: none;
}
.jd-textarea :deep(.el-textarea__inner:hover) {
  border-color: rgba(0, 212, 255, 0.4);
}
.jd-textarea :deep(.el-textarea__inner:focus) {
  border-color: var(--accent-cyan);
  box-shadow: 0 0 0 1px rgba(0, 212, 255, 0.2);
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
.analyze-btn {
  width: 280px;
  height: 48px;
  font-size: 16px;
  letter-spacing: 2px;
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