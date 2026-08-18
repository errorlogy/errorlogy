import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  RefreshCw, Rss, Search, Upload, Loader2, Radio, Link2, Zap, Landmark,
  AlertTriangle, FileText, X, Play, Layers,
} from 'lucide-react'
import { api } from '../lib/api'
import { common } from '../lib/ru'
import type { CepAlert, IngestDocumentDetail, IngestDocumentSummary, IngestStatus } from '../lib/types'

export function IngestPage() {
  const navigate = useNavigate()
  const [status, setStatus] = useState<IngestStatus | null>(null)
  const [documents, setDocuments] = useState<IngestDocumentSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [fetching, setFetching] = useState(false)
  const [ingesting, setIngesting] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState('')
  const [manualTitle, setManualTitle] = useState('')
  const [manualCountry, setManualCountry] = useState('')
  const [manualText, setManualText] = useState('')
  const [manualUrl, setManualUrl] = useState('')
  const [batchText, setBatchText] = useState('')
  const [alerts, setAlerts] = useState<CepAlert[]>([])
  const [docModal, setDocModal] = useState<IngestDocumentDetail | null>(null)
  const [docModalLoading, setDocModalLoading] = useState(false)

  const load = useCallback(async () => {
    try {
      const [st, alertRes, docRes] = await Promise.all([
        api.ingestStatus(),
        api.signalAlerts({ cep_threshold: 0.5, limit: 20 }),
        api.ingestDocuments(undefined, 30),
      ])
      setStatus(st)
      setAlerts(alertRes.alerts)
      setDocuments(docRes.documents)
      setError('')
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Не удалось загрузить статус ingest')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
    const t = setInterval(load, 8000)
    return () => clearInterval(t)
  }, [load])

  async function openDocument(docId: string) {
    setDocModalLoading(true)
    try {
      setDocModal(await api.ingestDocumentById(docId))
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Не удалось загрузить документ')
    } finally {
      setDocModalLoading(false)
    }
  }

  async function runAction(fn: () => Promise<unknown>) {
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

  async function processPending() {
    setProcessing(true)
    setError('')
    try {
      await api.ingestProcessPending(10, true)
      await load()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка обработки pending')
    } finally {
      setProcessing(false)
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
      await load()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка ingest')
    } finally {
      setIngesting(false)
    }
  }

  async function submitBatch() {
    const chunks = batchText.split(/\n---+\n/).map(s => s.trim()).filter(Boolean)
    if (chunks.length === 0) return
    setIngesting(true)
    setError('')
    try {
      await api.ingestBatch({
        documents: chunks.map((text, i) => ({
          source: 'manual',
          source_type: 'batch',
          title: `Batch doc ${i + 1}`,
          country: manualCountry,
          text,
        })),
        auto_analyze: true,
        structure_only: true,
      })
      setBatchText('')
      await load()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка batch ingest')
    } finally {
      setIngesting(false)
    }
  }

  async function submitUrl() {
    if (!manualUrl.trim()) return
    setIngesting(true)
    setError('')
    try {
      await api.ingestUrl({ url: manualUrl.trim(), auto_analyze: true })
      setManualUrl('')
      await load()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка ingest URL')
    } finally {
      setIngesting(false)
    }
  }

  if (loading && !status) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-500">
        <Loader2 className="animate-spin mr-2" size={18} /> Загрузка монитора потока…
      </div>
    )
  }

  const s = status!
  const f = s.fetchers
  const webProvider = s.web_search_provider
  const webReady = !!(f?.openrouter || f?.gemini || f?.exa)
  const usGovReady = !!(f?.federal_register || f?.courtlistener || f?.oig)
  const docList = documents.length > 0 ? documents : s.recent_documents

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Radio size={22} className="text-emerald-400" />
            Монитор потока данных
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            RSS + US gov API + URL + web search → Scout → engine → signals
          </p>
        </div>
        <div className="flex items-center gap-2">
          {s.documents_pending > 0 && (
            <button
              onClick={processPending}
              disabled={processing}
              className="flex items-center gap-2 bg-amber-700 hover:bg-amber-600 disabled:opacity-40 text-white rounded-xl px-3 py-2 text-sm font-medium"
            >
              {processing ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
              Обработать pending ({s.documents_pending})
            </button>
          )}
          <button onClick={load} className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800">
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded-lg p-3 text-red-300 text-sm">{error}</div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
        {[
          { label: 'Документы', value: s.documents_total },
          { label: 'Проанализировано', value: s.documents_analyzed },
          { label: 'В очереди', value: s.documents_pending },
          { label: 'Сигналы', value: s.signals_total },
          { label: 'Алерты', value: s.active_alerts_count ?? alerts.length },
          { label: 'Web', value: webProvider || '—' },
        ].map(k => (
          <div key={k.label} className="bg-slate-800 rounded-xl p-3">
            <div className="text-[10px] text-slate-500 uppercase tracking-widest">{k.label}</div>
            <div className="text-lg font-bold text-white mt-1 truncate">{k.value}</div>
          </div>
        ))}
      </div>

      {f && (
        <div className="flex flex-wrap gap-2 text-[10px]">
          {Object.entries(f).map(([name, on]) => (
            <span key={name} className={`px-2 py-1 rounded-full ${on ? 'bg-emerald-900/50 text-emerald-300' : 'bg-slate-800 text-slate-500'}`}>
              {name}: {on ? common.on : common.off}
            </span>
          ))}
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        <button
          onClick={() => runAction(() => api.ingestFetchAll({ num_results: 2, max_items_per_feed: 2, auto_analyze: true }))}
          disabled={fetching}
          className="flex items-center gap-2 bg-emerald-700 hover:bg-emerald-600 disabled:opacity-40 text-white rounded-xl px-4 py-2 text-sm font-medium"
        >
          {fetching ? <Loader2 size={16} className="animate-spin" /> : <Zap size={16} />}
          Загрузить всё (RSS + US gov + web)
        </button>
        <button
          onClick={() => runAction(() => api.ingestFetchUsGov({ limit_per_source: 3, auto_analyze: true }))}
          disabled={fetching || !usGovReady}
          className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-40 text-white rounded-xl px-4 py-2 text-sm font-medium"
        >
          <Landmark size={16} /> US gov
        </button>
        <button
          onClick={() => runAction(() => api.ingestFetchRss({ max_items_per_feed: 3, auto_analyze: true }))}
          disabled={fetching || !f?.rss}
          className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-40 text-white rounded-xl px-4 py-2 text-sm font-medium"
        >
          <Rss size={16} /> RSS
        </button>
        <button
          onClick={() => runAction(() => api.ingestFetchWeb({ num_results: 2, auto_analyze: true }))}
          disabled={fetching || !webReady}
          className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-40 text-white rounded-xl px-4 py-2 text-sm font-medium"
        >
          <Search size={16} /> Web search
        </button>
        <button
          onClick={() => runAction(() => api.ingestFetchExa({ num_results: 2, auto_analyze: true }))}
          disabled={fetching || !f?.exa}
          className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-40 text-white rounded-xl px-4 py-2 text-sm font-medium"
        >
          <Search size={16} /> Exa (optional)
        </button>
      </div>

      {s.us_gov_configured && Object.keys(s.us_gov_configured).length > 0 && (
        <div className="flex flex-wrap gap-2 text-[10px]">
          <span className="text-slate-500">US gov:</span>
          {Object.entries(s.us_gov_configured).map(([name, on]) => (
            <span key={name} className={`px-2 py-1 rounded-full ${on ? 'bg-blue-900/50 text-blue-300' : 'bg-slate-800 text-slate-500'}`}>
              {name}: {on ? common.on : common.off}
            </span>
          ))}
        </div>
      )}

      {!webReady && (
        <p className="text-xs text-amber-400">
          Web search использует OpenRouter или Gemini. Exa опционален.
        </p>
      )}

      {Object.keys(s.sources).length > 0 && (
        <div className="text-xs text-slate-400">
          Источники: {Object.entries(s.sources).map(([k, v]) => `${k}=${v}`).join(', ')}
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        <section className="bg-slate-800 rounded-xl p-4">
          <h2 className="text-xs text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
            <AlertTriangle size={14} className="text-amber-400" /> CEP ранние предупреждения (≥0.5)
          </h2>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {alerts.length === 0 ? (
              <p className="text-sm text-slate-500">Нет активных CEP-алертов</p>
            ) : (
              alerts.map(a => (
                <div key={`${a.iso3}-${a.doc_id}`} className="flex flex-col gap-0.5 text-sm bg-slate-900 rounded-lg px-3 py-2">
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-slate-300">{a.country} · {a.iso3}</span>
                    <span className={
                      a.severity === 'high' ? 'text-red-400' :
                      a.severity === 'medium' ? 'text-amber-400' : 'text-yellow-500'
                    }>{a.severity} · CEP {a.cep}</span>
                  </div>
                  <div className="text-[10px] text-slate-500 truncate">
                    {a.doc_id} · {a.recorded_at ? new Date(a.recorded_at).toLocaleString() : '—'}
                  </div>
                  {a.case_id && (
                    <button
                      onClick={() => navigate(`/result/${encodeURIComponent(a.case_id)}`)}
                      className="text-[10px] text-red-400 hover:text-red-300 text-left mt-1"
                    >
                      {common.viewAnalysis} →
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </section>

        <section className="bg-slate-800 rounded-xl p-4">
          <h2 className="text-xs text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
            <Rss size={14} /> Потоки сигналов по странам
          </h2>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {s.signal_streams.length === 0 ? (
              <p className="text-sm text-slate-500">Сигналов пока нет — запустите fetch или ручной ingest</p>
            ) : (
              s.signal_streams.map(st => (
                <div key={st.iso3} className="flex justify-between text-sm bg-slate-900 rounded-lg px-3 py-2">
                  <span className="font-mono text-slate-300">{st.iso3}</span>
                  <span className="text-red-400">CEP max {st.max_cep}</span>
                  <span className="text-slate-500">{st.points} pts</span>
                </div>
              ))
            )}
          </div>
        </section>

        <section className="md:col-span-2 bg-slate-800 rounded-xl p-4">
          <h2 className="text-xs text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
            <FileText size={14} /> Документы
          </h2>
          <div className="space-y-2 max-h-72 overflow-y-auto">
            {docList.length === 0 ? (
              <p className="text-sm text-slate-500">Документов пока нет</p>
            ) : (
              docList.map(d => (
                <div key={d.doc_id} className="bg-slate-900 rounded-lg px-3 py-2 text-xs">
                  <div className="flex justify-between gap-2 items-start">
                    <button
                      onClick={() => openDocument(d.doc_id)}
                      className="text-slate-200 truncate text-left hover:text-white flex-1"
                    >
                      {d.title || d.doc_id}
                    </button>
                    <span className={
                      d.status === 'analyzed' ? 'text-green-400' :
                      d.status === 'pending' ? 'text-amber-400' : 'text-slate-500'
                    }>{d.status}</span>
                  </div>
                  <div className="text-slate-500 mt-1 flex justify-between items-center gap-2">
                    <span>{d.source} · {d.country || '—'} · {d.text_len} chars</span>
                    {d.status === 'analyzed' && d.case_id && (
                      <button
                        onClick={() => navigate(`/result/${encodeURIComponent(d.case_id!)}`)}
                        className="text-red-400 hover:text-red-300 shrink-0"
                      >
                        {common.viewAnalysis}
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      <section className="bg-slate-800 rounded-xl p-4 space-y-3">
        <h2 className="text-xs text-slate-400 uppercase tracking-widest flex items-center gap-2">
          <Link2 size={14} /> Ingest по URL
        </h2>
        <div className="flex gap-3">
          <input value={manualUrl} onChange={e => setManualUrl(e.target.value)} placeholder="https://..."
            className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm" />
          <button onClick={submitUrl} disabled={ingesting || !manualUrl.trim()}
            className="bg-slate-600 hover:bg-slate-500 disabled:opacity-50 text-white rounded-lg px-4 py-2 text-sm font-medium flex items-center gap-2">
            {ingesting ? <Loader2 size={16} className="animate-spin" /> : <Link2 size={16} />}
            Fetch URL
          </button>
        </div>
      </section>

      <section className="bg-slate-800 rounded-xl p-4 space-y-3">
        <h2 className="text-xs text-slate-400 uppercase tracking-widest flex items-center gap-2">
          <Upload size={14} /> Ручной ingest (в т.ч. MCP paste)
        </h2>
        <div className="grid md:grid-cols-2 gap-3">
          <input value={manualTitle} onChange={e => setManualTitle(e.target.value)} placeholder="Название"
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm" />
          <input value={manualCountry} onChange={e => setManualCountry(e.target.value)} placeholder="Страна (USA)"
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm" />
        </div>
        <textarea value={manualText} onChange={e => setManualText(e.target.value)} rows={5}
          placeholder="Вставьте статью, отчёт или результат Exa MCP…"
          className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm font-mono" />
        <button onClick={submitManual} disabled={ingesting}
          className="bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white rounded-lg px-4 py-2 text-sm font-medium flex items-center gap-2">
          {ingesting ? <Loader2 size={16} className="animate-spin" /> : <Upload size={16} />}
          Ingest + анализ
        </button>
      </section>

      <section className="bg-slate-800 rounded-xl p-4 space-y-3">
        <h2 className="text-xs text-slate-400 uppercase tracking-widest flex items-center gap-2">
          <Layers size={14} /> Batch ingest (разделитель <code className="text-slate-500">---</code> на отдельной строке)
        </h2>
        <textarea value={batchText} onChange={e => setBatchText(e.target.value)} rows={6}
          placeholder={'First document text...\n---\nSecond document text...'}
          className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm font-mono" />
        <button onClick={submitBatch} disabled={ingesting || !batchText.trim()}
          className="bg-slate-600 hover:bg-slate-500 disabled:opacity-50 text-white rounded-lg px-4 py-2 text-sm font-medium flex items-center gap-2">
          {ingesting ? <Loader2 size={16} className="animate-spin" /> : <Layers size={16} />}
          Batch ingest + анализ
        </button>
      </section>

      {(docModal || docModalLoading) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" onClick={() => setDocModal(null)}>
          <div
            className="bg-slate-900 border border-slate-700 rounded-xl max-w-2xl w-full max-h-[80vh] flex flex-col shadow-xl"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
              <div className="min-w-0">
                <h3 className="text-sm font-semibold text-white truncate">
                  {docModal?.title || docModal?.doc_id || 'Документ'}
                </h3>
                {docModal && (
                  <p className="text-[10px] text-slate-500 font-mono mt-0.5">
                    {docModal.doc_id} · {docModal.status} · {docModal.source}
                  </p>
                )}
              </div>
              <button onClick={() => setDocModal(null)} className="text-slate-500 hover:text-white p-1">
                <X size={18} />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              {docModalLoading && !docModal ? (
                <div className="flex items-center gap-2 text-slate-500 text-sm">
                  <Loader2 size={16} className="animate-spin" /> {common.loading}
                </div>
              ) : docModal ? (
                <>
                  <pre className="text-xs text-slate-300 whitespace-pre-wrap font-mono leading-relaxed">
                    {docModal.text}
                  </pre>
                  {docModal.error_msg && (
                    <p className="mt-3 text-xs text-red-400">{docModal.error_msg}</p>
                  )}
                </>
              ) : null}
            </div>
            {docModal?.case_id && (
              <div className="px-4 py-3 border-t border-slate-800">
                <button
                  onClick={() => {
                    navigate(`/result/${encodeURIComponent(docModal.case_id!)}`)
                    setDocModal(null)
                  }}
                  className="bg-red-600 hover:bg-red-500 text-white rounded-lg px-4 py-2 text-sm font-medium"
                >
                  {common.viewAnalysis}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
