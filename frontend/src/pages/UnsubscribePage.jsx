import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import axios from 'axios'

export default function UnsubscribePage() {
  const [searchParams] = useSearchParams()
  const email = searchParams.get('email') || ''

  const [status, setStatus]   = useState(null)   // null | 'loading' | 'success' | 'error'
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!email) {
      setStatus('error')
      setMessage('No email address provided. Please use the unsubscribe link from your email.')
    }
  }, [email])

  const handleUnsubscribe = async () => {
    setStatus('loading')
    try {
      const { data } = await axios.get(`/api/unsubscribe?email=${encodeURIComponent(email)}`)
      setStatus('success')
      setMessage(data.message)
    } catch (err) {
      setStatus('error')
      setMessage(err.response?.data?.detail ?? 'Something went wrong. Please try again.')
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-slate-900 to-blue-900 px-6 py-8 text-white text-center">
          <div className="text-4xl mb-3">📭</div>
          <h2 className="text-xl font-bold">Unsubscribe</h2>
          <p className="text-blue-200 text-sm mt-2">
            We're sorry to see you go.
          </p>
        </div>

        <div className="px-6 py-8 space-y-5 text-center">
          {status === null && email && (
            <>
              <p className="text-sm text-slate-600">
                You are about to unsubscribe <span className="font-semibold text-slate-800">{email}</span> from Market News Daily.
              </p>
              <button
                onClick={handleUnsubscribe}
                className="w-full py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg transition-colors text-sm"
              >
                Yes, unsubscribe me
              </button>
              <Link
                to="/"
                className="block text-sm text-slate-400 hover:text-slate-600 transition-colors"
              >
                Cancel — keep me subscribed
              </Link>
            </>
          )}

          {status === 'loading' && (
            <p className="text-sm text-slate-500">Unsubscribing…</p>
          )}

          {status === 'success' && (
            <>
              <div className="bg-green-50 border border-green-200 text-green-700 rounded-lg px-4 py-3 text-sm font-medium">
                ✓ {message}
              </div>
              <p className="text-sm text-slate-500">
                You will no longer receive Market News Daily emails.
              </p>
              <Link
                to="/subscribe"
                className="block text-sm text-blue-600 hover:text-blue-700 transition-colors"
              >
                Changed your mind? Subscribe again
              </Link>
            </>
          )}

          {status === 'error' && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
              {message}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
