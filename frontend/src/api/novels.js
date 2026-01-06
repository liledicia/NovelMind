import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: '/api',  // 通过Vite代理转发到 http://localhost:8000/api
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
apiClient.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API请求失败:', error)
    return Promise.reject(error)
  }
)

/**
 * 搜索小说
 * @param {string} query - 小说名称
 * @returns {Promise}
 */
export const searchNovel = async (query) => {
  return apiClient.get('/novels/search', {
    params: { q: query }
  })
}

/**
 * 获取推荐列表
 * @param {number} bookId - 小说ID
 * @param {number} limit - 推荐数量
 * @returns {Promise}
 */
export const getRecommendations = async (bookId, limit = 10) => {
  return apiClient.get(`/recommendations/${bookId}`, {
    params: { limit }
  })
}

/**
 * 健康检查
 * @returns {Promise}
 */
export const healthCheck = async () => {
  return apiClient.get('/health')
}
