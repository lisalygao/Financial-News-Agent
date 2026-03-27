import { useState, useEffect } from 'react'
import axios from 'axios'

const SENTIMENT_CONFIG = {
  Bullish: { arrow: '↑', word: 'Positive', color: 'text-red-600',    bg: 'bg-red-50',    border: 'border-red-200'    },
  Bearish: { arrow: '↓', word: 'Negative', color: 'text-green-600',  bg: 'bg-green-50',  border: 'border-green-200'  },
  Neutral: { arrow: '—', word: 'Neutral',  color: 'text-yellow-600', bg: 'bg-yellow-50', border: 'border-yellow-200' },
}

function SentimentBadge({ label, score }) {
  const c = SENTIMENT_CONFIG[label] ?? SENTIMENT_CONFIG.Neutral
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full border ${c.bg} ${c.border} ${c.color}`}>
      {c.arrow} {c.word} {score}/100
    </span>
  )
}

function groupByDate(items) {
  const groups = {}
  for (const item of items) {
    const day = new Date(item.fetched_at).toLocaleDateString('en-US', {
      weekday: 'long', month: 'long', day: 'numeric', year: 'numeric',
    })
    if (!groups[day]) groups[day] = []
    groups[day].push(item)
  }
  return groups
}

export default function ArchivePage() {
  const [groups, setGroups] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    axios.get('/api/archive')
      .then(({ data }) => setGroups(groupByDate(data.items)))
      .catch(() => setError('Could not load archive.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex justify-center items-center py-24">
      <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
    </div>
  )

  if (error) return (
    <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-5 py-4 text-sm">{error}</div>
  )

  const days = Object.keys(groups)

  if (days.length === 0) return (
    <div className="bg-white rounded-xl border border-slate-200 py-20 text-center text-slate-400">
      <p className="text-4xl mb-3">🗄️</p>
      <p className="font-medium">Archive is empty</p>
      <p className="text-sm mt-1">Fetch news on the News page to start building the archive.</p>
    </div>
  )

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-900">News Archive</h2>
        <p className="text-slate-500 text-sm mt-1">
          {Object.values(groups).flat().length} stored articles across {days.length} day{days.length !== 1 ? 's' : ''}
        </p>
      </div>

      <div className="space-y-8">
        {days.map((day) => (
          <section key={day}>
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3 pb-2 border-b border-slate-200">
              {day}
            </h3>
            <div className="space-y-3">
              {groups[day].map((item) => (
                <div
                  key={item.id}
                  className="bg-white rounded-lg border border-slate-200 px-5 py-4 flex items-start gap-4 hover:shadow-sm transition-shadow"
                >
                  <div className="flex-1 min-w-0">
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm font-semibold text-slate-900 hover:text-blue-700 transition-colors leading-snug"
                    >
                      {item.title}
                      <span className="text-blue-400 ml-1 text-xs">↗</span>
                    </a>
                    {item.summary && (
                      <p className="text-xs text-slate-500 mt-1 leading-relaxed line-clamp-2">
                        {item.summary}
                      </p>
                    )}
                  </div>
                  <div className="flex-shrink-0 mt-0.5">
                    <SentimentBadge label={item.sentiment_label} score={item.sentiment_score} />
                  </div>
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  )
}
