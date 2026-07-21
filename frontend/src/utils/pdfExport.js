/**
 * ============================================================
 *  pdfExport.js — pdfmake 方案 · 文字可选中的真正 PDF
 *
 *  彻底替代 html2pdf.js + html2canvas 截图方案
 * ============================================================
 */
import pdfMake from 'pdfmake/build/pdfmake'
import { ElMessage } from 'element-plus'
import { getFontBase64 } from './pdfmake-fonts'
import { handleApiError } from './request'

const FONT_FAMILY = 'NotoSansSC'
const VFS_KEY = 'NotoSansSC-Regular.otf'

let fontReady = false

/**
 * 返回 { fonts, vfs } 供 createPdf() 的第 3、4 参数使用。
 *
 * pdfmake 源码签名（已验证）：
 *   createPdf(docDefinition, tableLayouts, fonts, vfs)
 *
 * 将 fonts/vfs 作为参数透传，绕过全局 pdfMake.vfs 对象引用问题。
 */
export async function ensureChineseFont() {
  if (fontReady) return

  const base64 = await getFontBase64()

  // fonts —— 直接赋值到 pdfMake.fonts（fonts 结构无闭包问题）
  pdfMake.fonts = {
    ...(pdfMake.fonts || {}),
    [FONT_FAMILY]: {
      normal: VFS_KEY,
      bold: VFS_KEY,
      italics: VFS_KEY,
      bolditalics: VFS_KEY,
    },
  }

  // vfs —— 作为独立对象传入 createPdf()，不依赖全局引用
  pdfMake._customVfs = { [VFS_KEY]: base64 }

  fontReady = true
}

export function safeExportChart(chart) {
  if (!chart) return null
  try {
    // 优先使用 ECharts 5.x getRenderedCanvas 方法
    const canvas = chart.getRenderedCanvas
      ? chart.getRenderedCanvas({ pixelRatio: 2, backgroundColor: '#ffffff' })
      : null
    if (canvas && canvas.width > 0 && canvas.height > 0) {
      return canvas.toDataURL('image/png')
    }
    // 回退到 getDataURL
    return chart.getDataURL({ type: 'png', pixelRatio: 2, backgroundColor: '#ffffff' })
  } catch (e) {
    console.warn('[PDF Export] 图表导出失败:', e.message)
    ElMessage.warning('图表渲染失败，报告中图表部分将显示为占位文字')
    return null
  }
}

function sanitize(str) {
  if (typeof str !== 'string') return str
  return str.replace(/[\u200B-\u200D\uFEFF\u00AD\u2060\u2028\u2029\u202A-\u202E]/g, '')
}

export async function exportPDF(reportData, radarImg, barImg) {
  try {
    await ensureChineseFont()

    const docDefinition = {
      pageSize: 'A4',
      pageMargins: [40, 40, 40, 40],

      defaultStyle: {
        font: FONT_FAMILY,
        fontSize: 11,
        lineHeight: 1.5,
        color: '#1e293b',
      },

      styles: {
        reportTitle: {
          font: FONT_FAMILY,
          fontSize: 24,
          bold: true,
          color: '#0f172a',
          alignment: 'center',
          margin: [0, 0, 0, 4],
        },
        sectionTitle: {
          font: FONT_FAMILY,
          fontSize: 14,
          bold: true,
          color: '#1e40af',
          margin: [0, 14, 0, 6],
        },
      },

      content: buildContent(reportData, radarImg, barImg),
    }

    // pdfmake createPdf(docDefinition, tableLayouts, fonts, vfs)
    // 第 3 参数 = pdfMake.fonts（全局已注入 NotoSansSC）
    // 第 4 参数 = pdfMake._customVfs（独立 vfs 对象，含中文字体 base64）
    pdfMake.createPdf(docDefinition, null, pdfMake.fonts, pdfMake._customVfs).download(
      `OfferPilot_${sanitize(reportData.candidateName || '报告')}.pdf`
    )
    ElMessage.success('PDF 报告已成功导出！')
  } catch (err) {
    console.error('[PDF Export] 导出失败:', err)

    // 构造标准错误对象，复用 handleApiError 统一处理
    const error = new Error(err.message || 'PDF 导出失败')
    error.code = 'PDF_EXPORT_FAILED'

    // 区分字体加载失败
    if (err.message?.includes('font') || err.message?.includes('vfs')) {
      ElMessage.error('【PDF 导出】中文字体加载失败，请检查网络连接后重试')
    } else if (err.message?.includes('download')) {
      ElMessage.error('【PDF 导出】浏览器阻止了文件下载，请检查下载设置')
    } else {
      handleApiError(error, 'PDF 导出')
    }
    throw error
  }
}

function buildContent(d, radarImg, barImg) {
  const content = []

  content.push({ text: 'OfferPilot 求职分析报告', style: 'reportTitle' })

  content.push({
    margin: [0, 16, 0, 10],
    table: {
      widths: ['*', '*'],
      body: [
        [
          { text: `姓    名：${sanitize(d.candidateName)}`, margin: [0, 2] },
          { text: `学    历：${sanitize(d.candidateEdu)}`, margin: [0, 2] },
        ],
        [
          { text: `工作经验：${d.candidateExpYears} 年`, margin: [0, 2] },
          { text: `目标岗位：${sanitize(d.jobTitle)}`, margin: [0, 2] },
        ],
        [
          { text: `匹配度：${d.overallMatch}%`, margin: [0, 2], colSpan: 2 },
          {},
        ],
      ],
    },
    layout: 'noBorders',
  })

  content.push({ text: '能力画像雷达图', style: 'sectionTitle' })
  if (radarImg) {
    content.push({ image: radarImg, width: 300, alignment: 'center', margin: [0, 4, 0, 8] })
  } else {
    content.push({ text: '（图表暂不可用）', color: '#94a3b8', italics: true, alignment: 'center', margin: [0, 4, 0, 8] })
  }

  content.push({ text: '多维能力得分对比', style: 'sectionTitle' })
  if (barImg) {
    content.push({ image: barImg, width: 400, alignment: 'center', margin: [0, 4, 0, 8] })
  } else {
    content.push({ text: '（图表暂不可用）', color: '#94a3b8', italics: true, alignment: 'center', margin: [0, 4, 0, 8] })
  }

  content.push({ text: '优势技能', style: 'sectionTitle' })
  if ((d.strengths || []).length) {
    d.strengths.forEach((s) => {
      content.push({ text: `• ${sanitize(s.skill)}（${sanitize(s.level)}）`, margin: [8, 2] })
    })
  } else {
    content.push({ text: '（暂无数据）', color: '#94a3b8', italics: true })
  }

  content.push({ text: '能力差距', style: 'sectionTitle' })
  if ((d.weaknesses || []).length) {
    d.weaknesses.forEach((w) => {
      content.push({
        stack: [
          { text: sanitize(w.skill), bold: true, margin: [0, 2], font: FONT_FAMILY },
          { text: sanitize(w.gap), margin: [4, 0, 0, 6], color: '#64748b', fontSize: 10, font: FONT_FAMILY },
        ],
        margin: [8, 2],
      })
    })
  } else {
    content.push({ text: '（暂无数据）', color: '#94a3b8', italics: true })
  }

  content.push({ text: '14 天学习规划', style: 'sectionTitle' })
  if ((d.studyPlan || []).length) {
    d.studyPlan.forEach((p) => {
      content.push({ text: `${sanitize(p.days)}：${sanitize(p.topic)}`, margin: [8, 2] })
    })
  } else {
    content.push({ text: '（暂无数据）', color: '#94a3b8', italics: true })
  }

  content.push({ text: '面试建议', style: 'sectionTitle' })
  if ((d.interviewQuestions || []).length) {
    d.interviewQuestions.forEach((q, idx) => {
      content.push({ text: `${idx + 1}. ${sanitize(q)}`, margin: [8, 2] })
    })
  } else {
    content.push({ text: '（暂无数据）', color: '#94a3b8', italics: true })
  }

  return content
}