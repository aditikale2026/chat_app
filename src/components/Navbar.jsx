import { LogOut, Upload, MessageCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { authAPIClient } from '../utils/api'
import { useState } from 'react'

export const Navbar = () => {
  const navigate = useNavigate()
  const { logout } = useAuth()
  const [loading, setLoading] = useState(false)

  // ⭐ FILE THAT CALLS THE LOGOUT POST REQUEST
  const handleLogout = async () => {
    setLoading(true)
    try {
      await authAPIClient.logout()
      logout()
      navigate('/login')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <nav className="bg-darker border-b border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <MessageCircle size={24} />
            </div>
            <h1 className="text-xl font-bold text-white">RAG Chat</h1>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/chat')}
              className="flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-gray-800 transition text-gray-300 hover:text-white"
              title="Chat"
            >
              <MessageCircle size={20} />
              <span className="hidden sm:inline">Chat</span>
            </button>

            <button
              onClick={() => navigate('/upload')}
              className="flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-gray-800 transition text-gray-300 hover:text-white"
              title="Upload"
            >
              <Upload size={20} />
              <span className="hidden sm:inline">Upload</span>
            </button>

            <button
              onClick={handleLogout}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 transition text-white disabled:opacity-50"
            >
              <LogOut size={20} />
              <span className="hidden sm:inline">{loading ? 'Logging out...' : 'Logout'}</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
