import SentimentMeter from './SentimentMeter'
import StepAnalysis from './StepAnalysis'

export default function NewsCard({ item, index }) {
  const date = new Date(item.fetched_at).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })

  const steps = Array.isArray(item.analysis_steps)
    ? item.analysis_steps
    : []

  return (
    <article className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition-shadow">
      {/* Card header */}
      <div className="px-5 pt-5 pb-3">
        {/* Top row: number + title + sentiment badge */}
        <div className="flex items-start gap-3">
          <span className="flex-shrink-0 w-7 h-7 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center mt-0.5">
            {index + 1}
          </span>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-3">
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-base font-semibold text-slate-900 hover:text-blue-700 transition-colors leading-snug block"
              >
                {item.title}
                <span className="inline-block ml-1 text-blue-400 text-sm">↗</span>
              </a>
              {/* Sentiment badge — top right */}
              <div className="flex-shrink-0 mt-0.5">
                <SentimentMeter
                  label={item.sentiment_label}
                  score={item.sentiment_score ?? 50}
                />
              </div>
            </div>

            {/* Source + date row — top left, below title */}
            <div className="flex items-center gap-2 mt-1.5 flex-wrap">
              {item.source && (
                <span className="text-xs font-medium text-blue-700 bg-blue-50 border border-blue-100 rounded px-2 py-0.5">
                  {item.source}
                </span>
              )}
              <span className="text-xs text-slate-400">{date}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="px-5 pb-3">
        <p className="text-sm text-slate-600 leading-relaxed">{item.summary}</p>
      </div>

      {/* Article summary accordion */}
      <div className="px-5 pb-5">
        <StepAnalysis steps={steps} />
      </div>
    </article>
  )
}
