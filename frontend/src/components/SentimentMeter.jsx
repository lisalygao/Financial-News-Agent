/**
 * SentimentMeter
 * Standard color coding:
 *   Bullish  → Green  ↑ (Positive)
 *   Neutral  → Yellow — (Neutral)
 *   Bearish  → Red    ↓ (Negative)
 */
export default function SentimentMeter({ label, score }) {
  const config = {
    Bullish: {
      arrow: '↑',
      word: 'Bullish',
      textColor: 'text-green-700',
      barColor: 'bg-green-500',
      badgeBg: 'bg-green-50',
      badgeBorder: 'border-green-200',
    },
    Bearish: {
      arrow: '↓',
      word: 'Bearish',
      textColor: 'text-red-600',
      barColor: 'bg-red-500',
      badgeBg: 'bg-red-50',
      badgeBorder: 'border-red-200',
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
    <div className={`inline-flex items-center gap-2 rounded-full border ${c.badgeBorder} ${c.badgeBg} px-3 py-1`}>
      <span className={`text-sm font-bold ${c.textColor}`}>
        {c.arrow} {c.word}
      </span>
      <span className={`text-sm font-extrabold ${c.textColor}`}>
        {score}<span className="text-xs font-normal text-slate-400">/100</span>
      </span>
    </div>
  )
}
