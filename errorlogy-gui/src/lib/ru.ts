/** User-facing Russian copy for Errorlogy GUI. Technical IDs stay in English. */

export const nav = {
  dashboard: 'Обзор',
  mas: 'Метрики MAS',
  ingest: 'Поток данных',
  globe: 'Глобус',
  analyze: 'Анализ',
  result: 'Результат',
  forecast: 'Прогноз',
  streamForecast: 'Прогноз потока',
  taxonomy: 'Таксономия',
} as const

export const common = {
  loading: 'Загрузка…',
  noData: 'нет данных',
  pipelineNoData: 'данные не возвращены pipeline',
  backendOffline:
    'Backend недоступен после 60 с ожидания. Проверьте лог запуска API (путь ниже) или запустите вручную.',
  backendOfflineManualCmd:
    'cd C:\\Users\\Public\\ERRORLOGY_MVP\\errorlogy-mas\n%LOCALAPPDATA%\\Programs\\Python\\Python312\\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000',
  backendOfflineLauncherHint:
    'Либо запустите: powershell -ExecutionPolicy Bypass -File C:\\Users\\Public\\ERRORLOGY_MVP\\errorlogy-gui\\scripts\\start-errorlogy.ps1',
  backendStarting: 'Запуск backend…',
  goAnalyze: 'Перейти к анализу',
  viewResult: 'Смотреть результат',
  viewForecast: 'Смотреть прогноз',
  viewAnalysis: 'Смотреть анализ',
  refresh: 'Обновить',
  local: '(локально)',
  engine: 'engine',
  full: 'full',
  on: 'ВКЛ',
  off: 'выкл',
} as const

export const muNote =
  'μ — степень нечёткой принадлежности (membership), не вероятность. Отдельно от confidence, evidence_grade и scenario_probability.'

export const horizonLabels: Record<string, string> = {
  near: 'ближний',
  short: 'краткосрочный',
  medium: 'среднесрочный',
  long: 'долгосрочный',
}

export const stageLabels: Record<string, string> = {
  weak_signal: 'слабый сигнал',
  ignored_warning: 'игнор предупреждения',
  escalation: 'эскалация',
  failure: 'сбой',
  inquiry: 'расследование',
}

export const urgencyLabels: Record<string, string> = {
  low: 'низкая',
  medium: 'средняя',
  high: 'высокая',
}

export const evidenceGradeLabels: Record<string, string> = {
  weak: 'слабая',
  moderate: 'умеренная',
  strong: 'сильная',
}

export const analyzeModes = {
  engineOnly: 'Только engine (эвристика)',
  structureOnly: 'LightweightScout + engine',
  dualRun: 'Dual-run (engine vs full MAS)',
  full: 'Полный MAS pipeline',
} as const

export const pipelineModeLabels = {
  demo: 'Офлайн-демо (Challenger engine-only)',
  dualRun: 'Dual-run (engine vs full)',
  structureOnly: 'LightweightScout + engine',
  engineOnly: 'Только engine',
  full: 'Полный MAS pipeline',
} as const

/** Engine modules that contribute to forecasts (TZ §9). */
export const engineModules = [
  { id: 'wms', label: 'WMS', desc: 'MSI, CEP — индекс слабых сигналов' },
  { id: 'classifier', label: 'Classifier', desc: 'Нечёткая μ по 217 режимам' },
  { id: 'alpha', label: 'α', desc: 'Распространение по графу таксономии' },
  { id: 'pno', label: 'PNO', desc: 'Режим системы PNO-1..7' },
  { id: 'acc', label: 'ACC', desc: 'Кластеры вклада ошибок' },
  { id: 'egd', label: 'EGD', desc: 'Динамика эхо-камеры' },
  { id: 't4d', label: 'T4D', desc: 'Временная worldline событий' },
  { id: 'cat', label: 'CAT', desc: 'Гипотеза катастрофы' },
  { id: 'fpd', label: 'FPD', desc: 'Нечёткий прогноз траектории' },
  { id: 'lbi', label: 'LBI', desc: 'Альтернативы улучшения' },
] as const

/** Stream forecast (Horizon 2) — modules contributing to aggregate view. */
export const streamEngineModules: Record<string, string> = {
  ingest: 'Поток документов: RSS, gov, web search → сигналы в БД',
  signals: 'Временные ряды CEP/MSI по странам из проанализированных документов',
  wms: 'Weak Multisource Signal — индекс слабых сигналов (MSI)',
  cep: 'Cumulative Error Pressure — накопленное давление ошибки (не вероятность)',
  msi: 'Multisource Signal Index — агрегат слабых сигналов',
  taxonomy: '217 атомарных режимов v16 — классификация вкладов ошибок',
  pno: 'Persistent Non-Optimality — домinant PNO-1..7 по кейсам',
  egd: 'Echo-room Dynamics — давление эхо-камеры по странам',
}
