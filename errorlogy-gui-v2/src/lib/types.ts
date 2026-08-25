export interface ModeScore {
  mode_id: string
  name: string
  mu: number
  confidence: number
  evidence_grade: 'weak' | 'moderate' | 'strong'
  contributing_signals: string[]
}

export interface ErrorWorldlinePoint {
  t: string
  stage: 'weak_signal' | 'ignored_warning' | 'escalation' | 'failure' | 'inquiry'
  modes: string[]
  description: string
}

export interface T4DResult {
  worldline: ErrorWorldlinePoint[]
  warning_to_action_latency_risk: number
  intervention_window_loss: number
  irreversibility_threshold_risk: number
}

export interface ModeForecast {
  mode_id: string
  mu_forecast: number
  scenario_probability: number
  confidence: number
  evidence_grade: string
}

export interface EarlyWarning {
  signal: string
  urgency: 'low' | 'medium' | 'high'
  description: string
}

export interface FPDResult {
  horizon: 'near' | 'short' | 'medium' | 'long'
  mode_forecasts: ModeForecast[]
  pno_transition_forecast: string
  early_warnings: EarlyWarning[]
  confidence: number
}

export interface CaseAnalysis {
  case_id: string
  top_modes: ModeScore[]
  t4d: T4DResult
  fpd: FPDResult
  metadata?: {
    engine?: string
    engine_only?: boolean
    structure_only?: boolean
    pipeline_metrics?: PipelineRunMetric
  }
}

export interface CaseListItem {
  case_id: string
  title: string
  country: string
  year: number | null
  engine_only: boolean
  created_at: string
}

export interface IngestDocumentSummary {
  doc_id: string
  source: string
  source_type: string
  url: string
  title: string
  country: string
  status: string
  case_id?: string | null
  ingested_at: string
  analyzed_at?: string | null
  text_len: number
}

export interface IngestSignalPoint {
  country: string
  iso3: string
  case_id: string
  doc_id: string
  msi: number
  cep: number
  echo_pressure: number
  dominant_pno: string
  cat: string
  recorded_at: string
}

export interface CepAlert {
  country: string
  iso3: string
  cep: number
  latest_cep: number
  max_cep_window: number
  doc_id: string
  case_id: string
  recorded_at: string
  severity: 'low' | 'medium' | 'high'
  signal_count_window: number
}

export interface SignalTrend {
  iso3: string
  country: string
  cep_max: number
  cep_latest: number
  cep_delta_7d: number
  signal_count: number
  last_signal_at: string
}

export interface IngestFetcherStatus {
  url: boolean
  rss: boolean
  openrouter: boolean
  gemini: boolean
  exa: boolean
}

export interface IngestStatus {
  engine: string
  exa_configured: boolean
  fetchers?: IngestFetcherStatus
  documents_total: number
  documents_pending: number
  documents_analyzed: number
  signals_total: number
  active_alerts_count?: number
  last_ingest_at: string | null
  sources: Record<string, number>
  recent_documents: IngestDocumentSummary[]
}

export interface CountryStats {
  iso3: string
  name: string
  cases: number
  avg_mu: number
  max_cep: number
  dominant_pno: string
}

export interface AgentStepMetric {
  agent_id: string
  kind: 'engine' | 'llm'
  duration_ms: number
  status: string
  provider?: string | null
  model?: string | null
}

export interface PipelineRunMetric {
  run_id: string
  case_id: string
  engine_only: boolean
  engine_version: string
  started_at: string
  finished_at?: string | null
  status: string
  steps: AgentStepMetric[]
  totals: {
    total_duration_ms: number
    engine_steps: number
    llm_steps: number
  }
}

export interface HealthInfo {
  status: string
  engine?: string
  providers: string[]
  taxonomy_modes: number
  alpha_edges: number
}

export interface StreamForecastCaseSummary extends CaseListItem {
  top_modes: Array<{ mode_id: string; name: string; mu: number }>
}

export interface StreamForecastResponse {
  generated_at: string
  window_days: number
  filters: { country: string | null; iso3: string | null }
  taxonomy: {
    version: string | null
    mode_count: number
    counts: Record<string, number>
    alpha_edges: number
    dominant_modes: Array<{
      mode_id: string
      name: string
      case_hits: number
      avg_mu: number
    }>
  }
  ingest: {
    documents_total: number
    pending: number
    analyzed: number
    signals_total: number
    last_ingest_at: string | null
    sources_breakdown: Record<string, number>
    active_alerts_count: number
    fetchers_configured: Record<string, boolean>
  }
  engine: { version: string; modules: string[] }
  engine_modules_used: string[]
  alerts: CepAlert[]
  trends: SignalTrend[]
  countries: CountryStats[]
  recent_cases: StreamForecastCaseSummary[]
  horizon_note: string
  methodology: string
}
