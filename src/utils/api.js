import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'
const RAG_BASE_URL = 'http://localhost:8000'

// ─────────────────────────────────────────────────────────────
// Axios instances
// ─────────────────────────────────────────────────────────────

const authAPI = axios.create({
  baseURL: '/auth',
  withCredentials: true,
})

const ragAPI = axios.create({
  baseURL: '/rag',
  withCredentials: true,
})

// ─────────────────────────────────────────────────────────────
// Request interceptor - add bearer token from localStorage
// ─────────────────────────────────────────────────────────────

const addTokenInterceptor = (axiosInstance) => {
  axiosInstance.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => Promise.reject(error)
  )
}

addTokenInterceptor(authAPI)
addTokenInterceptor(ragAPI)

// ─────────────────────────────────────────────────────────────
// Response interceptor - handle 401 & token refresh
// ─────────────────────────────────────────────────────────────

const addRefreshInterceptor = (axiosInstance) => {
  axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config

      // Handle 401 Unauthorized
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true

        // Try to refresh token
        try {
          const response = await axios.post(
            `/auth/refresh`,
            {},
            { withCredentials: true }
          )
          const newToken = response.data.access_token
          localStorage.setItem('access_token', newToken)

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return axiosInstance(originalRequest)
        } catch (refreshError) {
          // Refresh failed - clear auth and trigger logout
          localStorage.removeItem('access_token')
          window.dispatchEvent(new Event('session-expired'))
          return Promise.reject(refreshError)
        }
      }

      return Promise.reject(error)
    }
  )
}

addRefreshInterceptor(authAPI)
addRefreshInterceptor(ragAPI)

// ─────────────────────────────────────────────────────────────
// Auth API methods
// ─────────────────────────────────────────────────────────────

export const authAPIClient = {
  register: (username, password) =>
    authAPI.post('/register', { username, password }),

  login: (username, password) =>
    authAPI.post('/login', { username, password }),

  logout: () =>
    authAPI.post('/logout'),

  me: () =>
    authAPI.get('/me'),

  refresh: () =>
    authAPI.post('/refresh'),
}

// ─────────────────────────────────────────────────────────────
// RAG API methods
// ─────────────────────────────────────────────────────────────

export const ragAPIClient = {
  query: (question) =>
    ragAPI.post('/query', { query: question }),

  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return ragAPI.post('/upload_document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  getUserDocuments: () =>
    ragAPI.get('/user_documents'),

  deleteDocument: (docId) =>
    ragAPI.delete(`/delete_document/${docId}`),
}

export default { authAPIClient, ragAPIClient }