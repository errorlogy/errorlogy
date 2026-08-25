import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Loader2, Play, FileSearch, Clock, TrendingUp, Cpu, Bot, History,
} from 'lucide-react'
import { api } from '../lib/api'
import {
  common, horizonLabels, stageLabels, urgencyLabels, muNote, nav,
} from '../lib/en'
import { cn, muColor, URGENCY_COLOR } from '../lib/utils'
import type { AgentStepMetric, CaseAnalysis, CaseListItem } from '../lib/types'
import { Section } from '../components/Section'

export function CaseForecastPage() {
  const [searchParams] = useSearchParams()
  const presetId = searchParams.get('id') ?? ''

  const [caseId, setCaseId] = useState(presetId || `case-${Date.now()}`)
  const [title, setTitle] = useState('')
  const [country, setCountry] = useState('')
  const [rawText, setRawText] = useState('')
  const [engineOnly, setEngineOnly] = useState(true)
  const [useStream, setUseStream] = useState(true)

  const [running, setRunning] = useState(false)
  const [steps, setSteps] = useState<AgentStepMetric[]>([])
  const [result, setResult] = useState<CaseAnalysis | null>(null)
  const [error, setError] = useState('')
  const [recentCases, setRecentCases] = useState<CaseListItem[]>([])
  const [loadingCase, setLoadingCase] = useState(false)

  useEffect(() => {
    api.listCases(12).then(r => setRecentCases(r.cases)).catch(() => {})
  }, [])

  const loadExistingCase = useCallback(async (id: string) => {
    setLoadingCase(true)
    setError('')
    try {
      const data = await api.getCase(id)
      setResult(data)
      setCaseId(data.case_id)
    } catch {
      setError(`Кейс «${id}» не найден`)
      setResult(null)
    } finally {
      setLoadingCase(false)
    }
  }, [])

  useEffect(() => {
    if (presetId) {
      setCaseId(presetId)
      void loadExistingCase(presetId)
    }
  }, [presetId, loadExistingCase])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!rawText.trim()) {
      setError('Введите текст кейса')
      return
    }
    setRunning(true)
    setError('')
    setSteps([])
    setResult(null)

    const params = {
      case_id: caseId.trim() || `case-${Date.now()}`,
      raw_text: rawText,
      title: title || undefined,
      country: country || undefined,
      engine_only: engineOnly,
    }

    try {
      const data = useStream
        ? await api.analyzeStream(params, step => setSteps(prev => [...prev, step]))
        : await api.analyze(params)
      setResult(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Ошибка анализа')
    } finally {
      setRunning(false)
    }
  }

  const modeName = (id: string) =>
    result?.top_modes.find(m => m.mode_id === id)?.name ?? id

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <FileSearch size={22} className="text-blue-400" />
          {nav.case}
        </h1>
        <p className="text-slate-400 text-sm mt-1 max-w-2xl">
          Запуск анализа кейса → FPD (μ_forecast, сценарии) и T4D (worldline).
          По умолчанию engine_only для скорости.
        </p>
      </div>

      <p className="text-xs text-slate-500 border border-slate-800 rounded-lg px-3 py-2">{muNote}</p>

      <form onSubmit={e => void handleSubmit(e)} className="bg-slate-800 rounded-xl p-4 space-y-4">
        <div className="grid sm:grid-cols-2 gap-3">
          <label className="block">
            <span className="text-xs text-slate-500">case_id</span>
            <input
              value={caseId}
              onChange={e => setCaseId(e.target.value)}
              className="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
              placeholder="case-001"
            />
          </label>
          <label className="block">
            <span className="text-xs text-slate-500">Страна</span>
            <input
              value={country}
              onChange={e => setCountry(e.target.value)}
              className="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
              placeholder="USA"
            />
          </label>
        </div>
        <label className="block">
          <span className="text-xs text-slate-500">Заголовок (опционально)</span>
          <input
            value={title}
            onChange={e => setTitle(e.target.value)}
            className="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
          />
        </label>
        <label className="block">
          <span className="text-xs text-slate-500">Текст кейса *</span>
          <textarea
            value={rawText}
            onChange={e => setRawText(e.target.value)}
            rows={6}
            className="mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 font-mono"
            placeholder="Описание governance-инцидента…"
          />
        </label>
        <div className="flex flex-wrap gap-4 text-sm">
          <label className="flex items-center gap-2 text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={engineOnly}
              onChange={e => setEngineOnly(e.target.checked)}
              className="rounded"
            />
            Только engine (быстро)
          </label>
          <label className="flex items-center gap-2 text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={useStream}
              onChange={e => setUseStream(e.target.checked)}
              className="rounded"
            />
            SSE-поток шагов
          </label>
        </div>
        <button
          type="submit"
          disabled={running || !rawText.trim()}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg px-4 py-2 text-sm font-semibold"
        >
          {running ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
          Запустить анализ
        </button>
      </form>

      {error && (
        <div className="bg-red-900/20 border border-red-700/40 rounded-lg px-4 py-2 text-red-200 text-sm">{error}</div>
      )}

      {running && steps.length > 0 && (
        <Section title="Шаги pipeline" icon={<Cpu size={14} className="text-red-400" />}>
          <div className="space-y-1">
            {steps.map((s, i) => (
              <div key={`${s.agent_id}-${i}`} className="flex items-center justify-between text-xs bg-slate-900 rounded px-2 py-1.5">
                <span className="flex items-center gap-2">
                  {s.kind === 'llm' ? <Bot size={12} className="text-purple-400" /> : <Cpu size={12} className="text-red-400" />}
                  <span className="font-mono text-slate-300">{s.agent_id}</span>
                </span>
                <span className="text-slate-500">{s.duration_ms} ms · {s.status}</span>
              </div>
            ))}
          </div>
        </Section>
      )}

      {loadingCase && (
        <div className="flex items-center gap-2 text-slate-500 text-sm">
          <Loader2 size={16} className="animate-spin" /> Загрузка кейса…
        </div>
      )}

      {recentCases.length > 0 && !result && (
        <Section title="Недавние кейсы" icon={<History size={14} />}>
          <div className="space-y-2">
            {recentCases.map(c => (
              <button
                key={c.case_id}
                type="button"
                onClick={() => void loadExistingCase(c.case_id)}
                className="w-full text-left flex justify-between gap-3 bg-slate-900 hover:border-blue-600/40 border border-slate-700 rounded-lg px-3 py-2 text-sm"
              >
                <span className="truncate text-slate-200">{c.title || c.case_id}</span>
                <TrendingUp size={14} className="text-blue-400 shrink-0" />
              </button>
            ))}
          </div>
        </Section>
      )}

      {result && (
        <>
          <div className="text-xs text-slate-500 font-mono">
            {result.case_id}
            {result.metadata?.engine_only && ' · engine_only'}
            {result.metadata?.engine && ` · ${result.metadata.engine}`}
          </div>

          {result.metadata?.pipeline_metrics && (
            <Section title="Агенты pipeline" icon={<Bot size={14} className="text-purple-400" />}>
              <div className="flex flex-wrap gap-2">
                {result.metadata.pipeline_metrics.steps.map((s, i) => (
                  <span
                    key={`${s.agent_id}-${i}`}
                    className={cn(
                      'text-xs font-mono px-2 py-1 rounded border',
                      s.kind === 'llm'
                        ? 'bg-purple-900/30 border-purple-800/50 text-purple-300'
                        : 'bg-red-900/30 border-red-800/50 text-red-300',
                    )}
                  >
                    {s.agent_id}
                  </span>
                ))}
              </div>
            </Section>
          )}

          <Section title="Режимы таксономии (топ)" icon={<TrendingUp size={14} className="text-blue-400" />}>
            <div className="space-y-2">
              {result.top_modes.slice(0, 8).map(m => (
                <div key={m.mode_id} className="flex justify-between text-xs bg-slate-900 rounded px-3 py-2">
                  <span>
                    <span className="font-mono text-slate-400">{m.mode_id}</span>
                    <span className="text-slate-300 ml-2">{m.name}</span>
                  </span>
                  <span className={muColor(m.mu)}>μ={m.mu.toFixed(3)}</span>
                </div>
              ))}
            </div>
          </Section>

          <Section title="FPD — прогноз" icon={<TrendingUp size={14} className="text-cyan-400" />}>
            <div className="mb-4 flex flex-wrap gap-4 text-sm">
              <div>
                <span className="text-slate-500">Горизонт: </span>
                <span className="text-white font-semibold">
                  {horizonLabels[result.fpd.horizon] ?? result.fpd.horizon}
                </span>
              </div>
              <div>
                <span className="text-slate-500">Confidence: </span>
                <span className="text-white">{(result.fpd.confidence * 100).toFixed(0)}%</span>
              </div>
              {result.fpd.pno_transition_forecast && (
                <div className="text-slate-400 text-xs">{result.fpd.pno_transition_forecast}</div>
              )}
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-slate-500 text-left">
                    <th className="pb-2 pr-3">Режим</th>
                    <th className="pb-2 pr-3">μ_forecast</th>
                    <th className="pb-2 pr-3">scenario_probability</th>
                    <th className="pb-2">grade</th>
                  </tr>
                </thead>
                <tbody>
                  {result.fpd.mode_forecasts.map(mf => (
                    <tr key={mf.mode_id} className="border-t border-slate-700">
                      <td className="py-1.5 pr-3">
                        <span className="font-mono text-slate-400">{mf.mode_id}</span>
                        <span className="text-slate-300 ml-1">{modeName(mf.mode_id)}</span>
                      </td>
                      <td className={cn('py-1.5 pr-3 font-mono', muColor(mf.mu_forecast))}>
                        {mf.mu_forecast.toFixed(3)}
                      </td>
                      <td className="py-1.5 pr-3 font-mono text-slate-400">
                        {(mf.scenario_probability * 100).toFixed(1)}%
                      </td>
                      <td className="py-1.5 text-slate-500">{mf.evidence_grade}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-[10px] text-slate-500 mt-2">
              μ_forecast — нечёткая принадлежность; scenario_probability — вес сценария (отдельная величина).
            </p>

            {result.fpd.early_warnings.length > 0 && (
              <div className="mt-4 space-y-2">
                <p className="text-[10px] text-slate-500 uppercase">Ранние предупреждения</p>
                {result.fpd.early_warnings.map((w, i) => (
                  <div key={i} className="text-xs bg-slate-900 rounded px-3 py-2 flex gap-2">
                    <span className={cn('px-1.5 py-0.5 rounded text-[10px]', URGENCY_COLOR[w.urgency])}>
                      {urgencyLabels[w.urgency]}
                    </span>
                    <span className="text-slate-300">{w.description}</span>
                  </div>
                ))}
              </div>
            )}
          </Section>

          <Section title="T4D — временная шкала" icon={<Clock size={14} className="text-amber-400" />}>
            {result.t4d.worldline.length > 0 ? (
              <div className="space-y-3">
                {result.t4d.worldline.map((pt, i) => (
                  <div key={i} className="flex gap-3 text-xs">
                    <span className="font-mono text-slate-500 w-24 shrink-0">{pt.t || '—'}</span>
                    <span className="text-amber-400/80 w-28 shrink-0">{stageLabels[pt.stage] ?? pt.stage}</span>
                    <span className="text-slate-300">{pt.description}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">{common.noData}</p>
            )}
            <div className="mt-4 grid sm:grid-cols-3 gap-2 text-xs text-slate-500">
              <div>Latency risk: {result.t4d.warning_to_action_latency_risk.toFixed(2)}</div>
              <div>Window loss: {result.t4d.intervention_window_loss.toFixed(2)}</div>
              <div>Irreversibility: {result.t4d.irreversibility_threshold_risk.toFixed(2)}</div>
            </div>
          </Section>
        </>
      )}
    </div>
  )
}
