import { useState } from 'react'
import axios from 'axios'

export default function SubscribePage() {
  const [form, setForm]       = useState({ first_name: '', last_name: '', email: '' })
  const [status, setStatus]   = useState(null)   // null | 'loading' | 'success' | 'error'
  const [message, setMessage] = useState('')

  const handleChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus('loading')
    setMessage('')
    try {
      const { data } = await axios.post('/api/subscribe', form)
      setStatus('success')
      setMessage(data.message)
      setForm({ first_name: '', last_name: '', email: '' })
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
          <div className="text-4xl mb-3">📬</div>
          <h2 className="text-xl font-bold">Stay Ahead of the Market</h2>
          <p className="text-blue-200 text-sm mt-2">
            Get AI-powered financial analysis delivered daily.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-6 py-8 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wide">
                First Name
              </label>
              <input
                name="first_name"
                value={form.first_name}
                onChange={handleChange}
                placeholder="Jane"
                required
                className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wide">
                Last Name
              </label>
              <input
                name="last_name"
                value={form.last_name}
                onChange={handleChange}
                placeholder="Doe"
                required
                className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wide">
              Email Address
            </label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="jane@example.com"
              required
              className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
            />
          </div>

          <button
            type="submit"
            disabled={status === 'loading'}
            className="w-full py-3 bg-blue-700 hover:bg-blue-800 text-white font-bold rounded-lg transition-colors disabled:opacity-60 disabled:cursor-not-allowed text-sm"
          >
            {status === 'loading' ? 'Subscribing…' : 'Subscribe Now'}
          </button>

          {/* Feedback */}
          {status === 'success' && (
            <div className="bg-green-50 border border-green-200 text-green-700 rounded-lg px-4 py-3 text-sm font-medium text-center">
              ✓ {message}
            </div>
          )}
          {status === 'error' && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm text-center">
              {message}
            </div>
          )}
        </form>
      </div>
    </div>
  )
}
