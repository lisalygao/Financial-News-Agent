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
      <div className="flex items-start gap-3 px-5 pt-5 pb-3">
        <span className="flex-shrink-0 w-7 h-7 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center mt-0.5">
          {index + 1}
        </span>
        <div className="flex-1 min-w-0">
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-base font-semibold text-slate-900 hover:text-blue-700 transition-colors leading-snug block"
          >
            {item.title}
            <span className="inline-block ml-1 text-blue-400 text-sm">↗</span>
          </a>
          <p className="text-xs text-slate-400 mt-1">{date}</p>
        </div>
      </div>

      {/* Summary */}
      <div className="px-5 pb-3">
        <p className="text-sm text-slate-600 leading-relaxed">{item.summary}</p>
      </div>

      {/* Step analysis accordion */}
      <div className="px-5 pb-3">
        <StepAnalysis steps={steps} />
      </div>

      {/* Sentiment */}
      <div className="px-5 pb-5">
        <SentimentMeter
          label={item.sentiment_label}
          score={item.sentiment_score ?? 50}
        />
      </div>
    </article>
  )
}
