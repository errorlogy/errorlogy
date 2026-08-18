import type { CaseAnalysis } from './types'
import { toIso3 } from './countryCodes'

const STORAGE_KEY = 'errorlogy_case_history'

export interface StoredCase {
  case_id: string
  title: string
  country: string
  iso3: string
  year: number
  dominant_pno: string
  max_mu: number
  cep: number
  cat: string
  echo_pressure: number
  analyzed_at: string
  engine_only?: boolean
}

export function loadStoredCases(): StoredCase[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

export function saveCase(
  analysis: CaseAnalysis,
  meta: { title?: string; country?: string; year?: number },
): StoredCase {
  const iso3 = toIso3(meta.country ?? '')
  const entry: StoredCase = {
    case_id: analysis.case_id,
    title: meta.title || analysis.case_id,
    country: meta.country ?? '',
    iso3,
    year: meta.year ?? 0,
    dominant_pno: analysis.pno.dominant_pno,
    max_mu: analysis.top_modes[0]?.mu ?? 0,
    cep: analysis.wms.cep,
    cat: analysis.cat.catastrophe_hypothesis,
    echo_pressure: analysis.egd.echo_room_pressure,
    analyzed_at: new Date().toISOString(),
    engine_only: analysis.metadata?.engine_only,
  }
  const cases = loadStoredCases().filter(c => c.case_id !== entry.case_id)
  cases.unshift(entry)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(cases.slice(0, 50)))
  return entry
}
