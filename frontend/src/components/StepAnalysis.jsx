import { useState } from 'react'

export default function StepAnalysis({ steps = [] }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="mt-3 border border-slate-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 hover:bg-slate-100 transition-colors text-left"
      >
        <span className="text-sm font-semibold text-slate-700">
          📌 Article Highlights
        </span>
        <span className="text-slate-400 text-sm">{open ? '▲ collapse' : '▼ expand'}</span>
      </button>

      {open && (
        <ul className="px-4 py-3 space-y-2 bg-white list-none">
          {steps.map((step, i) => (
            <li key={i} className="flex gap-3 text-sm text-slate-600">
              <span className="flex-shrink-0 mt-1.5 w-1.5 h-1.5 rounded-full bg-blue-500"></span>
              <span className="leading-relaxed">{step}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
