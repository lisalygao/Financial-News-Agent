/**
 * SentimentMeter
 * Per user spec:
 *   Bullish  → Red   ↑ up arrow   (Positive)
 *   Neutral  → Yellow — flat line  (Neutral)
 *   Bearish  → Green ↓ down arrow  (Negative)
 */
export default function SentimentMeter({ label, score }) {
  const config = {
    Bullish: {
      arrow: '↑',
      word: 'Positive',
      textColor: 'text-red-600',
      barColor: 'bg-red-500',
      badgeBg: 'bg-red-50',
      badgeBorder: 'border-red-200',
    },
    Bearish: {
      arrow: '↓',
      word: 'Negative',
      textColor: 'text-green-600',
      barColor: 'bg-green-500',
      badgeBg: 'bg-green-50',
      badgeBorder: 'border-green-200',
    },
    Neutral: {
      arrow: '—',
      word: 'Neutral',
      textColor: 'text-yellow-600',
      barColor: 'bg-yellow-400',
      badgeBg: 'bg-yellow-50',
      badgeBorder: 'border-yellow-200',
    },
  }

  const c = config[label] ?? config.Neutral

  return (
    <div className={`rounded-lg border ${c.badgeBorder} ${c.badgeBg} px-4 py-3`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className={`text-2xl font-black leading-none ${c.textColor}`}>
            {c.arrow}
          </span>
          <div>
            <span className={`text-sm font-bold ${c.textColor}`}>
              {c.word} · {label}
            </span>
            <p className="text-xs text-slate-500">Market Sentiment</p>
          </div>
        </div>
        <span className={`text-2xl font-extrabold ${c.textColor}`}>
          {score}<span className="text-sm font-normal text-slate-400">/100</span>
        </span>
      </div>

      {/* Gauge bar */}
      <div className="relative h-2.5 rounded-full bg-slate-200 overflow-hidden">
        {/* Color zone gradient */}
        <div className="absolute inset-0 flex">
          <div className="flex-1 bg-green-300 opacity-50" />
          <div className="flex-1 bg-yellow-300 opacity-50" />
          <div className="flex-1 bg-red-300 opacity-50" />
        </div>
        {/* Score fill */}
        <div
          className={`absolute inset-y-0 left-0 ${c.barColor} transition-all duration-700 rounded-full`}
          style={{ width: `${score}%` }}
        />
      </div>

      <div className="flex justify-between text-xs text-slate-400 mt-1">
        <span>Bearish</span>
        <span>Neutral</span>
        <span>Bullish</span>
      </div>
    </div>
  )
}
