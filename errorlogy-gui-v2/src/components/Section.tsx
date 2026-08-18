import { cn } from '../lib/utils'

export function Section({
  title,
  icon,
  children,
  className,
}: {
  title: string
  icon?: React.ReactNode
  children: React.ReactNode
  className?: string
}) {
  return (
    <div className={cn('bg-slate-800 rounded-xl overflow-hidden', className)}>
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700/50">
        {icon}
        <span className="text-xs text-slate-400 uppercase tracking-widest font-semibold">{title}</span>
      </div>
      <div className="p-4">{children}</div>
    </div>
  )
}

export function Stat({ label, value, mono }: { label: string; value: string | number; mono?: boolean }) {
  return (
    <div className="bg-slate-900 rounded-lg p-3">
      <div className="text-[10px] text-slate-500 uppercase">{label}</div>
      <div className={cn('text-lg font-bold text-slate-200 mt-1', mono && 'text-sm font-mono')}>{value}</div>
    </div>
  )
}
