/** User-facing English copy for Errorlogy GUI. Technical IDs stay in English. */

export const nav = {
  dashboard: 'Overview',
  mas: 'MAS Metrics',
  ingest: 'Data Stream',
  globe: 'Globe',
  analyze: 'Analyze',
  result: 'Result',
  forecast: 'Forecast',
  streamForecast: 'Stream Forecast',
  taxonomy: 'Taxonomy',
} as const

export const common = {
  loading: 'Loading…',
  noData: 'no data',
  pipelineNoData: 'pipeline returned no data',
  backendOffline:
    'Backend unavailable after 60 s wait. Check the API launch log (path below) or start manually.',
  backendOfflineManualCmd:
    'cd C:\\Users\\Public\\ERRORLOGY_MVP\\errorlogy-mas\n%LOCALAPPDATA%\\Programs\\Python\\Python312\\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000',
  backendOfflineLauncherHint:
    'Or run: powershell -ExecutionPolicy Bypass -File C:\\Users\\Public\\ERRORLOGY_MVP\\errorlogy-gui\\scripts\\start-errorlogy.ps1',
  backendStarting: 'Starting backend…',
  goAnalyze: 'Go to Analyze',
  viewResult: 'View result',
  viewForecast: 'View forecast',
  viewAnalysis: 'View analysis',
  refresh: 'Refresh',
  local: '(local)',
  engine: 'engine',
  full: 'full',
  on: 'ON',
  off: 'off',
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

export const evidenceGradeLabels: Record<string, string> = {
  weak: 'weak',
  moderate: 'moderate',
  strong: 'strong',
}

export const analyzeModes = {
  engineOnly: 'Engine only (heuristic)',
  structureOnly: 'LightweightScout + engine',
  dualRun: 'Dual-run (engine vs full MAS)',
  full: 'Full MAS pipeline',
} as const

export const pipelineModeLabels = {
  demo: 'Offline demo (Challenger engine-only)',
  dualRun: 'Dual-run (engine vs full)',
  structureOnly: 'LightweightScout + engine',
  engineOnly: 'Engine only',
  full: 'Full MAS pipeline',
} as const

/** Engine modules that contribute to forecasts (TZ §9). */
export const engineModules = [
  { id: 'wms', label: 'WMS', desc: 'MSI, CEP — weak signal index' },
  { id: 'classifier', label: 'Classifier', desc: 'Fuzzy μ over 217 modes' },
  { id: 'alpha', label: 'α', desc: 'Propagation over taxonomy graph' },
  { id: 'pno', label: 'PNO', desc: 'System regime PNO-1..7' },
  { id: 'acc', label: 'ACC', desc: 'Error contribution clusters' },
  { id: 'egd', label: 'EGD', desc: 'Echo-room dynamics' },
  { id: 't4d', label: 'T4D', desc: 'Temporal event worldline' },
  { id: 'cat', label: 'CAT', desc: 'Catastrophe hypothesis' },
  { id: 'fpd', label: 'FPD', desc: 'Fuzzy trajectory forecast' },
  { id: 'lbi', label: 'LBI', desc: 'Improvement alternatives' },
] as const

/** Stream forecast (Horizon 2) — modules contributing to aggregate view. */
export const streamEngineModules: Record<string, string> = {
  ingest: 'Document stream: RSS, gov, web search → signals in DB',
  signals: 'CEP/MSI time series by country from analyzed documents',
  wms: 'Weak Multisource Signal — weak signal index (MSI)',
  cep: 'Cumulative Error Pressure — accumulated error pressure (not probability)',
  msi: 'Multisource Signal Index — aggregate of weak signals',
  taxonomy: '217 atomic v16 modes — error contribution classification',
  pno: 'Persistent Non-Optimality — dominant PNO-1..7 per cases',
  egd: 'Echo-room Dynamics — echo-room pressure by country',
}
