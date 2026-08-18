import { useEffect, useMemo, useRef, useState } from 'react'
import Globe, { type GlobeMethods } from 'react-globe.gl'
import type { CountryStats } from '../lib/types'
import { intensityColor, maxCases, statsByIso3 } from '../lib/countryStats'

interface GeoFeature {
  properties: Record<string, string>
  geometry: unknown
}

interface Props {
  countries: CountryStats[]
  selectedIso3: string | null
  onSelect: (iso3: string | null, stats: CountryStats | null) => void
}

// Local bundle — file:// in Electron cannot use protocol-relative //cdn URLs
const GEO_URL = `${import.meta.env.BASE_URL}geo/countries-110m.geojson`
const EARTH_IMG = 'https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-night.jpg'
const EARTH_BUMP = 'https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-topology.png'
const SKY_IMG = 'https://cdn.jsdelivr.net/npm/three-globe/example/img/night-sky.png'

function featureIso(f: GeoFeature): string {
  const p = f.properties
  const iso = p.ISO_A3 || p.ADM0_A3 || p.GU_A3 || ''
  return iso === '-99' ? '' : iso
}

export function ErrorlogyGlobe({ countries, selectedIso3, onSelect }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const globeRef = useRef<GlobeMethods | undefined>(undefined)
  const [polygons, setPolygons] = useState<GeoFeature[]>([])
  const [geoError, setGeoError] = useState('')
  const [dims, setDims] = useState({ w: 800, h: 600 })

  const lookup = useMemo(() => statsByIso3(countries), [countries])
  const maxC = useMemo(() => maxCases(countries), [countries])

  useEffect(() => {
    setGeoError('')
    fetch(GEO_URL)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then((geo: { features: GeoFeature[] }) => setPolygons(geo.features))
      .catch((e: Error) => {
        setPolygons([])
        setGeoError(e.message || 'GeoJSON load failed')
      })
  }, [])

  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const ro = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect
      if (width > 0 && height > 0) setDims({ w: Math.floor(width), h: Math.floor(height) })
    })
    ro.observe(el)
    const rect = el.getBoundingClientRect()
    if (rect.width > 0 && rect.height > 0) {
      setDims({ w: Math.floor(rect.width), h: Math.floor(rect.height) })
    }
    return () => ro.disconnect()
  }, [])

  useEffect(() => {
    const g = globeRef.current
    if (!g?.pointOfView || !selectedIso3) return
    const target = polygons.find(f => featureIso(f) === selectedIso3)
    if (!target) return
    const coords = JSON.stringify(target.geometry)
    const nums = coords.match(/-?\d+\.?\d*/g)?.map(Number) ?? []
    if (nums.length >= 2) {
      let latSum = 0, lngSum = 0, n = 0
      for (let i = 0; i < nums.length - 1; i += 2) {
        const lng = nums[i], lat = nums[i + 1]
        if (Math.abs(lat) <= 90 && Math.abs(lng) <= 180) {
          lngSum += lng; latSum += lat; n++
        }
      }
      if (n > 0) {
        g.pointOfView({ lat: latSum / n, lng: lngSum / n, altitude: 1.6 }, 800)
      }
    }
  }, [selectedIso3, polygons])

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full min-h-[420px] rounded-xl overflow-hidden bg-slate-950 border border-slate-800"
    >
      {geoError && (
        <div className="absolute top-3 left-3 z-10 bg-red-900/80 border border-red-700 text-red-200 text-xs px-3 py-2 rounded-lg">
          Map data: {geoError}
        </div>
      )}
      {polygons.length === 0 && !geoError && (
        <div className="absolute inset-0 flex items-center justify-center text-slate-500 text-sm">
          Loading globe…
        </div>
      )}
      {dims.w > 0 && dims.h > 0 && (
        <Globe
          ref={globeRef}
          width={dims.w}
          height={dims.h}
          backgroundColor="rgba(2, 6, 23, 0)"
          globeImageUrl={EARTH_IMG}
          bumpImageUrl={EARTH_BUMP}
          backgroundImageUrl={SKY_IMG}
          polygonsData={polygons}
          polygonAltitude={(d: object) => {
            const iso = featureIso(d as GeoFeature)
            const s = lookup.get(iso)
            return s ? 0.015 + (s.cases / maxC) * 0.1 : 0.004
          }}
          polygonCapColor={(d: object) => {
            const iso = featureIso(d as GeoFeature)
            if (iso === selectedIso3) return 'rgba(248, 113, 113, 0.92)'
            const s = lookup.get(iso)
            if (!s) return 'rgba(30, 41, 59, 0.25)'
            return intensityColor(s.cases / maxC)
          }}
          polygonSideColor={() => 'rgba(239, 68, 68, 0.2)'}
          polygonStrokeColor={() => 'rgba(148, 163, 184, 0.35)'}
          polygonLabel={(d: object) => {
            const iso = featureIso(d as GeoFeature)
            const s = lookup.get(iso)
            const name = (d as GeoFeature).properties?.NAME || iso
            if (!s) return `<div style="color:#94a3b8;font-size:11px">${name}</div>`
            return `<div style="background:#0f172a;border:1px solid #334155;border-radius:6px;padding:6px 8px;font-size:11px;color:#e2e8f0">
              <b>${s.name}</b><br/>
              Cases: ${s.cases} · avg mu ${s.avg_mu.toFixed(2)}<br/>
              PNO: ${s.dominant_pno} · CEP ${s.max_cep.toFixed(2)}
            </div>`
          }}
          onPolygonClick={(d: object) => {
            const iso = featureIso(d as GeoFeature)
            if (!iso) return
            onSelect(iso, lookup.get(iso) ?? null)
          }}
          atmosphereColor="#ef4444"
          atmosphereAltitude={0.14}
          animateIn
        />
      )}
    </div>
  )
}
