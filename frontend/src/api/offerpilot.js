import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

export async function uploadResume(file) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/resume/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function analyzeMatch({ resumeId = '', resumeData = null, jobText }) {
  const response = await api.post('/match', {
    resume_id: resumeId,
    resume_data: resumeData,
    job_text: jobText,
  })
  return response.data
}

export async function getInterviewQuestions(payload) {
  const response = await api.post('/interview/questions', payload)
  return response.data
}

export async function scoreInterviewAnswer(question, answer) {
  const response = await api.post('/interview/score', { question, answer })
  return response.data
}

export async function summarizeInterview(records) {
  const response = await api.post('/interview/summary', { records })
  return response.data
}

export async function generateLearningPath(payload) {
  const response = await api.post('/learning/path', payload)
  return response.data
}

export async function getQuestionCount() {
  const response = await api.get('/questions/count')
  return response.data
}
