import request from '../utils/request'

/**
 * 上传简历文件（PDF/DOCX），提取结构化信息
 * @param {File} file - 简历文件
 * @returns {Promise<{success: boolean, resume_id: string, data: object}>}
 */
export async function uploadResume(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/resume/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/**
 * 解析岗位 JD 文本
 * @param {string} jobText - JD 文本内容
 * @returns {Promise<{success: boolean, data: object}>}
 */
export async function parseJd(jobText) {
  return request.post('/parse_jd', { job_text: jobText })
}