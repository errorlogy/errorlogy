import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const STAGE_COLORS: Record<string, string> = {
  weak_signal:     '#6366f1',
  ignored_warning: '#f59e0b',
  escalation:      '#ef4444',
  failure:         '#dc2626',
  inquiry:         '#10b981',
}

export const GRADE_COLOR: Record<string, string> = {
  weak:     'text-yellow-400 border-yellow-400/30 bg-yellow-400/10',
  moderate: 'text-blue-400 border-blue-400/30 bg-blue-400/10',
  strong:   'text-green-400 border-green-400/30 bg-green-400/10',
}

export const URGENCY_COLOR: Record<string, string> = {
  low:    'bg-slate-700 text-slate-300',
  medium: 'bg-amber-900/50 text-amber-300',
  high:   'bg-red-900/50 text-red-300',
}

export function muColor(mu: number): string {
  if (mu >= 0.75) return 'text-red-400'
  if (mu >= 0.5)  return 'text-amber-400'
  if (mu >= 0.25) return 'text-blue-400'
  return 'text-slate-500'
}

export function muBar(mu: number): string {
  if (mu >= 0.75) return 'bg-red-500'
  if (mu >= 0.5)  return 'bg-amber-500'
  if (mu >= 0.25) return 'bg-blue-500'
  return 'bg-slate-600'
}
