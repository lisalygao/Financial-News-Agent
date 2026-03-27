import { Link, useLocation } from 'react-router-dom'

const NAV = [
  { path: '/',          label: 'News'      },
  { path: '/archive',   label: 'Archive'   },
]

export default function Header() {
  const { pathname } = useLocation()

  return (
    <header className="bg-gradient-to-r from-slate-900 to-blue-900 text-white shadow-lg">
      <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight">📈 AI Market News</h1>
          <p className="text-blue-300 text-xs mt-0.5">Gemini-powered financial intelligence</p>
        </div>

        <nav className="flex items-center gap-1">
          {NAV.map(({ path, label }) => (
            <Link
              key={path}
              to={path}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                pathname === path
                  ? 'bg-white/20 text-white'
                  : 'text-blue-200 hover:bg-white/10 hover:text-white'
              }`}
            >
              {label}
            </Link>
          ))}
          <Link
            to="/subscribe"
            className="ml-2 px-4 py-1.5 bg-white text-blue-900 rounded-md text-sm font-bold hover:bg-blue-50 transition-colors"
          >
            ✉ Subscribe
          </Link>
        </nav>
      </div>
    </header>
  )
}
