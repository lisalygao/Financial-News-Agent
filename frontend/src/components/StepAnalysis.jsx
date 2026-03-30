import { useState } from 'react'

export default function StepAnalysis({ steps = [] }) {
  const [open, setOpen] = useState(false)

  const paragraph = steps.join(' ')

  return (
    <div className="mt-3 border border-slate-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 hover:bg-slate-100 transition-colors text-left"
      >
        <span className="text-sm font-semibold text-slate-700">
          📄 Article Summary
        </span>
        <span className="text-slate-400 text-sm">{open ? '▲ collapse' : '▼ expand'}</span>
      </button>

      {open && (
        <div className="px-4 py-3 bg-white">
          <p className="text-sm text-slate-600 leading-relaxed">{paragraph}</p>
        </div>
      )}
    </div>
  )
}
