<template>
  <div class="interview-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">
        <el-icon class="title-icon"><ChatLineRound /></el-icon>
        AI 模拟面试
      </h2>
      <p class="page-desc">与 OfferPilot 面试 Agent 进行多轮对话，获得实时点评与改进建议</p>
    </div>

    <!-- 面试控制栏 -->
    <div class="tech-card control-bar">
      <div class="control-info">
        <div class="interview-stats">
          <div class="stat">
            <span class="stat-label">当前轮次</span>
            <span class="stat-value">{{ currentRound }} / {{ totalRounds }}</span>
          </div>
          <div class="stat">
            <span class="stat-label">平均评分</span>
            <span class="stat-value rating-stars">
              <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= Math.round(currentAvg) }">★</span>
              <span class="rating-num">{{ currentAvg.toFixed(1) }}/5</span>
            </span>
          </div>
          <div class="stat">
            <span class="stat-label">已用时</span>
            <span class="stat-value">{{ formattedTime }}</span>
          </div>
        </div>
      </div>
      <div class="control-actions">
        <!-- 暂停/继续 -->
        <el-button
          v-if="interviewStarted && !interviewEnded"
          :type="isPaused ? 'success' : 'warning'"
          size="small"
          :plain="!isPaused"
          @click="togglePause"
        >
          {{ isPaused ? '继续面试' : '暂停面试' }}
        </el-button>
        <el-button
          v-if="!interviewStarted"
          type="primary"
          size="large"
          class="glow-btn start-btn"
          @click="startInterview"
        >
          🎙️ 进入模拟面试
        </el-button>
        <el-button
          v-else-if="!interviewEnded && !isPaused"
          type=""
          size="small"
          plain
          @click="skipQuestion"
        >
          跳过此题
        </el-button>
        <el-button
          v-if="interviewEnded"
          type="primary"
          size="large"
          class="glow-btn"
          @click="goToReport"
        >
          📊 查看面试分析报告
        </el-button>
        <el-button
          v-if="interviewStarted && !interviewEnded"
          type="danger"
          size="small"
          plain
          @click="endInterview"
        >
          结束面试
        </el-button>
      </div>
    </div>

    <!-- 聊天区域 -->
    <div class="tech-card chat-container" ref="chatContainer">
      <!-- 语言选择器 -->
      <div v-if="!interviewStarted" class="lang-selector-wrap">
        <div class="lang-selector-hint">选择编程语言</div>
        <div class="lang-options-row">
          <div
            v-for="lang in LANGUAGES"
            :key="lang.key"
            class="lang-pill"
            :class="{ active: selectedLang === lang.key }"
            @click="selectedLang = lang.key"
          >
            <span class="lang-pill-icon">{{ lang.icon }}</span>
            <span class="lang-pill-label">{{ lang.label }}</span>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="messages.length === 0" class="chat-empty">
        <div class="empty-icon">
          <svg viewBox="0 0 120 120" fill="none">
            <circle cx="60" cy="60" r="50" stroke="var(--accent-cyan)" stroke-width="1.5" opacity="0.3" />
            <circle cx="60" cy="60" r="30" stroke="var(--accent-teal)" stroke-width="1" opacity="0.2" stroke-dasharray="6 3" />
            <text x="60" y="55" text-anchor="middle" fill="var(--text-secondary)" font-size="28" opacity="0.6">💬</text>
            <text x="60" y="85" text-anchor="middle" fill="var(--text-secondary)" font-size="11" opacity="0.5">AI 面试官已就绪</text>
          </svg>
        </div>
        <p class="empty-text">点击上方「进入模拟面试」开始您的 AI 面试之旅</p>
        <p class="empty-hint">Agent 将模拟真实面试场景，对您的回答进行智能点评</p>
      </div>

      <!-- 消息列表 -->
      <div
        v-for="(msg, index) in messages"
        :key="index"
        class="message-wrapper"
      >
        <!-- AI 消息 -->
        <div v-if="msg.role == 'ai'" class="message-row ai-row">
          <div class="message-avatar ai-avatar">
            <span>AI</span>
          </div>
          <div class="message-bubble ai-bubble">
            <div class="bubble-header">
              <span class="bubble-sender">AI 面试官</span>
              <span class="bubble-time">{{ msg.time }}</span>
            </div>
            <!-- 分段卡片渲染 -->
            <div v-if="msg.isStructured" class="structured-content">
              <template v-for="(seg, sIdx) in msg.segments" :key="sIdx">
                <p v-if="seg.type == 'transition'" class="transition-text">{{ seg.text }}</p>
                <div v-else class="seg-bar" :class="'bar-' + seg.type">
                  <div class="seg-label-wrap">
                    <span class="seg-dot" :class="'dot-' + seg.type"></span>
                    <span class="seg-label">{{ segLabel(seg.type) }}</span>
                  </div>
                  <div class="seg-text">{{ seg.text }}</div>
                </div>
              </template>
            </div>
            <div v-else class="bubble-content" v-html="msg.content" />
            <!-- 评分卡片 -->
            <div v-if="msg.rating" class="rating-card">
              <div class="rating-header">
                <span class="rating-label">💡 回答点评</span>
                <span class="rating-stars-display">
                  <span v-for="i in 5" :key="i" class="star-lg" :class="{ filled: i <= msg.rating }">★</span>
                </span>
              </div>
              <p class="rating-suggestion">{{ msg.suggestion }}</p>
              <div v-if="msg.improvements" class="improvement-tags">
                <span class="improve-label">改进建议：</span>
                <el-tag
                  v-for="(item, idx) in msg.improvements"
                  :key="idx"
                  size="small"
                  type="warning"
                  effect="plain"
                >
                  {{ item }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- 用户消息 -->
        <div v-else class="message-row user-row">
          <div class="message-bubble user-bubble">
            <div class="bubble-header">
              <span class="bubble-sender">我</span>
              <span class="bubble-time">{{ msg.time }}</span>
            </div>
            <div class="bubble-content">{{ msg.content }}</div>
          </div>
          <div class="message-avatar user-avatar">
            <span>👤</span>
          </div>
        </div>

        <!-- 打字指示器 -->
        <div v-if="msg.typing" class="message-row ai-row">
          <div class="message-avatar ai-avatar">
            <span>AI</span>
          </div>
          <div class="message-bubble ai-bubble typing-bubble">
            <div class="typing-dots">
              <span class="dot" />
              <span class="dot" />
              <span class="dot" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="tech-card input-bar" v-if="interviewStarted && !interviewEnded && !isPaused">
      <el-input
        v-model="userInput"
        type="textarea"
        :rows="2"
        placeholder="请输入您的回答...（按 Enter 发送，Shift+Enter 换行）"
        class="chat-input"
        :disabled="isAiTyping"
        @keydown.enter.exact="handleSend"
      />
      <el-button
        type="primary"
        class="glow-btn send-btn"
        :disabled="!userInput.trim() || isAiTyping"
        :loading="isAiTyping"
        @click="handleSend"
      >
        <el-icon><Promotion /></el-icon>
        发送回答
      </el-button>
    </div>

    <!-- 面试结束总结 -->
    <transition name="slide-up">
      <div v-if="interviewEnded && summary" class="tech-card summary-card">
        <div class="summary-header">
          <h3>🎉 面试总结</h3>
          <el-tag type="success" size="large" effect="plain">面试完成</el-tag>
        </div>
        <div class="summary-grid">
          <div class="summary-item">
            <span class="s-label">综合评分</span>
            <span class="s-value gradient-text" style="font-size: 36px; font-weight: 800;">
              {{ summary.overallRating }} / 5.0
            </span>
          </div>
          <div class="summary-item">
            <span class="s-label">回答轮次</span>
            <span class="s-value">{{ summary.totalRounds }} 轮</span>
          </div>
          <div class="summary-item">
            <span class="s-label">优势领域</span>
            <span class="s-value">{{ summary.strength }}</span>
          </div>
          <div class="summary-item">
            <span class="s-label">提升方向</span>
            <span class="s-value">{{ summary.improvement }}</span>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ChatLineRound, Select, VideoPause, VideoPlay, Monitor, Check, CopyDocument } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getInterviewQuestions, scoreInterviewAnswer, summarizeInterview, generateLearningPath } from '../api/offerpilot'
import { loadSession, saveSession } from '../utils/session'
import { handleApiError } from '../utils/request'

const router = useRouter()
const chatContainer = ref(null)
const userInput = ref('')

// 面试状态
const interviewStarted = ref(false)
const interviewEnded = ref(false)
const isAiTyping = ref(false)
const isPaused = ref(false)
const isScoring = ref(false)
const answerSubmitted = ref(false)
const currentRound = ref(0)
const selectedLang = ref('Python')
const currentQuestionData = ref(null)
const totalRounds = 6

// 计时器
const elapsedSeconds = ref(0)
let timerInterval = null

// 消息列表
const messages = ref([])
// 评分历史
const ratingHistory = ref([])
// 面试总结
const summary = ref(null)

// 平均评分
const currentAvg = computed(() => {
  if (ratingHistory.value.length === 0) return 0
  const sum = ratingHistory.value.reduce((a, b) => a + b, 0)
  return sum / ratingHistory.value.length
})

// 格式化时间
const formattedTime = computed(() => {
  const m = Math.floor(elapsedSeconds.value / 60)
  const s = elapsedSeconds.value % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})

const LANGUAGES = [
  { key: 'Python', label: 'Python', icon: '🐍' },
  { key: 'Java', label: 'Java', icon: '☕' },
  { key: 'C++', label: 'C++', icon: '⚡' },
  { key: 'JavaScript', label: 'JavaScript', icon: '🟨' },
  { key: 'Go', label: 'Go', icon: '🔵' },
  { key: 'C', label: 'C', icon: '🔧' },
]


const questions = ref([])
const interviewRecords = ref([])

// 开始面试
async function startInterview() {
  interviewStarted.value = true
  interviewEnded.value = false
  messages.value = []
  ratingHistory.value = []
  interviewRecords.value = []
  summary.value = null
  currentRound.value = 0
  elapsedSeconds.value = 0
  userInput.value = ''

  if (timerInterval) clearInterval(timerInterval)

  // 启动计时
  timerInterval = setInterval(() => {
    elapsedSeconds.value++
  }, 1000)

  const session = loadSession()
  const inferredPosition = session.matchResult?.job_info?.job_title || session.interviewPosition || '后端开发工程师'
  const inferredTags = session.matchResult?.job_info?.required_skills || session.matchResult?.match?.matched_required || []

  try {
    const response = await getInterviewQuestions({
      position: inferredPosition,
      difficulty: 'medium',
      tags: inferredTags,
    })
    questions.value = response.data?.questions || []
    saveSession({ interviewQuestions: questions.value, interviewPosition: inferredPosition })
  } catch (error) {
    handleApiError(error, '获取面试题')
    interviewStarted.value = false
    return
  }

  // 发送第一道面试题
  if (questions.value.length === 0) {
    ElMessage.error('暂无可用面试题，请稍后重试')
    interviewStarted.value = false
    return
  }
  nextTick(() => {
    sendAiMessage(formatQuestion(questions.value[0]))
    currentRound.value = 1
  })
}

// AI 发送消息
function sendAiMessage(content, rating = null, suggestion = null, improvements = null) {
  isAiTyping.value = true

  // 添加打字指示器
  messages.value.push({ role: 'ai', content: '', time: getTime(), typing: true })
  scrollToBottom()

  const delay = 600 + Math.random() * 800
  setTimeout(() => {
    // 移除打字指示器
    messages.value = messages.value.filter(m => !m.typing)

    // 解析分段结构
    const parsed = parseStructuredContent(content)

    messages.value.push({
      role: 'ai',
      content,
      time: getTime(),
      rating,
      suggestion,
      improvements,
      isStructured: parsed.isStructured,
      segments: parsed.segments
    })
    isAiTyping.value = false
    scrollToBottom()
  }, delay)
}

// 解析 【标签】 分段内容
function parseStructuredContent(text) {
  // 检查是否包含 【】
  if (!text || !text.includes('【')) {
    return { isStructured: false, segments: [] }
  }

  const segments = []
  const regex = /【([^】]+)】\s*([\s\S]*?)(?=【|$)/g
  let lastEnd = 0
  let match
  let hasBracket = false

  while ((match = regex.exec(text)) !== null) {
    hasBracket = true
    const label = match[1]
    const segText = match[2].trim()

    // 标签前的内容作为过渡语
    const beforeText = text.slice(lastEnd, match.index).trim()
    if (beforeText) {
      segments.push({ type: 'transition', text: beforeText })
    }

    segments.push({ type: getSegmentType(label), text: segText, rawLabel: label })
    lastEnd = match.index + match[0].length
  }

  // 如果没有【】标签，返回非结构化
  if (!hasBracket) {
    return { isStructured: false, segments: [] }
  }

  // 最后一段之后的内容
  const afterText = text.slice(lastEnd).trim()
  if (afterText) {
    segments.push({ type: 'transition', text: afterText })
  }

  return { isStructured: true, segments }
}

// 分段标签类型（用于 CSS 类名）
function getSegmentType(label) {
  const typeMap = {
    '题目': 'question',
    '示例': 'example',
    '要求': 'requirement',
    '进阶思考': 'advanced',
    '关注点': 'focus',
    '场景描述': 'scenario',
    '问题': 'problem',
  }
  return typeMap[label] || 'other'
}

// 分段标签中文名称
function segLabel(label) {
  const labelMap = {
    'question': '📝 题目',
    'example': '📌 示例',
    'requirement': '🎯 要求',
    'advanced': '💡 进阶思考',
    'focus': '🔍 关注点',
    'scenario': '🏗️ 场景描述',
    'problem': '❓ 问题',
    'other': '📋 其他',
  }
  return labelMap[label] || label
}

function formatQuestion(questionData) {
  if (!questionData) return '当前没有可用面试题，请稍后重试。'
  return questionData.interviewer_text || questionData.description || questionData.question || questionData.title || '请回答当前问题。'
}

function normalizeRating(totalScore) {
  const score = Number(totalScore) || 0
  return Math.max(1, Math.min(5, Math.round((score / 20) * 2) / 2))
}

// 用户发送回答
async function handleSend() {
  if (!userInput.value.trim() || isAiTyping.value) return

  const userMsg = userInput.value.trim()
  userInput.value = ''

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userMsg,
    time: getTime()
  })
  scrollToBottom()

  // AI 点评
  const questionIndex = currentRound.value - 1
  const questionData = questions.value[questionIndex]

  let rating = 3
  let suggestion = ''
  let improvements = []

  try {
    const response = await scoreInterviewAnswer(questionData, userMsg)
    const scoreData = response.data || response
    rating = normalizeRating(scoreData.total_score || 0)
    suggestion = scoreData.suggestion || scoreData.summary || '回答已记录'
    improvements = scoreData.weaknesses || scoreData.improvements || []

    interviewRecords.value.push({
      question: questionData.title || questionData.question || questionData.interviewer_text || '',
      question_data: questionData,
      answer: userMsg,
      score: scoreData,
    })
    saveSession({ interviewRecords: interviewRecords.value })
  } catch (error) {
    handleApiError(error, '面试评分')
    const fallback = generateFeedback(questionIndex, userMsg)
    rating = fallback.rating
    suggestion = fallback.suggestion
    improvements = fallback.improvements

  }

  // 记录评分
  ratingHistory.value.push(rating)

  // 发送点评
  const feedbackText = generateFeedbackText(rating, suggestion)
  sendAiMessage(feedbackText, rating, suggestion, improvements)

  // 判断是否继续下一题
  if (currentRound.value < totalRounds) {
    // 延迟发送下一题
    setTimeout(() => {
      currentRound.value++
      sendAiMessage(formatQuestion(questions.value[currentRound.value - 1]))
    }, 1500)
  } else {
    // 面试结束
    setTimeout(() => {
      endInterview()
    }, 2000)
  }
}

// 暂停/继续
function togglePause() {
  isPaused.value = !isPaused.value
  if (isPaused.value) {
    ElMessage({ message: '面试已暂停', type: 'success', icon: '', duration: 2000 })
  } else {
    ElMessage({ message: '面试已继续', type: 'success', icon: '', duration: 2000 })
  }
}

// 跳过当前题
function skipQuestion() {
  if (isAiTyping.value || interviewEnded.value || isPaused.value) return

  ElMessage.info('已跳过当前题目')

  if (currentRound.value < totalRounds) {
    currentRound.value++
    sendAiMessage(formatQuestion(questions.value[currentRound.value - 1]))
  } else {
    setTimeout(() => {
      endInterview()
    }, 1500)
  }
}

// 结束面试
async function endInterview() {
  interviewEnded.value = true
  isAiTyping.value = false
  isPaused.value = false
  clearInterval(timerInterval)

  const session = loadSession()

  try {
    const summaryResponse = await summarizeInterview(interviewRecords.value)
    const learningResponse = await generateLearningPath({
      resume_id: session.resumeId || '',
      job_id: session.jobId || '',
      position: session.interviewPosition || '后端开发工程师',
      duration: '14天',
    })
    saveSession({
      interviewSummaryRaw: summaryResponse.data?.summary || summaryResponse.summary || '',
      learningPlan: learningResponse.data || learningResponse,
    })
  } catch (error) {
    handleApiError(error, '面试总结')
    ElMessage.warning('面试总结生成失败，您仍可手动查看答题记录')
  }

  // 生成总结
  summary.value = {
    overallRating: currentAvg.value.toFixed(1),
    totalRounds: ratingHistory.value.length,
    strength: ratingHistory.value.length > 0 && currentAvg.value >= 3.5
      ? '项目经验表述、技术广度'
      : '基础扎实，态度认真',
    improvement: '微服务架构设计、容器化技术、高并发场景经验'
  }

  // 发送结束语
  if (!messages.value.some(m => m.role === 'ai' && m.content.includes('面试结束'))) {
    messages.value.push({
      role: 'ai',
      content: `🎉 <strong>模拟面试结束！</strong><br><br>感谢您的参与。您的综合评分为 <strong style="color: var(--accent-cyan);">${currentAvg.value.toFixed(1)} / 5.0</strong>。<br><br>建议您查看完整的<strong>求职分析报告</strong>，获取详细的能力画像和学习规划。`,
      time: getTime()
    })
  }
  saveSession({ interviewSummary: summary.value })
  scrollToBottom()
}

// 生成点评（Mock）
function generateFeedback(index, userMsg) {
  // 基于回答长度和关键词做简单模拟
  const length = userMsg.length
  const baseRating = 2.5 + (length > 50 ? 0.5 : 0) + (length > 100 ? 0.5 : 0) + (length > 200 ? 0.5 : 0)
  const randomAdjust = (Math.random() - 0.5) * 1.0
  const rating = Math.min(5, Math.max(1, Math.round((baseRating + randomAdjust) * 2) / 2))

  const suggestions = {
    4.5: '回答非常全面，技术深度和广度都表现优秀。如果能补充具体的数据指标（如接口耗时优化百分比），会更有说服力。',
    4: '回答结构清晰，技术要点覆盖较全。建议增加更多实际案例中的问题解决细节。',
    3.5: '回答基本到位，但技术深度可以进一步加强。建议多用 STAR 法则（情境-任务-行动-结果）组织回答。',
    3: '回答涉及了一些要点，但整体深度不够。建议提前准备具体的项目案例和数据支撑。',
    2.5: '回答较为笼统，缺少具体的技术细节。建议针对常见面试题提前准备结构化的回答模板。',
    2: '回答内容偏少，建议多分享实际项目中的技术选型理由和遇到的问题。'
  }

  const allImprovements = [
    '补充具体数据指标',
    '使用 STAR 法则组织回答',
    '增加技术细节深度',
    '准备实际案例支撑',
    '梳理系统架构设计思路',
    '关注高并发场景方案'
  ]

  const suggestion = suggestions[rating] || suggestions[3]
  const improvements = allImprovements.sort(() => Math.random() - 0.5).slice(0, 2 + Math.floor(Math.random() * 2))

  return { rating, suggestion, improvements }
}

// 生成点评文本
function generateFeedbackText(rating, suggestion) {
  const stars = '⭐'.repeat(Math.floor(rating)) + (rating % 1 >= 0.5 ? '✨' : '')
  return `📝 <strong>回答点评</strong> ${stars} (${rating}/5.0)<br><br>${suggestion}`
}

// 获取当前时间
function getTime() {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

// 前往报告页
function goToReport() {
  router.push('/report')
}

// 组件销毁时清除定时器
onUnmounted(() => {
  clearInterval(timerInterval)
})
</script>

<style>
.interview-view {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 130px);
}

/* 页面标题 */
.page-header {
  margin-bottom: 16px;
  flex-shrink: 0;
}
.page-title {
  font-size: 22px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-primary);
  margin-bottom: 4px;
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

/* 控制栏 */
.control-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  margin-bottom: 16px;
  flex-shrink: 0;
}
.interview-stats {
  display: flex;
  gap: 32px;
}
.stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stat-label {
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}
.stat-value {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}
.rating-stars {
  display: flex;
  align-items: center;
  gap: 2px;
}
.star {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.2);
  transition: color 0.3s ease;
}
.star.filled {
  color: #f59e0b;
}
.rating-num {
  font-size: 13px;
  margin-left: 6px;
  color: var(--text-primary);
}
.control-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}
.start-btn {
  letter-spacing: 1px;
}

/* 聊天容器 */
.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  margin-bottom: 16px;
  min-height: 300px;
  position: relative;
}

/* 空状态 */
.chat-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 280px;
}
.empty-icon {
  width: 120px;
  height: 120px;
  margin-bottom: 20px;
}
.empty-icon svg {
  width: 100%;
  height: 100%;
}
.empty-text {
  font-size: 15px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}
.empty-hint {
  font-size: 12px;
  color: var(--text-secondary);
  opacity: 0.6;
}

/* 消息行 */
.message-wrapper {
  margin-bottom: 16px;
}
.message-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  animation: msgSlideIn 0.3s ease;
}
@keyframes msgSlideIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.ai-row {
  flex-direction: row;
}
.user-row {
  flex-direction: row-reverse;
}

/* 头像 */
.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}
.ai-avatar {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 229, 160, 0.15));
  border: 1px solid rgba(0, 212, 255, 0.3);
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-cyan);
}
.user-avatar {
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(168, 85, 247, 0.15));
  border: 1px solid rgba(124, 58, 237, 0.3);
}

/* 聊天气泡 */
.message-bubble {
  max-width: 75%;
  padding: 14px 18px;
  border-radius: var(--radius-md);
  position: relative;
}
.ai-bubble {
  background: rgba(0, 212, 255, 0.06);
  border: 1px solid rgba(0, 212, 255, 0.15);
  border-top-left-radius: 4px;
}
.user-bubble {
  background: rgba(124, 58, 237, 0.08);
  border: 1px solid rgba(124, 58, 237, 0.2);
  border-top-right-radius: 4px;
}
.bubble-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.bubble-sender {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}
.bubble-time {
  font-size: 10px;
  color: var(--text-secondary);
  opacity: 0.6;
}
.bubble-content {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.8;
}
.bubble-content :deep(br) {
  display: block;
  content: '';
  margin: 4px 0;
}

/* 评分卡片 */
.rating-card {
  margin-top: 12px;
  padding: 14px;
  background: rgba(245, 158, 11, 0.06);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: var(--radius-sm);
}
.rating-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.rating-label {
  font-size: 13px;
  font-weight: 600;
  color: #f59e0b;
}
.rating-stars-display {
  display: flex;
  gap: 2px;
}
.star-lg {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.15);
}
.star-lg.filled {
  color: #f59e0b;
}
.rating-suggestion {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 10px;
}
.improvement-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}
.improve-label {
  font-size: 11px;
  color: var(--text-secondary);
}
.improvement-tags :deep(.el-tag) {
  background: rgba(245, 158, 11, 0.1) !important;
  border-color: rgba(245, 158, 11, 0.25) !important;
  color: #f59e0b !important;
}

/* 打字指示器 */
.typing-bubble {
  padding: 16px 20px;
}
.typing-dots {
  display: flex;
  gap: 6px;
}
.typing-dots .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-cyan);
  animation: typingBounce 1.4s ease-in-out infinite;
}
.typing-dots .dot:nth-child(2) {
  animation-delay: 0.2s;
}
.typing-dots .dot:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

/* 输入栏 */
.input-bar {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  align-items: flex-end;
  flex-shrink: 0;
}
.chat-input {
  flex: 1;
}
.chat-input :deep(.el-textarea__inner) {
  background: rgba(10, 22, 40, 0.6);
  border: 1px solid var(--border-glass);
  color: var(--text-primary);
  font-size: 14px;
  border-radius: var(--radius-sm);
  resize: none;
}
.chat-input :deep(.el-textarea__inner:hover) {
  border-color: rgba(0, 212, 255, 0.4);
}
.chat-input :deep(.el-textarea__inner:focus) {
  border-color: var(--accent-cyan);
  box-shadow: 0 0 0 1px rgba(0, 212, 255, 0.2);
}
.send-btn {
  height: 46px;
  flex-shrink: 0;
  letter-spacing: 1px;
}

/* 面试总结 */
.summary-card {
  margin-top: 16px;
  flex-shrink: 0;
}
.summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.summary-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}
.summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.summary-item {
  padding: 16px;
  background: rgba(0, 212, 255, 0.04);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
}
.s-label {
  display: block;
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 6px;
}
.s-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}
/* 语言选择器 */
.lang-selector-wrap { text-align: center; padding: 10px 0 6px; margin-bottom: 4px; }
.lang-selector-hint { font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 14px; letter-spacing: 0.5px; }
.lang-options-row { display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; }
.lang-pill { display: flex; align-items: center; gap: 6px; padding: 8px 18px; border-radius: 20px; border: 1px solid var(--border-glass); background: rgba(10,22,40,0.4); cursor: pointer; transition: all 0.25s ease; }
.lang-pill:hover { border-color: rgba(0,212,255,0.4); background: rgba(0,212,255,0.08); transform: translateY(-1px); }
.lang-pill.active { border-color: var(--accent-cyan); background: rgba(0,212,255,0.12); box-shadow: 0 0 10px rgba(0,212,255,0.15); }
.lang-pill-icon { font-size: 16px; }
.lang-pill-label { font-size: 13px; font-weight: 600; color: var(--text-primary); }

/* 气泡标签 */
.bubble-tag { font-size: 10px; padding: 1px 8px; border-radius: 10px; background: rgba(0,212,255,0.12); color: var(--accent-cyan); border: 1px solid rgba(0,212,255,0.2); }

/* 结构化分段卡片 */
/* 结构化分段 — 彩色竖条 */
.structured-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.transition-text {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.8;
  margin-bottom: 2px;
}

/* 彩色竖条容器 */
.seg-bar {
  padding: 6px 0 6px 12px;
  border-left: 3px solid;
  margin-bottom: 2px;
}
.seg-label-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}
.seg-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}
.seg-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
}
.seg-text {
  font-size: 13.5px;
  line-height: 1.7;
  color: var(--text-primary);
  white-space: pre-wrap;
}

/* 各段颜色 — 竖条 + 圆点 + 标签统一 */
.bar-question { border-left-color: rgba(0, 212, 255, 0.7); }
.bar-question .seg-label { color: #00d4ff; }
.bar-question .seg-dot { background: #00d4ff; }

.bar-example { border-left-color: rgba(0, 229, 160, 0.7); }
.bar-example .seg-label { color: #00e5a0; }
.bar-example .seg-dot { background: #00e5a0; }

.bar-requirement { border-left-color: rgba(245, 158, 11, 0.7); }
.bar-requirement .seg-label { color: #f59e0b; }
.bar-requirement .seg-dot { background: #f59e0b; }

.bar-advanced { border-left-color: rgba(168, 85, 247, 0.7); }
.bar-advanced .seg-label { color: #a855f7; }
.bar-advanced .seg-dot { background: #a855f7; }

.bar-focus { border-left-color: rgba(239, 68, 68, 0.7); }
.bar-focus .seg-label { color: #ef4444; }
.bar-focus .seg-dot { background: #ef4444; }

.bar-scenario { border-left-color: rgba(59, 130, 246, 0.7); }
.bar-scenario .seg-label { color: #3b82f6; }
.bar-scenario .seg-dot { background: #3b82f6; }

.bar-problem { border-left-color: rgba(236, 72, 153, 0.7); }
.bar-problem .seg-label { color: #ec4899; }
.bar-problem .seg-dot { background: #ec4899; }

.bar-other { border-left-color: rgba(148, 163, 184, 0.7); }
.bar-other .seg-label { color: #94a3b8; }
.bar-other .seg-dot { background: #94a3b8; }
.copy-code-btn { color: var(--accent-cyan) !important; font-size: 12px; }
</style>