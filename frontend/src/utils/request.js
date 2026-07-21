/**
 * ============================================================
 *  request.js — 统一 HTTP 客户端
 *
 *  功能：
 *    1. axios 实例封装（baseURL / timeout / auth）
 *    2. showLoading() / hideLoading() — 全屏 Loading 遮罩
 *    3. handleApiError() — 统一错误分类与提示
 *    4. 请求/响应拦截器自动管理 Loading 状态
 *
 *  错误分类：
 *    - 网络错误（Network Error / 无响应）
 *    - 后端 500 内部错误
 *    - 请求超时（ECONNABORTED）
 *    - 文件上传失败（413 + 自定义 context）
 *    - PDF 导出失败（自定义 context 传入）
 * ============================================================
 */
import axios from 'axios'
import { ElMessage, ElLoading } from 'element-plus'

// ==================== 全局 Loading 管理 ====================
let loadingInstance = null  // ElLoading.service 实例引用
let loadingCounter = 0       // 并发请求计数

/**
 * 显示全屏 Loading 遮罩
 * @param {string} text - Loading 文字提示
 */
export function showLoading(text = '加载中...') {
  loadingCounter++
  if (!loadingInstance) {
    loadingInstance = ElLoading.service({
      lock: true,
      text,
      background: 'rgba(10, 22, 40, 0.85)',
      customClass: 'app-loading-overlay',
    })
  }
}

/**
 * 隐藏全屏 Loading 遮罩
 * 使用引用计数机制：只有最后一个并发请求完成时才关闭遮罩
 */
export function hideLoading() {
  loadingCounter = Math.max(0, loadingCounter - 1)
  if (loadingCounter === 0 && loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
  }
}

// ==================== 统一错误处理 ====================

/**
 * 统一 API 错误处理
 *
 * 错误分类：
 *   - 网络错误：浏览器无法连接到服务器
 *   - 超时错误：请求超过 timeout 配置
 *   - HTTP 4xx：客户端参数/权限/资源错误
 *   - HTTP 5xx：服务端内部错误
 *   - 文件上传失败：413 / 网络中断
 *   - PDF 导出失败：业务层传入 context 区分
 *
 * @param {Error}  error   - axios 错误对象
 * @param {string} context - 业务上下文（如 '简历上传'、'PDF 导出'），用于语义化提示
 * @returns {Promise<never>} 始终 reject，方便调用方继续链式处理
 */
export function handleApiError(error, context = '') {
  const prefix = context ? `【${context}】` : ''

  // ----- 有服务端响应（HTTP 状态码异常） -----
  if (error.response) {
    const { status, data } = error.response
    const serverMsg = data?.detail || data?.message || ''

    switch (status) {
      case 400:
        ElMessage.error(`${prefix}${serverMsg || '请求参数有误，请检查输入'}`)
        break
      case 401:
        ElMessage.error('登录已过期，请重新登录')
        localStorage.removeItem('offerpilot_token')
        localStorage.removeItem('offerpilot_session_v1')
        window.location.hash = '#/login'
        break
      case 403:
        ElMessage.error(`${prefix}没有权限访问该资源`)
        break
      case 404:
        ElMessage.error(`${prefix}请求的资源不存在`)
        break
      case 413:
        ElMessage.error(`${prefix}上传文件过大，请压缩后重试（建议 ≤ 10MB）`)
        break
      case 422:
        ElMessage.error(`${prefix}${serverMsg || '请求数据格式有误'}`)
        break
      case 429:
        ElMessage.warning(`${prefix}请求过于频繁，请稍后重试`)
        break
      case 500:
        ElMessage.error(`${prefix}${serverMsg || '服务器内部错误，请稍后重试'}`)
        break
      case 502:
      case 503:
      case 504:
        ElMessage.error(`${prefix}服务暂时不可用，请稍后重试`)
        break
      default:
        ElMessage.error(`${prefix}${serverMsg || `请求失败 (${status})`}`)
    }

  // ----- 请求超时 -----
  } else if (error.code === 'ECONNABORTED') {
    ElMessage.error(`${prefix}请求超时，请检查网络后重试`)

  // ----- 网络错误（无响应 / CORS / DNS 解析失败） -----
  } else if (
    error.message === 'Network Error' ||
    error.code === 'ERR_NETWORK' ||
    !error.response
  ) {
    ElMessage.error(`${prefix}网络连接失败，请检查后端服务是否已启动`)

  // ----- 请求被取消 -----
  } else if (axios.isCancel(error)) {
    console.warn('[Request] 请求已被取消:', error.message)

  // ----- 兜底未知错误 -----
  } else {
    ElMessage.error(`${prefix}${error.message || '未知错误'}`)
  }

  return Promise.reject(error)
}

// ==================== Axios 实例 ====================
const request = axios.create({
  baseURL: '/api',
  timeout: 120000, // 2 分钟超时（匹配 LLM 调用耗时）
  headers: {
    'Content-Type': 'application/json',
  },
})

// ==================== 请求拦截器 ====================
request.interceptors.request.use(
  (config) => {
    // 自动携带 Token
    const token = localStorage.getItem('offerpilot_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 自动显示 Loading（默认开启，可通过 config.showLoading = false 关闭）
    if (config.showLoading !== false) {
      showLoading(config.loadingText || '加载中...')
    }

    return config
  },
  (error) => {
    hideLoading()
    return Promise.reject(error)
  }
)

// ==================== 响应拦截器 ====================
request.interceptors.response.use(
  (response) => {
    // 自动关闭 Loading
    if (response.config.showLoading !== false) {
      hideLoading()
    }
    // 直接返回 data，业务层无需再解一层 .data
    return response.data
  },
  (error) => {
    // 自动关闭 Loading
    if (error.config?.showLoading !== false) {
      hideLoading()
    }
    // 统一错误处理
    let context = ''
    if (error.config?.url?.includes('/resume/upload')) context = '简历上传'
    else if (error.config?.url?.includes('/match')) context = '匹配分析'
    else if (error.config?.url?.includes('/interview')) context = '模拟面试'
    else if (error.config?.url?.includes('/learning')) context = '学习规划'
    // PDF 导出失败不走 axios，由业务层自行调用 handleApiError

    return handleApiError(error, context)
  }
)

export default request