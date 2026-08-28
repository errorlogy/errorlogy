import { useCallback, useEffect, useState } from 'react'
import {
  GitFork, RefreshCw, Loader2, Search, ChevronRight,
} from 'lucide-react'
import { api } from '../lib/api'
import { common, discoursePage } from '../lib/en'
import type { MemeticLineageResponse } from '../lib/types'
import { Section } from '../components/Section'
import { cn } from '../lib/utils'

function EpistemicBadge() {
  return (
    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded border bg-slate-800 text-slate-300 border-slate-700">
      INSTITUTIONAL_MODEL
    </span>
  )
}

function LineageTree({ lineage }: { lineage: string[] }) {
  if (lineage.length === 0) {
    return <p className="text-sm text-slate-500">{discoursePage.noLineage}</p>
  }
  return (
    <ol className="space-y-1">
      {lineage.map((id, idx) => (
        <li key={`${id}-${idx}`} className="flex items-center gap-2 text-sm">
          {idx > 0 && <ChevronRight size={12} className="text-slate-600 shrink-0" />}
          <span
            className={cn(
              'font-mono text-xs rounded px-2 py-1 border',
              idx === lineage.length - 1
                ? 'border-amber-500/60 bg-amber-900/20 text-amber-200'
                : 'border-slate-700 bg-slate-900 text-slate-400',
            )}
          >
            {id}
          </span>
          {idx === 0 && (
            <span className="text-[10px] text-slate-600 uppercase">{discoursePage.root}</span>
          )}
          {idx === lineage.length - 1 && idx > 0 && (
            <span className="text-[10px] text-slate-600 uppercase">{discoursePage.leaf}</span>
          )}
        </li>
      ))}
    </ol>
  )
}

export function DiscoursePage() {
  const [storyId, setStoryId] = useState('')
  const [queryId, setQueryId] = useState('')
  const [data, setData] = useState<MemeticLineageResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async (id: string) => {
    const trimmed = id.trim()
    if (!trimmed) return
    setLoading(true)
    setError('')
    try {
      const res = await api.memeticLineage(trimmed)
      setData(res)
      setQueryId(trimmed)
    } catch (e: unknown) {
      setData(null)
      setError(e instanceof Error ? e.message : 'Failed to load lineage')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load('mvp-discourse-sample')
    setStoryId('mvp-discourse-sample')
  }, [load])

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    void load(storyId)
  }

  const forkEdges = data?.graph.edges.filter(e => e.edge_type === 'narrative_fork') ?? []
  const symbolicEdges = data?.graph.edges.filter(e => e.edge_type === 'symbolic_variant') ?? []

  return (
    <div className="p-6 space-y-6 pb-12">
      <div className="flex flex-wrap justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <GitFork size={22} className="text-violet-400" />
            {discoursePage.title}
          </h1>
          <p className="text-slate-400 text-sm mt-1 max-w-2xl">{discoursePage.subtitle}</p>
        </div>
        <div className="flex items-center gap-2">
          <EpistemicBadge />
          <button
            type="button"
            onClick={() => queryId && void load(queryId)}
            disabled={loading || !queryId}
            className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300"
          >
            {loading ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
            {common.refresh}
          </button>
        </div>
      </div>

      <p className="text-xs text-slate-500 border border-slate-800 rounded-lg px-3 py-2 leading-relaxed">
        {discoursePage.epistemicNote}
      </p>

      <form onSubmit={handleSubmit} className="flex flex-wrap gap-2 items-end">
        <label className="flex-1 min-w-[200px]">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">
            {discoursePage.storyIdLabel}
          </span>
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              value={storyId}
              onChange={e => setStoryId(e.target.value)}
              placeholder={discoursePage.storyIdPlaceholder}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-violet-600"
            />
          </div>
        </label>
        <button
          type="submit"
          disabled={loading || !storyId.trim()}
          className="bg-violet-800 hover:bg-violet-700 disabled:opacity-50 border border-violet-700 rounded-lg px-4 py-2 text-xs text-violet-100"
        >
          {loading ? discoursePage.loadingLineage : discoursePage.loadLineage}
        </button>
      </form>

      {error && (
        <div className="bg-red-900/20 border border-red-700/40 rounded-lg px-4 py-2 text-red-200 text-sm">
          {error}
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        <Section title={discoursePage.lineageTitle} icon={<GitFork size={14} className="text-amber-400" />}>
          <p className="text-[10px] text-slate-500 mb-3">
            GET /api/events/memetic/lineage/{queryId || '{story_id}'}
          </p>
          {data ? (
            <LineageTree lineage={data.lineage} />
          ) : (
            <p className="text-sm text-slate-500">{discoursePage.noData}</p>
          )}
        </Section>

        <Section title={discoursePage.forksTitle} icon={<GitFork size={14} className="text-cyan-400" />}>
          {data && data.descendants.length > 0 ? (
            <ul className="space-y-1">
              {data.descendants.map(d => (
                <li key={d}>
                  <button
                    type="button"
                    onClick={() => {
                      setStoryId(d)
                      void load(d)
                    }}
                    className="text-xs font-mono text-cyan-300 hover:text-cyan-200 underline-offset-2 hover:underline"
                  >
                    {d}
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-500">{discoursePage.noForks}</p>
          )}
        </Section>
      </div>

      {data && data.graph.edges.length > 0 && (
        <Section title={discoursePage.edgesTitle} icon={<GitFork size={14} className="text-slate-400" />}>
          <div className="space-y-3">
            {forkEdges.length > 0 && (
              <div>
                <p className="text-[10px] text-slate-500 uppercase mb-2">{discoursePage.narrativeForks}</p>
                <div className="space-y-1">
                  {forkEdges.map(e => (
                    <div key={`${e.parent}-${e.child}`} className="text-xs font-mono text-slate-400">
                      {e.parent} → {e.child}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {symbolicEdges.length > 0 && (
              <div>
                <p className="text-[10px] text-slate-500 uppercase mb-2">{discoursePage.symbolicVariants}</p>
                <div className="space-y-1">
                  {symbolicEdges.map(e => (
                    <div key={`${e.parent}-${e.child}-sym`} className="text-xs font-mono text-slate-400">
                      {e.parent} → {e.child}
                      {e.carrier != null && (
                        <span className="text-slate-600 ml-2">({String(e.carrier)})</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Section>
      )}
    </div>
  )
}
