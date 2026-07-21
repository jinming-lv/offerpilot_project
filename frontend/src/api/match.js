import request from '../utils/request'

/**
 * 分析简历与岗位 JD 的匹配度
 * @param {Object} payload
 * @param {string} payload.resumeId - 简历 ID
 * @param {Object|null} payload.resumeData - 简历解析数据（可选，兼容前端直接传数据）
 * @param {string} payload.jobText - 岗位 JD 文本
 * @returns {Promise<{success: boolean, data: {match: object, analysis: object, radar: object, job_info: object}}>}
 */
export async function analyzeMatch({ resumeId = '', resumeData = null, jobText }) {
  return request.post('/match', {
    resume_id: resumeId,
    resume_data: resumeData,
    job_text: jobText,
  })
}