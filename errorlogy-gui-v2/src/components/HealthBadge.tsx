import { useEffect, useState } from 'react'
import { Activity, Loader2 } from 'lucide-react'
import { checkApiHealth } from '../lib/api'
import type { HealthInfo } from '../lib/types'
import { cn } from '../lib/utils'

export function HealthBadge() {
  const [health, setHealth] = useState<HealthInfo | null>(null)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    let cancelled = false
    const poll = async () => {
      const h = await checkApiHealth()
      if (!cancelled) {
        setHealth(h)
        setChecking(false)
      }
    }
    void poll()
    const t = setInterval(poll, 15000)
    return () => {
      cancelled = true
      clearInterval(t)
    }
  }, [])

  if (checking && !health) {
    return (
      <span className="flex items-center gap-1.5 text-xs text-slate-500">
        <Loader2 size={12} className="animate-spin" />
        API…
      </span>
    )
  }

  const ok = health?.status === 'ok' || health?.status === 'healthy'

  return (
    <span
      className={cn(
        'flex items-center gap-1.5 text-xs px-2 py-1 rounded-full border',
        ok
          ? 'bg-emerald-900/30 text-emerald-300 border-emerald-800/50'
          : 'bg-red-900/30 text-red-300 border-red-800/50',
      )}
      title={health ? `engine ${health.engine ?? '—'} · ${health.taxonomy_modes} режимов` : commonOffline}
    >
      <Activity size={12} />
      {ok ? 'API OK' : 'API offline'}
      {ok && health?.engine && (
        <span className="text-emerald-500/80 font-mono hidden md:inline">{health.engine}</span>
      )}
    </span>
  )
}

const commonOffline = 'Запустите: cd errorlogy-mas && python api/main.py'
