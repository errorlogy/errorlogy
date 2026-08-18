import { useEffect, useState, useMemo } from 'react'
import { Search, Network } from 'lucide-react'
import { api } from '../lib/api'
import { cn } from '../lib/utils'
import type { TaxonomyMode, AlphaEdge } from '../lib/types'

const FAMILY_COLORS: Record<string, string> = {
  CB:  'bg-red-500/20 text-red-300 border-red-500/30',
  SF:  'bg-purple-500/20 text-purple-300 border-purple-500/30',
  MP:  'bg-blue-500/20 text-blue-300 border-blue-500/30',
  PNO: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  GT:  'bg-green-500/20 text-green-300 border-green-500/30',
  ACC: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  EGD: 'bg-teal-500/20 text-teal-300 border-teal-500/30',
  FPD: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
  LBI: 'bg-lime-500/20 text-lime-300 border-lime-500/30',
  CAT: 'bg-pink-500/20 text-pink-300 border-pink-500/30',
  T4D: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  WMS: 'bg-violet-500/20 text-violet-300 border-violet-500/30',
  HM:  'bg-slate-500/20 text-slate-300 border-slate-500/30',
  LCJ: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
  LAC: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  LCC: 'bg-sky-500/20 text-sky-300 border-sky-500/30',
}

function familyColor(family: string) {
  return FAMILY_COLORS[family] ?? 'bg-slate-700 text-slate-300 border-slate-600'
}

export function Taxonomy() {
  const [modes, setModes] = useState<TaxonomyMode[]>([])
  const [edges, setEdges] = useState<AlphaEdge[]>([])
  const [meta, setMeta] = useState<{ version: string; counts: Record<string, number> } | null>(null)
  const [query, setQuery] = useState('')
  const [familyFilter, setFamilyFilter] = useState('ALL')
  const [selected, setSelected] = useState<TaxonomyMode | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [tab, setTab] = useState<'modes' | 'graph'>('modes')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.modes(), api.edges(), api.taxonomy()])
      .then(([m, e, t]) => { setModes(m); setEdges(e); setMeta({ version: t.version, counts: t.counts }) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  async function selectMode(m: TaxonomyMode) {
    setSelected(m)
    setDetailLoading(true)
    try {
      const detail = await api.mode(m.id)
      setSelected(detail)
    } catch {
      /* keep list item */
    } finally {
      setDetailLoading(false)
    }
  }

  const families = useMemo(() => {
    const set = new Set(modes.map(m => m.family))
    return ['ALL', ...Array.from(set).sort()]
  }, [modes])

  const filtered = useMemo(() => {
    const q = query.toLowerCase()
    return modes.filter(m => {
      const matchFam = familyFilter === 'ALL' || m.family === familyFilter
      const matchQ = !q || m.id.toLowerCase().includes(q) || m.name.toLowerCase().includes(q) ||
        (m.definition ?? '').toLowerCase().includes(q)
      return matchFam && matchQ
    })
  }, [modes, query, familyFilter])

  const connectedEdges = useMemo(() => {
    if (!selected) return []
    return edges.filter(e => e.from === selected.id || e.to === selected.id)
  }, [selected, edges])

  return (
    <div className="flex-1 flex overflow-hidden">
      {/* Left panel */}
      <div className="flex flex-col w-80 shrink-0 border-r border-slate-800">
        <div className="p-3 space-y-2 border-b border-slate-800">
          <div className="flex gap-2">
            <button onClick={() => setTab('modes')}
              className={cn('flex-1 text-xs py-1.5 rounded-lg font-semibold transition-colors',
                tab === 'modes' ? 'bg-red-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-slate-200')}>
              Modes ({filtered.length})
            </button>
            <button onClick={() => setTab('graph')}
              className={cn('flex-1 text-xs py-1.5 rounded-lg font-semibold transition-colors flex items-center justify-center gap-1.5',
                tab === 'graph' ? 'bg-red-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-slate-200')}>
              <Network size={12} /> Граф ({edges.length})
            </button>
          </div>

          {tab === 'modes' && (
            <>
              <div className="relative">
                <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
                <input value={query} onChange={e => setQuery(e.target.value)}
                  placeholder="Поиск режимов…"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-red-500" />
              </div>
              <div className="flex flex-wrap gap-1 max-h-24 overflow-y-auto">
                {families.map(f => (
                  <button key={f} onClick={() => setFamilyFilter(f)}
                    className={cn('text-[10px] px-1.5 py-0.5 rounded border transition-colors',
                      familyFilter === f
                        ? 'bg-red-600 border-red-600 text-white'
                        : f === 'ALL'
                          ? 'bg-slate-700 border-slate-600 text-slate-300 hover:bg-slate-600'
                          : cn(familyColor(f), 'hover:opacity-80'))}>
                    {f}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto">
          {loading && (
            <p className="text-xs text-slate-500 p-4 text-center">Загрузка таксономии…</p>
          )}
          {tab === 'modes' ? (
            <div className="divide-y divide-slate-800/50">
              {filtered.map(m => (
                <button key={m.id} onClick={() => selectMode(m)}
                  className={cn('w-full text-left px-3 py-2.5 transition-colors hover:bg-slate-800/60',
                    selected?.id === m.id ? 'bg-slate-800 border-l-2 border-l-red-500 pl-2.5' : '')}>
                  <div className="flex items-center gap-1.5">
                    <span className={cn('text-[10px] font-mono px-1 py-0.5 rounded border shrink-0', familyColor(m.family))}>
                      {m.id}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 mt-1 leading-snug">{m.name}</p>
                </button>
              ))}
              {!loading && filtered.length === 0 && (
                <p className="text-slate-500 text-xs p-4 text-center">Нет подходящих режимов.</p>
              )}
            </div>
          ) : (
            <div className="divide-y divide-slate-800/50">
              {edges.map((e, i) => (
                <div key={i} className="px-3 py-2 flex items-center gap-2 text-[10px] font-mono">
                  <span className={cn('px-1 py-0.5 rounded border', familyColor(e.from.replace(/-\d+$/, '').replace(/\d+$/, '')))}>
                    {e.from}
                  </span>
                  <span className={cn('shrink-0 font-bold', e.weight > 0 ? 'text-green-400' : 'text-red-400')}>
                    {e.weight > 0 ? '+' : ''}{e.weight.toFixed(2)}
                  </span>
                  <span className={cn('px-1 py-0.5 rounded border', familyColor(e.to.replace(/-\d+$/, '').replace(/\d+$/, '')))}>
                    {e.to}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Right: detail panel */}
      <div className="flex-1 overflow-y-auto p-6">
        {meta && (
          <div className="mb-4 flex flex-wrap gap-2 text-[10px]">
            <span className="px-2 py-1 bg-slate-800 text-slate-300 rounded font-mono">v{meta.version}</span>
            {Object.entries(meta.counts).map(([k, n]) => (
              <span key={k} className="px-2 py-1 bg-slate-800/60 text-slate-400 rounded">
                {k}: {n}
              </span>
            ))}
          </div>
        )}
        {selected ? (
          <div className="space-y-5 max-w-xl">
            {detailLoading && (
              <p className="text-xs text-slate-500">Загрузка деталей режима…</p>
            )}
            <div>
              <span className={cn('text-xs font-mono px-2 py-1 rounded border', familyColor(selected.family))}>
                {selected.id}
              </span>
              <h2 className="text-xl font-bold text-white mt-2">{selected.name}</h2>
              <div className="flex gap-3 mt-1 text-xs text-slate-500">
                <span>Семейство: <span className="text-slate-400">{selected.family}</span></span>
                {selected.layer && <span>Слой: <span className="text-slate-400">{selected.layer}</span></span>}
                {selected.category && <span>Категория: <span className="text-slate-400">{selected.category}</span></span>}
              </div>
            </div>

            {selected.definition && (
              <div className="bg-slate-800 rounded-xl p-4">
                <p className="text-xs text-slate-500 uppercase tracking-widest mb-2">Определение</p>
                <p className="text-sm text-slate-300 leading-relaxed">{selected.definition}</p>
              </div>
            )}

            {selected.operational_signal && (
              <div className="bg-slate-800 rounded-xl p-4">
                <p className="text-xs text-slate-500 uppercase tracking-widest mb-2">Операционный сигнал</p>
                <p className="text-sm text-slate-300 leading-relaxed">{selected.operational_signal}</p>
              </div>
            )}

            {selected.meta_dimensions && selected.meta_dimensions.length > 0 && (
              <div className="bg-slate-800 rounded-xl p-4">
                <p className="text-xs text-slate-500 uppercase tracking-widest mb-2">Meta-измерения</p>
                <div className="flex gap-2 flex-wrap">
                  {selected.meta_dimensions.map(d => (
                    <span key={d} className="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-300 font-mono">{d}</span>
                  ))}
                </div>
              </div>
            )}

            {connectedEdges.length > 0 && (
              <div className="bg-slate-800 rounded-xl p-4">
                <p className="text-xs text-slate-500 uppercase tracking-widest mb-3">
                  Alpha-связи ({connectedEdges.length})
                </p>
                <div className="space-y-1.5">
                  {connectedEdges.map((e, i) => {
                    const isOut = e.from === selected.id
                    const other = isOut ? e.to : e.from
                    const otherFamily = other.replace(/-\d+$/, '').replace(/\d+$/, '')
                    return (
                      <div key={i} className="flex items-center gap-2 text-xs">
                        <span className={cn('text-[10px] font-semibold shrink-0 w-6',
                          isOut ? 'text-blue-400' : 'text-purple-400')}>
                          {isOut ? 'OUT' : 'IN'}
                        </span>
                        <span className={cn('font-mono text-[10px] px-1 py-0.5 rounded border cursor-pointer hover:opacity-80',
                          familyColor(otherFamily))}
                          onClick={() => { const m = modes.find(x => x.id === other); if (m) void selectMode(m) }}>
                          {other}
                        </span>
                        <span className={cn('font-mono font-bold', e.weight > 0 ? 'text-green-400' : 'text-red-400')}>
                          {e.weight > 0 ? '+' : ''}{e.weight.toFixed(3)}
                        </span>
                        {e.confidence !== undefined && (
                          <span className="text-slate-500 text-[10px]">conf {e.confidence.toFixed(2)}</span>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center text-slate-600 space-y-2">
              <Network size={40} className="mx-auto" />
              <p className="text-sm">Выберите режим</p>
              <p className="text-xs">{modes.length} режимов · {edges.length} alpha рёбер</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
