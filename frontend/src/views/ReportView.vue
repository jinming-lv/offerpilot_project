<template>
  <div class="report-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">
        <el-icon class="title-icon"><PieChart /></el-icon>
        求职分析报告
      </h2>
      <p class="page-desc">OfferPilot 多智能体分析结果 · 全面评估你的求职竞争力</p>
    </div>

    <!-- 顶部概览卡片行 -->
    <div class="overview-row">
      <!-- 总体匹配度 -->
      <div class="tech-card match-card">
        <h4 class="card-title">📊 总体匹配度</h4>
        <div class="match-content">
          <div class="match-ring" ref="matchRingRef" />
          <div class="match-info">
            <span class="match-percent gradient-text">{{ reportData.overallMatch }}%</span>
            <span class="match-label">综合匹配指数</span>
          </div>
        </div>
      </div>

      <!-- 岗位信息 -->
      <div class="tech-card job-card">
        <h4 class="card-title">🎯 目标岗位</h4>
        <div class="job-info">
          <div class="job-title-text">{{ reportData.jobTitle }}</div>
          <div class="job-company">{{ reportData.jobCompany }}</div>
          <div class="job-meta">
            <el-tag v-for="tag in reportData.jobTags" :key="tag" size="small" type="info">{{ tag }}</el-tag>
          </div>
        </div>
      </div>

      <!-- 候选人概览 -->
      <div class="tech-card candidate-card">
        <h4 class="card-title">👤 候选人</h4>
        <div class="candidate-info">
          <div class="candidate-name">{{ reportData.candidateName }}</div>
          <div class="candidate-detail">{{ reportData.candidateEdu }}</div>
          <div class="candidate-detail">工作经验 {{ reportData.candidateExpYears }} 年</div>
        </div>
      </div>
    </div>

    <!-- 主要分析区域 -->
    <div class="analysis-grid">
      <!-- 能力画像雷达图 -->
      <div class="tech-card radar-card">
        <h4 class="card-title">🕸️ 能力画像雷达图</h4>
        <div class="chart-container" ref="radarChartRef" />
      </div>

      <!-- 优劣势卡片 -->
      <div class="strength-weakness-col">
        <!-- 优势 -->
        <div class="tech-card strength-card">
          <h4 class="card-title" style="color: var(--accent-teal);">✅ 优势技能</h4>
          <div class="tag-group">
            <el-tag
              v-for="(item, idx) in reportData.strengths"
              :key="'s-' + idx"
              size="default"
              type="success"
              effect="plain"
              class="skill-tag-item"
            >
              {{ item.skill }}
              <span class="tag-level">{{ item.level }}</span>
            </el-tag>
          </div>
        </div>

        <!-- 不足 -->
        <div class="tech-card weakness-card">
          <h4 class="card-title" style="color: #f56c6c;">⚠️ 能力差距</h4>
          <div class="weakness-list">
            <div
              v-for="(item, idx) in reportData.weaknesses"
              :key="'w-' + idx"
              class="weakness-item"
            >
              <div class="weakness-skill">
                <el-tag size="default" type="danger" effect="plain">
                  {{ item.skill }}
                </el-tag>
              </div>
              <span class="weakness-gap">{{ item.gap }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 各维度得分对比图 -->
    <div class="tech-card bar-chart-card">
      <h4 class="card-title">📈 多维能力得分对比</h4>
      <div class="chart-container chart-bar" ref="barChartRef" />
    </div>

    <!-- 学习规划时间线 -->
    <div class="tech-card timeline-card">
      <h4 class="card-title">🗓️ 14 天学习规划路线</h4>
      <div class="timeline-wrap">
        <el-timeline>
          <el-timeline-item
            v-for="(item, idx) in reportData.studyPlan"
            :key="idx"
            :timestamp="item.days"
            placement="top"
            :color="getPriorityColor(item.priority)"
            :hollow="item.priority === 'low'"
          >
            <div class="timeline-content">
              <span class="timeline-topic">{{ item.topic }}</span>
              <el-tag
                :type="getPriorityTagType(item.priority)"
                size="small"
                effect="plain"
              >
                {{ getPriorityLabel(item.priority) }}
              </el-tag>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
    </div>

    <!-- 面试建议 -->
    <div class="tech-card interview-suggest-card">
      <h4 class="card-title">💬 面试准备建议</h4>
      <div class="suggest-list">
        <div
          v-for="(q, idx) in reportData.interviewQuestions"
          :key="idx"
          class="suggest-item"
        >
          <span class="suggest-num">{{ idx + 1 }}</span>
          <span class="suggest-text">{{ q }}</span>
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="action-bar">
      <el-button type="primary" size="large" class="glow-btn" @click="handleExportPDF">
        <el-icon><Download /></el-icon>
        一键导出 PDF 报告
      </el-button>
      <el-button size="large" plain class="secondary-btn" @click="goToInterview">
        <el-icon><ChatLineRound /></el-icon>
        开始模拟面试
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { PieChart, Download, ChatLineRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { loadSession } from '../utils/session'

const router = useRouter()

// 图表 DOM 引用
const matchRingRef = ref(null)
const radarChartRef = ref(null)
const barChartRef = ref(null)

// 图表实例
let matchChart = null
let radarChart = null
let barChart = null

// Mock 报告数据
const reportData = reactive({
  overallMatch: 86,
  jobTitle: 'Python 后端开发工程师',
  jobCompany: '某知名互联网科技公司 · 技术部',
  candidateName: '张三',
  candidateEdu: '本科 · 计算机科学与技术',
  candidateExpYears: 3,
  jobTags: ['3-5年经验', '本科及以上', '薪资 20-35K'],
  strengths: [
    { skill: 'Python', level: '精通' },
    { skill: 'MySQL', level: '熟练' },
    { skill: 'Django', level: '熟练' },
    { skill: 'Git', level: '熟练' },
    { skill: 'RESTful API 设计', level: '掌握' },
    { skill: 'Linux 运维', level: '掌握' }
  ],
  weaknesses: [
    { skill: 'Redis', gap: '缺少缓存中间件实战经验，建议补充 Redis 集群与缓存策略知识' },
    { skill: 'Docker', gap: '未掌握容器化部署技术，需从 Docker 基础到 Compose 编排系统学习' },
    { skill: 'K8s', gap: '不了解容器编排，建议掌握 Pod、Service、Deployment 等核心概念' },
    { skill: '消息队列', gap: '无 RabbitMQ / Kafka 使用经验，建议了解异步解耦与削峰场景' }
  ],
  dimensionScores: [
    { name: '核心技能', value: 88 },
    { name: '项目经验', value: 82 },
    { name: '学历背景', value: 90 },
    { name: '岗位匹配', value: 85 },
    { name: '面试表现', value: 78 }
  ],
  studyPlan: [
    { days: 'Day 1-2', topic: 'Redis 核心数据结构与缓存策略实战', priority: 'high' },
    { days: 'Day 3-4', topic: 'Docker 容器化基础：镜像构建与 Dockerfile 最佳实践', priority: 'high' },
    { days: 'Day 5-6', topic: 'Docker Compose 多容器编排与服务互联', priority: 'medium' },
    { days: 'Day 7-8', topic: '消息队列 RabbitMQ 入门与实践：发布订阅模式', priority: 'medium' },
    { days: 'Day 9-10', topic: 'Kubernetes 核心概念：Pod、Service、Deployment', priority: 'low' },
    { days: 'Day 11-12', topic: '微服务架构设计模式概览与实践案例分析', priority: 'low' },
    { days: 'Day 13-14', topic: '综合实战：搭建微服务 + 缓存 + 容器化 Demo 项目', priority: 'high' }
  ],
  interviewQuestions: [
    '请介绍你最近的项目中，如何设计数据库表结构来支撑高并发场景？考虑索引优化和查询性能。',
    '如果线上服务出现性能瓶颈（QPS 骤降、延迟飙升），你会从哪些维度进行排查和优化？请列出具体工具与方法论。',
    '谈谈你对 RESTful API 设计的理解，以及在项目中如何保证 API 的安全性和幂等性？',
    '假如你需要从零搭建一个微服务项目，你会如何选型技术栈？考虑服务发现、配置中心、日志收集等基础设施。'
  ]
})

function getDefaultScores() {
  return [
    { name: '核心技能', value: 88 },
    { name: '项目经验', value: 82 },
    { name: '学历背景', value: 90 },
    { name: '岗位匹配', value: 85 },
    { name: '面试表现', value: 78 }
  ]
}

function inferExperienceYears(experienceList) {
  if (!Array.isArray(experienceList) || experienceList.length === 0) return 0
  return Math.min(5, Math.max(1, experienceList.length + 1))
}

function normalizeStudyPlan(plan) {
  if (Array.isArray(plan?.roadmap)) {
    return plan.roadmap.map((item, index) => ({
      days: item.days || `Day ${item.day || index + 1}`,
      topic: item.topic || item.content || '学习内容',
      priority: item.priority || (item.estimated_hours >= 3 ? 'high' : 'medium')
    }))
  }

  if (Array.isArray(plan?.studyPlan)) return plan.studyPlan

  return reportData.studyPlan
}

function hydrateFromSession() {
  const session = loadSession()
  const resumeData = session.resumeData || {}
  const matchResult = session.matchResult || {}
  const jobInfo = matchResult.job_info || {}
  const matchData = matchResult.match || {}
  const radarData = matchResult.radar || {}
  const interviewSummary = session.interviewSummary || {}
  const learningPlan = session.learningPlan || {}

  const basicInfo = resumeData.basic_info || {}
  const matchedSkills = matchData.matched_required || matchData.matched_skills || []
  const missingSkills = matchData.missing_required || matchData.missing_skills || []
  const preferredSkills = jobInfo.preferred_skills || []

  reportData.overallMatch = matchData.match_score ?? matchResult.match_score ?? 86
  reportData.jobTitle = jobInfo.job_title || session.interviewPosition || 'Python 后端开发工程师'
  reportData.jobCompany = '本地联调岗位'
  reportData.candidateName = basicInfo.name || '张三'
  reportData.candidateEdu = [basicInfo.education, basicInfo.major].filter(Boolean).join(' · ') || '本科 · 计算机科学与技术'
  reportData.candidateExpYears = inferExperienceYears(resumeData.experience)
  reportData.jobTags = [
    ...(jobInfo.experience_level ? [jobInfo.experience_level] : ['3-5年经验']),
    ...(jobInfo.education ? [jobInfo.education] : ['本科及以上']),
    `匹配度 ${reportData.overallMatch}%`
  ]

  reportData.strengths = (matchedSkills.length ? matchedSkills : (resumeData.skills || []).slice(0, 5)).map((skill, index) => ({
    skill,
    level: index < 2 ? '精通' : '熟练'
  }))

  reportData.weaknesses = (missingSkills.length ? missingSkills : preferredSkills.slice(0, 4)).map((skill) => ({
    skill,
    gap: `建议补充 ${skill} 的实战经验`
  }))

  if (radarData.dimensions && Array.isArray(radarData.dimensions) && radarData.dimensions.length) {
    reportData.dimensionScores = radarData.dimensions.map((name, index) => ({
      name,
      value: typeof radarData.resume?.[index] === 'number'
        ? Math.round(radarData.resume[index] * 100)
        : getDefaultScores()[index % 5].value
    }))
  } else {
    reportData.dimensionScores = getDefaultScores()
  }

  reportData.studyPlan = normalizeStudyPlan(learningPlan)

  if (Array.isArray(session.interviewQuestions) && session.interviewQuestions.length) {
    reportData.interviewQuestions = session.interviewQuestions.map((item) => item.title || item.question || item.interviewer_text || item.description || '面试题目')
  } else if (session.interviewSummaryRaw) {
    reportData.interviewQuestions = [session.interviewSummaryRaw]
  }
}

// 优先级颜色映射
function getPriorityColor(priority) {
  const map = { high: '#f56c6c', medium: '#e6a23c', low: '#409eff' }
  return map[priority] || '#409eff'
}

function getPriorityTagType(priority) {
  const map = { high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

function getPriorityLabel(priority) {
  const map = { high: '🔴 高优先', medium: '🟡 中优先', low: '🔵 低优先' }
  return map[priority] || priority
}

// 初始化环形进度图
function initMatchChart() {
  if (!matchRingRef.value) return
  matchChart = echarts.init(matchRingRef.value)

  const option = {
    series: [
      {
        type: 'gauge',
        startAngle: 210,
        endAngle: -30,
        min: 0,
        max: 100,
        center: ['50%', '55%'],
        radius: '90%',
        splitNumber: 10,
        axisLine: {
          show: true,
          lineStyle: {
            width: 18,
            color: [
              [0.3, '#f56c6c'],
              [0.6, '#e6a23c'],
              [0.85, '#00d4ff'],
              [1, '#00e5a0']
            ]
          }
        },
        pointer: {
          icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
          length: '55%',
          width: 8,
          offsetCenter: [0, '-10%'],
          itemStyle: {
            color: 'auto'
          }
        },
        axisTick: {
          length: 10,
          lineStyle: {
            color: 'auto',
            width: 2
          }
        },
        splitLine: {
          length: 22,
          lineStyle: {
            color: 'auto',
            width: 4
          }
        },
        axisLabel: {
          show: false,
          color: '#94a3b8',
          fontSize: 11,
          distance: 20,
          formatter: '{value}%'
        },
        title: {
          offsetCenter: [0, '25%'],
          fontSize: 13,
          color: '#94a3b8'
        },
        detail: {
          show: false
        },
        data: [{ value: reportData.overallMatch, name: '匹配度' }]
      }
    ]
  }

  matchChart.setOption(option)
}

// 初始化雷达图
function initRadarChart() {
  if (!radarChartRef.value) return
  radarChart = echarts.init(radarChartRef.value)

  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(10, 22, 40, 0.9)',
      borderColor: 'rgba(0, 212, 255, 0.3)',
      textStyle: { color: '#e2e8f0' }
    },
    legend: {
      bottom: 0,
      textStyle: { color: '#94a3b8', fontSize: 12 },
      data: ['候选人画像', '岗位要求']
    },
    radar: {
      center: ['50%', '48%'],
      radius: '68%',
      indicator: reportData.dimensionScores.map(d => ({
        name: d.name,
        max: 100
      })),
      axisName: {
        color: '#94a3b8',
        fontSize: 12
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(0, 212, 255, 0.02)', 'rgba(0, 212, 255, 0.04)']
        }
      },
      splitLine: {
        lineStyle: { color: 'rgba(0, 212, 255, 0.15)' }
      },
      axisLine: {
        lineStyle: { color: 'rgba(0, 212, 255, 0.2)' }
      }
    },
    series: [
      {
        name: '候选人画像',
        type: 'radar',
        data: [
          { value: reportData.dimensionScores.map(d => d.value), name: '候选人画像' }
        ],
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: '#00d4ff',
          width: 2,
          shadowBlur: 8,
          shadowColor: 'rgba(0, 212, 255, 0.5)'
        },
        areaStyle: {
          color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.05)' }
          ])
        },
        itemStyle: {
          color: '#00d4ff',
          borderColor: '#fff',
          borderWidth: 1
        }
      },
      {
        name: '岗位要求',
        type: 'radar',
        data: [
          { value: [90, 88, 85, 95, 80], name: '岗位要求' }
        ],
        symbol: 'diamond',
        symbolSize: 5,
        lineStyle: {
          color: '#00e5a0',
          width: 2,
          type: 'dashed',
          shadowBlur: 6,
          shadowColor: 'rgba(0, 229, 160, 0.4)'
        },
        areaStyle: {
          color: 'rgba(0, 229, 160, 0.08)'
        },
        itemStyle: {
          color: '#00e5a0'
        }
      }
    ]
  }

  radarChart.setOption(option)
}

// 初始化柱状图对比
function initBarChart() {
  if (!barChartRef.value) return
  barChart = echarts.init(barChartRef.value)

  const categories = reportData.dimensionScores.map(d => d.name)
  const scores = reportData.dimensionScores.map(d => d.value)
  const required = [90, 88, 85, 95, 80]

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(10, 22, 40, 0.9)',
      borderColor: 'rgba(0, 212, 255, 0.3)',
      textStyle: { color: '#e2e8f0' }
    },
    legend: {
      textStyle: { color: '#94a3b8', fontSize: 12 },
      data: ['我的得分', '岗位要求']
    },
    grid: {
      left: '3%',
      right: '5%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLine: { lineStyle: { color: 'rgba(0, 212, 255, 0.25)' } },
      axisLabel: { color: '#94a3b8', fontSize: 12 },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      splitLine: { lineStyle: { color: 'rgba(0, 212, 255, 0.08)' } },
      axisLabel: { color: '#94a3b8', fontSize: 11, formatter: '{value}' }
    },
    series: [
      {
        name: '我的得分',
        type: 'bar',
        data: scores,
        barWidth: 22,
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#00d4ff' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.3)' }
          ])
        },
        label: {
          show: true,
          position: 'top',
          color: '#00d4ff',
          fontSize: 12,
          fontWeight: 'bold',
          formatter: '{c}分'
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 16,
            shadowColor: 'rgba(0, 212, 255, 0.6)'
          }
        }
      },
      {
        name: '岗位要求',
        type: 'bar',
        data: required,
        barWidth: 22,
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 229, 160, 0.5)' },
            { offset: 1, color: 'rgba(0, 229, 160, 0.1)' }
          ]),
          borderColor: 'rgba(0, 229, 160, 0.5)',
          borderWidth: 1,
          borderType: 'dashed'
        },
        label: {
          show: true,
          position: 'top',
          color: '#00e5a0',
          fontSize: 12,
          formatter: '{c}分'
        }
      }
    ]
  }

  barChart.setOption(option)
}

// 窗口 resize 处理
function handleResize() {
  matchChart?.resize()
  radarChart?.resize()
  barChart?.resize()
}

// 导出 PDF（Mock）
function handleExportPDF() {
  ElMessage({
    message: '正在生成 PDF 报告，请稍候...',
    type: 'info',
    duration: 2000
  })

  setTimeout(() => {
    ElMessage({
      message: '✅ PDF 报告已生成并开始下载！',
      type: 'success',
      duration: 3000
    })
  }, 1500)
}

// 前往面试页
function goToInterview() {
  router.push('/interview')
}

onMounted(() => {
  hydrateFromSession()
  nextTick(() => {
    initMatchChart()
    initRadarChart()
    initBarChart()
  })
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  matchChart?.dispose()
  radarChart?.dispose()
  barChart?.dispose()
})
</script>

<style scoped>
.report-view {
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 40px;
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

/* 卡片通用标题 */
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  letter-spacing: 0.5px;
}

/* 顶部概览行 */
.overview-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

/* 匹配度卡片 */
.match-content {
  display: flex;
  align-items: center;
  gap: 8px;
}
.match-ring {
  width: 140px;
  height: 140px;
  flex-shrink: 0;
}
.match-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.match-percent {
  font-size: 32px;
  font-weight: 800;
  line-height: 1;
}
.match-label {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 岗位信息卡片 */
.job-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.job-title-text {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
}
.job-company {
  font-size: 13px;
  color: var(--text-secondary);
}
.job-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 4px;
}

/* 候选人卡片 */
.candidate-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.candidate-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}
.candidate-detail {
  font-size: 13px;
  color: var(--text-secondary);
}

/* 分析区 */
.analysis-grid {
  display: grid;
  grid-template-columns: 1.3fr 0.7fr;
  gap: 20px;
  margin-bottom: 24px;
}

/* 图表容器 */
.chart-container {
  width: 100%;
  height: 360px;
}

/* 优势/不足列 */
.strength-weakness-col {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 优势标签组 */
.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.skill-tag-item {
  font-size: 13px !important;
  padding: 4px 14px !important;
  height: auto !important;
  line-height: 1.6 !important;
}
.skill-tag-item :deep(.el-tag__content) {
  display: flex;
  align-items: center;
  gap: 6px;
}
.tag-level {
  font-size: 10px;
  opacity: 0.7;
}
.strength-card :deep(.el-tag--success) {
  background: rgba(0, 229, 160, 0.08) !important;
  border-color: rgba(0, 229, 160, 0.25) !important;
  color: var(--accent-teal) !important;
}

/* 不足列表 */
.weakness-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.weakness-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  background: rgba(245, 108, 108, 0.04);
  border: 1px solid rgba(245, 108, 108, 0.12);
  border-radius: var(--radius-sm);
}
.weakness-gap {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* 柱状图卡片 */
.bar-chart-card {
  margin-bottom: 24px;
}
.chart-bar {
  height: 320px;
}

/* 时间线卡片 */
.timeline-card {
  margin-bottom: 24px;
}
.timeline-wrap {
  padding: 8px 0;
}
.timeline-wrap :deep(.el-timeline-item__timestamp) {
  color: var(--accent-cyan);
  font-size: 13px;
  font-weight: 600;
}
.timeline-wrap :deep(.el-timeline-item__node) {
  border-color: rgba(0, 212, 255, 0.3);
}
.timeline-wrap :deep(.el-timeline-item__content) {
  color: var(--text-primary);
}
.timeline-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.timeline-topic {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.6;
}

/* 面试建议 */
.interview-suggest-card {
  margin-bottom: 28px;
}
.suggest-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.suggest-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(0, 212, 255, 0.04);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-glass);
}
.suggest-num {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-accent);
  color: #0a1628;
  font-size: 12px;
  font-weight: 700;
  border-radius: 50%;
  flex-shrink: 0;
}
.suggest-text {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.8;
}

/* 底部操作栏 */
.action-bar {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 8px;
}
.secondary-btn {
  border-color: rgba(0, 212, 255, 0.3) !important;
  color: var(--accent-cyan) !important;
  background: rgba(0, 212, 255, 0.06) !important;
}
.secondary-btn:hover {
  border-color: rgba(0, 212, 255, 0.6) !important;
  background: rgba(0, 212, 255, 0.12) !important;
}

/* 响应式 */
@media (max-width: 900px) {
  .overview-row {
    grid-template-columns: 1fr;
  }
  .analysis-grid {
    grid-template-columns: 1fr;
  }
  .match-content {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
}
</style>