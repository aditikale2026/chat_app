import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authAPIClient } from '../utils/api'

const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [sessionExpired, setSessionExpired] = useState(false)

  // ─────────────────────────────────────────────────────────────
  // Rehydrate on mount - check if user already has valid token
  // ─────────────────────────────────────────────────────────────
  useEffect(() => {
    const rehydrate = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const { data } = await authAPIClient.me()
          setUser(data)
          setLoading(false)
        } catch (err) {
          localStorage.removeItem('access_token')
          setUser(null)
          setLoading(false)
        }
      } else {
        setLoading(false)
      }
    }
    rehydrate()
  }, [])

  // ─────────────────────────────────────────────────────────────
  // Listen for session-expired event from API interceptor
  // ─────────────────────────────────────────────────────────────
  useEffect(() => {
    const handler = () => setSessionExpired(true)
    window.addEventListener('session-expired', handler)
    return () => window.removeEventListener('session-expired', handler)
  }, [])

  // ─────────────────────────────────────────────────────────────
  // Login - POST /auth/login
  // ─────────────────────────────────────────────────────────────
  const login = useCallback(async (username, password) => {
    const { data } = await authAPIClient.login(username, password)
    localStorage.setItem('access_token', data.access_token)
    // Extract user info from JWT (alternatively call /auth/me)
    setUser({ username, role: 'user' })
    setSessionExpired(false)
    return data
  }, [])

  // ─────────────────────────────────────────────────────────────
  // Register - POST /auth/register
  // ─────────────────────────────────────────────────────────────
  const register = useCallback(async (username, password) => {
    const { data } = await authAPIClient.register(username, password)
    localStorage.setItem('access_token', data.access_token)
    setUser({ username, role: 'user' })
    setSessionExpired(false)
    return data
  }, [])

  // ─────────────────────────────────────────────────────────────
  // Logout - POST /auth/logout
  // ─────────────────────────────────────────────────────────────
  const logout = useCallback(async () => {
    try {
      await authAPIClient.logout()
    } catch (err) {
      console.error('Logout error:', err)
    }
    localStorage.removeItem('access_token')
    setUser(null)
    setSessionExpired(false)
  }, [])

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    sessionExpired,
    setSessionExpired,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
