import { useState } from 'react'
import { Navbar } from '../components/Navbar'
import { ragAPI } from '../utils/api'
import { Upload as UploadIcon, CheckCircle, AlertCircle, Loader } from 'lucide-react'

export const UploadPage = () => {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('') // 'success', 'error', ''

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      // Validate file type
      const validTypes = ['application/pdf', 'text/plain']
      if (!validTypes.includes(selectedFile.type)) {
        setMessageType('error')
        setMessage('Only PDF and TXT files are supported')
        setFile(null)
        return
      }

      // Validate file size (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setMessageType('error')
        setMessage('File size must be less than 10MB')
        setFile(null)
        return
      }

      setFile(selectedFile)
      setMessage('')
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setMessage('')

    try {
      await ragAPI.upload(file)
      setMessageType('success')
      setMessage(`✓ "${file.name}" uploaded successfully! Start asking questions about it.`)
      setFile(null)
      document.querySelector('input[type="file"]').value = ''
    } catch (err) {
      setMessageType('error')
      setMessage(err.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-screen flex flex-col bg-dark">
      <Navbar />

      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="bg-darker border border-gray-800 rounded-xl shadow-2xl p-8">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <UploadIcon size={32} />
              </div>
              <h1 className="text-2xl font-bold text-white mb-2">Upload Documents</h1>
              <p className="text-gray-400">Upload PDF or TXT files to ask questions about them</p>
            </div>

            <form onSubmit={handleUpload} className="space-y-6">
              <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-blue-500 transition cursor-pointer group">
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.txt"
                  className="hidden"
                  id="file-input"
                />
                <label htmlFor="file-input" className="block cursor-pointer">
                  <div className="flex flex-col items-center gap-2 group-hover:text-blue-400 transition">
                    <UploadIcon size={32} className="text-gray-500 group-hover:text-blue-400" />
                    <p className="text-white font-semibold">
                      {file ? file.name : 'Click to select a file'}
                    </p>
                    <p className="text-sm text-gray-400">PDF or TXT • Max 10MB</p>
                  </div>
                </label>
              </div>

              {message && (
                <div
                  className={`flex items-start gap-3 p-4 rounded-lg ${
                    messageType === 'success'
                      ? 'bg-green-900/20 border border-green-700'
                      : 'bg-red-900/20 border border-red-700'
                  }`}
                >
                  {messageType === 'success' ? (
                    <CheckCircle size={20} className="text-green-500 flex-shrink-0 mt-0.5" />
                  ) : (
                    <AlertCircle size={20} className="text-red-500 flex-shrink-0 mt-0.5" />
                  )}
                  <p
                    className={`text-sm ${
                      messageType === 'success' ? 'text-green-400' : 'text-red-400'
                    }`}
                  >
                    {message}
                  </p>
                </div>
              )}

              <button
                type="submit"
                disabled={!file || loading}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading && <Loader size={20} className="animate-spin" />}
                {loading ? 'Uploading...' : 'Upload Document'}
              </button>
            </form>

            <div className="mt-8 p-4 bg-dark rounded-lg">
              <p className="text-sm text-gray-400 mb-3">
                <span className="font-semibold text-white">Pro Tips:</span>
              </p>
              <ul className="text-sm text-gray-400 space-y-2">
                <li>• Upload PDFs or text files to create a knowledge base</li>
                <li>• Ask specific questions about the uploaded content</li>
                <li>• Use complete sentences for better results</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
