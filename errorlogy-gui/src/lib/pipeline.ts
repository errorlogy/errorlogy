/** Shared 14-agent pipeline definition — matches errorlogy-mas orchestrator. */



export type AgentKind = 'engine' | 'llm'



export interface PipelineStep {

  id: string

  label: string

  desc: string

  descRu: string

  kind: AgentKind

}



export const PIPELINE_STEPS: PipelineStep[] = [

  { id: 'scout',         label: 'Scout',         desc: 'Extract structure + weak signals', descRu: 'Структура кейса + слабые сигналы', kind: 'llm' },

  { id: 'wms',           label: 'WMS',           desc: 'Multisource Signal Index', descRu: 'Индекс мультиисточниковых сигналов', kind: 'engine' },

  { id: 'classifier',    label: 'Classifier',    desc: 'Fuzzy μ scoring (217 modes)', descRu: 'Нечёткая μ по 217 режимам', kind: 'engine' },

  { id: 'alpha',         label: 'α-Propagation', desc: 'Graph activation', descRu: 'Распространение по графу α', kind: 'engine' },

  { id: 'pno',           label: 'PNO',           desc: 'System regime PNO-1..7', descRu: 'Режим системы PNO-1..7', kind: 'engine' },

  { id: 'acc',           label: 'ACC',           desc: 'Contribution clusters', descRu: 'Кластеры вклада ошибок', kind: 'engine' },

  { id: 'egd',           label: 'EGD',           desc: 'Echo-room dynamics', descRu: 'Динамика эхо-камеры', kind: 'engine' },

  { id: 't4d',           label: 'T4D',           desc: 'Temporal worldline', descRu: 'Временная worldline', kind: 'engine' },

  { id: 'cat',           label: 'CAT',           desc: 'Catastrophe hypothesis', descRu: 'Гипотеза катастрофы', kind: 'engine' },

  { id: 'fpd',           label: 'FPD',           desc: 'Fuzzy forecast', descRu: 'Нечёткий прогноз траектории', kind: 'engine' },

  { id: 'lbi',           label: 'LBI',           desc: 'Betterment alternatives', descRu: 'Альтернативы улучшения', kind: 'llm' },

  { id: 'red_team',      label: 'Red Team',      desc: 'Adversarial review', descRu: 'Adversarial review', kind: 'llm' },

  { id: 'card_compiler', label: 'Card Compiler', desc: 'Public explanation', descRu: 'Публичная карточка объяснения', kind: 'llm' },

  { id: 'neutrality',    label: 'Neutrality',    desc: 'Language audit', descRu: 'Аудит нейтральности языка', kind: 'llm' },

]



export const AGENT_LABELS: Record<string, string> = Object.fromEntries(

  PIPELINE_STEPS.map(s => [s.id, `${s.label} — ${s.descRu}`]),

)

