import type {
  CaseAnalysis, HealthInfo, IngestDocumentSummary, IngestSignalPoint,
  IngestStatus, AgentStepMetric, StreamForecastResponse, CaseListItem,
  CrossLayerListResponse, CrossLayerLayersResponse, CrossLayerPostResponse,
  MemeticLineageResponse,
} from './types'

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
  } catch { /* private mode */ }
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
    throw new ApiError('Network unavailable — is FastAPI running on :8000?', 0, 'network')
  }

  if (!res.ok) {
    const detail = await parseErrorBody(res)
    throw new ApiError(`${init.method ?? 'GET'} ${path} → ${res.status}${detail ? `: ${detail}` : ''}`, res.status, classifyError(res.status))
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
  }) => {
    const qs = new URLSearchParams()
    if (params.engine_only) qs.set('engine_only', 'true')
    if (params.structure_only) qs.set('structure_only', 'true')
    const q = qs.toString() ? `?${qs}` : ''
    const { engine_only: _e, structure_only: _s, ...body } = params
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
    },
    onStep: (step: AgentStepMetric) => void,
  ): Promise<CaseAnalysis> => {
    const qs = new URLSearchParams()
    if (params.engine_only) qs.set('engine_only', 'true')
    if (params.structure_only) qs.set('structure_only', 'true')
    const q = qs.toString() ? `?${qs}` : ''
    const { engine_only: _e, structure_only: _s, ...body } = params

    let res: Response
    try {
      res = await fetch(BASE + `/api/analyze/stream${q}`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify(body),
      })
    } catch {
      throw new ApiError('Network unavailable — is FastAPI running on :8000?', 0, 'network')
    }

    if (!res.ok) {
      const detail = await parseErrorBody(res)
      throw new ApiError(`POST /api/analyze/stream → ${res.status}: ${detail}`, res.status, classifyError(res.status))
    }
    if (!res.body) throw new ApiError('Empty response from analyze stream', 0, 'network')

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

  ingestStatus: () => get<IngestStatus>('/api/ingest/status'),

  ingestDocuments: (status?: string, limit = 30) => {
    const qs = new URLSearchParams()
    if (status) qs.set('status', status)
    qs.set('limit', String(limit))
    return get<{ documents: IngestDocumentSummary[] }>(`/api/ingest/documents?${qs}`)
  },

  ingestSignals: (params?: { limit?: number }) => {
    const qs = new URLSearchParams()
    if (params?.limit != null) qs.set('limit', String(params.limit))
    const q = qs.toString() ? `?${qs}` : ''
    return get<{ signals: IngestSignalPoint[] }>(`/api/ingest/signals${q}`)
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
    title?: string
    country?: string
    text: string
    auto_analyze?: boolean
    structure_only?: boolean
  }) => post<Record<string, unknown>>('/api/ingest', body),

  ingestFetchRss: (body?: { max_items_per_feed?: number; auto_analyze?: boolean }) =>
    post<Record<string, unknown>>('/api/ingest/fetch-rss', body ?? {}),

  ingestProcessPending: (limit = 10, structureOnly = true) =>
    post<{ processed: unknown[] }>(
      `/api/ingest/process-pending?limit=${limit}&structure_only=${structureOnly}`,
    ),

  crossLayerList: (params?: { limit?: number; story_id?: string; event_type?: string }) => {
    const qs = new URLSearchParams()
    if (params?.limit != null) qs.set('limit', String(params.limit))
    if (params?.story_id) qs.set('story_id', params.story_id)
    if (params?.event_type) qs.set('event_type', params.event_type)
    const q = qs.toString() ? `?${qs}` : ''
    return get<CrossLayerListResponse>(`/api/events/cross-layer${q}`)
  },

  crossLayerLayers: () =>
    get<CrossLayerLayersResponse>('/api/events/cross-layer/layers'),

  crossLayerPost: (body: {
    story_id: string
    event_type: string
    activated_layers?: string[]
    jurisdiction_set?: string[]
    coordination_forum?: string
    epistemic_label?: string
  }) => post<CrossLayerPostResponse>('/api/events/cross-layer', body),

  memeticLineage: (storyId: string) =>
    get<MemeticLineageResponse>(
      `/api/events/memetic/lineage/${encodeURIComponent(storyId)}`,
    ),
}

export async function checkApiHealth(): Promise<HealthInfo | null> {
  try {
    return await api.health()
  } catch {
    return null
  }
}
