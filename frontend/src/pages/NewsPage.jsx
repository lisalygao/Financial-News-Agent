import { useState, useEffect } from 'react'
import axios from 'axios'
import NewsCard from '../components/NewsCard'

export default function NewsPage() {
  const [items, setItems]       = useState([])
  const [loading, setLoading]   = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError]       = useState(null)

  const loadNews = async () => {
    try {
      const { data } = await axios.get('/api/news')
      setItems(data.items)
      setError(null)
    } catch {
      setError('Could not load news. Try refreshing.')
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    setError(null)
    try {
      await axios.post('/api/news/refresh')
      await loadNews()
    } catch {
      setError('Refresh failed. Please try again.')
    } finally {
      setRefreshing(false)
    }
  }

  useEffect(() => { loadNews() }, [])

  return (
    <div>
      {/* Page header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Today's Top Stories</h2>
          <p className="text-slate-500 text-sm mt-1">AI-powered analysis of the 5 biggest market headlines</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing || loading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-700 text-white rounded-lg text-sm font-semibold hover:bg-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span className={refreshing ? 'animate-spin' : ''}>⟳</span>
          {refreshing ? 'Fetching…' : 'Refresh'}
        </button>
      </div>

      {/* States */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-24 text-slate-400">
          <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4" />
          <p>Loading latest news…</p>
        </div>
      )}

      {error && !loading && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-5 py-4 text-sm mb-6">
          {error}
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="bg-white rounded-xl border border-slate-200 py-20 text-center text-slate-400">
          <p className="text-4xl mb-3">📰</p>
          <p className="font-medium">No news yet</p>
          <p className="text-sm mt-1">Click <strong>Refresh</strong> to fetch today's headlines.</p>
        </div>
      )}

      {/* News cards */}
      {!loading && items.length > 0 && (
        <div className="space-y-5">
          {items.map((item, i) => (
            <NewsCard key={item.id} item={item} index={i} />
          ))}
        </div>
      )}
    </div>
  )
}
