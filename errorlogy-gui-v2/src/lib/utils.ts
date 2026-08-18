import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const SEVERITY_STYLE: Record<string, string> = {
  high: 'bg-red-900/40 text-red-300 border-red-800/50',
  medium: 'bg-amber-900/30 text-amber-300 border-amber-800/40',
  low: 'bg-slate-800 text-slate-400 border-slate-700',
}

export const URGENCY_COLOR: Record<string, string> = {
  low: 'bg-slate-700 text-slate-300',
  medium: 'bg-amber-900/50 text-amber-300',
  high: 'bg-red-900/50 text-red-300',
}

export function muColor(mu: number): string {
  if (mu >= 0.75) return 'text-red-400'
  if (mu >= 0.5) return 'text-amber-400'
  if (mu >= 0.25) return 'text-blue-400'
  return 'text-slate-500'
}
