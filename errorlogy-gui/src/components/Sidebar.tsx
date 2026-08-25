import { useEffect, useState } from 'react'
import { NavLink } from 'react-router-dom'
import { LayoutDashboard, ScanSearch, BookOpen, Activity, Globe2, Radio, FileBarChart, TrendingUp, Waves } from 'lucide-react'
import { cn } from '../lib/utils'
import { checkApiHealth } from '../lib/api'
import { nav } from '../lib/en'

const links = [
  { to: '/',         icon: LayoutDashboard, label: nav.dashboard },
  { to: '/mas',      icon: Activity,        label: nav.mas },
  { to: '/ingest',   icon: Radio,           label: nav.ingest },
  { to: '/globe',    icon: Globe2,          label: nav.globe },
  { to: '/analyze',  icon: ScanSearch,      label: nav.analyze },
  { to: '/forecast', icon: TrendingUp,      label: nav.forecast },
  { to: '/forecast/stream', icon: Waves,    label: nav.streamForecast },
  { to: '/result',   icon: FileBarChart,    label: nav.result },
  { to: '/taxonomy', icon: BookOpen,        label: nav.taxonomy },
]

export function Sidebar() {
  const [apiOnline, setApiOnline] = useState<boolean | null>(null)

  useEffect(() => {
    let cancelled = false
    const poll = () => {
      checkApiHealth()
        .then(h => { if (!cancelled) setApiOnline(!!h) })
        .catch(() => { if (!cancelled) setApiOnline(false) })
    }
    poll()
    const id = window.setInterval(poll, 30_000)
    return () => { cancelled = true; window.clearInterval(id) }
  }, [])

  const apiTitle = apiOnline
    ? 'MAS API онлайн'
    : apiOnline === false
      ? 'MAS API офлайн'
      : 'Проверка API…'

  return (
    <div className="w-14 flex flex-col items-center py-4 gap-1 bg-slate-950 border-r border-slate-800 shrink-0">
      <div className="relative w-8 h-8 rounded-lg bg-red-600 flex items-center justify-center mb-4" title={apiTitle}>
        <Activity size={16} className="text-white" />
        <span className={cn(
          'absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-slate-950',
          apiOnline === null && 'bg-slate-500',
          apiOnline === true && 'bg-green-500',
          apiOnline === false && 'bg-red-500',
        )} />
      </div>
      {links.map(({ to, icon: Icon, label }) => (
        <NavLink key={to} to={to} title={label}
          className={({ isActive }) => cn(
            'w-10 h-10 flex items-center justify-center rounded-lg transition-colors',
            isActive
              ? 'bg-red-600/20 text-red-400'
              : 'text-slate-500 hover:text-slate-200 hover:bg-slate-800'
          )}>
          <Icon size={18} />
        </NavLink>
      ))}
    </div>
  )
}
