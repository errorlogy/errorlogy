import { Link } from 'react-router-dom'
import { Waves, FileSearch, Radio, BookOpen, ArrowRight } from 'lucide-react'
import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { home, muNote, nav } from '../lib/en'
import type { HealthInfo } from '../lib/types'
import { DataFlowDiagram } from '../components/DataFlowDiagram'

const cards = [
  {
    to: '/stream',
    icon: Waves,
    title: nav.stream,
    desc: home.streamForecastDesc,
    color: 'cyan',
  },
  {
    to: '/case',
    icon: FileSearch,
    title: nav.case,
    desc: home.caseForecastDesc,
    color: 'blue',
  },
  {
    to: '/data',
    icon: Radio,
    title: nav.data,
    desc: 'Статус ingest, загрузка RSS, ручной ввод — что входит в поток сигналов.',
    color: 'green',
  },
] as const

const colorMap = {
  cyan: 'border-cyan-800/50 hover:border-cyan-600/60 bg-cyan-900/10',
  blue: 'border-blue-800/50 hover:border-blue-600/60 bg-blue-900/10',
  green: 'border-emerald-800/50 hover:border-emerald-600/60 bg-emerald-900/10',
}

export function HomePage() {
  const [health, setHealth] = useState<HealthInfo | null>(null)

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth(null))
  }, [])

  return (
    <div className="p-6 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">{home.title}</h1>
        <p className="text-slate-400 mt-2 max-w-2xl leading-relaxed">{home.subtitle}</p>
      </div>

      <p className="text-xs text-slate-500 border border-slate-800 rounded-lg px-3 py-2 leading-relaxed">
        {muNote}
      </p>

      {health && (
        <div className="grid sm:grid-cols-3 gap-3 text-sm">
          <div className="bg-slate-800 rounded-lg px-4 py-3">
            <div className="text-slate-500 text-xs">Режимов таксономии</div>
            <div className="text-white font-bold text-lg">{health.taxonomy_modes}</div>
          </div>
          <div className="bg-slate-800 rounded-lg px-4 py-3">
            <div className="text-slate-500 text-xs">α-рёбер</div>
            <div className="text-white font-bold text-lg">{health.alpha_edges}</div>
          </div>
          <div className="bg-slate-800 rounded-lg px-4 py-3">
            <div className="text-slate-500 text-xs">Engine</div>
            <div className="text-white font-mono text-sm">{health.engine ?? '—'}</div>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-slate-800/60 rounded-xl p-5 border border-slate-700/50">
          <h2 className="text-sm font-semibold text-cyan-300 flex items-center gap-2">
            <Waves size={18} />
            {home.streamForecastTitle}
          </h2>
          <p className="text-sm text-slate-400 mt-2 leading-relaxed">{home.streamForecastDesc}</p>
        </div>
        <div className="bg-slate-800/60 rounded-xl p-5 border border-slate-700/50">
          <h2 className="text-sm font-semibold text-blue-300 flex items-center gap-2">
            <FileSearch size={18} />
            {home.caseForecastTitle}
          </h2>
          <p className="text-sm text-slate-400 mt-2 leading-relaxed">{home.caseForecastDesc}</p>
        </div>
      </div>

      <div>
        <h2 className="text-xs text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
          <BookOpen size={14} />
          {home.methodologyTitle}
        </h2>
        <ul className="space-y-2">
          {home.methodologyPoints.map((p, i) => (
            <li key={i} className="text-sm text-slate-400 flex gap-2">
              <span className="text-cyan-600 shrink-0">•</span>
              {p}
            </li>
          ))}
        </ul>
        <div className="mt-4">
          <DataFlowDiagram
            steps={[
              { id: 'ingest', label: 'Ingest', desc: 'RSS, gov, ручной ввод' },
              { id: 'signals', label: 'Signals', desc: 'MSI, CEP по странам' },
              { id: 'engine', label: 'Engine', desc: 'WMS, Classifier, FPD', highlight: true },
              { id: 'out', label: 'Прогноз', desc: 'Тренды, алерты, μ' },
            ]}
          />
        </div>
      </div>

      <div className="grid sm:grid-cols-3 gap-4">
        {cards.map(({ to, icon: Icon, title, desc, color }) => (
          <Link
            key={to}
            to={to}
            className={`block rounded-xl border p-4 transition-colors group ${colorMap[color]}`}
          >
            <Icon size={22} className="text-slate-300 mb-2" />
            <h3 className="font-semibold text-white">{title}</h3>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed line-clamp-3">{desc}</p>
            <span className="inline-flex items-center gap-1 text-xs text-cyan-400 mt-3 group-hover:gap-2 transition-all">
              Открыть <ArrowRight size={14} />
            </span>
          </Link>
        ))}
      </div>
    </div>
  )
}
