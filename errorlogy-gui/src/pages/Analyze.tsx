import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Play, Loader2, AlertTriangle, Calculator, Sparkles, GitCompare, BookOpen } from 'lucide-react'
import { api, checkApiHealth, isNetworkError } from '../lib/api'
import { saveCase } from '../lib/caseStore'
import { AGENT_LABELS } from '../lib/pipeline'
import { analyzeModes, muNote } from '../lib/en'
import type { CaseAnalysis, AgentStepMetric } from '../lib/types'

const CHALLENGER_PRESET = {
  caseId: 'US-NASA-1986-CHALLENGER-01',
  title: 'STS-51L Space Shuttle Challenger',
  country: 'USA',
  year: '1986',
  text: `NASA managers approved the Challenger launch despite engineer dissent about O-ring performance in cold temperatures. Thiokol engineers recommended no launch below 53F. Management reversed position after schedule pressure. Groupthink and authority bias were documented.`,
}

export function Analyze() {
  const navigate = useNavigate()
  const [caseId, setCaseId] = useState('MY-CASE-001')
  const [title, setTitle]   = useState('')
  const [country, setCountry] = useState('')
  const [year, setYear]     = useState('')
  const [text, setText]     = useState('')
  const [engineOnly, setEngineOnly] = useState(false)
  const [structureOnly, setStructureOnly] = useState(false)
  const [dualRun, setDualRun] = useState(false)
  const [running, setRunning] = useState(false)
  const [liveSteps, setLiveSteps] = useState<AgentStepMetric[]>([])
  const [error, setError]   = useState('')
  const [apiOnline, setApiOnline] = useState<boolean | null>(null)
  const [loadingDemo, setLoadingDemo] = useState(false)

  useEffect(() => {
    checkApiHealth().then(h => setApiOnline(!!h))
  }, [])

  function loadChallenger() {
    setCaseId(CHALLENGER_PRESET.caseId)
    setTitle(CHALLENGER_PRESET.title)
    setCountry(CHALLENGER_PRESET.country)
    setYear(CHALLENGER_PRESET.year)
    setText(CHALLENGER_PRESET.text)
  }

  async function loadDemoResult() {
    setLoadingDemo(true)
    setError('')
    try {
      const result = await api.loadDemoAnalysis()
      sessionStorage.setItem('last_analysis', JSON.stringify(result))
      saveCase(result, { title: CHALLENGER_PRESET.title, country: CHALLENGER_PRESET.country, year: 1986 })
      navigate(`/result/${encodeURIComponent(result.case_id)}`)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load demo')
    } finally {
      setLoadingDemo(false)
    }
  }

  async function run() {
    if (!text.trim()) { setError('Paste source text first'); return }
    if (dualRun && (engineOnly || structureOnly)) {
      setError('Dual-run runs engine + full MAS — disable other modes')
      return
    }
    setError('')
    setRunning(true)
    setLiveSteps([])

    try {
      const params = {
        case_id: caseId || 'CASE-001',
        raw_text: text,
        title, country,
        year: year ? parseInt(year) : undefined,
        engine_only: engineOnly && !dualRun,
        structure_only: structureOnly && !dualRun,
        dual_run: dualRun,
      }

      const upsertStep = (step: AgentStepMetric) => {
        setLiveSteps(prev => {
          const idx = prev.findIndex(s => s.agent_id === step.agent_id)
          if (idx >= 0) {
            const next = [...prev]
            next[idx] = step
            return next
          }
          return [...prev, step]
        })
      }

      let result: CaseAnalysis
      try {
        result = await api.analyzeStream(params, upsertStep)
      } catch (streamErr) {
        if (isNetworkError(streamErr)) {
          result = await api.analyze(params)
        } else {
          throw streamErr
        }
      }
      if (result.metadata?.pipeline_metrics?.steps?.length) {
        setLiveSteps(result.metadata.pipeline_metrics.steps)
      }
      sessionStorage.setItem('last_analysis', JSON.stringify(result))
      if (country) saveCase(result, { title, country, year: year ? parseInt(year) : undefined })
      navigate(`/result/${encodeURIComponent(result.case_id)}`)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Analysis failed')
    } finally {
      setRunning(false)
    }
  }

  const modeLabel = dualRun
    ? analyzeModes.dualRun
    : structureOnly
      ? analyzeModes.structureOnly
      : engineOnly
        ? analyzeModes.engineOnly
        : analyzeModes.full

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white">Governance case analysis</h1>
          <p className="text-slate-400 text-sm mt-2 max-w-2xl leading-relaxed">
            Errorlogy pipeline (spec) returns: taxonomy modes with μ, WMS/CEP, PNO, ACC, EGD, T4D timeline,
            CAT hypothesis, FPD forecast, and public card. Results on Result and Forecast pages.
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {apiOnline === false && (
            <button onClick={loadDemoResult} disabled={loadingDemo}
              className="text-xs text-slate-300 hover:text-white border border-slate-600 rounded-lg px-3 py-1.5 flex items-center gap-1.5">
              {loadingDemo ? <Loader2 size={12} className="animate-spin" /> : <BookOpen size={12} />}
              Challenger demo (offline)
            </button>
          )}
          <button onClick={loadChallenger} className="text-xs text-slate-400 hover:text-red-400 border border-slate-700 rounded-lg px-3 py-1.5">
            Load Challenger
          </button>
        </div>
      </div>

      {apiOnline === false && (
        <div className="bg-amber-900/20 border border-amber-700/50 rounded-lg p-3 text-amber-200 text-sm">
          Backend offline — start FastAPI on :8000 or use Challenger demo to preview UI.
        </div>
      )}

      <p className="text-xs text-slate-500 border border-slate-800 rounded-lg px-3 py-2">{muNote}</p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: 'case_id', value: caseId, set: setCaseId, placeholder: 'US-NASA-1986-CHALLENGER-01' },
          { label: 'Title', value: title, set: setTitle, placeholder: 'Event title' },
          { label: 'Country', value: country, set: setCountry, placeholder: 'USA (for map)' },
          { label: 'Year', value: year, set: setYear, placeholder: '1986' },
        ].map(f => (
          <div key={f.label}>
            <label className="text-xs text-slate-500 uppercase tracking-widest block mb-1">{f.label}</label>
            <input value={f.value} onChange={e => f.set(e.target.value)} placeholder={f.placeholder}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-red-500" />
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-3">
        <label className={`flex items-center gap-3 cursor-pointer bg-slate-800/60 border rounded-xl p-3 ${engineOnly && !dualRun ? 'border-red-600' : 'border-slate-700'}`}>
          <input type="checkbox" checked={engineOnly} disabled={dualRun || structureOnly}
            onChange={e => { setEngineOnly(e.target.checked); if (e.target.checked) setStructureOnly(false) }}
            className="rounded border-slate-600 text-red-600 focus:ring-red-500" />
          <Calculator size={16} className="text-red-400" />
          <div>
            <div className="text-sm text-slate-200 font-medium">Engine only</div>
            <div className="text-[10px] text-slate-500">Heuristic, no LLM</div>
          </div>
        </label>

        <label className={`flex items-center gap-3 cursor-pointer bg-slate-800/60 border rounded-xl p-3 ${structureOnly ? 'border-amber-600' : 'border-slate-700'}`}>
          <input type="checkbox" checked={structureOnly} disabled={dualRun || engineOnly}
            onChange={e => { setStructureOnly(e.target.checked); if (e.target.checked) setEngineOnly(false) }}
            className="rounded border-slate-600 text-amber-600 focus:ring-amber-500" />
          <Sparkles size={16} className="text-amber-400" />
          <div>
            <div className="text-sm text-slate-200 font-medium">LightweightScout</div>
            <div className="text-[10px] text-slate-500">1 LLM (Scout) + engine</div>
          </div>
        </label>

        <label className={`flex items-center gap-3 cursor-pointer bg-slate-800/60 border rounded-xl p-3 ${dualRun ? 'border-purple-600' : 'border-slate-700'}`}>
          <input type="checkbox" checked={dualRun}
            onChange={e => { setDualRun(e.target.checked); if (e.target.checked) { setEngineOnly(false); setStructureOnly(false) } }}
            className="rounded border-slate-600 text-purple-600 focus:ring-purple-500" />
          <GitCompare size={16} className="text-purple-400" />
          <div>
            <div className="text-sm text-slate-200 font-medium">Dual-run</div>
            <div className="text-[10px] text-slate-500">Compare engine vs full MAS</div>
          </div>
        </label>
      </div>

      <div>
        <label className="text-xs text-slate-500 uppercase tracking-widest block mb-1">Source text</label>
        <textarea value={text} onChange={e => setText(e.target.value)}
          rows={12} placeholder="Paste governance event description…"
          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-red-500 resize-none font-mono leading-relaxed" />
      </div>

      {error && (
        <div className="flex items-start gap-2 bg-red-900/30 border border-red-700 rounded-lg p-3 text-red-300 text-sm">
          <AlertTriangle size={16} className="shrink-0 mt-0.5" />{error}
        </div>
      )}

      {running && (
        <div className="bg-slate-800 rounded-xl p-4">
          <p className="text-xs text-slate-500 uppercase tracking-widest mb-3">
            {modeLabel} — waiting for API…
          </p>
          {liveSteps.length > 0 ? (
            <div className="space-y-1.5">
              {liveSteps.map(s => (
                <div key={s.agent_id} className="flex items-center justify-between text-xs">
                  <span className="text-slate-300 flex items-center gap-2">
                    {s.status === 'running' && <Loader2 size={12} className="animate-spin text-amber-400" />}
                    {AGENT_LABELS[s.agent_id] ?? s.agent_id}
                  </span>
                  <span className="text-slate-500 font-mono">
                    {s.status === 'running' ? '…' : `${s.duration_ms.toFixed(0)}ms`}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center gap-2 text-slate-400 text-sm">
              <Loader2 size={16} className="animate-spin" />
              Pipeline running (full MAS may take 1–2 min)…
            </div>
          )}
        </div>
      )}

      <button onClick={run} disabled={running}
        className="flex items-center gap-2 bg-red-600 hover:bg-red-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl px-6 py-3 font-semibold transition-colors">
        {running ? <Loader2 size={18} className="animate-spin" /> : <Play size={18} />}
        {running ? 'Analyzing…' : `Run — ${modeLabel}`}
      </button>
    </div>
  )
}
