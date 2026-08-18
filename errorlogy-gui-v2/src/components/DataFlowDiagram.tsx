import { ArrowRight } from 'lucide-react'
import { cn } from '../lib/utils'

export interface FlowStep {
  id: string
  label: string
  desc?: string
  highlight?: boolean
}

export function DataFlowDiagram({ steps, className }: { steps: FlowStep[]; className?: string }) {
  return (
    <div className={cn('flex flex-wrap items-stretch gap-2', className)}>
      {steps.map((step, i) => (
        <div key={step.id} className="flex items-center gap-2 min-w-0">
          <div
            className={cn(
              'flex-1 min-w-[120px] rounded-xl border px-3 py-2.5',
              step.highlight
                ? 'bg-cyan-900/20 border-cyan-700/50'
                : 'bg-slate-800/80 border-slate-700/50',
            )}
          >
            <div className="text-xs font-semibold text-slate-200">{step.label}</div>
            {step.desc && (
              <div className="text-[10px] text-slate-500 mt-0.5 leading-snug">{step.desc}</div>
            )}
          </div>
          {i < steps.length - 1 && (
            <ArrowRight size={16} className="text-slate-600 shrink-0 hidden sm:block" />
          )}
        </div>
      ))}
    </div>
  )
}
