import { cn, muColor, muBar, GRADE_COLOR } from '../lib/utils'
import type { ModeScore } from '../lib/types'

export function ModeBadge({ mode, compact }: { mode: ModeScore; compact?: boolean }) {
  if (compact) {
    return (
      <span className={cn('inline-flex items-center gap-1 text-xs font-mono px-1.5 py-0.5 rounded border', GRADE_COLOR[mode.evidence_grade])}>
        {mode.mode_id}
        <span className={cn('font-bold', muColor(mode.mu))}>{mode.mu.toFixed(2)}</span>
      </span>
    )
  }
  return (
    <div className="bg-slate-800 rounded-lg p-3 space-y-2">
      <div className="flex items-center justify-between gap-2">
        <span className="font-mono text-xs text-slate-400">{mode.mode_id}</span>
        <span className={cn('text-xs px-1.5 py-0.5 rounded border', GRADE_COLOR[mode.evidence_grade])}>
          {mode.evidence_grade}
        </span>
      </div>
      <p className="text-sm text-slate-200 leading-snug">{mode.name}</p>
      <div className="flex items-center gap-2">
        <div className="flex-1 h-1.5 rounded-full bg-slate-700 overflow-hidden">
          <div className={cn('h-full rounded-full transition-all', muBar(mode.mu))} style={{ width: `${mode.mu * 100}%` }} />
        </div>
        <span className={cn('text-xs font-bold font-mono w-10 text-right', muColor(mode.mu))}>μ {mode.mu.toFixed(2)}</span>
      </div>
    </div>
  )
}
