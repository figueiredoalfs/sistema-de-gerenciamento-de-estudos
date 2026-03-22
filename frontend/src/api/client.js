import axios from 'axios'

const client = axios.create({
  baseURL: '/',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let _refreshing = false
let _refreshQueue = []

client.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config

    if (error.response?.status === 401 && !original._retried) {
      const refreshToken = localStorage.getItem('refresh_token')

      if (!refreshToken) {
        localStorage.removeItem('token')
        window.location.href = '/login'
        return Promise.reject(error)
      }

      if (_refreshing) {
        // Enfileira a requisição enquanto o refresh está em andamento
        return new Promise((resolve, reject) => {
          _refreshQueue.push({ resolve, reject, config: original })
        })
      }

      original._retried = true
      _refreshing = true

      try {
        const { data } = await axios.post('/auth/refresh', { refresh_token: refreshToken })
        localStorage.setItem('token', data.access_token)
        if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token)
        original.headers.Authorization = `Bearer ${data.access_token}`

        // Retenta requisições enfileiradas
        _refreshQueue.forEach(({ resolve, config }) => {
          config.headers.Authorization = `Bearer ${data.access_token}`
          resolve(client(config))
        })
        _refreshQueue = []

        return client(original)
      } catch {
        _refreshQueue.forEach(({ reject }) => reject(error))
        _refreshQueue = []
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(error)
      } finally {
        _refreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default client
