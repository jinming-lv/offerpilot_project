import request from '../utils/request'

/**
 * 生成学习路径规划
 * @param {Object} payload
 * @param {string} payload.resumeId - 简历 ID
 * @param {string} payload.jobId - 岗位 ID
 * @param {string} payload.position - 目标岗位
 * @param {string} payload.duration - 学习时长（如 "14天"）
 * @returns {Promise<{success: boolean, data: {roadmap: Array}}>}
 */
export async function generateLearningPath(payload) {
  return request.post('/learning/path', payload)
}

/**
 * 获取面试题库题目总数
 * @returns {Promise<{success: boolean, data: number}>}
 */
export async function getQuestionCount() {
  return request.get('/questions/count')
}