import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  Loader2, Calendar, TrendingUp, Cpu, Bot, Layers, AlertTriangle,
  ArrowLeft, Clock, History, ScanSearch, Waves,
} from 'lucide-react'
import { api } from '../lib/api'
import { PIPELINE_STEPS } from '../lib/pipeline'
import {
  common, horizonLabels, stageLabels, urgencyLabels, evidenceGradeLabels,
  muNote, engineModules, pipelineModeLabels, nav,
} from '../lib/ru'
import { cn, muColor, URGENCY_COLOR } from '../lib/utils'
import type { CaseAnalysis, CaseListItem, AgentStepMetric } from '../lib/types'

export function Forecast() {
  const { caseId } = useParams<{ caseId?: string }>()
  const navigate = useNavigate()
  const [analysis, setAnalysis] = useState<CaseAnalysis | null>(null)
  const [loading, setLoading] = useState(!!caseId)
  const [loadError, setLoadError] = useState('')
  const [recentCases, setRecentCases] = useState<CaseListItem[]>([])

  useEffect(() => {
    api.listCases(8).then(r => setRecentCases(r.cases)).catch(() => {})
  }, [])

  useEffect(() => {
    let cancelled = false

    async function load() {
      setLoadError('')
      if (caseId) {
        setLoading(true)
        try {
          const fromApi = await api.getCase(caseId)
          if (cancelled) return
          setAnalysis(fromApi)
          sessionStorage.setItem('last_analysis', JSON.stringify(fromApi))
          return
        } catch {
          if (cancelled) return
          setLoadError(`Кейс «${caseId}» не найден на сервере`)
        } finally {
          if (!cancelled) setLoading(false)
        }
      }

      const raw = sessionStorage.getItem('last_analysis')
      if (raw && !cancelled) {
        const parsed = JSON.parse(raw) as CaseAnalysis
        setAnalysis(parsed)
        if (caseId && parsed.case_id !== caseId) {
          setLoadError(`Кейс «${caseId}» не найден — показан последний результат сессии`)
        }
      }
    }

    void load()
    return () => { cancelled = true }
  }, [caseId])

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-500 gap-2">
        <Loader2 size={18} className="animate-spin" /> Загрузка прогноза…
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <TrendingUp size={22} className="text-blue-400" />
            Прогноз (FPD)
          </h1>
          <p className="text-slate-400 text-sm mt-2 max-w-2xl leading-relaxed">
            Здесь показываются прогнозные сценарии, даты из временной шкалы T4D, модели pipeline
            и вклад модулей Errorlogy (таксономия, агенты, engine). Сначала запустите анализ кейса.
          </p>
          <Link
            to="/forecast/stream"
            className="inline-flex items-center gap-2 mt-3 text-sm text-cyan-400 hover:text-cyan-300"
          >
            <Waves size={16} /> {nav.streamForecast} (Horizon 2) →
          </Link>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 text-center space-y-4">
          <Clock size={40} className="mx-auto text-slate-600" />
          <p className="text-slate-400">Анализ не загружен</p>
          <button
            onClick={() => navigate('/analyze')}
            className="inline-flex items-center gap-2 bg-red-600 hover:bg-red-500 text-white rounded-xl px-5 py-2.5 font-semibold"
          >
            <ScanSearch size={16} /> {common.goAnalyze}
          </button>
        </div>

        {recentCases.length > 0 && (
          <div className="bg-slate-800 rounded-xl p-4">
            <p className="text-xs text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
              <History size={14} /> Недавние кейсы
            </p>
            <div className="space-y-2">
              {recentCases.map(c => (
                <button
                  key={c.case_id}
                  onClick={() => navigate(`/forecast/${encodeURIComponent(c.case_id)}`)}
                  className="w-full text-left flex items-center justify-between gap-3 bg-slate-900 hover:bg-slate-900/80 border border-slate-700 hover:border-blue-600/40 rounded-lg px-3 py-2 transition-colors"
                >
                  <div className="min-w-0">
                    <div className="text-sm text-slate-200 truncate">{c.title || c.case_id}</div>
                    <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                      {c.country || '—'} · {c.year ?? '—'}
                    </div>
                  </div>
                  <TrendingUp size={14} className="text-blue-400 shrink-0" />
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  const pm = analysis.metadata?.pipeline_metrics
  const modeName = (id: string) =>
    analysis.top_modes.find(m => m.mode_id === id)?.name ?? id

  const pipelineLabel = analysis.metadata?.demo
    ? pipelineModeLabels.demo
    : analysis.metadata?.dual_run_diff
      ? pipelineModeLabels.dualRun
      : analysis.metadata?.structure_only
        ? pipelineModeLabels.structureOnly
        : analysis.metadata?.engine_only
          ? pipelineModeLabels.engineOnly
          : pipelineModeLabels.full

  const stepStatus = (agentId: string): AgentStepMetric | undefined =>
    pm?.steps?.find(s => s.agent_id === agentId)

  const t4dDates = analysis.t4d.worldline.map(pt => pt.t).filter(Boolean)
  const runStarted = pm?.started_at
  const runFinished = pm?.finished_at

  const llmProviders = [...new Set(
    (pm?.steps ?? [])
      .filter(s => s.kind === 'llm' && s.provider)
      .map(s => `${s.provider}${s.model ? ` / ${s.model}` : ''}`),
  )]

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {loadError && (
        <div className="bg-amber-900/20 border border-amber-700/40 rounded-lg px-4 py-2 text-amber-200 text-sm">
          {loadError}
        </div>
      )}

      <div className="flex items-start gap-3">
        <button onClick={() => navigate('/analyze')} className="text-slate-500 hover:text-slate-200 transition-colors mt-1">
          <ArrowLeft size={18} />
        </button>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <TrendingUp size={22} className="text-blue-400" />
            Прогноз — {analysis.case_id}
          </h1>
          <p className="text-slate-400 text-xs mt-1 flex flex-wrap items-center gap-2">
            {pipelineLabel}
            {analysis.metadata?.engine && (
              <span className="px-1.5 py-0.5 bg-red-900/40 text-red-300 rounded text-[10px] font-mono">
                {analysis.metadata.engine}
              </span>
            )}
            <Link to={`/result/${encodeURIComponent(analysis.case_id)}`} className="text-red-400 hover:text-red-300">
              Полный результат →
            </Link>
          </p>
        </div>
      </div>

      <p className="text-xs text-slate-500 border border-slate-800 rounded-lg px-3 py-2 leading-relaxed">
        {muNote}
      </p>

      {/* Dates */}
      <Section title="Даты и горизонт" icon={<Calendar size={14} className="text-blue-400" />}>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-slate-900 rounded-lg p-4 space-y-3">
            <div>
              <div className="text-[10px] text-slate-500 uppercase tracking-widest">Горизонт FPD</div>
              <div className="text-lg font-bold text-blue-400 mt-1">
                {horizonLabels[analysis.fpd.horizon] ?? analysis.fpd.horizon}
                <span className="text-slate-500 text-sm font-normal ml-2">({analysis.fpd.horizon})</span>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Категория горизонта из engine FPD — абсолютные календарные даты прогноза pipeline не возвращает.
              </p>
            </div>
            <div>
              <div className="text-[10px] text-slate-500 uppercase tracking-widest">Уверенность прогноза FPD</div>
              <div className="text-lg font-bold text-slate-200 mt-1">
                {(analysis.fpd.confidence * 100).toFixed(0)}%
                <span className="text-slate-500 text-xs font-normal ml-2">(confidence — не μ)</span>
              </div>
            </div>
          </div>

          <div className="bg-slate-900 rounded-lg p-4 space-y-3">
            <div className="text-[10px] text-slate-500 uppercase tracking-widest">T4D — метки времени worldline</div>
            {t4dDates.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {analysis.t4d.worldline.map((pt, i) => (
                  <div key={i} className="text-xs bg-slate-800 rounded px-2 py-1.5 border border-slate-700">
                    <span className="font-mono text-slate-300">{pt.t}</span>
                    <span className="text-slate-500 ml-2">{stageLabels[pt.stage] ?? pt.stage}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">{common.pipelineNoData}</p>
            )}

            <div className="text-[10px] text-slate-500 uppercase tracking-widest pt-2">Запуск pipeline</div>
            {runStarted ? (
              <p className="text-xs font-mono text-slate-300">
                {new Date(runStarted).toLocaleString('ru-RU')}
                {runFinished && ` → ${new Date(runFinished).toLocaleString('ru-RU')}`}
              </p>
            ) : (
              <p className="text-sm text-slate-500">{common.noData}</p>
            )}
          </div>
        </div>
      </Section>

      {/* Predicted events */}
      <Section title="Прогнозируемые сценарии и события" icon={<TrendingUp size={14} className="text-blue-400" />}>
        {analysis.fpd.pno_transition_forecast && (
          <div className="bg-slate-900 rounded-lg p-3 mb-4">
            <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Переход PNO</div>
            <p className="text-sm text-slate-300 leading-relaxed">{analysis.fpd.pno_transition_forecast}</p>
          </div>
        )}

        {analysis.fpd.mode_forecasts.length > 0 ? (
          <div className="overflow-x-auto mb-4">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-slate-500 text-left">
                  <th className="pb-2 pr-3">mode_id</th>
                  <th className="pb-2 pr-3">Режим</th>
                  <th className="pb-2 pr-3">μ_forecast</th>
                  <th className="pb-2 pr-3">scenario_probability</th>
                  <th className="pb-2 pr-3">confidence</th>
                  <th className="pb-2">evidence_grade</th>
                </tr>
              </thead>
              <tbody>
                {analysis.fpd.mode_forecasts.map(f => (
                  <tr key={f.mode_id} className="border-t border-slate-700 text-slate-300">
                    <td className="py-1.5 pr-3 font-mono">{f.mode_id}</td>
                    <td className="py-1.5 pr-3 text-slate-400">{modeName(f.mode_id)}</td>
                    <td className={cn('py-1.5 pr-3 font-bold', muColor(f.mu_forecast))}>
                      {f.mu_forecast.toFixed(2)}
                      <span className="text-slate-600 font-normal ml-1">μ</span>
                    </td>
                    <td className="py-1.5 pr-3">{f.scenario_probability.toFixed(2)}</td>
                    <td className="py-1.5 pr-3">{f.confidence.toFixed(2)}</td>
                    <td className="py-1.5">{evidenceGradeLabels[f.evidence_grade] ?? f.evidence_grade}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="text-[10px] text-slate-500 mt-2">
              μ_forecast — нечёткая принадлежность прогнозируемого режима. scenario_probability — отдельная метрика сценария.
            </p>
          </div>
        ) : (
          <p className="text-sm text-slate-500 mb-4">{common.pipelineNoData}</p>
        )}

        {analysis.fpd.early_warnings.length > 0 && (
          <div className="space-y-2">
            <div className="text-[10px] text-slate-500 uppercase tracking-widest">Ранние предупреждения FPD</div>
            {analysis.fpd.early_warnings.map((w, i) => (
              <div key={i} className={cn('flex items-start gap-2.5 rounded-lg px-3 py-2', URGENCY_COLOR[w.urgency])}>
                <span className="text-xs font-semibold uppercase tracking-wide shrink-0 mt-0.5">
                  {urgencyLabels[w.urgency] ?? w.urgency}
                </span>
                <div>
                  <p className="text-xs font-semibold">{w.signal}</p>
                  <p className="text-xs opacity-80 mt-0.5">{w.description}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {analysis.t4d.worldline.length > 0 && (
          <div className="mt-4 pt-4 border-t border-slate-700">
            <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-2">T4D — прогнозные этапы worldline</div>
            <div className="space-y-2">
              {analysis.t4d.worldline.map((pt, i) => (
                <div key={i} className="bg-slate-900 rounded-lg px-3 py-2 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-slate-400">{pt.t || common.noData}</span>
                    <span className="text-blue-400">{stageLabels[pt.stage] ?? pt.stage}</span>
                  </div>
                  <p className="text-slate-300 mt-1 leading-relaxed">{pt.description}</p>
                  {pt.modes.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1.5">
                      {pt.modes.map(m => (
                        <span key={m} className="text-[10px] font-mono px-1.5 py-0.5 bg-slate-800 text-slate-400 rounded">{m}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </Section>

      {/* Models used */}
      <Section title="Модели и pipeline" icon={<Cpu size={14} className="text-red-400" />}>
        <div className="grid md:grid-cols-3 gap-3 mb-4">
          <div className="bg-slate-900 rounded-lg p-3">
            <div className="text-[10px] text-slate-500 uppercase">Engine</div>
            <div className="text-sm font-bold text-red-400 font-mono mt-1">
              {pm?.engine_version ?? analysis.metadata?.engine ?? common.noData}
            </div>
          </div>
          <div className="bg-slate-900 rounded-lg p-3">
            <div className="text-[10px] text-slate-500 uppercase">Режим запуска</div>
            <div className="text-sm font-bold text-slate-200 mt-1">{pipelineLabel}</div>
          </div>
          <div className="bg-slate-900 rounded-lg p-3">
            <div className="text-[10px] text-slate-500 uppercase">LLM providers</div>
            <div className="text-sm text-amber-300 mt-1">
              {llmProviders.length > 0 ? llmProviders.join(', ') : (analysis.metadata?.engine_only ? 'не использовались' : common.noData)}
            </div>
          </div>
        </div>

        {pm?.steps?.length ? (
          <div className="space-y-1.5">
            {pm.steps.map((s, i) => (
              <div key={`${s.agent_id}-${i}`} className="flex items-center justify-between text-xs bg-slate-900 rounded px-3 py-2">
                <span className="text-slate-300 font-mono">{s.agent_id}</span>
                <span className={cn(
                  'px-1.5 py-0.5 rounded text-[10px]',
                  s.kind === 'engine' ? 'bg-red-900/40 text-red-300' : 'bg-amber-900/30 text-amber-300',
                )}>{s.kind}</span>
                <span className="text-slate-500">{s.status} · {s.duration_ms.toFixed(0)}ms</span>
                {s.provider && (
                  <span className="text-slate-600 truncate max-w-[140px]">{s.provider}/{s.model}</span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">{common.pipelineNoData} (metadata.pipeline_metrics)</p>
        )}
      </Section>

      {/* Errorlogy aspects */}
      <Section title="Аспекты Errorlogy в прогнозе" icon={<Layers size={14} className="text-purple-400" />}>
        <div className="space-y-4">
          <div>
            <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-2">Таксономия — top_modes (μ после α)</div>
            {analysis.top_modes.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {analysis.top_modes.slice(0, 8).map(m => (
                  <div key={m.mode_id} className="bg-slate-900 rounded-lg px-2.5 py-1.5 text-xs border border-slate-700">
                    <span className="font-mono text-slate-400">{m.mode_id}</span>
                    <span className={cn('ml-2 font-bold', muColor(m.mu))}>μ={m.mu.toFixed(2)}</span>
                    <p className="text-slate-300 mt-0.5">{m.name}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">{common.noData}</p>
            )}
          </div>

          <div>
            <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-2">Агенты pipeline (14 шагов)</div>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
              {PIPELINE_STEPS.map(step => {
                const ran = stepStatus(step.id)
                return (
                  <div
                    key={step.id}
                    className={cn(
                      'rounded-lg p-2 text-center border text-xs',
                      ran
                        ? step.kind === 'engine' ? 'border-red-900/50 bg-red-950/20' : 'border-amber-900/30 bg-amber-950/10'
                        : 'border-slate-700 bg-slate-900 opacity-60',
                    )}
                  >
                    <div className="font-semibold text-slate-200">{step.label}</div>
                    <div className="text-[10px] text-slate-500 mt-0.5 leading-tight">{step.descRu}</div>
                    <div className="text-[10px] mt-1 font-mono">
                      {ran ? (
                        <span className="text-green-400">{ran.status}</span>
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          <div>
            <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-2">Engine-модули (TZ §9)</div>
            <div className="grid md:grid-cols-2 gap-2">
              {engineModules.map(mod => {
                const contrib = getModuleContribution(analysis, mod.id)
                return (
                  <div key={mod.id} className="bg-slate-900 rounded-lg px-3 py-2 flex items-start gap-2 text-xs">
                    <Bot size={12} className={contrib ? 'text-green-400 shrink-0 mt-0.5' : 'text-slate-600 shrink-0 mt-0.5'} />
                    <div>
                      <span className="font-semibold text-slate-200">{mod.label}</span>
                      <span className="text-slate-500 ml-2">{mod.desc}</span>
                      {contrib && <p className="text-slate-400 mt-0.5">{contrib}</p>}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {analysis.cat.catastrophe_hypothesis && (
            <div className="bg-purple-900/20 border border-purple-700/30 rounded-lg p-3">
              <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">CAT — гипотеза катастрофы</div>
              <p className="text-sm text-purple-300 font-mono">{analysis.cat.catastrophe_hypothesis}</p>
              <p className="text-xs text-slate-400 mt-1">{analysis.cat.explanation}</p>
            </div>
          )}
        </div>
      </Section>

      {analysis.metadata?.engine_warnings && analysis.metadata.engine_warnings.length > 0 && (
        <div className="bg-amber-900/20 border border-amber-700/40 rounded-xl p-4 space-y-1.5">
          <p className="text-xs text-amber-400 uppercase tracking-widest">Предупреждения engine</p>
          {analysis.metadata.engine_warnings.map((w, i) => (
            <p key={i} className="text-xs text-amber-200 flex gap-2">
              <AlertTriangle size={12} className="shrink-0 mt-0.5" />{w}
            </p>
          ))}
        </div>
      )}
    </div>
  )
}

function getModuleContribution(analysis: CaseAnalysis, moduleId: string): string | null {
  switch (moduleId) {
    case 'wms':
      return `MSI ${analysis.wms.msi.toFixed(2)}, CEP ${analysis.wms.cep.toFixed(2)}`
    case 'pno':
      return `Домinant: ${analysis.pno.dominant_pno}`
    case 'acc':
      return analysis.acc.max_contribution_cluster.name
    case 'egd':
      return `Echo pressure ${analysis.egd.echo_room_pressure.toFixed(2)}`
    case 't4d':
      return `${analysis.t4d.worldline.length} точек worldline`
    case 'cat':
      return analysis.cat.catastrophe_hypothesis
    case 'fpd':
      return `Horizon ${analysis.fpd.horizon}, ${analysis.fpd.mode_forecasts.length} прогнозов режимов`
    case 'lbi':
      return `${analysis.lbi.alternatives.length} альтернатив улучшения`
    case 'alpha':
      return `${analysis.alpha.activated_edges.length} активированных рёбер`
    case 'classifier':
      return `${analysis.top_modes.length} top_modes`
    default:
      return null
  }
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
