import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Activity, Layers, GitBranch, Cpu, ArrowRight, Circle, Globe2, Calculator, Radio, History, TrendingUp, Loader2 } from 'lucide-react'
import { api, waitForApiHealth } from '../lib/api'
import { loadStoredCases } from '../lib/caseStore'
import { PIPELINE_STEPS } from '../lib/pipeline'
import { common, muNote } from '../lib/ru'
import type { HealthInfo, CaseListItem } from '../lib/types'

export function Dashboard() {
  const [health, setHealth] = useState<HealthInfo | null>(null)
  const [recentCases, setRecentCases] = useState<CaseListItem[]>([])
  const [starting, setStarting] = useState(true)
  const [error, setError] = useState('')
  const [apiLogPath, setApiLogPath] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const electron = (window as Window & { electron?: { getApiStartupLogPath?: () => Promise<string> } }).electron
    void electron?.getApiStartupLogPath?.().then(setApiLogPath).catch(() => {})

    void (async () => {
      const h = await waitForApiHealth({ maxAttempts: 60, intervalMs: 1000 })
      setStarting(false)
      if (h) {
        setHealth(h)
        api.listCases(10)
          .then(r => setRecentCases(r.cases))
          .catch(() => { /* offline — fall back to localStorage below */ })
      } else {
        setError(common.backendOffline)
      }
    })()
  }, [])

  const localCases = loadStoredCases().slice(0, 10)
  const showCases = recentCases.length > 0 ? recentCases : localCases.map(c => ({
    case_id: c.case_id,
    title: c.title,
    country: c.country,
    year: c.year || null,
    engine_only: c.engine_only ?? false,
    created_at: c.analyzed_at,
  }))

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Errorlogy MAS</h1>
        <p className="text-slate-400 mt-1 text-sm">
          Гибридная аналитика: детерминированный engine v1-math + интерпретация LLM
        </p>
      </div>

      {starting && !health && (
        <div className="bg-slate-800/60 border border-slate-700 rounded-lg p-4 text-slate-400 text-sm flex items-center gap-2">
          <Loader2 size={16} className="animate-spin shrink-0" />
          {common.backendStarting}
        </div>
      )}

      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 text-red-300 text-sm space-y-2">
          <p>{error}</p>
          {apiLogPath && (
            <p className="text-xs text-red-200/90">
              Лог запуска API: <span className="font-mono break-all">{apiLogPath}</span>
            </p>
          )}
          <p className="text-xs text-red-200/90">{common.backendOfflineLauncherHint}</p>
          <pre className="text-[11px] font-mono whitespace-pre-wrap bg-red-950/40 rounded p-2 border border-red-800/40">
            {common.backendOfflineManualCmd}
          </pre>
        </div>
      )}

      {health && (
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          <Stat icon={<Activity size={18} />} label="Статус" value={health.status.toUpperCase()} accent="text-green-400" />
          <Stat icon={<Calculator size={18} />} label="Engine" value={health.engine ?? 'v1-math'} accent="text-red-400" />
          <Stat icon={<Layers size={18} />} label="Режимов таксономии" value={health.taxonomy_modes?.toString() ?? '—'} accent="text-blue-400" />
          <Stat icon={<GitBranch size={18} />} label="Alpha рёбер" value={health.alpha_edges?.toString() ?? '—'} accent="text-purple-400" />
          <Stat icon={<Cpu size={18} />} label="LLM providers" value={health.providers?.length.toString() ?? '—'} accent="text-amber-400" />
        </div>
      )}

      {health?.providers && (
        <div className="bg-slate-800 rounded-xl p-4">
          <p className="text-xs text-slate-500 uppercase tracking-widest mb-3">Активные LLM providers</p>
          <div className="flex flex-wrap gap-2">
            {health.providers.map(p => (
              <span key={p} className="px-2.5 py-1 bg-slate-700 text-slate-200 rounded-full text-xs font-medium">{p}</span>
            ))}
          </div>
        </div>
      )}

      <div className="bg-slate-800 rounded-xl p-4">
        <div className="flex items-center justify-between mb-4">
          <p className="text-xs text-slate-500 uppercase tracking-widest">Pipeline анализа — 14 агентов</p>
          <div className="flex gap-3 text-[10px]">
            <span className="flex items-center gap-1 text-red-400"><span className="w-2 h-2 rounded bg-red-500/60" /> engine</span>
            <span className="flex items-center gap-1 text-amber-400"><span className="w-2 h-2 rounded bg-amber-500/60" /> LLM</span>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-7 gap-2">
          {PIPELINE_STEPS.map((step, i) => (
            <div key={step.id} className="relative">
              <div className={`bg-slate-900 rounded-lg p-2.5 text-center border ${
                step.kind === 'engine' ? 'border-red-900/50' : 'border-amber-900/30'
              }`}>
                <div className="text-[10px] font-mono text-slate-500 mb-0.5">{String(i + 1).padStart(2, '0')}</div>
                <div className="text-xs font-semibold text-slate-200">{step.label}</div>
                <div className="text-[10px] text-slate-500 mt-0.5 leading-tight">{step.descRu}</div>
              </div>
              {i < PIPELINE_STEPS.length - 1 && (
                <div className="hidden md:block absolute -right-1.5 top-1/2 -translate-y-1/2 text-slate-600 z-10">
                  <Circle size={3} fill="currentColor" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <p className="text-xs text-slate-500 border border-slate-800 rounded-lg px-3 py-2">{muNote}</p>

      {showCases.length > 0 && (
        <div className="bg-slate-800 rounded-xl p-4">
          <p className="text-xs text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
            <History size={14} /> Недавние кейсы
            {recentCases.length === 0 && localCases.length > 0 && (
              <span className="text-slate-600 normal-case">{common.local}</span>
            )}
          </p>
          <div className="space-y-2">
            {showCases.map(c => (
              <button
                key={c.case_id}
                onClick={() => navigate(`/result/${encodeURIComponent(c.case_id)}`)}
                className="w-full text-left flex items-center justify-between gap-3 bg-slate-900 hover:bg-slate-900/80 border border-slate-700 hover:border-red-600/40 rounded-lg px-3 py-2 transition-colors"
              >
                <div className="min-w-0">
                  <div className="text-sm text-slate-200 truncate">{c.title || c.case_id}</div>
                  <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                    {c.country || '—'} · {c.year ?? '—'}
                    {c.engine_only && ' · engine'}
                  </div>
                </div>
                <ArrowRight size={14} className="text-slate-500 shrink-0" />
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-4">
        <button
          onClick={() => navigate('/analyze')}
          className="bg-red-600 hover:bg-red-500 text-white rounded-xl p-4 flex items-center justify-center gap-3 font-semibold transition-colors">
          <ScanSearch size={20} />
          Анализ кейса
          <ArrowRight size={18} />
        </button>
        <button
          onClick={() => navigate('/forecast')}
          className="bg-blue-700 hover:bg-blue-600 text-white rounded-xl p-4 flex items-center justify-center gap-3 font-semibold transition-colors">
          <TrendingUp size={20} />
          Прогноз
          <ArrowRight size={18} />
        </button>
        <button
          onClick={() => navigate('/ingest')}
          className="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white rounded-xl p-4 flex items-center justify-center gap-3 font-semibold transition-colors">
          <Radio size={20} className="text-emerald-400" />
          Поток данных
          <ArrowRight size={18} />
        </button>
        <button
          onClick={() => navigate('/mas')}
          className="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white rounded-xl p-4 flex items-center justify-center gap-3 font-semibold transition-colors">
          <Activity size={20} className="text-red-400" />
          Метрики MAS
          <ArrowRight size={18} />
        </button>
        <button
          onClick={() => navigate('/globe')}
          className="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white rounded-xl p-4 flex items-center justify-center gap-3 font-semibold transition-colors">
          <Globe2 size={20} className="text-red-400" />
          Глобус
          <ArrowRight size={18} />
        </button>
      </div>
    </div>
  )
}

function Stat({ icon, label, value, accent }: { icon: React.ReactNode; label: string; value: string; accent: string }) {
  return (
    <div className="bg-slate-800 rounded-xl p-4 flex items-start gap-3">
      <span className={accent}>{icon}</span>
      <div>
        <div className="text-xs text-slate-500 uppercase tracking-widest">{label}</div>
        <div className={`text-lg font-bold mt-0.5 ${accent}`}>{value}</div>
      </div>
    </div>
  )
}

function ScanSearch({ size }: { size: number }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/><path d="M11 8v6M8 11h6"/></svg>
}
