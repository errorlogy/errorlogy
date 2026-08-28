import { NavLink } from 'react-router-dom'
import { Home, Waves, FileSearch, Radio, Layers, GitFork } from 'lucide-react'
import { nav } from '../lib/en'
import { cn } from '../lib/utils'
import { HealthBadge } from './HealthBadge'

const links: Array<{ to: string; icon: typeof Home; label: string; end?: boolean }> = [
  { to: '/', icon: Home, label: nav.home, end: true },
  { to: '/stream', icon: Waves, label: nav.stream },
  { to: '/case', icon: FileSearch, label: nav.case },
  { to: '/data', icon: Radio, label: nav.data },
  { to: '/layers', icon: Layers, label: nav.layers },
  { to: '/discourse', icon: GitFork, label: nav.discourse },
]

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col min-h-screen bg-slate-900 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/95 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <span className="text-lg font-bold text-white shrink-0">
              Errorlogy <span className="text-cyan-400 font-normal text-sm">v2</span>
            </span>
            <span className="text-xs text-slate-500 hidden sm:inline truncate">
              Forecast · Streams · Methodology
            </span>
          </div>
          <HealthBadge />
        </div>
        <nav className="max-w-6xl mx-auto px-4 pb-2 flex gap-1 overflow-x-auto">
          {links.map(({ to, icon: Icon, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm whitespace-nowrap transition-colors',
                  isActive
                    ? 'bg-cyan-900/40 text-cyan-300 border border-cyan-800/50'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800',
                )
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="flex-1 max-w-6xl w-full mx-auto">{children}</main>
    </div>
  )
}
