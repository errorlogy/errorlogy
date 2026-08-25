import { useCallback, useEffect, useState } from 'react'

import { useNavigate } from 'react-router-dom'

import { Activity, Bot, Cpu, RefreshCw, Zap } from 'lucide-react'

import { api } from '../lib/api'

import { common } from '../lib/en'

import type { MasMetricsSummary, PipelineRunMetric } from '../lib/types'

import { cn } from '../lib/utils'



export function MasPage() {

  const navigate = useNavigate()

  const [data, setData] = useState<MasMetricsSummary | null>(null)

  const [error, setError] = useState('')

  const [loading, setLoading] = useState(true)



  const load = useCallback(async () => {

    try {

      setData(await api.masMetrics())

      setError('')

    } catch {

      setError(common.backendOffline)

    } finally {

      setLoading(false)

    }

  }, [])



  useEffect(() => {

    load()

    const id = setInterval(load, 5000)

    return () => clearInterval(id)

  }, [load])



  const last = data?.last_run

  const sessionFromStorage = (() => {

    try {

      const raw = sessionStorage.getItem('last_analysis')

      if (!raw) return null

      const a = JSON.parse(raw)

      return a.metadata?.pipeline_metrics as PipelineRunMetric | undefined

    } catch {

      return null

    }

  })()



  const displayRun = last?.steps?.length ? last : sessionFromStorage



  return (

    <div className="flex-1 overflow-y-auto p-6 space-y-6">

      <div className="flex items-center justify-between">

        <div>

          <h1 className="text-xl font-bold text-white flex items-center gap-2">

            <Activity size={22} className="text-red-400" />

            MAS Orchestrator

          </h1>

          <p className="text-slate-500 text-xs mt-1">

            Agent metrics — engine vs LLM · time · tokens · session history

          </p>

        </div>

        <button onClick={load} className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800" title="Refresh">

          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />

        </button>

      </div>



      {error && (

        <div className="bg-red-900/30 border border-red-700 rounded-lg p-3 text-red-300 text-sm">{error}</div>

      )}



      {data && (

        <>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">

            <Kpi label="Engine" value={data.engine_version} icon={<Cpu size={16} />} accent="text-red-400" />

            <Kpi label="Runs (session)" value={String(data.runs_in_session)} icon={<Zap size={16} />} accent="text-amber-400" />

            <Kpi label="LLM calls" value={String(data.total_llm_calls)} icon={<Bot size={16} />} accent="text-blue-400" />

            <Kpi label="Engine steps" value={String(data.total_engine_calls)} icon={<Cpu size={16} />} accent="text-purple-400" />

            <Kpi label="Tokens in/out" value={`${data.total_input_tokens}/${data.total_output_tokens}`} icon={<Activity size={16} />} accent="text-green-400" />

          </div>



          <div className="grid md:grid-cols-3 gap-4">

            <div className="md:col-span-2 bg-slate-800 rounded-xl p-4">

              <p className="text-xs text-slate-500 uppercase tracking-widest mb-3">

                Last pipeline run {displayRun ? `· ${displayRun.case_id}` : ''}

              </p>

              {displayRun?.steps?.length ? (

                <StepTimeline run={displayRun} />

              ) : (

                <p className="text-slate-500 text-sm">No runs yet — use Analyze.</p>

              )}

            </div>



            <div className="bg-slate-800 rounded-xl p-4">

              <p className="text-xs text-slate-500 uppercase tracking-widest mb-3">Agent registry (14)</p>

              <div className="space-y-1.5">

                {data.agent_registry.map(a => (

                  <div key={a.id} className="flex items-center justify-between text-xs">

                    <span className="text-slate-300">{a.label}</span>

                    <span className={cn(

                      'px-1.5 py-0.5 rounded font-mono text-[10px]',

                      a.kind === 'engine' ? 'bg-red-900/40 text-red-300' : 'bg-amber-900/30 text-amber-300',

                    )}>{a.kind}</span>

                  </div>

                ))}

              </div>

            </div>

          </div>



          {data.recent_runs.length > 0 && (

            <div className="bg-slate-800 rounded-xl p-4">

              <p className="text-xs text-slate-500 uppercase tracking-widest mb-3">Recent runs</p>

              <div className="overflow-x-auto">

                <table className="w-full text-xs">

                  <thead>

                    <tr className="text-slate-500 text-left">

                      <th className="pb-2 pr-4">Case</th>

                      <th className="pb-2 pr-4">Mode</th>

                      <th className="pb-2 pr-4">Duration</th>

                      <th className="pb-2 pr-4">Engine</th>

                      <th className="pb-2 pr-4">LLM</th>

                      <th className="pb-2">Tokens</th>

                    </tr>

                  </thead>

                  <tbody>

                    {data.recent_runs.map(r => (

                      <tr

                        key={r.run_id}

                        onClick={() => r.case_id && navigate(`/result/${encodeURIComponent(r.case_id)}`)}

                        className={cn(

                          'border-t border-slate-700 text-slate-300',

                          r.case_id && 'cursor-pointer hover:bg-slate-700/50',

                        )}

                      >

                        <td className="py-2 pr-4 font-mono">{r.case_id}</td>

                        <td className="py-2 pr-4">{r.engine_only ? common.engine : common.full}</td>

                        <td className="py-2 pr-4">{(r.totals.total_duration_ms / 1000).toFixed(1)}s</td>

                        <td className="py-2 pr-4">{r.totals.engine_steps}</td>

                        <td className="py-2 pr-4">{r.totals.llm_steps}</td>

                        <td className="py-2">{r.totals.input_tokens}+{r.totals.output_tokens}</td>

                      </tr>

                    ))}

                  </tbody>

                </table>

              </div>

            </div>

          )}

        </>

      )}

    </div>

  )

}



function StepTimeline({ run }: { run: PipelineRunMetric }) {

  const maxMs = Math.max(...run.steps.map(s => s.duration_ms), 1)

  const t = run.totals



  return (

    <div className="space-y-3">

      <div className="flex gap-4 text-[10px] text-slate-500">

        <span>Total {(t.total_duration_ms / 1000).toFixed(2)}s</span>

        <span className="text-red-400">engine {(t.engine_duration_ms / 1000).toFixed(2)}s</span>

        <span className="text-amber-400">LLM {(t.llm_duration_ms / 1000).toFixed(2)}s</span>

        {t.input_tokens > 0 && <span>tokens {t.input_tokens}→{t.output_tokens}</span>}

      </div>

      <div className="space-y-2">

        {run.steps.map((s, i) => (

          <div key={`${s.agent_id}-${i}`} className="flex items-center gap-3">

            <span className="w-24 text-[10px] text-slate-400 truncate font-mono">{s.agent_id}</span>

            <div className="flex-1 h-5 bg-slate-900 rounded overflow-hidden relative">

              <div

                className={cn(

                  'h-full rounded transition-all',

                  s.kind === 'engine' ? 'bg-red-600/70' : 'bg-amber-500/70',

                )}

                style={{ width: `${Math.max(4, (s.duration_ms / maxMs) * 100)}%` }}

              />

            </div>

            <span className="w-14 text-[10px] text-slate-500 text-right">{s.duration_ms.toFixed(0)}ms</span>

            {s.kind === 'llm' && (

              <span className="w-28 text-[10px] text-slate-600 truncate">{s.provider}/{s.model}</span>

            )}

          </div>

        ))}

      </div>

    </div>

  )

}



function Kpi({ label, value, icon, accent }: { label: string; value: string; icon: React.ReactNode; accent: string }) {

  return (

    <div className="bg-slate-800 rounded-xl p-3">

      <div className={cn('mb-1', accent)}>{icon}</div>

      <div className="text-[10px] text-slate-500 uppercase">{label}</div>

      <div className={cn('text-sm font-bold mt-0.5', accent)}>{value}</div>

    </div>

  )

}

