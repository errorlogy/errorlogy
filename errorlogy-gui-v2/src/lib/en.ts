/** English UI strings for forecast-focused v2. */

export const nav = {
  home: 'Overview',
  stream: 'Stream Forecast',
  case: 'Case Forecast',
  data: 'Data Streams',
  layers: 'Institutional Layers',
  discourse: 'Narrative Forks',
} as const

export const common = {
  loading: 'Loading…',
  noData: 'no data',
  refresh: 'Refresh',
  backendOffline: 'Backend unavailable. Start errorlogy-mas API on port 8000.',
  backendManualCmd: 'cd errorlogy-mas && python api/main.py',
} as const

export const muNote =
  'μ — fuzzy membership degree, not probability. Separate from confidence, evidence_grade, and scenario_probability.'

export const horizonLabels: Record<string, string> = {
  near: 'near-term',
  short: 'short-term',
  medium: 'medium-term',
  long: 'long-term',
}

export const stageLabels: Record<string, string> = {
  weak_signal: 'weak signal',
  ignored_warning: 'ignored warning',
  escalation: 'escalation',
  failure: 'failure',
  inquiry: 'inquiry',
}

export const urgencyLabels: Record<string, string> = {
  low: 'low',
  medium: 'medium',
  high: 'high',
}

export const streamEngineModules: Record<string, string> = {
  ingest: 'Document stream: RSS, gov, web → signals in DB',
  signals: 'CEP/MSI time series by country',
  wms: 'Weak Multisource Signal — weak signal index (MSI)',
  cep: 'Cumulative Error Pressure — accumulated pressure (not probability)',
  msi: 'Multisource Signal Index',
  taxonomy: '217 v16 modes — error classification',
  pno: 'Persistent Non-Optimality PNO-1..7',
  egd: 'Echo-room Dynamics — echo-room pressure',
}

export const home = {
  title: 'Errorlogy — Forecast',
  subtitle: 'Simplified interface: stream and case forecast, transparent methodology.',
  caseForecastTitle: 'Case forecast (Horizon 1)',
  caseForecastDesc:
    'Analysis of a single governance case: pipeline WMS → Classifier → … → FPD/T4D. ' +
    'Returns μ_forecast by mode, scenarios, and temporal worldline. ' +
    'Suitable for reviewing a specific incident or document.',
  streamForecastTitle: 'Stream forecast (Horizon 2)',
  streamForecastDesc:
    'Aggregate over ingest stream: CEP trends, escalation alerts, country statistics. ' +
    'Does not compute calendar dates — shows error pressure over time.',
  methodologyTitle: 'How we forecast',
  methodologyPoints: [
    'Documents → signals (MSI, CEP) via engine v1-math',
    'Case: fuzzy classification of 217 modes → α-graph → FPD (μ_forecast) + T4D (worldline)',
    'Stream: signal aggregation by country, CEP thresholds, trends over N-day window',
    'μ ≠ probability; scenario_probability is a separate scenario value',
  ],
} as const

export const layersPage = {
  title: 'Institutional layers',
  subtitle:
    'EU supranational topology and live cross-layer event feed. ' +
    'Institutional model only — not a legal verdict.',
  topologyTitle: 'EU / national topology',
  layersTitle: 'Institution layer registry',
  eventsTitle: 'Cross-layer events',
  eventsSubtitle: 'GET /api/events/cross-layer — polled every 12s',
  noEvents: 'No cross-layer events yet.',
  selectEvent: 'Select an event to highlight activated layers on the map.',
  sampleEvent: 'Activate sample event',
  samplePosting: 'Posting sample…',
  epistemicNote:
    'Outputs carry epistemic_label (INSTITUTIONAL_MODEL, OPERATIONAL, …). ' +
    'Activated layers are framing signals, not sovereignty claims.',
  aboutLink: 'AI Native Gov — institutional topology contracts',
  aboutUrl: 'https://github.com/errorlogy/ai-native-gov',
  nationalStates: 'Sample member states (×27 modeled)',
} as const

export const discoursePage = {
  title: 'Narrative fork lineage',
  subtitle:
    'Read-only discourse graph view: story lineage and fork edges from the memetic runtime API.',
  storyIdLabel: 'Story ID',
  storyIdPlaceholder: 'e.g. mvp-discourse-sample',
  loadLineage: 'Load lineage',
  loadingLineage: 'Loading…',
  lineageTitle: 'Root-to-node lineage',
  forksTitle: 'Descendant forks',
  edgesTitle: 'Graph edges',
  narrativeForks: 'Narrative forks',
  symbolicVariants: 'Symbolic variant edges',
  root: 'root',
  leaf: 'selected',
  noLineage: 'No lineage path found for this story ID.',
  noForks: 'No descendant forks registered.',
  noData: 'Enter a story ID to load lineage.',
  epistemicNote:
    'Discourse graph outputs are INSTITUTIONAL_MODEL framing — analytical lineage, not a legal verdict.',
  clauseBadge: 'POSLEDNIY_ZAVET',
  couplingTitle: 'Market coupling events',
  couplingEmpty: 'No memetic_market_coupling_snapshot events for this story.',
  couplingLoading: 'Loading coupling events…',
  peakVelocity: 'peak velocity',
  decayTau: 'decay τ (h)',
  cohortBadge: 'cohort',
} as const

export const dataStreams = {
  title: 'Data streams',
  subtitle: 'What enters the system and how it becomes forecast signals.',
  pipelineSteps: [
    { id: 'sources', label: 'Sources', desc: 'RSS, gov APIs, manual input, URL' },
    { id: 'ingest', label: 'Ingest', desc: 'Documents in SQLite, deduplication' },
    { id: 'analyze', label: 'Analyze', desc: 'Engine/MAS → modes, WMS, CEP' },
    { id: 'signals', label: 'Signals', desc: 'Time series by country' },
    { id: 'forecast', label: 'Forecast', desc: 'Trends, alerts, FPD per case' },
  ],
} as const
