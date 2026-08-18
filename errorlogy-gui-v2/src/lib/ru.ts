/** Russian UI strings for forecast-focused v2. */

export const nav = {
  home: 'Обзор',
  stream: 'Прогноз потока',
  case: 'Прогноз по кейсу',
  data: 'Потоки данных',
} as const

export const common = {
  loading: 'Загрузка…',
  noData: 'нет данных',
  refresh: 'Обновить',
  backendOffline: 'Backend недоступен. Запустите errorlogy-mas API на порту 8000.',
  backendManualCmd: 'cd errorlogy-mas && python api/main.py',
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

export const streamEngineModules: Record<string, string> = {
  ingest: 'Поток документов: RSS, gov, web → сигналы в БД',
  signals: 'Временные ряды CEP/MSI по странам',
  wms: 'Weak Multisource Signal — индекс слабых сигналов (MSI)',
  cep: 'Cumulative Error Pressure — накопленное давление (не вероятность)',
  msi: 'Multisource Signal Index',
  taxonomy: '217 режимов v16 — классификация ошибок',
  pno: 'Persistent Non-Optimality PNO-1..7',
  egd: 'Echo-room Dynamics — давление эхо-камеры',
}

export const home = {
  title: 'Errorlogy — Прогноз',
  subtitle: 'Упрощённый интерфейс: потоковый и кейсовый прогноз, прозрачная методология.',
  caseForecastTitle: 'Кейсовый прогноз (Horizon 1)',
  caseForecastDesc:
    'Анализ одного governance-кейса: pipeline WMS → Classifier → … → FPD/T4D. ' +
    'Возвращает μ_forecast по режимам, сценарии и временную worldline. ' +
    'Подходит для разбора конкретного инцидента или документа.',
  streamForecastTitle: 'Потоковый прогноз (Horizon 2)',
  streamForecastDesc:
    'Агрегат по ingest-потоку: CEP-тренды, алерты эскалации, статистика стран. ' +
    'Не вычисляет календарные даты — показывает давление ошибки во времени.',
  methodologyTitle: 'Как мы прогнозируем',
  methodologyPoints: [
    'Документы → сигналы (MSI, CEP) через engine v1-math',
    'Кейс: нечёткая классификация 217 режимов → α-граф → FPD (μ_forecast) + T4D (worldline)',
    'Поток: агрегация сигналов по странам, пороги CEP, тренды за окно N дней',
    'μ ≠ вероятность; scenario_probability — отдельная величина сценария',
  ],
} as const

export const dataStreams = {
  title: 'Потоки данных',
  subtitle: 'Что входит в систему и как превращается в сигналы для прогноза.',
  pipelineSteps: [
    { id: 'sources', label: 'Источники', desc: 'RSS, gov APIs, ручной ввод, URL' },
    { id: 'ingest', label: 'Ingest', desc: 'Документы в SQLite, дедупликация' },
    { id: 'analyze', label: 'Анализ', desc: 'Engine/MAS → режимы, WMS, CEP' },
    { id: 'signals', label: 'Сигналы', desc: 'Временные ряды по странам' },
    { id: 'forecast', label: 'Прогноз', desc: 'Тренды, алерты, FPD по кейсам' },
  ],
} as const
