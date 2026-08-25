import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Loader2, RefreshCw, Radio, BookOpen, Cpu, AlertTriangle, TrendingUp,
  Globe2, History, Waves,
} from 'lucide-react'
import { api, isNetworkError } from '../lib/api'
import { common, muNote, nav, streamEngineModules } from '../lib/en'
import { cn, SEVERITY_STYLE } from '../lib/utils'
import type { StreamForecastResponse } from '../lib/types'
import { DataFlowDiagram } from '../components/DataFlowDiagram'
import { Section, Stat } from '../components/Section'

export function StreamForecastPage() {
  const [data, setData] = useState<StreamForecastResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [offline, setOffline] = useState(false)
  const [error, setError] = useState('')
  const [windowDays, setWindowDays] = useState(30)

  const load = useCallback(async () => {
    setLoading(true)
    setOffline(false)
    setError('')
    try {
      const health = await api.health()
      if (!health) {
        setOffline(true)
        setData(null)
        return
      }
      const res = await api.streamForecast({ window_days: windowDays, limit: 30 })
      setData(res)
    } catch (e: unknown) {
      if (isNetworkError(e)) {
        setOffline(true)
      } else {
        setError(e instanceof Error ? e.message : 'Не удалось загрузить прогноз потока')
      }
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [windowDays])

  useEffect(() => {
    void load()
  }, [load])

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center py-24 text-slate-500 gap-2">
        <Loader2 size={18} className="animate-spin" />
        {common.loading}
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Waves size={22} className="text-cyan-400" />
            {nav.stream}
          </h1>
          <p className="text-slate-400 text-sm mt-1 max-w-2xl">
            Агрегат Horizon 2: ingest → сигналы → engine → тренды и алерты.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={windowDays}
            onChange={e => setWindowDays(Number(e.target.value))}
            className="bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-slate-300"
          >
            {[7, 14, 30, 60].map(d => (
              <option key={d} value={d}>{d} дн.</option>
            ))}
          </select>
          <button
            onClick={() => void load()}
            disabled={loading}
            className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300"
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            {common.refresh}
          </button>
        </div>
      </div>

      {offline && (
        <div className="bg-red-900/20 border border-red-700/40 rounded-lg px-4 py-3 text-red-200 text-sm">
          <p>{common.backendOffline}</p>
          <pre className="mt-2 text-xs font-mono text-red-300/80">{common.backendManualCmd}</pre>
        </div>
      )}
      {error && (
        <div className="bg-amber-900/20 border border-amber-700/40 rounded-lg px-4 py-2 text-amber-200 text-sm">
          {error}
        </div>
      )}

      {data && (
        <>
          <DataFlowDiagram
            steps={[
              { id: 'ingest', label: 'Ingest', desc: `${data.ingest.documents_total} док.` },
              { id: 'signals', label: 'Signals', desc: `${data.ingest.signals_total} сигн.` },
              { id: 'engine', label: 'Engine', desc: data.engine.version, highlight: true },
              { id: 'trends', label: 'Trends/Alerts', desc: `${data.alerts.length} алертов` },
            ]}
          />

          <p className="text-xs text-slate-500 border border-slate-800 rounded-lg px-3 py-2">{muNote}</p>

          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 space-y-2">
            <p className="text-sm text-slate-300 leading-relaxed">{data.methodology}</p>
            <p className="text-xs text-slate-500">{data.horizon_note}</p>
            <p className="text-[10px] text-slate-600 font-mono">
              {new Date(data.generated_at).toLocaleString('ru-RU')}
              {' · '}окно {data.window_days} дн.
            </p>
          </div>

          <Section title="Ingest" icon={<Radio size={14} className="text-green-400" />}>
            <div className="grid md:grid-cols-4 gap-3 mb-4">
              <Stat label="Документов" value={data.ingest.documents_total} />
              <Stat label="Ожидают" value={data.ingest.pending} />
              <Stat label="Проанализировано" value={data.ingest.analyzed} />
              <Stat label="Сигналов" value={data.ingest.signals_total} />
            </div>
            {data.ingest.last_ingest_at && (
              <p className="text-xs text-slate-500 mb-3">
                Последний ingest: {new Date(data.ingest.last_ingest_at).toLocaleString('ru-RU')}
              </p>
            )}
            <div className="flex flex-wrap gap-2">
              {Object.entries(data.ingest.sources_breakdown).map(([src, n]) => (
                <span key={src} className="text-xs bg-slate-900 rounded px-2 py-1 border border-slate-700">
                  <span className="text-slate-400">{src}</span>
                  <span className="text-slate-200 font-bold ml-2">{n}</span>
                </span>
              ))}
            </div>
            <Link to="/data" className="inline-block mt-3 text-xs text-cyan-400 hover:text-cyan-300">
              Управление потоками →
            </Link>
          </Section>

          <Section title="Таксономия" icon={<BookOpen size={14} className="text-purple-400" />}>
            <div className="grid md:grid-cols-3 gap-3 mb-4">
              <Stat label="Версия" value={data.taxonomy.version ?? common.noData} mono />
              <Stat label="Режимов" value={data.taxonomy.mode_count} />
              <Stat label="α-рёбер" value={data.taxonomy.alpha_edges} />
            </div>
            <div className="flex flex-wrap gap-2">
              {data.taxonomy.dominant_modes.map(m => (
                <div key={m.mode_id} className="bg-slate-900 rounded-lg px-2.5 py-1.5 text-xs border border-slate-700">
                  <span className="font-mono text-slate-400">{m.mode_id}</span>
                  <span className="text-slate-300 ml-2">{m.name}</span>
                  <span className="text-slate-500 ml-2">μ≈{m.avg_mu.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Модули engine" icon={<Cpu size={14} className="text-red-400" />}>
            <div className="grid md:grid-cols-2 gap-2">
              {data.engine_modules_used.map(mod => (
                <div key={mod} className="bg-slate-900 rounded-lg px-3 py-2 text-xs">
                  <span className="font-semibold text-slate-200 uppercase">{mod}</span>
                  <p className="text-slate-400 mt-0.5">{streamEngineModules[mod] ?? 'Модуль engine'}</p>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Алерты CEP" icon={<AlertTriangle size={14} className="text-amber-400" />}>
            {data.alerts.length > 0 ? (
              <div className="space-y-2">
                {data.alerts.map(a => (
                  <div
                    key={`${a.iso3}-${a.recorded_at}`}
                    className={cn('flex justify-between gap-3 rounded-lg px-3 py-2 border text-xs', SEVERITY_STYLE[a.severity])}
                  >
                    <div>
                      <span className="font-semibold">{a.country}</span>
                      <span className="font-mono text-slate-500 ml-2">{a.iso3}</span>
                      {a.case_id && (
                        <Link to={`/case?id=${encodeURIComponent(a.case_id)}`} className="ml-2 text-cyan-400">
                          кейс →
                        </Link>
                      )}
                    </div>
                    <span className="font-bold">CEP {a.cep.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">Нет алертов за окно {data.window_days} дн.</p>
            )}
          </Section>

          <Section title="Тренды" icon={<TrendingUp size={14} className="text-blue-400" />}>
            {data.trends.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-slate-500 text-left">
                      <th className="pb-2 pr-3">Страна</th>
                      <th className="pb-2 pr-3">CEP max</th>
                      <th className="pb-2 pr-3">CEP latest</th>
                      <th className="pb-2 pr-3">Δ</th>
                      <th className="pb-2">Сигналов</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.trends.map(t => (
                      <tr key={t.iso3} className="border-t border-slate-700 text-slate-300">
                        <td className="py-1.5 pr-3">{t.country} <span className="font-mono text-slate-500">{t.iso3}</span></td>
                        <td className="py-1.5 pr-3">{t.cep_max.toFixed(2)}</td>
                        <td className="py-1.5 pr-3">{t.cep_latest.toFixed(2)}</td>
                        <td className={cn('py-1.5 pr-3 font-mono', t.cep_delta_7d >= 0 ? 'text-red-400' : 'text-green-400')}>
                          {t.cep_delta_7d >= 0 ? '+' : ''}{t.cep_delta_7d.toFixed(2)}
                        </td>
                        <td className="py-1.5">{t.signal_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-sm text-slate-500">{common.noData}</p>
            )}
          </Section>

          <Section title="Страны" icon={<Globe2 size={14} className="text-emerald-400" />}>
            <div className="space-y-2">
              {data.countries.slice(0, 10).map(c => (
                <div key={c.iso3} className="flex justify-between bg-slate-900 rounded-lg px-3 py-2 text-xs">
                  <span className="text-slate-200">{c.name} <span className="font-mono text-slate-500">{c.iso3}</span></span>
                  <span className="text-slate-400">{c.cases} кейс. · CEP {c.max_cep.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Недавние кейсы" icon={<History size={14} className="text-blue-400" />}>
            {data.recent_cases.length > 0 ? (
              <div className="space-y-2">
                {data.recent_cases.map(c => (
                  <Link
                    key={c.case_id}
                    to={`/case?id=${encodeURIComponent(c.case_id)}`}
                    className="block bg-slate-900 hover:bg-slate-900/80 border border-slate-700 hover:border-blue-600/40 rounded-lg px-3 py-2 transition-colors"
                  >
                    <div className="text-sm text-slate-200 truncate">{c.title || c.case_id}</div>
                    <div className="text-[10px] text-slate-500 font-mono">{c.country} · {c.year ?? '—'}</div>
                    {c.top_modes.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {c.top_modes.slice(0, 3).map(m => (
                          <span key={m.mode_id} className="text-[10px] font-mono px-1.5 py-0.5 bg-slate-800 text-slate-400 rounded">
                            {m.mode_id} μ={m.mu.toFixed(2)}
                          </span>
                        ))}
                      </div>
                    )}
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">{common.noData}</p>
            )}
          </Section>
        </>
      )}
    </div>
  )
}
