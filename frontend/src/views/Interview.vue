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
            <span class="stat-value">{{ currentRound }} / 5</span>
          </div>
          <div class="stat">
            <span class="stat-label">平均评分</span>
            <span class="stat-value rating-stars">
              <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= avgRating }">★</span>
              <span class="rating-num">{{ avgRating.toFixed(1) }}</span>
            </span>
          </div>
          <div class="stat">
            <span class="stat-label">已用时</span>
            <span class="stat-value">{{ formattedTime }}</span>
          </div>
        </div>
      </div>
      <div class="control-actions">
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
          v-else-if="!interviewEnded"
          type="warning"
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
        <div v-if="msg.role === 'ai'" class="message-row ai-row">
          <div class="message-avatar ai-avatar">
            <span>AI</span>
          </div>
          <div class="message-bubble ai-bubble">
            <div class="bubble-header">
              <span class="bubble-sender">AI 面试官</span>
              <span class="bubble-time">{{ msg.time }}</span>
            </div>
            <div class="bubble-content" v-html="msg.content" />
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
    <div class="tech-card input-bar" v-if="interviewStarted && !interviewEnded">
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
import { ChatLineRound, Promotion } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const chatContainer = ref(null)
const userInput = ref('')

// 面试状态
const interviewStarted = ref(false)
const interviewEnded = ref(false)
const isAiTyping = ref(false)
const currentRound = ref(0)
const totalRounds = 5

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
const avgRating = computed(() => {
  if (ratingHistory.value.length === 0) return 3.0
  const sum = ratingHistory.value.reduce((a, b) => a + b, 0)
  return sum / ratingHistory.value.length
})

// 格式化时间
const formattedTime = computed(() => {
  const m = Math.floor(elapsedSeconds.value / 60)
  const s = elapsedSeconds.value % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})

// Mock 面试题库
const questionBank = [
  {
    question: '欢迎参加 OfferPilot AI 模拟面试！我是您的 AI 面试官。\n\n首先，<strong>请简要介绍一下您最近的单体项目经验</strong>，包括项目背景、您担任的角色以及使用的核心技术栈。',
    rating: null,
    suggestion: null,
    improvements: null
  },
  {
    question: '<strong>在您的项目中，您是如何设计数据库表结构来支撑高并发场景的？</strong>请举例说明您对索引优化、SQL 调优或分库分表的实践经验。',
    rating: null,
    suggestion: null,
    improvements: null
  },
  {
    question: '<strong>请谈谈您在项目中使用过的缓存策略和技术选型。</strong>比如 Redis 在什么场景下使用？遇到过哪些缓存穿透/雪崩问题，又是如何解决的？',
    rating: null,
    suggestion: null,
    improvements: null
  },
  {
    question: '<strong>如果线上服务突然出现性能瓶颈（QPS 骤降、延迟飙升），您会从哪些维度进行排查和优化？</strong>请描述您的排查思路和工具链。',
    rating: null,
    suggestion: null,
    improvements: null
  },
  {
    question: '最后一道题：<strong>请谈谈您对容器化技术（Docker/K8s）的理解，以及您在实际项目中是否有过使用经验？</strong>如果没有，请分享您的学习计划或看法。',
    rating: null,
    suggestion: null,
    improvements: null
  }
]

// 开始面试
function startInterview() {
  interviewStarted.value = true
  interviewEnded.value = false
  messages.value = []
  ratingHistory.value = []
  summary.value = null
  currentRound.value = 0
  elapsedSeconds.value = 0
  userInput.value = ''

  // 启动计时
  timerInterval = setInterval(() => {
    elapsedSeconds.value++
  }, 1000)

  // 发送第一道面试题
  nextTick(() => {
    sendAiMessage(questionBank[0].question)
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
    messages.value.push({
      role: 'ai',
      content,
      time: getTime(),
      rating,
      suggestion,
      improvements
    })
    isAiTyping.value = false
    scrollToBottom()
  }, delay)
}

// 用户发送回答
function handleSend() {
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
  const { rating, suggestion, improvements } = generateFeedback(questionIndex, userMsg)

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
      sendAiMessage(questionBank[currentRound.value - 1].question)
    }, 1500)
  } else {
    // 面试结束
    setTimeout(() => {
      endInterview()
    }, 2000)
  }
}

// 跳过当前题
function skipQuestion() {
  if (isAiTyping.value || interviewEnded.value) return

  ElMessage.info('已跳过当前题目')

  if (currentRound.value < totalRounds) {
    currentRound.value++
    sendAiMessage(questionBank[currentRound.value - 1].question)
  } else {
    setTimeout(() => {
      endInterview()
    }, 1500)
  }
}

// 结束面试
function endInterview() {
  interviewEnded.value = true
  isAiTyping.value = false
  clearInterval(timerInterval)

  // 生成总结
  summary.value = {
    overallRating: avgRating.value.toFixed(1),
    totalRounds: ratingHistory.value.length,
    strength: ratingHistory.value.length > 0 && avgRating.value >= 3.5
      ? '项目经验表述、技术广度'
      : '基础扎实，态度认真',
    improvement: '微服务架构设计、容器化技术、高并发场景经验'
  }

  // 发送结束语
  if (!messages.value.some(m => m.role === 'ai' && m.content.includes('面试结束'))) {
    messages.value.push({
      role: 'ai',
      content: `🎉 <strong>模拟面试结束！</strong><br><br>感谢您的参与。您的综合评分为 <strong style="color: var(--accent-cyan);">${avgRating.value.toFixed(1)} / 5.0</strong>。<br><br>建议您查看完整的<strong>求职分析报告</strong>，获取详细的能力画像和学习规划。`,
      time: getTime()
    })
  }
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

<style scoped>
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
</style>