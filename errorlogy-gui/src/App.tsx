import { lazy, Suspense } from 'react'
import { HashRouter, Routes, Route } from 'react-router-dom'
import { TitleBar } from './components/TitleBar'
import { Sidebar } from './components/Sidebar'
import { Dashboard } from './pages/Dashboard'
import { Analyze } from './pages/Analyze'
import { Result } from './pages/Result'
import { Taxonomy } from './pages/Taxonomy'
import { MasPage } from './pages/MasPage'
import { IngestPage } from './pages/IngestPage'
import { Forecast } from './pages/Forecast'
import { ForecastStream } from './pages/ForecastStream'

const GlobePage = lazy(() =>
  import('./pages/GlobePage').then((m) => ({ default: m.GlobePage })),
)

export default function App() {
  return (
    <HashRouter>
      <div className="flex flex-col h-screen bg-slate-900 text-slate-100 overflow-hidden select-none">
        <TitleBar />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          <main className="flex-1 flex flex-col overflow-hidden">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/mas" element={<MasPage />} />
              <Route path="/ingest" element={<IngestPage />} />
              <Route
                path="/globe"
                element={
                  <Suspense fallback={<div className="flex-1 flex items-center justify-center text-slate-400">Loading globe…</div>}>
                    <GlobePage />
                  </Suspense>
                }
              />
              <Route path="/analyze" element={<Analyze />} />
              <Route path="/forecast" element={<Forecast />} />
              <Route path="/forecast/stream" element={<ForecastStream />} />
              <Route path="/forecast/:caseId" element={<Forecast />} />
              <Route path="/result" element={<Result />} />
              <Route path="/result/:caseId" element={<Result />} />
              <Route path="/taxonomy" element={<Taxonomy />} />
            </Routes>
          </main>
        </div>
      </div>
    </HashRouter>
  )
}
