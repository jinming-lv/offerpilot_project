import request from '../utils/request'

/**
 * 获取 AI 模拟面试题目
 * @param {Object} payload
 * @param {string} payload.position - 目标岗位
 * @param {string} payload.difficulty - 难度 (easy/medium/hard)
 * @param {Array<string>} payload.tags - 技能标签
 * @returns {Promise<{success: boolean, data: {questions: Array, total: number, position: string}}>}
 */
export async function getInterviewQuestions(payload) {
  return request.post('/interview/questions', payload)
}

/**
 * 对面试回答进行评分
 * @param {Object} question - 面试题对象
 * @param {string} answer - 用户回答
 * @returns {Promise<{success: boolean, data: {total_score: number, suggestion: string, weaknesses: Array}}>}
 */
export async function scoreInterviewAnswer(question, answer) {
  return request.post('/interview/score', { question, answer })
}

/**
 * 生成面试总结
 * @param {Array} records - 面试记录列表
 * @returns {Promise<{success: boolean, data: {summary: string}}>}
 */
export async function summarizeInterview(records) {
  return request.post('/interview/summary', { records })
}