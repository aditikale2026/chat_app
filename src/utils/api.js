import axios from 'axios'

const API = axios.create({
  baseURL: '',
  withCredentials: true,
})

// Add token to every request
API.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authAPI = {
  login: (username, password) =>
    API.post('/ui/login', { username, password }),
  register: (username, password) =>
    API.post('/ui/register', { username, password }),
  logout: () =>
    API.post('/ui/logout'),
}

export const ragAPI = {
  query: (query) =>
    API.post('/rag/query', { query }),
  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return API.post('/rag/upload_document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export const healthAPI = {
  check: () =>
    API.get('/health'),
}

export default API
