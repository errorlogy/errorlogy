export interface ModeScore {
  mode_id: string
  name: string
  mu: number
  confidence: number
  evidence_grade: 'weak' | 'moderate' | 'strong'
  contributing_signals: string[]
}

export interface WMSResult {
  msi: number
  cep: number
  active_signals: string[]
  early_warning_hypothesis: string
}

export interface PNOResult {
  dominant_pno: string
  scores: Record<string, number>
  explanation: string
}

export interface ClusterResult {
  cluster_id: string
  name: string
  score: number
  signature_modes: string[]
  explanation: string
}

export interface ACCResult {
  max_contribution_cluster: ClusterResult
  clusters: ClusterResult[]
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

export interface CATResult {
  catastrophe_hypothesis: string
  bifurcation_risk: number
  hysteresis_risk: number
  explanation: string
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

export interface BettermentAlternative {
  alternative_id: string
  title: string
  target_modes: string[]
  expected_reduction: number
  feasibility: number
  risk_of_new_errors: string[]
  explanation: string
}

export interface LBIResult {
  alternatives: BettermentAlternative[]
}

export interface AlphaResult {
  initial_mu: Record<string, number>
  propagated_mu: Record<string, number>
  activated_edges: Array<{ from_id: string; to_id: string; weight: number; delta_mu: number }>
  top_modes: ModeScore[]
}

export interface EGDResult {
  echo_room_pressure: number
  hidden_signal_prior: number
  likely_egd_modes: ModeScore[]
}

export interface CaseAnalysis {
  case_id: string
  top_modes: ModeScore[]
  wms: WMSResult
  alpha: AlphaResult
  pno: PNOResult
  acc: ACCResult
  egd: EGDResult
  t4d: T4DResult
  cat: CATResult
  fpd: FPDResult
  lbi: LBIResult
  public_explanation: string
  red_team_notes: string[]
  neutrality_flags: string[]
  metadata?: {
    engine?: string
    engine_only?: boolean
    structure_only?: boolean
    demo?: boolean
    engine_warnings?: string[]
    pipeline_metrics?: PipelineRunMetric
    dual_run_diff?: {
      top_modes_jaccard: number
      top_modes_overlap: string[]
      engine_only_top5: string[]
      full_top5: string[]
      pno_match: boolean
      cat_match: boolean
      red_team_flags: string[]
      needs_human_review: boolean
    }
    dual_run_red_team_flagged?: boolean
    engine_only_snapshot?: {
      top_modes: ModeScore[]
      dominant_pno: string
      cat: string
    }
  }
}

export interface CountryCaseSummary {
  case_id: string
  title: string
  year: number
  country: string
  dominant_pno: string
  max_mu: number
  cep: number
  cat: string
}

export interface CountryStats {
  iso3: string
  name: string
  cases: number
  avg_mu: number
  max_cep: number
  avg_echo_pressure: number
  dominant_pno: string
  top_families: Record<string, number>
  recent_cases: CountryCaseSummary[]
  last_signal_at?: string | null
  signal_points?: number
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

export interface IngestDocumentDetail extends IngestDocumentSummary {
  text: string
  error_msg?: string | null
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

export interface SignalStreamSummary {
  iso3: string
  country: string
  points: number
  last_signal_at: string
  max_cep: number
  avg_msi: number
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
  federal_register?: boolean
  courtlistener?: boolean
  govinfo?: boolean
  oig?: boolean
  legiscan?: boolean
}

export interface IngestStatus {
  engine: string
  exa_configured: boolean
  fetchers?: IngestFetcherStatus
  us_gov_configured?: Record<string, boolean>
  web_search_provider?: string | null
  documents_total: number
  documents_pending: number
  documents_analyzed: number
  signals_total: number
  active_alerts_count?: number
  last_ingest_at: string | null
  sources: Record<string, number>
  recent_documents: IngestDocumentSummary[]
  signal_streams: SignalStreamSummary[]
}

export interface CountryStatsResponse {
  engine: string
  source?: 'database' | 'seed' | 'empty'
  total_cases: number
  countries: CountryStats[]
}

export interface AgentStepMetric {
  agent_id: string
  kind: 'engine' | 'llm'
  duration_ms: number
  status: string
  provider?: string | null
  model?: string | null
  input_tokens?: number
  output_tokens?: number
  detail?: string
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
    engine_duration_ms: number
    llm_duration_ms: number
    input_tokens: number
    output_tokens: number
  }
}

export interface MasMetricsSummary {
  engine_version: string
  runs_in_session: number
  total_llm_calls: number
  total_engine_calls: number
  total_input_tokens: number
  total_output_tokens: number
  last_run: PipelineRunMetric | null
  recent_runs: Array<{
    run_id: string
    case_id: string
    status: string
    engine_only: boolean
    started_at: string
    totals: PipelineRunMetric['totals']
  }>
  agent_registry: Array<{ id: string; label: string; kind: 'engine' | 'llm' }>
}

export interface TaxonomyMode {
  id: string
  family: string
  layer: string
  name: string
  category?: string
  definition?: string
  operational_signal?: string
  source_field?: string
  meta_dimensions?: string[]
}

export interface AlphaEdge {
  from: string
  to: string
  weight: number
  confidence?: number
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
  methodology_ru: string
}
