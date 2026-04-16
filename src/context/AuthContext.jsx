import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkAuth = () => {
      // Check if token exists in localStorage or cookies
      const token = localStorage.getItem('access_token') || 
                    document.cookie.split('; ').find(row => row.startsWith('access_token='))?.split('=')[1]
      
      if (token) {
        setUser({ authenticated: true, token })
      }
      setLoading(false)
    }
    checkAuth()
  }, [])

  const login = (userData) => {
    setUser(userData)
    // Store token if provided
    if (userData.token) {
      localStorage.setItem('access_token', userData.token)
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('access_token')
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
