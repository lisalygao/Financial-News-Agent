import { Routes, Route, Navigate } from 'react-router-dom'
import Header from './components/Header'
import NewsPage from './pages/NewsPage'
import SubscribePage from './pages/SubscribePage'
import ArchivePage from './pages/ArchivePage'

export default function App() {
  return (
    <div className="min-h-screen bg-slate-100">
      <Header />
      <main className="max-w-4xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<NewsPage />} />
          <Route path="/subscribe" element={<SubscribePage />} />
          <Route path="/archive" element={<ArchivePage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}
