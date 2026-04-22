/**
 * Axios-based API client.
 * Automatically attaches the JWT token from localStorage to every request.
 */

import axios from 'axios'

// ── Types ─────────────────────────────────────────────────────────────────────

export interface Token {
  access_token: string
  token_type: string
}

export interface User {
  id: string
  email: string
  is_active: boolean
  free_analyses_used: number
  stripe_customer_id: string | null
  created_at: string
  updated_at: string
}

export interface ClauseAnalysis {
  id: string
  title: string
  original_text: string
  plain_english: string
  risk_level: 'low' | 'medium' | 'high'
  risk_score: number
  red_flags: string[]
  recommendation: string
}

export interface Analysis {
  id: string
  user_id: string
  filename: string
  file_url: string | null
  status: 'pending' | 'processing' | 'completed' | 'failed'
  overall_risk_score: number | null
  overall_risk_level: 'low' | 'medium' | 'high' | null
  summary: string | null
  clauses: ClauseAnalysis[] | null
  created_at: string
  updated_at: string
}

export interface AnalysisSummary {
  id: string
  filename: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  overall_risk_score: number | null
  overall_risk_level: 'low' | 'medium' | 'high' | null
  created_at: string
}

export interface AnalysisListResponse {
  items: AnalysisSummary[]
  total: number
  page: number
  per_page: number
}

// ── Axios instance ────────────────────────────────────────────────────────────

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token before each request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Redirect to login on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

// ── Auth ──────────────────────────────────────────────────────────────────────

export const authApi = {
  register: (email: string, password: string) =>
    api.post<Token>('/auth/register', { email, password }),

  login: (email: string, password: string) =>
    api.post<Token>('/auth/login', { email, password }),

  me: () => api.get<User>('/auth/me'),
}

// ── Contracts ─────────────────────────────────────────────────────────────────

export const contractsApi = {
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post<Analysis>('/contracts/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  list: (page = 1, perPage = 20) =>
    api.get<AnalysisListResponse>('/contracts', { params: { page, per_page: perPage } }),

  get: (id: string) => api.get<Analysis>(`/contracts/${id}`),

  delete: (id: string) => api.delete(`/contracts/${id}`),
}

export default api
