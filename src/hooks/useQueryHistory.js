import { useState, useEffect } from 'react'

const STORAGE_KEY = 'rag_query_history'
const MAX_HISTORY = 50

export const useQueryHistory = () => {
  const [history, setHistory] = useState([])

  // Load history from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        setHistory(parsed)
      } catch (err) {
        console.error('Failed to parse query history:', err)
        setHistory([])
      }
    }
  }, [])

  // Persist history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history))
  }, [history])

  // Add a new entry to history
  const addEntry = (entry) => {
    const newEntry = {
      id: `${Date.now()}_${Math.random()}`,
      timestamp: new Date().toISOString(),
      ...entry,
    }

    setHistory((prev) => {
      const updated = [newEntry, ...prev]
      // Keep only the most recent MAX_HISTORY entries
      return updated.slice(0, MAX_HISTORY)
    })
  }

  // Clear all history
  const clearHistory = () => {
    setHistory([])
    localStorage.removeItem(STORAGE_KEY)
  }

  return { history, addEntry, clearHistory }
}
