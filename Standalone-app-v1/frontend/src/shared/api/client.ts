/**
 * Centralised Axios API client.
 *
 * Usage:
 *   import apiClient from '@/shared/api/client'
 *   const data = await apiClient.get('/api/estimates')
 *
 * In development the Vite proxy forwards /api/* → backend:8000.
 * In Docker the VITE_API_TARGET env var overrides the target automatically.
 */
import axios from 'axios'

const apiClient = axios.create({
  // Empty baseURL: Vite dev-server proxy handles /api/* in dev.
  // For production builds set VITE_API_BASE_URL at build time if needed.
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30_000,
})

// Request interceptor — attach API key if configured
apiClient.interceptors.request.use((config) => {
  const apiKey = import.meta.env.VITE_API_KEY
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey
  }
  return config
})

// Response interceptor — unwrap ApiResponse envelope
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Normalise error messages
    const message =
      error.response?.data?.error?.message ??
      error.response?.data?.detail ??
      error.message ??
      'Errore sconosciuto'
    return Promise.reject(new Error(message))
  },
)

export default apiClient
