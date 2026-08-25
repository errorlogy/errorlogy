import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  RefreshCw, Rss, Upload, Loader2, Radio, Play, FileText,
} from 'lucide-react'
import { api } from '../lib/api'
import { common, dataStreams, nav } from '../lib/en'
import type { IngestDocumentSummary, IngestSignalPoint, IngestStatus } from '../lib/types'
import { DataFlowDiagram } from '../components/DataFlowDiagram'
import { Section, Stat } from '../components/Section'

export function DataStreamsPage() {
  const [status, setStatus] = useState<IngestStatus | null>(null)
  const [documents, setDocuments] = useState<IngestDocumentSummary[]>([])
  const [signals, setSignals] = useState<IngestSignalPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [fetching, setFetching] = useState(false)
  const [ingesting, setIngesting] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState('')
  const [manualTitle, setManualTitle] = useState('')
  const [manualCountry, setManualCountry] = useState('')
  const [manualText, setManualText] = useState('')

  const load = useCallback(async () => {
    try {
      const [st, docRes, sigRes] = await Promise.all([
        api.ingestStatus(),
        api.ingestDocuments(undefined, 20),
        api.ingestSignals({ limit: 15 }),
      ])
      setStatus(st)
      setDocuments(docRes.documents)
      setSignals(sigRes.signals)
      setError('')
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Не удалось загрузить статус')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
    const t = setInterval(() => void load(), 12000)
    return () => clearInterval(t)
  }, [load])

  async function runFetch(fn: () => Promise<unknown>) {
    setFetching(true)
    setError('')
    try {
      await fn()
      await load()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка fetch')
    } finally {
      setFetching(false)
    }
  }

  async function submitManual() {
    if (!manualText.trim()) return
    setIngesting(true)
    setError('')
    try {
      await api.ingestDocument({
        source: 'manual',
        source_type: 'manual',
        title: manualTitle,
        country: manualCountry,
        text: manualText,
        auto_analyze: true,
        structure_only: true,
      })
      setManualText('')
      setManualTitle('')
      await load()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка ingest')
    } finally {
      setIngesting(false)
    }
  }

  async function processPending() {
    setProcessing(true)
    try {
      await api.ingestProcessPending(10, true)
      await load()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка обработки')
    } finally {
      setProcessing(false)
    }
  }

  if (loading && !status) {
    return (
      <div className="flex items-center justify-center py-24 text-slate-500 gap-2">
        <Loader2 size={18} className="animate-spin" />
        {common.loading}
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-wrap justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Radio size={22} className="text-green-400" />
            {dataStreams.title}
          </h1>
          <p className="text-slate-400 text-sm mt-1 max-w-2xl">{dataStreams.subtitle}</p>
        </div>
        <button
          onClick={() => void load()}
          className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300"
        >
          <RefreshCw size={14} />
          {common.refresh}
        </button>
      </div>

      <DataFlowDiagram
        steps={dataStreams.pipelineSteps.map((s, i) => ({
          ...s,
          highlight: i === 2,
        }))}
      />

      {error && (
        <div className="bg-red-900/20 border border-red-700/40 rounded-lg px-4 py-2 text-red-200 text-sm">{error}</div>
      )}

      {status && (
        <Section title="Статус ingest" icon={<Radio size={14} className="text-green-400" />}>
          <div className="grid sm:grid-cols-4 gap-3 mb-4">
            <Stat label="Документов" value={status.documents_total} />
            <Stat label="Ожидают" value={status.documents_pending} />
            <Stat label="Проанализировано" value={status.documents_analyzed} />
            <Stat label="Сигналов" value={status.signals_total} />
          </div>
          {status.last_ingest_at && (
            <p className="text-xs text-slate-500 mb-3">
              Последний ingest: {new Date(status.last_ingest_at).toLocaleString('ru-RU')}
            </p>
          )}
          <div className="flex flex-wrap gap-2 mb-4">
            {Object.entries(status.sources).map(([src, n]) => (
              <span key={src} className="text-xs bg-slate-900 rounded px-2 py-1 border border-slate-700">
                {src}: <strong className="text-slate-200">{n}</strong>
              </span>
            ))}
          </div>
          {status.fetchers && (
            <div className="flex flex-wrap gap-2 text-[10px]">
              {Object.entries(status.fetchers).map(([k, on]) => (
                <span
                  key={k}
                  className={`px-2 py-0.5 rounded font-mono ${on ? 'bg-emerald-900/40 text-emerald-300' : 'bg-slate-800 text-slate-500'}`}
                >
                  {k} {on ? 'ON' : 'off'}
                </span>
              ))}
            </div>
          )}
        </Section>
      )}

      <Section title="Загрузка данных" icon={<Rss size={14} className="text-cyan-400" />}>
        <div className="flex flex-wrap gap-2 mb-4">
          <button
            onClick={() => void runFetch(() => api.ingestFetchRss({ max_items_per_feed: 5, auto_analyze: true }))}
            disabled={fetching}
            className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-300 disabled:opacity-50"
          >
            {fetching ? <Loader2 size={14} className="animate-spin" /> : <Rss size={14} />}
            Fetch RSS
          </button>
          <button
            onClick={() => void processPending()}
            disabled={processing}
            className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-300 disabled:opacity-50"
          >
            {processing ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
            Обработать pending
          </button>
        </div>

        <div className="space-y-3 border-t border-slate-700/50 pt-4">
          <p className="text-xs text-slate-500 flex items-center gap-1">
            <Upload size={12} /> Ручной ввод
          </p>
          <input
            value={manualTitle}
            onChange={e => setManualTitle(e.target.value)}
            placeholder="Заголовок"
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
          />
          <input
            value={manualCountry}
            onChange={e => setManualCountry(e.target.value)}
            placeholder="Страна (USA, GBR…)"
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
          />
          <textarea
            value={manualText}
            onChange={e => setManualText(e.target.value)}
            rows={4}
            placeholder="Вставьте текст документа…"
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
          />
          <button
            onClick={() => void submitManual()}
            disabled={ingesting || !manualText.trim()}
            className="flex items-center gap-2 bg-green-700 hover:bg-green-600 disabled:opacity-50 text-white rounded-lg px-4 py-2 text-sm"
          >
            {ingesting ? <Loader2 size={14} className="animate-spin" /> : <Upload size={14} />}
            Отправить в ingest
          </button>
        </div>
      </Section>

      <Section title="Документы → сигналы" icon={<FileText size={14} />}>
        <p className="text-xs text-slate-500 mb-3">
          Документы проходят анализ (engine) → извлекаются MSI, CEP, PNO → записываются как сигналы для{' '}
          <Link to="/stream" className="text-cyan-400">{nav.stream}</Link>.
        </p>
        {documents.length > 0 ? (
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {documents.map(d => (
              <div key={d.doc_id} className="flex justify-between text-xs bg-slate-900 rounded px-3 py-1.5">
                <span className="truncate text-slate-300">{d.title || d.doc_id}</span>
                <span className="text-slate-500 shrink-0 ml-2">{d.status} · {d.source}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">{common.noData}</p>
        )}

        {signals.length > 0 && (
          <div className="mt-4">
            <p className="text-[10px] text-slate-500 uppercase mb-2">Последние сигналы</p>
            <div className="space-y-1 max-h-40 overflow-y-auto">
              {signals.map((s, i) => (
                <div key={`${s.doc_id}-${i}`} className="flex justify-between text-xs bg-slate-900/80 rounded px-3 py-1.5 font-mono">
                  <span className="text-slate-400">{s.country} {s.iso3}</span>
                  <span>MSI {s.msi.toFixed(2)} · CEP {s.cep.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </Section>
    </div>
  )
}
