import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { api } from '../lib/api'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, RadarChart,
  PolarGrid, PolarAngleAxis, Radar,
} from 'recharts'
import { AlertTriangle, TrendingUp, Clock, ArrowLeft, ChevronDown, ChevronUp, Radio, Network, Eye } from 'lucide-react'
import { cn, STAGE_COLORS, URGENCY_COLOR, muColor } from '../lib/utils'
import { common, horizonLabels, pipelineModeLabels, stageLabels, urgencyLabels, evidenceGradeLabels } from '../lib/en'
import { ModeBadge } from '../components/ModeBadge'
import type { CaseAnalysis } from '../lib/types'

export function Result() {
  const { caseId } = useParams<{ caseId?: string }>()
  const [analysis, setAnalysis] = useState<CaseAnalysis | null>(null)
  const [loading, setLoading] = useState(!!caseId)
  const [loadError, setLoadError] = useState('')
  const navigate = useNavigate()

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

  if (loading) return (
    <div className="flex-1 flex items-center justify-center text-slate-500 gap-2">
      <Loader2 size={18} className="animate-spin" /> Загрузка анализа…
    </div>
  )

  if (!analysis) return (
    <div className="flex-1 flex items-center justify-center text-slate-500 flex-col gap-3">
      <p>Анализа пока нет.</p>
      <button onClick={() => navigate('/analyze')} className="text-red-400 hover:underline text-sm">{common.goAnalyze} →</button>
    </div>
  )

  const pnoData = Object.entries(analysis.pno.scores).map(([k, v]) => ({ name: k, value: +(v * 100).toFixed(0) }))
  const topModes = analysis.top_modes.slice(0, 8)
  const topEdges = analysis.alpha.activated_edges
    .slice()
    .sort((a, b) => Math.abs(b.delta_mu) - Math.abs(a.delta_mu))
    .slice(0, 8)

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {loadError && (
        <div className="bg-amber-900/20 border border-amber-700/40 rounded-lg px-4 py-2 text-amber-200 text-sm">
          {loadError}
        </div>
      )}

      {/* Back + title */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate('/analyze')} className="text-slate-500 hover:text-slate-200 transition-colors">
          <ArrowLeft size={18} />
        </button>
        <div>
          <h1 className="text-xl font-bold text-white">{analysis.case_id}</h1>
          <p className="text-slate-400 text-xs flex items-center gap-2 flex-wrap">
            {analysis.metadata?.demo
              ? pipelineModeLabels.demo
              : analysis.metadata?.dual_run_diff
                ? pipelineModeLabels.dualRun
                : analysis.metadata?.structure_only
                  ? pipelineModeLabels.structureOnly
                  : analysis.metadata?.engine_only
                    ? pipelineModeLabels.engineOnly
                    : pipelineModeLabels.full}
            {analysis.metadata?.engine && (
              <span className="px-1.5 py-0.5 bg-red-900/40 text-red-300 rounded text-[10px] font-mono">{analysis.metadata.engine}</span>
            )}
          </p>
        </div>
      </div>

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

      {analysis.metadata?.dual_run_diff && (
        <Section title="Dual-run: Engine vs Full MAS">
          <div className="bg-slate-900 rounded-lg p-4 space-y-3 text-sm">
            <div className="flex flex-wrap gap-4">
              <span className="text-slate-400">Jaccard top-5: <b className="text-white">{(analysis.metadata.dual_run_diff.top_modes_jaccard * 100).toFixed(0)}%</b></span>
              <span className={analysis.metadata.dual_run_diff.pno_match ? 'text-green-400' : 'text-amber-400'}>
                PNO {analysis.metadata.dual_run_diff.pno_match ? 'совпадение' : 'расхождение'}
              </span>
              <span className={analysis.metadata.dual_run_diff.cat_match ? 'text-green-400' : 'text-amber-400'}>
                CAT {analysis.metadata.dual_run_diff.cat_match ? 'совпадение' : 'расхождение'}
              </span>
            </div>
            <div className="grid md:grid-cols-2 gap-3 text-xs font-mono">
              <div>
                <div className="text-slate-500 mb-1">Engine top-5</div>
                {analysis.metadata.dual_run_diff.engine_only_top5.map(id => (
                  <div key={id} className="text-red-300">{id}</div>
                ))}
              </div>
              <div>
                <div className="text-slate-500 mb-1">Full MAS top-5</div>
                {analysis.metadata.dual_run_diff.full_top5.map(id => (
                  <div key={id} className="text-amber-300">{id}</div>
                ))}
              </div>
            </div>
            {analysis.metadata.dual_run_diff.red_team_flags.length > 0 && (
              <div className="space-y-1">
                {analysis.metadata.dual_run_red_team_flagged && (
                  <p className="text-amber-400 text-xs mb-2">
                    Engine vs MAS расхождение — флаг Red Team
                  </p>
                )}
                {analysis.metadata.dual_run_diff.red_team_flags.map((f, i) => (
                  <div key={i} className="text-amber-300 text-xs flex gap-2">
                    <AlertTriangle size={12} className="shrink-0 mt-0.5" />{f}
                  </div>
                ))}
              </div>
            )}
          </div>
        </Section>
      )}

      {analysis.metadata?.pipeline_metrics && (
        <Section title="Метрики pipeline">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="bg-slate-900 rounded p-2">
              <div className="text-slate-500">Всего</div>
              <div className="text-white font-mono">{analysis.metadata.pipeline_metrics.totals.total_duration_ms}ms</div>
            </div>
            <div className="bg-slate-900 rounded p-2">
              <div className="text-slate-500">Engine</div>
              <div className="text-red-300 font-mono">{analysis.metadata.pipeline_metrics.totals.engine_duration_ms}ms</div>
            </div>
            <div className="bg-slate-900 rounded p-2">
              <div className="text-slate-500">LLM</div>
              <div className="text-amber-300 font-mono">{analysis.metadata.pipeline_metrics.totals.llm_duration_ms}ms</div>
            </div>
            <div className="bg-slate-900 rounded p-2">
              <div className="text-slate-500">Токены</div>
              <div className="text-white font-mono">
                {analysis.metadata.pipeline_metrics.totals.input_tokens}+{analysis.metadata.pipeline_metrics.totals.output_tokens}
              </div>
            </div>
          </div>
        </Section>
      )}

      {/* KPI row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Kpi label="PNO режим" value={analysis.pno.dominant_pno} color="text-red-400" icon={<AlertTriangle size={16}/>} />
        <Kpi label="MSI / CEP" value={`${analysis.wms.msi.toFixed(2)} / ${analysis.wms.cep.toFixed(2)}`} color="text-emerald-400" icon={<Radio size={16}/>} />
        <Kpi label="CAT гипотеза" value={analysis.cat.catastrophe_hypothesis} color="text-purple-400" icon={<TrendingUp size={16}/>} />
        <Kpi label="Прогноз FPD" value={`${horizonLabels[analysis.fpd.horizon] ?? analysis.fpd.horizon} / ${(analysis.fpd.confidence*100).toFixed(0)}%`} color="text-blue-400" icon={<Clock size={16}/>} />
      </div>

      <Section title="WMS — слабые мультиисточниковые сигналы">
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-slate-900 rounded-lg p-4 space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="text-[10px] text-slate-500 uppercase tracking-widest">MSI</div>
                <div className="text-2xl font-bold text-emerald-400">{analysis.wms.msi.toFixed(3)}</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-500 uppercase tracking-widest">CEP</div>
                <div className="text-2xl font-bold text-red-400">{analysis.wms.cep.toFixed(3)}</div>
              </div>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">{analysis.wms.early_warning_hypothesis}</p>
          </div>
          <div className="bg-slate-900 rounded-lg p-4">
            <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-2">Активные сигналы</div>
            <div className="flex flex-wrap gap-1.5">
              {analysis.wms.active_signals.map(s => (
                <span key={s} className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">{s}</span>
              ))}
            </div>
          </div>
        </div>
      </Section>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Top modes bar */}
        <Section title="Top режимы (μ после α-propagation)">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={topModes.map(m => ({ name: m.mode_id, mu: +(m.mu * 100).toFixed(0), label: m.name }))}
              layout="vertical" margin={{ left: 8, right: 24, top: 4, bottom: 4 }}>
              <XAxis type="number" domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} tickFormatter={v => `${v}%`} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'monospace' }} width={72} />
              <Tooltip
                content={({ active, payload }) =>
                  active && payload?.[0] ? (
                    <div className="bg-slate-900 border border-slate-700 rounded p-2 text-xs text-slate-200">
                      <div className="font-mono text-slate-400">{payload[0].payload.name}</div>
                      <div>{payload[0].payload.label}</div>
                      <div className="text-amber-400 font-bold">μ = {(payload[0].value as number / 100).toFixed(2)}</div>
                    </div>
                  ) : null
                }
              />
              <Bar dataKey="mu" radius={[0, 3, 3, 0]}>
                {topModes.map((m) => (
                  <Cell key={m.mode_id} fill={m.mu >= 0.75 ? '#ef4444' : m.mu >= 0.5 ? '#f59e0b' : '#3b82f6'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Section>

        {/* PNO radar */}
        <Section title="PNO — оценки режимов">
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={pnoData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} />
              <Radar name="PNO" dataKey="value" stroke="#ef4444" fill="#ef4444" fillOpacity={0.25} strokeWidth={2} />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
                labelStyle={{ color: '#94a3b8' }} itemStyle={{ color: '#f87171' }} />
            </RadarChart>
          </ResponsiveContainer>
          <p className="text-xs text-slate-500 text-center mt-1">{analysis.pno.explanation}</p>
        </Section>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Section title="α-Propagation — top активированные рёбра">
          <div className="space-y-1.5">
            {topEdges.map((e, i) => (
              <div key={i} className="flex items-center gap-2 text-xs font-mono bg-slate-900 rounded px-2 py-1.5">
                <Network size={12} className="text-slate-500 shrink-0" />
                <span className="text-slate-400">{e.from_id}</span>
                <span className={cn('font-bold', e.delta_mu > 0 ? 'text-green-400' : 'text-red-400')}>
                  {e.delta_mu > 0 ? '+' : ''}{e.delta_mu.toFixed(3)}
                </span>
                <span className="text-slate-400">→ {e.to_id}</span>
                <span className="text-slate-600 ml-auto">w={e.weight.toFixed(2)}</span>
              </div>
            ))}
          </div>
          <p className="text-[10px] text-slate-500 mt-2">
            μ = нечёткая принадлежность после распространения по графу — не вероятность.
          </p>
        </Section>

        <Section title="EGD — динамика эхо-камеры">
          <div className="bg-slate-900 rounded-lg p-4 space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="text-[10px] text-slate-500 uppercase tracking-widest">Давление эхо-камеры</div>
                <div className={cn('text-xl font-bold', analysis.egd.echo_room_pressure > 0.7 ? 'text-red-400' : 'text-amber-400')}>
                  {analysis.egd.echo_room_pressure.toFixed(2)}
                </div>
              </div>
              <div>
                <div className="text-[10px] text-slate-500 uppercase tracking-widest">Prior скрытого сигнала</div>
                <div className="text-xl font-bold text-purple-400">{analysis.egd.hidden_signal_prior.toFixed(2)}</div>
              </div>
            </div>
            <div className="space-y-2">
              {analysis.egd.likely_egd_modes.slice(0, 4).map(m => (
                <ModeBadge key={m.mode_id} mode={m} compact />
              ))}
            </div>
          </div>
        </Section>
      </div>

      {/* T4D Timeline */}
      <Section title="T4D — временная worldline">
        <div className="flex items-start gap-0 overflow-x-auto pb-2">
          {analysis.t4d.worldline.map((pt, i) => (
            <div key={i} className="flex flex-col items-center shrink-0" style={{ minWidth: 120 }}>
              <div className="w-3 h-3 rounded-full border-2 shrink-0 z-10"
                style={{ borderColor: STAGE_COLORS[pt.stage], background: STAGE_COLORS[pt.stage] + '40' }} />
              {i < analysis.t4d.worldline.length - 1 && (
                <div className="h-px flex-1 bg-slate-700 w-full absolute left-1/2" />
              )}
              <div className="mt-2 text-center px-2">
                <div className="text-[10px] font-mono text-slate-500">{pt.t}</div>
                <div className="text-xs font-semibold mt-0.5" style={{ color: STAGE_COLORS[pt.stage] }}>
                  {stageLabels[pt.stage] ?? pt.stage.replace(/_/g, ' ')}
                </div>
                <div className="text-[10px] text-slate-400 mt-1 leading-tight">{pt.description}</div>
              </div>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-3 gap-3 mt-3">
          {[
            { label: 'Риск задержки', value: analysis.t4d.warning_to_action_latency_risk },
            { label: 'Потеря окна', value: analysis.t4d.intervention_window_loss },
            { label: 'Необратимость', value: analysis.t4d.irreversibility_threshold_risk },
          ].map(m => (
            <div key={m.label} className="bg-slate-900 rounded-lg p-2.5 text-center">
              <div className="text-[10px] text-slate-500 uppercase tracking-widest">{m.label}</div>
              <div className={cn('text-lg font-bold mt-0.5', m.value > 0.7 ? 'text-red-400' : m.value > 0.4 ? 'text-amber-400' : 'text-green-400')}>
                {(m.value * 100).toFixed(0)}%
              </div>
            </div>
          ))}
        </div>
      </Section>

      <div className="grid md:grid-cols-2 gap-6">
        {/* ACC */}
        <Section title="ACC — кластеры вклада">
          <div className="space-y-2">
            {analysis.acc.clusters.slice(0, 5).map(c => (
              <div key={c.cluster_id} className={cn('rounded-lg p-2.5 border',
                c.cluster_id === analysis.acc.max_contribution_cluster.cluster_id
                  ? 'border-amber-500/40 bg-amber-500/5'
                  : 'border-slate-700 bg-slate-900')}>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-400">{c.cluster_id}</span>
                  <span className={cn('text-xs font-bold', c.score > 0.7 ? 'text-red-400' : c.score > 0.4 ? 'text-amber-400' : 'text-slate-400')}>
                    {(c.score * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-xs text-slate-200 mt-0.5">{c.name}</p>
              </div>
            ))}
          </div>
        </Section>

        {/* CAT */}
        <Section title="CAT — гипотеза катастрофы">
          <div className="bg-slate-900 rounded-lg p-4 space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-purple-400 font-mono">{analysis.cat.catastrophe_hypothesis}</span>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed">{analysis.cat.explanation}</p>
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: 'Риск бифуркации', value: analysis.cat.bifurcation_risk, color: 'text-red-400' },
                { label: 'Риск гистерезиса', value: analysis.cat.hysteresis_risk, color: 'text-purple-400' },
              ].map(m => (
                <div key={m.label} className="bg-slate-800 rounded p-2 text-center">
                  <div className="text-[10px] text-slate-500 uppercase tracking-widest">{m.label}</div>
                  <div className={cn('text-base font-bold', m.color)}>{(m.value * 100).toFixed(0)}%</div>
                </div>
              ))}
            </div>
          </div>
        </Section>
      </div>

      {/* FPD */}
      <Section title="FPD — прогноз">
        <div className="flex items-center gap-3 mb-3 flex-wrap">
          <span className="text-xs text-slate-500 uppercase tracking-widest">Горизонт</span>
          <span className="px-2 py-0.5 bg-blue-500/20 text-blue-300 rounded text-xs font-semibold">
            {horizonLabels[analysis.fpd.horizon] ?? analysis.fpd.horizon}
          </span>
          <span className="text-xs text-slate-500 uppercase tracking-widest ml-2">Confidence</span>
          <span className="text-blue-400 font-bold text-sm">{(analysis.fpd.confidence * 100).toFixed(0)}%</span>
          <button
            onClick={() => navigate(`/forecast/${encodeURIComponent(analysis.case_id)}`)}
            className="ml-auto text-xs text-blue-400 hover:text-blue-300"
          >
            Подробный прогноз →
          </button>
        </div>
        {analysis.fpd.mode_forecasts.length > 0 && (
          <div className="overflow-x-auto mb-3">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-slate-500 text-left">
                  <th className="pb-2 pr-3">mode_id</th>
                  <th className="pb-2 pr-3">μ_forecast</th>
                  <th className="pb-2 pr-3">scenario_probability</th>
                  <th className="pb-2 pr-3">confidence</th>
                  <th className="pb-2">evidence_grade</th>
                </tr>
              </thead>
              <tbody>
                {analysis.fpd.mode_forecasts.slice(0, 6).map(f => (
                  <tr key={f.mode_id} className="border-t border-slate-700 text-slate-300">
                    <td className="py-1.5 pr-3 font-mono">{f.mode_id}</td>
                    <td className={cn('py-1.5 pr-3 font-bold', muColor(f.mu_forecast))}>{f.mu_forecast.toFixed(2)}</td>
                    <td className="py-1.5 pr-3">{f.scenario_probability.toFixed(2)}</td>
                    <td className="py-1.5 pr-3">{f.confidence.toFixed(2)}</td>
                    <td className="py-1.5">{evidenceGradeLabels[f.evidence_grade] ?? f.evidence_grade}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {analysis.fpd.pno_transition_forecast && (
          <p className="text-xs text-slate-400 mb-3">{analysis.fpd.pno_transition_forecast}</p>
        )}
        <div className="space-y-1.5">
          {analysis.fpd.early_warnings.map((w, i) => (
            <div key={i} className={cn('flex items-start gap-2.5 rounded-lg px-3 py-2', URGENCY_COLOR[w.urgency])}>
              <span className="text-xs font-semibold uppercase tracking-wide shrink-0 mt-0.5">{urgencyLabels[w.urgency] ?? w.urgency}</span>
              <div>
                <p className="text-xs font-semibold">{w.signal}</p>
                <p className="text-xs opacity-80 mt-0.5">{w.description}</p>
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* LBI */}
      <Section title="LBI — альтернативы улучшения">
        <div className="space-y-2">
          {analysis.lbi.alternatives.map(alt => (
            <div key={alt.alternative_id} className="bg-slate-900 rounded-lg p-3 border border-slate-700">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-mono text-slate-500">{alt.alternative_id}</span>
                <div className="flex gap-2">
                  <span className="text-[10px] text-green-400 bg-green-500/10 px-1.5 rounded">
                    −{(alt.expected_reduction * 100).toFixed(0)}% ошибок
                  </span>
                  <span className="text-[10px] text-blue-400 bg-blue-500/10 px-1.5 rounded">
                    {(alt.feasibility * 100).toFixed(0)}% реализуемость
                  </span>
                </div>
              </div>
              <p className="text-sm text-slate-200 font-semibold mt-1">{alt.title}</p>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">{alt.explanation}</p>
            </div>
          ))}
        </div>
      </Section>

      {/* Red team */}
      {analysis.red_team_notes.length > 0 && (
        <Section title={`Red Team (${analysis.red_team_notes.length})`}>
          <div className="space-y-2">
            {analysis.red_team_notes.map((note, i) => (
              <div key={i} className="flex items-start gap-2.5 bg-slate-900 rounded-lg p-3 border border-amber-700/30">
                <AlertTriangle size={14} className="text-amber-400 shrink-0 mt-0.5" />
                <p className="text-xs text-slate-300 leading-relaxed">{note}</p>
              </div>
            ))}
          </div>
        </Section>
      )}

      {analysis.neutrality_flags.length > 0 && (
        <Section title={`Аудит нейтральности (${analysis.neutrality_flags.length})`}>
          <div className="space-y-2">
            {analysis.neutrality_flags.map((flag, i) => (
              <div key={i} className="flex items-start gap-2.5 bg-slate-900 rounded-lg p-3 border border-slate-600/40">
                <Eye size={14} className="text-slate-400 shrink-0 mt-0.5" />
                <p className="text-xs text-slate-300 leading-relaxed">{flag}</p>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Public Card */}
      <Section title="Публичная карточка объяснения">
        <div className="prose prose-invert prose-sm max-w-none">
          <pre className="whitespace-pre-wrap text-sm text-slate-200 leading-relaxed font-sans bg-slate-900 rounded-lg p-4 border border-green-700/30">
            {analysis.public_explanation}
          </pre>
        </div>
      </Section>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(true)
  return (
    <div className="bg-slate-800 rounded-xl overflow-hidden">
      <button onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-3 text-left">
        <span className="text-xs text-slate-400 uppercase tracking-widest font-semibold">{title}</span>
        {open ? <ChevronUp size={14} className="text-slate-500" /> : <ChevronDown size={14} className="text-slate-500" />}
      </button>
      {open && <div className="px-4 pb-4">{children}</div>}
    </div>
  )
}

function Kpi({ label, value, color, icon }: { label: string; value: string; color: string; icon: React.ReactNode }) {
  return (
    <div className="bg-slate-800 rounded-xl p-3 flex items-start gap-3">
      <span className={color}>{icon}</span>
      <div>
        <div className="text-[10px] text-slate-500 uppercase tracking-widest">{label}</div>
        <div className={cn('text-sm font-bold font-mono mt-0.5', color)}>{value}</div>
      </div>
    </div>
  )
}
