<template>
  <!--
    PdfReportTemplate.vue — 独立 PDF 打印模板组件
    ⚠️ 样式必须使用非 scoped，否则 html2pdf 无法读取
    ⚠️ 亮色 / 打印专用主题，与屏幕暗色主题完全隔离
  -->
  <div class="pdf-report">
    <!-- ===== 页眉 ===== -->
    <div class="pdf-header">
      <div class="pdf-logo">Offer<span class="hl">Pilot</span></div>
      <div class="pdf-title">求职竞争力分析报告</div>
      <div class="pdf-line" />
    </div>

    <!-- ===== 基本信息 ===== -->
    <table class="info-table">
      <tr>
        <td class="info-label">候选人</td>
        <td class="info-value">{{ props.reportData.candidateName }}</td>
        <td class="info-label">目标岗位</td>
        <td class="info-value">{{ props.reportData.jobTitle }}</td>
        <td class="info-label">日期</td>
        <td class="info-value">{{ reportDate }}</td>
      </tr>
      <tr>
        <td class="info-label">学历背景</td>
        <td class="info-value">{{ props.reportData.candidateEdu }}</td>
        <td class="info-label">工作经验</td>
        <td class="info-value">{{ props.reportData.candidateExpYears }} 年</td>
        <td class="info-label">综合匹配</td>
        <td class="info-value match-score">⭐ {{ props.reportData.overallMatch }}%</td>
      </tr>
    </table>

    <!-- ===== 能力画像雷达图 ===== -->
    <div class="section page-break-avoid">
      <h2 class="section-title">🕸️ 能力画像雷达图</h2>
      <div class="chart-wrap">
        <img
          v-if="props.chartImages.radarChart"
          :src="props.chartImages.radarChart"
          class="chart-img"
          alt="能力画像雷达图"
        />
        <span v-else class="chart-fallback">[ 雷达图数据暂不可用 ]</span>
      </div>
    </div>

    <!-- ===== 多维能力得分对比 ===== -->
    <div class="section page-break-avoid">
      <h2 class="section-title">📈 多维能力得分对比</h2>
      <div class="chart-wrap">
        <img
          v-if="props.chartImages.barChart"
          :src="props.chartImages.barChart"
          class="chart-img"
          alt="多维能力得分对比"
        />
        <span v-else class="chart-fallback">[ 柱状图数据暂不可用 ]</span>
      </div>
    </div>

    <!-- ===== 总体匹配度仪表盘 ===== -->
    <div class="section page-break-avoid">
      <h2 class="section-title">📊 总体匹配度</h2>
      <div class="chart-wrap chart-wrap-small">
        <img
          v-if="props.chartImages.matchChart"
          :src="props.chartImages.matchChart"
          class="chart-img chart-img-small"
          alt="总体匹配度仪表盘"
        />
        <span v-else class="chart-fallback">[ 仪表盘数据暂不可用 ]</span>
      </div>
    </div>

    <!-- ===== 优势与不足 ===== -->
    <div class="section page-break-avoid">
      <h2 class="section-title">✅ 优势技能 & ⚠️ 能力差距</h2>
      <div class="two-col">
        <div class="col">
          <h3 class="col-title good">优势技能</h3>
          <ul class="skill-list">
            <li v-for="(item, idx) in props.reportData.strengths" :key="'s-' + idx" class="skill-item good-item">
              <span class="skill-name">{{ item.skill }}</span>
              <span class="skill-level">{{ item.level }}</span>
            </li>
          </ul>
        </div>
        <div class="col">
          <h3 class="col-title bad">能力差距</h3>
          <ul class="skill-list">
            <li v-for="(item, idx) in props.reportData.weaknesses" :key="'w-' + idx" class="skill-item bad-item">
              <span class="skill-name">{{ item.skill }}</span>
              <span class="skill-gap">{{ item.gap }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- ===== 学习规划 ===== -->
    <div class="section page-break-avoid">
      <h2 class="section-title">🗓️ 14 天学习规划路线</h2>
      <table class="plan-table">
        <thead>
          <tr>
            <th>时间</th>
            <th>学习内容</th>
            <th>优先级</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, idx) in props.reportData.studyPlan" :key="'p-' + idx">
            <td class="plan-days">{{ item.days }}</td>
            <td class="plan-topic">{{ item.topic }}</td>
            <td>
              <span :class="'priority-tag priority-' + item.priority">
                {{ priorityLabel(item.priority) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ===== 面试建议 ===== -->
    <div class="section page-break-avoid">
      <h2 class="section-title">💬 面试准备建议</h2>
      <ol class="qa-list">
        <li v-for="(q, idx) in props.reportData.interviewQuestions" :key="'q-' + idx" class="qa-item">
          {{ q }}
        </li>
      </ol>
    </div>

    <!-- ===== 页脚 ===== -->
    <div class="pdf-footer">
      <div class="pdf-line" />
      <div class="footer-text">
        本报告由 OfferPilot 多智能体 AI 生成 · 仅供参考
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  reportData: {
    type: Object,
    required: true,
  },
  chartImages: {
    type: Object,
    default: () => ({
      matchChart: null,
      radarChart: null,
      barChart: null,
    }),
  },
})

const reportDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: 'long', day: 'numeric',
})

function priorityLabel(p) {
  const map = { high: '🔴 高优先', medium: '🟡 中优先', low: '🔵 低优先' }
  return map[p] || p
}
</script>

<style>
/* ================================================
   PDF 打印专用亮色主题 — 非 scoped，html2pdf 可读取
   ================================================ */

@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;800&display=swap');

@page {
  size: A4;
  margin: 20mm;
}

html,
body {
  margin: 0;
  padding: 0;
  background: #ffffff;
}

* {
  box-sizing: border-box;
}

.pdf-report,
.pdf-report * {
  scrollbar-width: none;
}

.pdf-report::-webkit-scrollbar,
.pdf-report *::-webkit-scrollbar {
  width: 0;
  height: 0;
}

.pdf-report {
  width: 170mm;
  max-width: 170mm;
  margin: 0 auto;
  padding: 0;
  font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
  font-size: 11px;
  color: #1e293b;
  background: #ffffff;
  line-height: 1.55;
}

.pdf-header {
  text-align: center;
  padding: 10px 0 6px;
  break-inside: avoid;
  page-break-inside: avoid;
}
.pdf-logo {
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: 1px;
}
.pdf-logo .hl {
  color: #0891b2;
}
.pdf-title {
  font-size: 11px;
  color: #475569;
  margin-top: 4px;
  letter-spacing: 1px;
}
.pdf-line {
  height: 1px;
  background: linear-gradient(90deg, #0ea5e9, #10b981);
  margin: 8px 0;
}

/* ===== 信息表 ===== */
.info-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}
.info-table td {
  padding: 3px 6px;
  border: 1px solid #e2e8f0;
  font-size: 10px;
}
.info-label {
  background: #f1f5f9;
  color: #64748b;
  font-weight: 600;
  width: 12%;
}
.info-value {
  color: #1e293b;
  width: 21%;
}
.match-score {
  color: #0d9488;
  font-weight: 700;
  font-size: 11px;
}

/* ===== 区块 ===== */
.section {
  margin-bottom: 12px;
  break-inside: avoid;
}
.page-break-avoid {
  page-break-inside: avoid;
  break-inside: avoid;
}
.section-title {
  font-size: 12px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 6px;
  padding-bottom: 4px;
  border-bottom: 2px solid #0ea5e9;
}

/* ===== 图表 ===== */
.chart-wrap {
  text-align: center;
  padding: 4px 0;
  break-inside: avoid;
  page-break-inside: avoid;
}
.chart-wrap-small {
  max-height: 120px;
  overflow: hidden;
}
.chart-img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
}
.chart-img-small {
  max-width: 50%;
}
.chart-fallback {
  display: inline-block;
  padding: 10px;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  color: #94a3b8;
  border-radius: 6px;
  font-size: 10px;
}

/* ===== 双栏 ===== */
.two-col {
  display: flex;
  gap: 12px;
  break-inside: avoid;
  page-break-inside: avoid;
}
.two-col .col {
  flex: 1;
}
.col-title {
  font-size: 11px;
  font-weight: 700;
  margin-bottom: 6px;
}
.col-title.good {
  color: #0d9488;
}
.col-title.bad {
  color: #ef4444;
}
.skill-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.skill-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 4px 8px;
  margin-bottom: 3px;
  border-radius: 4px;
  font-size: 10px;
}
.good-item {
  background: #f0fdfa;
  border-left: 3px solid #14b8a6;
}
.bad-item {
  background: #fef2f2;
  border-left: 3px solid #ef4444;
}
.skill-name {
  font-weight: 600;
}
.skill-level {
  color: #64748b;
  font-size: 9px;
}
.skill-gap {
  color: #64748b;
  font-size: 9px;
  max-width: 60%;
  text-align: right;
}

/* ===== 学习规划表格 ===== */
.plan-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
  break-inside: avoid;
  page-break-inside: avoid;
}
.plan-table th {
  background: #f1f5f9;
  color: #475569;
  padding: 5px 8px;
  text-align: left;
  border-bottom: 2px solid #cbd5e1;
  font-weight: 600;
}
.plan-table td {
  padding: 5px 8px;
  border-bottom: 1px solid #e2e8f0;
}
.plan-days {
  white-space: nowrap;
  color: #64748b;
  font-weight: 500;
}
.plan-topic {
  color: #1e293b;
}
.priority-tag {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 10px;
  font-size: 9px;
  font-weight: 600;
}
.priority-high {
  background: #fef2f2;
  color: #dc2626;
}
.priority-medium {
  background: #fffbeb;
  color: #d97706;
}
.priority-low {
  background: #eff6ff;
  color: #2563eb;
}

/* ===== 面试建议 ===== */
.qa-list {
  padding-left: 16px;
  margin: 0;
}
.qa-item {
  padding: 4px 0;
  font-size: 10px;
  color: #334155;
  line-height: 1.45;
}

/* ===== 页脚 ===== */
.pdf-footer {
  text-align: center;
  padding: 10px 0 6px;
  break-inside: avoid;
  page-break-inside: avoid;
}
.footer-text {
  font-size: 9px;
  color: #94a3b8;
}

@media print {
  .pdf-report {
    width: 100%;
    max-width: none;
  }
}
</style>