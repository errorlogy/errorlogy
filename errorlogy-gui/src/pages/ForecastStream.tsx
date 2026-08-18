import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Loader2, RefreshCw, Radio, BookOpen, Cpu, AlertTriangle, TrendingUp,
  Globe2, History, Waves, ArrowLeft,
} from 'lucide-react'
import { api, isNetworkError, waitForApiHealth } from '../lib/api'
import { common, muNote, nav, streamEngineModules } from '../lib/ru'
import { cn } from '../lib/utils'
import type { StreamForecastResponse } from '../lib/types'

const SEVERITY_STYLE: Record<string, string> = {
  high: 'bg-red-900/40 text-red-300 border-red-800/50',
  medium: 'bg-amber-900/30 text-amber-300 border-amber-800/40',
  low: 'bg-slate-800 text-slate-400 border-slate-700',
}

export function ForecastStream() {
  const navigate = useNavigate()
  const [data, setData] = useState<StreamForecastResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [starting, setStarting] = useState(true)
  const [offline, setOffline] = useState(false)
  const [apiLogPath, setApiLogPath] = useState('')
  const [error, setError] = useState('')
  const [windowDays, setWindowDays] = useState(30)

  useEffect(() => {
    const electron = (window as Window & { electron?: { getApiStartupLogPath?: () => Promise<string> } }).electron
    void electron?.getApiStartupLogPath?.().then(setApiLogPath).catch(() => {})
  }, [])

  const load = useCallback(async () => {
    setLoading(true)
    setStarting(true)
    setOffline(false)
    setError('')
    try {
      const health = await waitForApiHealth({ maxAttempts: 60, intervalMs: 1000 })
      setStarting(false)
      if (!health) {
        setOffline(true)
        setData(null)
        return
      }
      const res = await api.streamForecast({ window_days: windowDays, limit: 30 })
      setData(res)
    } catch (e: unknown) {
      setStarting(false)
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

  if ((starting || loading) && !data) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-slate-500 gap-2">
        <div className="flex items-center gap-2">
          <Loader2 size={18} className="animate-spin" />
          {starting ? common.backendStarting : common.loading}
        </div>
        {starting && (
          <p className="text-xs text-slate-600 max-w-sm text-center">
            Electron запускает FastAPI на :8000 — первая загрузка может занять до минуты.
          </p>
        )}
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      <div className="flex items-start gap-3">
        <button
          onClick={() => navigate('/forecast')}
          className="text-slate-500 hover:text-slate-200 transition-colors mt-1"
          title={nav.forecast}
        >
          <ArrowLeft size={18} />
        </button>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Waves size={22} className="text-cyan-400" />
            {nav.streamForecast}
          </h1>
          <p className="text-slate-400 text-sm mt-1 max-w-3xl leading-relaxed">
            Агрегат Horizon 2: ingest, CEP-тренды, страны и связь с кейсовым FPD.
            Абсолютные календарные даты здесь не вычисляются.
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
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
        <div className="bg-red-900/20 border border-red-700/40 rounded-lg px-4 py-3 text-red-200 text-sm space-y-2">
          <p>{common.backendOffline}</p>
          {apiLogPath && (
            <p className="text-xs text-red-300/90">
              Лог запуска API: <span className="font-mono break-all">{apiLogPath}</span>
            </p>
          )}
          <p className="text-xs text-red-300/90">{common.backendOfflineLauncherHint}</p>
          <div className="text-xs text-red-300/90">
            <p>Или запустите backend вручную в PowerShell:</p>
            <pre className="mt-1 p-2 bg-red-950/40 rounded border border-red-800/40 font-mono text-[11px] whitespace-pre-wrap">
              {common.backendOfflineManualCmd}
            </pre>
          </div>
        </div>
      )}
      {error && (
        <div className="bg-amber-900/20 border border-amber-700/40 rounded-lg px-4 py-2 text-amber-200 text-sm">
          {error}
        </div>
      )}

      {data && (
        <>
          <p className="text-xs text-slate-500 border border-slate-800 rounded-lg px-3 py-2 leading-relaxed">
            {muNote}
          </p>

          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 space-y-2">
            <p className="text-sm text-slate-300 leading-relaxed">{data.methodology_ru}</p>
            <p className="text-xs text-slate-500">{data.horizon_note}</p>
            <p className="text-[10px] text-slate-600 font-mono">
              generated_at: {new Date(data.generated_at).toLocaleString('ru-RU')}
              {' · '}engine {data.engine.version}
              {' · '}окно {data.window_days} дн.
            </p>
          </div>

          <Section title="Источники данных (ingest)" icon={<Radio size={14} className="text-green-400" />}>
            <div className="grid md:grid-cols-4 gap-3 mb-4">
              <Stat label="Документов" value={data.ingest.documents_total} />
              <Stat label="Ожидают" value={data.ingest.pending} />
              <Stat label="Проанализировано" value={data.ingest.analyzed} />
              <Stat label="Сигналов" value={data.ingest.signals_total} />
            </div>
            {data.ingest.last_ingest_at && (
              <p className="text-xs text-slate-500 mb-3">
                Последний ingest:{' '}
                <span className="font-mono text-slate-400">
                  {new Date(data.ingest.last_ingest_at).toLocaleString('ru-RU')}
                </span>
              </p>
            )}
            {Object.keys(data.ingest.sources_breakdown).length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {Object.entries(data.ingest.sources_breakdown).map(([src, n]) => (
                  <span key={src} className="text-xs bg-slate-900 rounded px-2 py-1 border border-slate-700">
                    <span className="text-slate-400">{src}</span>
                    <span className="text-slate-200 font-bold ml-2">{n}</span>
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">{common.noData}</p>
            )}
            <Link to="/ingest" className="inline-block mt-3 text-xs text-cyan-400 hover:text-cyan-300">
              Управление ingest →
            </Link>
          </Section>

          <Section title="Таксономия" icon={<BookOpen size={14} className="text-purple-400" />}>
            <div className="grid md:grid-cols-3 gap-3 mb-4">
              <Stat label="Версия" value={data.taxonomy.version ?? common.noData} mono />
              <Stat label="Режимов" value={data.taxonomy.mode_count} />
              <Stat label="α-рёбер" value={data.taxonomy.alpha_edges} />
            </div>
            {data.taxonomy.dominant_modes.length > 0 ? (
              <>
                <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-2">
                  Домinant режимы (из недавних кейсов)
                </p>
                <div className="flex flex-wrap gap-2">
                  {data.taxonomy.dominant_modes.map(m => (
                    <div key={m.mode_id} className="bg-slate-900 rounded-lg px-2.5 py-1.5 text-xs border border-slate-700">
                      <span className="font-mono text-slate-400">{m.mode_id}</span>
                      <span className="text-slate-300 ml-2">{m.name}</span>
                      <span className="text-slate-500 ml-2">μ≈{m.avg_mu.toFixed(2)} · {m.case_hits} кейс.</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p className="text-sm text-slate-500">{common.noData}</p>
            )}
          </Section>

          <Section title="Движки (engine)" icon={<Cpu size={14} className="text-red-400" />}>
            <div className="flex flex-wrap gap-2 mb-4">
              {data.engine_modules_used.map(mod => (
                <span
                  key={mod}
                  className="text-xs font-mono uppercase px-2 py-1 rounded bg-red-900/30 text-red-300 border border-red-800/40"
                >
                  {mod}
                </span>
              ))}
            </div>
            <div className="grid md:grid-cols-2 gap-2">
              {data.engine_modules_used.map(mod => (
                <div key={mod} className="bg-slate-900 rounded-lg px-3 py-2 text-xs">
                  <span className="font-semibold text-slate-200 uppercase">{mod}</span>
                  <p className="text-slate-400 mt-0.5 leading-relaxed">
                    {streamEngineModules[mod] ?? 'Модуль engine v1-math'}
                  </p>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Алерты эскалации (CEP)" icon={<AlertTriangle size={14} className="text-amber-400" />}>
            {data.alerts.length > 0 ? (
              <div className="space-y-2">
                {data.alerts.map(a => (
                  <div
                    key={`${a.iso3}-${a.recorded_at}`}
                    className={cn('flex items-center justify-between gap-3 rounded-lg px-3 py-2 border text-xs', SEVERITY_STYLE[a.severity])}
                  >
                    <div>
                      <span className="font-semibold">{a.country}</span>
                      <span className="font-mono text-slate-500 ml-2">{a.iso3}</span>
                      {a.case_id && (
                        <Link
                          to={`/forecast/${encodeURIComponent(a.case_id)}`}
                          className="ml-2 text-cyan-400 hover:text-cyan-300"
                        >
                          кейс →
                        </Link>
                      )}
                    </div>
                    <div className="text-right shrink-0">
                      <span className="font-bold">CEP {a.cep.toFixed(2)}</span>
                      <span className="text-slate-500 ml-2">({a.severity})</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">Нет алертов выше порога CEP за окно {data.window_days} дн.</p>
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
                      <th className="pb-2 pr-3">Δ окно</th>
                      <th className="pb-2">Сигналов</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.trends.map(t => (
                      <tr key={t.iso3} className="border-t border-slate-700 text-slate-300">
                        <td className="py-1.5 pr-3">
                          {t.country}
                          <span className="font-mono text-slate-500 ml-1">{t.iso3}</span>
                        </td>
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
                <p className="text-[10px] text-slate-500 mt-2">
                  CEP — накопленное давление ошибки, не вероятность. Δ — изменение за выбранное окно.
                </p>
              </div>
            ) : (
              <p className="text-sm text-slate-500">{common.noData}</p>
            )}
          </Section>

          <Section title="Страны" icon={<Globe2 size={14} className="text-emerald-400" />}>
            {data.countries.length > 0 ? (
              <div className="space-y-2">
                {data.countries.slice(0, 12).map(c => (
                  <div key={c.iso3} className="flex items-center justify-between bg-slate-900 rounded-lg px-3 py-2 text-xs">
                    <div>
                      <span className="text-slate-200">{c.name}</span>
                      <span className="font-mono text-slate-500 ml-2">{c.iso3}</span>
                    </div>
                    <div className="text-slate-400">
                      {c.cases} кейс. · CEP max {c.max_cep.toFixed(2)}
                      {c.dominant_pno && <span className="ml-2 text-slate-500">{c.dominant_pno}</span>}
                    </div>
                  </div>
                ))}
                <Link to="/globe" className="inline-block text-xs text-emerald-400 hover:text-emerald-300">
                  Открыть глобус →
                </Link>
              </div>
            ) : (
              <p className="text-sm text-slate-500">
                {common.noData} — запустите анализ кейсов или ingest для наполнения статистики.
              </p>
            )}
          </Section>

          <Section title="Связь с кейсовым прогнозом" icon={<History size={14} className="text-blue-400" />}>
            {data.recent_cases.length > 0 ? (
              <div className="space-y-2">
                {data.recent_cases.map(c => (
                  <button
                    key={c.case_id}
                    onClick={() => navigate(`/forecast/${encodeURIComponent(c.case_id)}`)}
                    className="w-full text-left flex items-start justify-between gap-3 bg-slate-900 hover:bg-slate-900/80 border border-slate-700 hover:border-blue-600/40 rounded-lg px-3 py-2 transition-colors"
                  >
                    <div className="min-w-0">
                      <div className="text-sm text-slate-200 truncate">{c.title || c.case_id}</div>
                      <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                        {c.country || '—'} · {c.year ?? '—'}
                      </div>
                      {c.top_modes.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1.5">
                          {c.top_modes.slice(0, 3).map(m => (
                            <span key={m.mode_id} className="text-[10px] font-mono px-1.5 py-0.5 bg-slate-800 text-slate-400 rounded">
                              {m.mode_id} μ={m.mu?.toFixed?.(2) ?? '—'}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <TrendingUp size={14} className="text-blue-400 shrink-0 mt-1" />
                  </button>
                ))}
                <p className="text-xs text-slate-500 pt-1">
                  Кейсовый FPD возвращает μ_forecast и horizon — откройте кейс для детального прогноза.
                </p>
              </div>
            ) : (
              <p className="text-sm text-slate-500">
                Нет проанализированных кейсов.{' '}
                <Link to="/analyze" className="text-red-400 hover:text-red-300">{common.goAnalyze}</Link>
              </p>
            )}
          </Section>
        </>
      )}
    </div>
  )
}

function Stat({ label, value, mono }: { label: string; value: string | number; mono?: boolean }) {
  return (
    <div className="bg-slate-900 rounded-lg p-3">
      <div className="text-[10px] text-slate-500 uppercase">{label}</div>
      <div className={cn('text-lg font-bold text-slate-200 mt-1', mono && 'text-sm font-mono')}>{value}</div>
    </div>
  )
}

function Section({ title, icon, children }: { title: string; icon?: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="bg-slate-800 rounded-xl overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700/50">
        {icon}
        <span className="text-xs text-slate-400 uppercase tracking-widest font-semibold">{title}</span>
      </div>
      <div className="p-4">{children}</div>
    </div>
  )
}
