import type {
  CaseAnalysis, TaxonomyMode, HealthInfo, AlphaEdge, CountryStatsResponse,
  MasMetricsSummary, IngestStatus, AgentStepMetric, CepAlert, SignalTrend,
  CaseListItem, IngestDocumentSummary, IngestDocumentDetail, IngestSignalPoint,
  StreamForecastResponse,
} from './types'

/** Dev: Vite proxy (relative). Packaged Electron: explicit localhost. Override via VITE_API_BASE. */
export const API_BASE =
  import.meta.env.VITE_API_BASE ??
  (import.meta.env.DEV ? '' : 'http://127.0.0.1:8000')

const BASE = API_BASE
const TOKEN_KEY = 'errorlogy_token'

export type ApiErrorKind = 'network' | 'unauthorized' | 'unavailable' | 'client' | 'server'

export class ApiError extends Error {
  readonly status: number
  readonly kind: ApiErrorKind

  constructor(message: string, status: number, kind: ApiErrorKind) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.kind = kind
  }
}

export function isNetworkError(err: unknown): boolean {
  return err instanceof ApiError && (err.kind === 'network' || err.status === 0)
}

function authHeaders(): Record<string, string> {
  const headers: Record<string, string> = {}
  try {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) headers.Authorization = `Bearer ${token}`
  } catch { /* SSR / private mode */ }
  return headers
}

function classifyError(status: number): ApiErrorKind {
  if (status === 401 || status === 403) return 'unauthorized'
  if (status === 503) return 'unavailable'
  if (status >= 500) return 'server'
  return 'client'
}

async function parseErrorBody(res: Response): Promise<string> {
  try {
    const text = await res.text()
    if (!text) return res.statusText
    try {
      const j = JSON.parse(text) as { detail?: string | unknown }
      if (typeof j.detail === 'string') return j.detail
      return text
    } catch {
      return text
    }
  } catch {
    return res.statusText
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let res: Response
  try {
    res = await fetch(BASE + path, {
      credentials: 'include',
      ...init,
      headers: {
        ...authHeaders(),
        ...(init.body != null ? { 'Content-Type': 'application/json' } : {}),
        ...init.headers,
      },
    })
  } catch {
    throw new ApiError('Network error — is FastAPI running on :8000?', 0, 'network')
  }

  if (!res.ok) {
    const detail = await parseErrorBody(res)
    const kind = classifyError(res.status)
    const prefix = kind === 'unauthorized' ? 'Unauthorized'
      : kind === 'unavailable' ? 'Service unavailable'
        : `${init.method ?? 'GET'} ${path}`
    throw new ApiError(`${prefix} → ${res.status}${detail ? `: ${detail}` : ''}`, res.status, kind)
  }

  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

async function get<T>(path: string): Promise<T> {
  return request<T>(path)
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
}

export const api = {
  health: () => get<HealthInfo>('/api/health'),

  analyze: (params: {
    case_id: string
    raw_text: string
    title?: string
    country?: string
    year?: number
    engine_only?: boolean
    structure_only?: boolean
    dual_run?: boolean
  }) => {
    const qs = new URLSearchParams()
    if (params.engine_only) qs.set('engine_only', 'true')
    if (params.structure_only) qs.set('structure_only', 'true')
    if (params.dual_run) qs.set('dual_run', 'true')
    const q = qs.toString() ? `?${qs}` : ''
    const { engine_only: _e, structure_only: _s, dual_run: _d, ...body } = params
    return post<CaseAnalysis>(`/api/analyze${q}`, body)
  },

  analyzeStream: async (
    params: {
      case_id: string
      raw_text: string
      title?: string
      country?: string
      year?: number
      engine_only?: boolean
      structure_only?: boolean
      dual_run?: boolean
    },
    onStep: (step: AgentStepMetric) => void,
  ): Promise<CaseAnalysis> => {
    const qs = new URLSearchParams()
    if (params.engine_only) qs.set('engine_only', 'true')
    if (params.structure_only) qs.set('structure_only', 'true')
    if (params.dual_run) qs.set('dual_run', 'true')
    const q = qs.toString() ? `?${qs}` : ''
    const { engine_only: _e, structure_only: _s, dual_run: _d, ...body } = params

    let res: Response
    try {
      res = await fetch(BASE + `/api/analyze/stream${q}`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify(body),
      })
    } catch {
      throw new ApiError('Network error — is FastAPI running on :8000?', 0, 'network')
    }

    if (!res.ok) {
      const detail = await parseErrorBody(res)
      throw new ApiError(`POST /api/analyze/stream → ${res.status}: ${detail}`, res.status, classifyError(res.status))
    }
    if (!res.body) throw new ApiError('No response body from analyze stream', 0, 'network')

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let result: CaseAnalysis | null = null

    const handleBlock = (block: string) => {
      let event = 'message'
      let data = ''
      for (const line of block.split('\n')) {
        if (line.startsWith('event:')) event = line.slice(6).trim()
        else if (line.startsWith('data:')) data += line.slice(5).trim()
      }
      if (!data) return
      const parsed = JSON.parse(data)
      if (event === 'step') onStep(parsed)
      else if (event === 'done') result = parsed as CaseAnalysis
      else if (event === 'error') throw new Error(parsed.detail ?? 'Analysis failed')
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const parts = buffer.split('\n\n')
      buffer = parts.pop() ?? ''
      for (const block of parts) {
        if (block.startsWith(':')) continue
        handleBlock(block)
      }
    }
    if (buffer && !buffer.startsWith(':')) handleBlock(buffer)

    if (!result) throw new Error('Stream ended without result')
    return result
  },

  getCase: (caseId: string) =>
    get<CaseAnalysis>(`/api/cases/${encodeURIComponent(caseId)}`),

  listCases: (limit = 50) =>
    get<{ cases: CaseListItem[] }>(`/api/stats/cases?limit=${limit}`),

  countryStats: () => get<CountryStatsResponse>('/api/stats/countries'),

  masMetrics: () => get<MasMetricsSummary>('/api/metrics'),

  taxonomy: () => get<{ version: string; counts: Record<string, number>; layers: Record<string, string>; meta_dimensions?: string[] }>('/api/taxonomy'),

  modes: () => get<TaxonomyMode[]>('/api/taxonomy/modes'),

  mode: (id: string) => get<TaxonomyMode>(`/api/taxonomy/mode/${encodeURIComponent(id)}`),

  edges: () => get<AlphaEdge[]>('/api/taxonomy/edges'),

  ingestStatus: () => get<IngestStatus>('/api/ingest/status'),

  ingestDocuments: (status?: string, limit = 50) => {
    const qs = new URLSearchParams()
    if (status) qs.set('status', status)
    qs.set('limit', String(limit))
    return get<{ documents: IngestDocumentSummary[] }>(`/api/ingest/documents?${qs}`)
  },

  ingestDocumentById: (docId: string) =>
    get<IngestDocumentDetail>(`/api/ingest/documents/${encodeURIComponent(docId)}`),

  ingestProcessPending: (limit = 10, structureOnly = true) =>
    post<{ processed: unknown[] }>(
      `/api/ingest/process-pending?limit=${limit}&structure_only=${structureOnly}`,
    ),

  ingestSignals: (params?: { country?: string; iso3?: string; limit?: number }) => {
    const qs = new URLSearchParams()
    if (params?.country) qs.set('country', params.country)
    if (params?.iso3) qs.set('iso3', params.iso3)
    if (params?.limit != null) qs.set('limit', String(params.limit))
    const q = qs.toString() ? `?${qs}` : ''
    return get<{ signals: IngestSignalPoint[] }>(`/api/ingest/signals${q}`)
  },

  signalAlerts: (params?: { cep_threshold?: number; country?: string; iso3?: string; limit?: number }) => {
    const qs = new URLSearchParams()
    if (params?.cep_threshold != null) qs.set('cep_threshold', String(params.cep_threshold))
    if (params?.country) qs.set('country', params.country)
    if (params?.iso3) qs.set('iso3', params.iso3)
    if (params?.limit != null) qs.set('limit', String(params.limit))
    const q = qs.toString() ? `?${qs}` : ''
    return get<{ count: number; alerts: CepAlert[] }>(`/api/signals/alerts${q}`)
  },

  signalTrends: (params?: { window_days?: number; limit?: number }) => {
    const qs = new URLSearchParams()
    if (params?.window_days != null) qs.set('window_days', String(params.window_days))
    if (params?.limit != null) qs.set('limit', String(params.limit))
    const q = qs.toString() ? `?${qs}` : ''
    return get<{ count: number; trends: SignalTrend[] }>(`/api/signals/trends${q}`)
  },

  streamForecast: (params?: {
    country?: string
    iso3?: string
    window_days?: number
    limit?: number
    cep_threshold?: number
  }) => {
    const qs = new URLSearchParams()
    if (params?.country) qs.set('country', params.country)
    if (params?.iso3) qs.set('iso3', params.iso3)
    if (params?.window_days != null) qs.set('window_days', String(params.window_days))
    if (params?.limit != null) qs.set('limit', String(params.limit))
    if (params?.cep_threshold != null) qs.set('cep_threshold', String(params.cep_threshold))
    const q = qs.toString() ? `?${qs}` : ''
    return get<StreamForecastResponse>(`/api/forecast/stream${q}`)
  },

  ingestDocument: (body: {
    source?: string
    source_type?: string
    url?: string
    title?: string
    country?: string
    text: string
    auto_analyze?: boolean
    structure_only?: boolean
  }) => post<Record<string, unknown>>('/api/ingest', body),

  ingestFetchExa: (body: { queries?: string[]; num_results?: number; auto_analyze?: boolean }) =>
    post<Record<string, unknown>>('/api/ingest/fetch-exa', body),

  ingestFetchWeb: (body?: { queries?: string[]; num_results?: number; provider?: string; auto_analyze?: boolean }) =>
    post<Record<string, unknown>>('/api/ingest/fetch-web', body ?? {}),

  ingestFetchRss: (body?: { max_items_per_feed?: number; auto_analyze?: boolean }) =>
    post<Record<string, unknown>>('/api/ingest/fetch-rss', body ?? {}),

  ingestFetchAll: (body?: { num_results?: number; max_items_per_feed?: number; auto_analyze?: boolean }) =>
    post<Record<string, unknown>>('/api/ingest/fetch-all', body ?? {}),

  ingestFetchUsGov: (body?: { sources?: string[]; limit_per_source?: number; auto_analyze?: boolean }) =>
    post<Record<string, unknown>>('/api/ingest/fetch-us-gov', body ?? {}),

  ingestUrl: (body: { url: string; auto_analyze?: boolean }) =>
    post<Record<string, unknown>>('/api/ingest/url', body),

  ingestBatch: (body: {
    documents: Array<{
      source?: string
      source_type?: string
      url?: string
      title?: string
      country?: string
      text: string
      doc_id?: string
    }>
    auto_analyze?: boolean
    structure_only?: boolean
  }) => post<Record<string, unknown>>('/api/ingest/batch', body),

  /** Offline demo — Challenger engine-only output from errorlogy-mas/examples. */
  loadDemoAnalysis: async (): Promise<CaseAnalysis> => {
    const res = await fetch(`${import.meta.env.BASE_URL}demo/challenger_output.json`)
    if (!res.ok) throw new Error('Demo data not found')
    const data = await res.json() as CaseAnalysis
    data.metadata = {
      ...data.metadata,
      engine_only: true,
      engine: data.metadata?.engine ?? 'v1-math',
      demo: true,
    }
    return data
  },
}

export async function checkApiHealth(): Promise<HealthInfo | null> {
  try {
    return await api.health()
  } catch {
    return null
  }
}

/** Poll until MAS API responds or retries exhausted (Electron cold start). */
export async function waitForApiHealth(opts?: {
  maxAttempts?: number
  intervalMs?: number
}): Promise<HealthInfo | null> {
  const maxAttempts = opts?.maxAttempts ?? 45
  const intervalMs = opts?.intervalMs ?? 1000
  for (let i = 0; i < maxAttempts; i++) {
    const health = await checkApiHealth()
    if (health) return health
    if (i < maxAttempts - 1) {
      await new Promise(r => setTimeout(r, intervalMs))
    }
  }
  return null
}
