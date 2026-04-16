import { useAuth } from '../context/AuthContext'
import { Navigate } from 'react-router-dom'

export const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-dark">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (!user?.authenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}
