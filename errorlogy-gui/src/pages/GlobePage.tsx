import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Globe2, RefreshCw, MapPin, TrendingUp, Radio } from 'lucide-react'
import { api } from '../lib/api'
import { mergeCountryStats } from '../lib/countryStats'
import { ErrorlogyGlobe } from '../components/ErrorlogyGlobe'
import type { CountryStats, SignalTrend } from '../lib/types'
import { muColor } from '../lib/utils'

export function GlobePage() {
  const [countries, setCountries] = useState<CountryStats[]>([])
  const [trends, setTrends] = useState<SignalTrend[]>([])
  const [selected, setSelected] = useState<CountryStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      const [seed, trendRes] = await Promise.all([
        api.countryStats(),
        api.signalTrends({ window_days: 7, limit: 50 }),
      ])
      setCountries(mergeCountryStats(seed))
      setTrends(trendRes.trends)
    } catch {
      setError('Could not load country stats — is FastAPI running on :8000?')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const trendByIso = useMemo(
    () => Object.fromEntries(trends.map(t => [t.iso3, t])),
    [trends],
  )

  const totalCases = useMemo(() => countries.reduce((s, c) => s + c.cases, 0), [countries])
  const topCountries = useMemo(() => [...countries].sort((a, b) => b.cases - a.cases).slice(0, 8), [countries])

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Globe2 size={22} className="text-red-400" />
            Global Errorlogy Map
          </h1>
          <p className="text-slate-500 text-xs mt-0.5">
            3D choropleth — case density, μ, PNO regimes by country · click a territory for detail
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500">{totalCases} cases tracked</span>
          <button onClick={load} className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors" title="Refresh">
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {error && (
        <div className="mx-6 mt-3 bg-red-900/30 border border-red-700 rounded-lg p-3 text-red-300 text-sm">{error}</div>
      )}

      <div className="flex-1 flex overflow-hidden min-h-0">
        <div className="flex-[2] p-4 min-w-0 min-h-0 flex flex-col">
          <ErrorlogyGlobe
            countries={countries}
            selectedIso3={selected?.iso3 ?? null}
            onSelect={(_iso, stats) => setSelected(stats)}
          />
        </div>

        <aside className="w-80 shrink-0 border-l border-slate-800 overflow-y-auto bg-slate-950/50 p-4 space-y-4">
          {selected ? (
            <CountryPanel stats={selected} trend={trendByIso[selected.iso3]} onClose={() => setSelected(null)} />
          ) : (
            <>
              <p className="text-xs text-slate-500 uppercase tracking-widest">Top countries by cases</p>
              <div className="space-y-2">
                {topCountries.map(c => {
                  const tr = trendByIso[c.iso3]
                  return (
                  <button
                    key={c.iso3}
                    onClick={() => setSelected(c)}
                    className="w-full text-left bg-slate-800/80 hover:bg-slate-800 border border-slate-700 rounded-lg p-3 transition-colors"
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-slate-200 text-sm">{c.name}</span>
                      <span className="text-xs font-mono text-red-400">{c.cases}</span>
                    </div>
                    <div className="text-[10px] text-slate-500 mt-1 flex gap-2 flex-wrap">
                      <span>{c.dominant_pno}</span>
                      <span className={muColor(c.avg_mu)}>μ̄ {(c.avg_mu * 100).toFixed(0)}%</span>
                      {tr && tr.cep_delta_7d !== 0 && (
                        <span className={tr.cep_delta_7d > 0 ? 'text-amber-400' : 'text-emerald-400'}>
                          CEP Δ7d {tr.cep_delta_7d > 0 ? '+' : ''}{(tr.cep_delta_7d * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                  </button>
                  )
                })}
              </div>
              <p className="text-[10px] text-slate-600 leading-relaxed">
                Run analyses with a country field to add local cases. Seed data from MAS corpus preview.
              </p>
            </>
          )}
        </aside>
      </div>
    </div>
  )
}

function CountryPanel({ stats, trend, onClose }: { stats: CountryStats; trend?: SignalTrend; onClose: () => void }) {
  const navigate = useNavigate()

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-start">
        <div>
          <div className="text-lg font-bold text-white">{stats.name}</div>
          <div className="text-xs font-mono text-slate-500">{stats.iso3}</div>
        </div>
        <button onClick={onClose} className="text-xs text-slate-500 hover:text-slate-300">✕</button>
      </div>

      {trend && (
        <div className="flex flex-wrap gap-1.5 text-[10px]">
          <span className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded font-mono">
            CEP max {trend.cep_max.toFixed(2)}
          </span>
          <span className={`px-2 py-0.5 rounded font-mono ${
            trend.cep_delta_7d > 0 ? 'bg-amber-900/40 text-amber-300' : 'bg-slate-800 text-slate-400'
          }`}>
            Δ7d {trend.cep_delta_7d >= 0 ? '+' : ''}{trend.cep_delta_7d.toFixed(2)}
          </span>
          <span className="px-2 py-0.5 bg-slate-800 text-slate-400 rounded font-mono">
            {trend.signal_count} signals
          </span>
        </div>
      )}

      <div className="grid grid-cols-2 gap-2">
        <MiniStat icon={<MapPin size={14} />} label="Cases" value={String(stats.cases)} />
        <MiniStat icon={<TrendingUp size={14} />} label="Avg μ" value={`${(stats.avg_mu * 100).toFixed(0)}%`} />
        <MiniStat icon={<Radio size={14} />} label="Max CEP" value={stats.max_cep.toFixed(2)} />
        <MiniStat icon={<Globe2 size={14} />} label="Echo P" value={stats.avg_echo_pressure.toFixed(2)} />
      </div>

      <div className="bg-slate-800 rounded-lg p-3">
        <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Dominant PNO</div>
        <div className="text-red-400 font-mono font-semibold">{stats.dominant_pno}</div>
      </div>

      {Object.keys(stats.top_families).length > 0 && (
        <div>
          <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-2">Mode families</div>
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(stats.top_families).map(([fam, n]) => (
              <span key={fam} className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-xs font-mono">
                {fam} <span className="text-red-400">{n}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {stats.recent_cases.length > 0 && (
        <div>
          <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-2">Recent cases</div>
          <div className="space-y-2">
            {stats.recent_cases.slice(0, 5).map(c => (
              <button
                key={c.case_id}
                onClick={() => navigate(`/result/${encodeURIComponent(c.case_id)}`)}
                className="w-full text-left bg-slate-900 border border-slate-700 rounded-lg p-2.5 hover:border-red-600/50 hover:bg-slate-800/80 transition-colors"
              >
                <div className="text-xs font-medium text-slate-200 leading-snug">{c.title}</div>
                <div className="text-[10px] text-slate-500 mt-1 font-mono">
                  {c.year || '—'} · {c.dominant_pno} · {c.cat}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function MiniStat({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-slate-800 rounded-lg p-2.5">
      <div className="text-red-400/80 mb-1">{icon}</div>
      <div className="text-[10px] text-slate-500 uppercase">{label}</div>
      <div className="text-sm font-semibold text-slate-200">{value}</div>
    </div>
  )
}
