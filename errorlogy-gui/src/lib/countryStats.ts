import type { CountryStats, CountryStatsResponse } from './types'
import { loadStoredCases } from './caseStore'

export function mergeCountryStats(seed: CountryStatsResponse): CountryStats[] {
  const byIso = new Map<string, CountryStats>()
  for (const c of seed.countries) {
    byIso.set(c.iso3, { ...c, recent_cases: [...c.recent_cases] })
  }

  const local = loadStoredCases()
  for (const lc of local) {
    if (!lc.iso3) continue
    const existing = byIso.get(lc.iso3)
    const summary = {
      case_id: lc.case_id,
      title: lc.title,
      year: lc.year,
      country: lc.country,
      dominant_pno: lc.dominant_pno,
      max_mu: lc.max_mu,
      cep: lc.cep,
      cat: lc.cat,
    }
    if (existing) {
      if (!existing.recent_cases.some(r => r.case_id === lc.case_id)) {
        existing.recent_cases.unshift(summary)
        existing.cases += 1
      }
      existing.avg_mu = (existing.avg_mu + lc.max_mu) / 2
      existing.max_cep = Math.max(existing.max_cep, lc.cep)
      existing.avg_echo_pressure = (existing.avg_echo_pressure + lc.echo_pressure) / 2
      existing.dominant_pno = lc.dominant_pno
    } else {
      byIso.set(lc.iso3, {
        iso3: lc.iso3,
        name: lc.country || lc.iso3,
        cases: 1,
        avg_mu: lc.max_mu,
        max_cep: lc.cep,
        avg_echo_pressure: lc.echo_pressure,
        dominant_pno: lc.dominant_pno,
        top_families: {},
        recent_cases: [summary],
      })
    }
  }

  return Array.from(byIso.values()).sort((a, b) => b.cases - a.cases)
}

export function statsByIso3(countries: CountryStats[]): Map<string, CountryStats> {
  return new Map(countries.map(c => [c.iso3, c]))
}

/** Choropleth color from case intensity [0,1]. */
export function intensityColor(intensity: number): string {
  const t = Math.max(0, Math.min(1, intensity))
  const r = Math.round(120 + t * 135)
  const g = Math.round(40 - t * 30)
  const b = Math.round(60 - t * 40)
  return `rgba(${r}, ${g}, ${b}, ${0.55 + t * 0.4})`
}

export function maxCases(countries: CountryStats[]): number {
  return Math.max(1, ...countries.map(c => c.cases))
}
