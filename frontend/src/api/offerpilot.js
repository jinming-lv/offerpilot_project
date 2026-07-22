/**
 * OfferPilot API 统一导出入口
 *
 * 各业务域 API 模块：
 *   - resume.js    简历上传、JD 解析
 *   - match.js     简历-岗位匹配分析
 *   - interview.js AI 模拟面试（出题、评分、总结）
 *   - learning.js  学习路径规划、题库信息
 */

// -- Resume 域 --
export { uploadResume, parseJd } from './resume'

// -- Match 域 --
export { analyzeMatch } from './match'

// -- Interview 域 --
export {
  getInterviewQuestions,
  scoreInterviewAnswer,
  summarizeInterview,
} from './interview'

// -- Learning 域 --
export { generateLearningPath, getQuestionCount } from './learning'

// -- Auth 域 --
export { login, checkMembership } from './auth'