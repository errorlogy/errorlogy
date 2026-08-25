/** Shared 14-agent pipeline definition — matches errorlogy-mas orchestrator. */

export type AgentKind = 'engine' | 'llm'

export interface PipelineStep {
  id: string
  label: string
  desc: string
  kind: AgentKind
}

export const PIPELINE_STEPS: PipelineStep[] = [
  { id: 'scout',         label: 'Scout',         desc: 'Extract structure + weak signals', kind: 'llm' },
  { id: 'wms',           label: 'WMS',           desc: 'Multisource Signal Index', kind: 'engine' },
  { id: 'classifier',    label: 'Classifier',    desc: 'Fuzzy μ scoring (217 modes)', kind: 'engine' },
  { id: 'alpha',         label: 'α-Propagation', desc: 'Graph activation', kind: 'engine' },
  { id: 'pno',           label: 'PNO',           desc: 'System regime PNO-1..7', kind: 'engine' },
  { id: 'acc',           label: 'ACC',           desc: 'Contribution clusters', kind: 'engine' },
  { id: 'egd',           label: 'EGD',           desc: 'Echo-room dynamics', kind: 'engine' },
  { id: 't4d',           label: 'T4D',           desc: 'Temporal worldline', kind: 'engine' },
  { id: 'cat',           label: 'CAT',           desc: 'Catastrophe hypothesis', kind: 'engine' },
  { id: 'fpd',           label: 'FPD',           desc: 'Fuzzy forecast', kind: 'engine' },
  { id: 'lbi',           label: 'LBI',           desc: 'Betterment alternatives', kind: 'llm' },
  { id: 'red_team',      label: 'Red Team',      desc: 'Adversarial review', kind: 'llm' },
  { id: 'card_compiler', label: 'Card Compiler', desc: 'Public explanation card', kind: 'llm' },
  { id: 'neutrality',    label: 'Neutrality',    desc: 'Language audit', kind: 'llm' },
]

export const AGENT_LABELS: Record<string, string> = Object.fromEntries(
  PIPELINE_STEPS.map(s => [s.id, `${s.label} — ${s.desc}`]),
)
