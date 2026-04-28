import { useState, useEffect } from 'react'

// Rate limit: max 5 queries per minute
const MAX_QUERIES = 5
const RATE_LIMIT_WINDOW = 60 * 1000 // 1 minute in milliseconds

export const useRateLimit = () => {
  const [blocked, setBlocked] = useState(false)
  const [secondsLeft, setSecondsLeft] = useState(0)
  const [queries, setQueries] = useState([]) // timestamps of recent queries

  // Check rate limit status when component mounts or queries change
  useEffect(() => {
    const now = Date.now()

    // Remove queries older than the time window
    const recentQueries = queries.filter((timestamp) => now - timestamp < RATE_LIMIT_WINDOW)
    const queriesAreDifferent =
      recentQueries.length !== queries.length ||
      recentQueries.some((timestamp, index) => timestamp !== queries[index])

    if (queriesAreDifferent) {
      setQueries(recentQueries)
    }

    // Check if rate limited
    if (recentQueries.length >= MAX_QUERIES) {
      setBlocked(true)
      const oldestQueryTime = recentQueries[0]
      const timeUntilUnlock = Math.ceil((RATE_LIMIT_WINDOW - (now - oldestQueryTime)) / 1000)
      setSecondsLeft(timeUntilUnlock)
    } else {
      setBlocked(false)
      setSecondsLeft(0)
    }
  }, [queries])

  // Tick down the countdown timer
  useEffect(() => {
    if (!blocked) return

    const interval = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          setBlocked(false)
          setQueries([])
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [blocked])

  // Record a new query
  const recordQuery = () => {
    if (!blocked) {
      setQueries((prev) => [...prev, Date.now()])
    }
  }

  return { blocked, secondsLeft, recordQuery }
}
