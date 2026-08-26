import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Layers, RefreshCw, Loader2, Zap, ExternalLink, Map,
} from 'lucide-react'
import { api } from '../lib/api'
import { common, layersPage } from '../lib/en'
import type { CrossLayerEvent } from '../lib/types'
import { Section } from '../components/Section'
import { cn } from '../lib/utils'

interface TopologyNode {
  id: string
  label: string
  group: 'eu' | 'national' | 'other'
  role?: string
}

interface EuTopologyData {
  supranational: Array<{ id: string; label: string; role?: string }>
  national_template: Array<{ id: string; label: string }>
  sample_states: Array<{ iso2: string; name: string }>
  other_layers: Array<{ id: string; label: string }>
}

const LAYER_LABELS: Record<string, string> = {
  'institution:eu-parliament': 'EU Parliament',
  'institution:eu-commission': 'EU Commission',
  'institution:eu-council': 'EU Council',
  'institution:eu-court-of-justice': 'EU Court of Justice',
  'institution:eu-transnational-ops': 'EU Transnational Ops',
  'institution:parliament': 'Parliament',
  'institution:executive': 'Executive',
  'institution:judiciary': 'Judiciary',
  'institution:interpol-analog': 'Interpol analog',
  'institution:transnational-ops': 'Transnational ops',
  'institution:ai-speaker': 'AI speaker',
  'institution:party-coalition': 'Party coalition',
  'institution:ai-minister': 'AI minister',
  'institution:ai-pm': 'AI PM',
  'institution:audit': 'Audit',
  'institution:ombudsman': 'Ombudsman',
  'institution:central-bank-analog': 'Central bank analog',
  'institution:regulatory-agency': 'Regulatory agency',
  'institution:national-instance': 'National instance',
  'institution:symbolic-visual': 'Symbolic visual',
}

function layerLabel(id: string): string {
  return LAYER_LABELS[id] ?? id.replace('institution:', '')
}

const SAMPLE_EVENT = {
  story_id: 'mvp-iter2-gui-sample',
  event_type: 'sanctions_coordination',
  jurisdiction_set: ['DE', 'FR', 'PL'],
  coordination_forum: 'EU Council',
  epistemic_label: 'INSTITUTIONAL_MODEL' as const,
}

function EpistemicBadge({ label }: { label: string }) {
  const tone =
    label === 'OPERATIONAL'
      ? 'bg-emerald-900/50 text-emerald-300 border-emerald-800/60'
      : label === 'COMPUTATIONAL_EVIDENCE'
        ? 'bg-violet-900/50 text-violet-300 border-violet-800/60'
        : label === 'PHILOSOPHICAL_INFERENCE'
          ? 'bg-amber-900/50 text-amber-300 border-amber-800/60'
          : 'bg-slate-800 text-slate-300 border-slate-700'
  return (
    <span className={cn('text-[10px] font-mono px-1.5 py-0.5 rounded border', tone)}>
      {label}
    </span>
  )
}

function TopologySchematic({
  nodes,
  highlighted,
  sampleStates,
}: {
  nodes: TopologyNode[]
  highlighted: Set<string>
  sampleStates: Array<{ iso2: string; name: string }>
}) {
  const euNodes = nodes.filter(n => n.group === 'eu')
  const nationalNodes = nodes.filter(n => n.group === 'national')
  const otherNodes = nodes.filter(n => n.group === 'other')

  const renderNode = (node: TopologyNode, compact = false) => {
    const active = highlighted.has(node.id)
    return (
      <div
        key={node.id}
        title={node.role ?? node.id}
        className={cn(
          'rounded-lg border px-2 py-1.5 text-center transition-all',
          compact ? 'text-[10px]' : 'text-xs',
          active
            ? 'border-amber-400/80 bg-amber-900/40 text-amber-100 shadow-[0_0_12px_rgba(251,191,36,0.25)]'
            : 'border-slate-700 bg-slate-900/80 text-slate-400',
        )}
      >
        <div className="font-medium truncate">{node.label}</div>
        {!compact && node.role && (
          <div className="text-[9px] text-slate-500 mt-0.5 line-clamp-2">{node.role}</div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <svg
        viewBox="0 0 400 48"
        className="w-full h-8 text-slate-600"
        aria-hidden
      >
        <rect x="20" y="8" width="360" height="32" rx="6" fill="none" stroke="currentColor" strokeWidth="1" strokeDasharray="4 3" />
        <text x="200" y="28" textAnchor="middle" fill="currentColor" fontSize="10">
          EU supranational tier
        </text>
      </svg>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
        {euNodes.map(n => renderNode(n))}
      </div>

      <svg viewBox="0 0 400 32" className="w-full h-6 text-slate-700" aria-hidden>
        <line x1="200" y1="0" x2="200" y2="32" stroke="currentColor" strokeWidth="1" />
        {[80, 140, 200, 260, 320].map(x => (
          <line key={x} x1="200" y1="16" x2={x} y2="32" stroke="currentColor" strokeWidth="1" opacity="0.5" />
        ))}
      </svg>

      <p className="text-[10px] text-slate-500 uppercase tracking-wider">{layersPage.nationalStates}</p>
      <div className="flex flex-wrap gap-1.5">
        {sampleStates.map(s => (
          <span
            key={s.iso2}
            className="text-[10px] bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-400"
            title={s.name}
          >
            {s.iso2}
          </span>
        ))}
        <span className="text-[10px] text-slate-600 self-center">+16 more</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {nationalNodes.map(n => renderNode(n, true))}
      </div>

      {otherNodes.length > 0 && (
        <>
          <p className="text-[10px] text-slate-500 uppercase tracking-wider pt-2">Cross-cutting layers</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
            {otherNodes.map(n => renderNode(n, true))}
          </div>
        </>
      )}
    </div>
  )
}

export function LayersPage() {
  const [topology, setTopology] = useState<EuTopologyData | null>(null)
  const [layers, setLayers] = useState<string[]>([])
  const [events, setEvents] = useState<CrossLayerEvent[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [posting, setPosting] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    try {
      const [layerRes, eventRes] = await Promise.all([
        api.crossLayerLayers(),
        api.crossLayerList({ limit: 50 }),
      ])
      setLayers(layerRes.layers)
      setEvents(eventRes.events)
      setError('')
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load cross-layer data')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetch('/eu-topology.json')
      .then(r => r.json() as Promise<EuTopologyData>)
      .then(setTopology)
      .catch(() => setTopology(null))
  }, [])

  useEffect(() => {
    void load()
    const t = setInterval(() => void load(), 12000)
    return () => clearInterval(t)
  }, [load])

  const selected = useMemo(
    () => events.find(e => e.event_id === selectedId) ?? null,
    [events, selectedId],
  )

  const highlighted = useMemo(() => {
    const set = new Set<string>()
    if (selected?.activated_layers) {
      for (const id of selected.activated_layers) set.add(id)
    }
    return set
  }, [selected])

  const topologyNodes = useMemo((): TopologyNode[] => {
    if (topology) {
      return [
        ...topology.supranational.map(n => ({
          id: n.id,
          label: n.label,
          group: 'eu' as const,
          role: n.role,
        })),
        ...topology.national_template.map(n => ({
          id: n.id,
          label: n.label,
          group: 'national' as const,
        })),
        ...topology.other_layers.map(n => ({
          id: n.id,
          label: n.label,
          group: 'other' as const,
        })),
      ].filter(n => layers.length === 0 || layers.includes(n.id))
    }
    return layers.map(id => ({
      id,
      label: layerLabel(id),
      group: id.startsWith('institution:eu-') ? 'eu' as const : 'other' as const,
    }))
  }, [topology, layers])

  const sampleStates = topology?.sample_states ?? [
    { iso2: 'DE', name: 'Germany' },
    { iso2: 'FR', name: 'France' },
    { iso2: 'PL', name: 'Poland' },
  ]

  async function activateSample() {
    setPosting(true)
    setError('')
    try {
      const res = await api.crossLayerPost(SAMPLE_EVENT)
      setSelectedId(res.event.event_id ?? null)
      await load()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to post sample event')
    } finally {
      setPosting(false)
    }
  }

  if (loading && layers.length === 0) {
    return (
      <div className="flex items-center justify-center py-24 text-slate-500 gap-2">
        <Loader2 size={18} className="animate-spin" />
        {common.loading}
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6 pb-12">
      <div className="flex flex-wrap justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Layers size={22} className="text-violet-400" />
            {layersPage.title}
          </h1>
          <p className="text-slate-400 text-sm mt-1 max-w-2xl">{layersPage.subtitle}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => void load()}
            className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300"
          >
            <RefreshCw size={14} />
            {common.refresh}
          </button>
          <button
            onClick={() => void activateSample()}
            disabled={posting}
            className="flex items-center gap-1.5 bg-violet-800 hover:bg-violet-700 disabled:opacity-50 border border-violet-700 rounded-lg px-3 py-1.5 text-xs text-violet-100"
          >
            {posting ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
            {posting ? layersPage.samplePosting : layersPage.sampleEvent}
          </button>
        </div>
      </div>

      <p className="text-xs text-slate-500 border border-slate-800 rounded-lg px-3 py-2 leading-relaxed">
        {layersPage.epistemicNote}
      </p>

      {error && (
        <div className="bg-red-900/20 border border-red-700/40 rounded-lg px-4 py-2 text-red-200 text-sm">
          {error}
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        <Section title={layersPage.topologyTitle} icon={<Map size={14} className="text-violet-400" />}>
          <TopologySchematic
            nodes={topologyNodes}
            highlighted={highlighted}
            sampleStates={sampleStates}
          />
          {selected && (
            <p className="text-xs text-amber-300/90 mt-4 border-t border-slate-700/50 pt-3">
              {layersPage.selectEvent} ({selected.activated_layers.length} layers)
            </p>
          )}
        </Section>

        <Section title={layersPage.eventsTitle} icon={<Layers size={14} className="text-cyan-400" />}>
          <p className="text-[10px] text-slate-500 mb-3">{layersPage.eventsSubtitle}</p>
          {events.length > 0 ? (
            <div className="space-y-2 max-h-[420px] overflow-y-auto">
              {events.map(ev => {
                const isSelected = ev.event_id === selectedId
                return (
                  <button
                    key={ev.event_id ?? `${ev.story_id}-${ev.event_type}`}
                    type="button"
                    onClick={() => setSelectedId(ev.event_id ?? null)}
                    className={cn(
                      'w-full text-left rounded-lg border px-3 py-2 transition-colors',
                      isSelected
                        ? 'border-amber-500/60 bg-amber-900/20'
                        : 'border-slate-700 bg-slate-900/60 hover:border-slate-600',
                    )}
                  >
                    <div className="flex flex-wrap items-center gap-2 justify-between">
                      <span className="text-xs font-mono text-slate-300 truncate">
                        {ev.story_id}
                      </span>
                      <EpistemicBadge label={ev.epistemic_label} />
                    </div>
                    <div className="text-[11px] text-slate-500 mt-1">{ev.event_type}</div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {ev.activated_layers.slice(0, 4).map(id => (
                        <span
                          key={id}
                          className="text-[9px] bg-slate-800 rounded px-1.5 py-0.5 text-slate-400"
                        >
                          {layerLabel(id)}
                        </span>
                      ))}
                      {ev.activated_layers.length > 4 && (
                        <span className="text-[9px] text-slate-600">
                          +{ev.activated_layers.length - 4}
                        </span>
                      )}
                    </div>
                    {ev.created_at && (
                      <div className="text-[9px] text-slate-600 mt-1">
                        {new Date(ev.created_at).toLocaleString('en-US')}
                      </div>
                    )}
                  </button>
                )
              })}
            </div>
          ) : (
            <p className="text-sm text-slate-500">{layersPage.noEvents}</p>
          )}
        </Section>
      </div>

      <Section title={layersPage.layersTitle} icon={<Layers size={14} className="text-slate-400" />}>
        <p className="text-[10px] text-slate-500 mb-3">
          GET /api/events/cross-layer/layers — {layers.length} registered layer IDs
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
          {layers.map(id => {
            const active = highlighted.has(id)
            return (
              <div
                key={id}
                className={cn(
                  'text-[10px] rounded-lg border px-2 py-1.5 font-mono truncate',
                  active
                    ? 'border-amber-400/70 bg-amber-900/30 text-amber-200'
                    : 'border-slate-700 bg-slate-900 text-slate-500',
                )}
                title={id}
              >
                {layerLabel(id)}
              </div>
            )
          })}
        </div>
      </Section>

      <footer className="border-t border-slate-800 pt-4 flex flex-wrap items-center gap-2 text-xs text-slate-500">
        <span>Institutional topology contracts:</span>
        <a
          href={layersPage.aboutUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-cyan-400 hover:text-cyan-300"
        >
          {layersPage.aboutLink}
          <ExternalLink size={12} />
        </a>
      </footer>
    </div>
  )
}
