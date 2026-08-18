import { Minus, Square, X } from 'lucide-react'

declare global {
  interface Window {
    electron?: {
      minimize: () => void
      maximize: () => void
      close: () => void
    }
  }
}

export function TitleBar() {
  const e = window.electron
  return (
    <div className="flex items-center justify-between h-9 bg-slate-950 select-none shrink-0 px-4 border-b border-slate-800"
         style={{ WebkitAppRegion: 'drag' } as React.CSSProperties}>
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-red-500" />
        <span className="text-xs font-semibold tracking-widest text-slate-400 uppercase">Errorlogy</span>
      </div>
      {e && (
        <div className="flex items-center gap-1" style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}>
          <button onClick={e.minimize}
            className="w-7 h-7 flex items-center justify-center rounded hover:bg-slate-700 text-slate-400 hover:text-white transition-colors">
            <Minus size={12} />
          </button>
          <button onClick={e.maximize}
            className="w-7 h-7 flex items-center justify-center rounded hover:bg-slate-700 text-slate-400 hover:text-white transition-colors">
            <Square size={11} />
          </button>
          <button onClick={e.close}
            className="w-7 h-7 flex items-center justify-center rounded hover:bg-red-600 text-slate-400 hover:text-white transition-colors">
            <X size={12} />
          </button>
        </div>
      )}
    </div>
  )
}
