import axios from 'axios'

// 生产环境用 VITE_API_BASE_URL（在 Vercel 设置环境变量）
// 开发环境通过 Vite proxy 转发，baseURL 为 /api 即可
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

apiClient.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API请求失败:', error)
    return Promise.reject(error)
  }
)

export const searchNovel = (query) =>
  apiClient.get('/novels/search', { params: { q: query } })

export const getRecommendations = (bookId, limit = 10) =>
  apiClient.get(`/recommendations/${bookId}`, { params: { limit } })

export const healthCheck = () =>
  apiClient.get('/health')
