/** Normalize free-text country input to ISO 3166-1 alpha-3 for globe matching. */
const ALIASES: Record<string, string> = {
  us: 'USA', usa: 'USA', 'united states': 'USA', 'united states of america': 'USA',
  uk: 'GBR', gbr: 'GBR', 'united kingdom': 'GBR', britain: 'GBR', england: 'GBR',
  fr: 'FRA', fra: 'FRA', france: 'FRA',
  de: 'DEU', deu: 'DEU', germany: 'DEU', deutschland: 'DEU',
  jp: 'JPN', jpn: 'JPN', japan: 'JPN',
  ru: 'RUS', rus: 'RUS', russia: 'RUS', 'russian federation': 'RUS',
  cn: 'CHN', chn: 'CHN', china: 'CHN',
  br: 'BRA', bra: 'BRA', brazil: 'BRA',
  in: 'IND', ind: 'IND', india: 'IND',
  ua: 'UKR', ukr: 'UKR', ukraine: 'UKR',
  ca: 'CAN', can: 'CAN', canada: 'CAN',
  au: 'AUS', aus: 'AUS', australia: 'AUS',
  za: 'ZAF', zaf: 'ZAF', 'south africa': 'ZAF',
  mx: 'MEX', mex: 'MEX', mexico: 'MEX',
  sa: 'SAU', sau: 'SAU', 'saudi arabia': 'SAU',
  kr: 'KOR', kor: 'KOR', 'south korea': 'KOR', korea: 'KOR',
  it: 'ITA', ita: 'ITA', italy: 'ITA',
  es: 'ESP', esp: 'ESP', spain: 'ESP',
  ng: 'NGA', nga: 'NGA', nigeria: 'NGA',
  eg: 'EGY', egy: 'EGY', egypt: 'EGY',
  pl: 'POL', pol: 'POL', poland: 'POL',
  tr: 'TUR', tur: 'TUR', turkey: 'TUR', türkiye: 'TUR',
}

export function toIso3(country: string): string {
  const raw = country.trim()
  if (!raw) return ''
  if (/^[A-Z]{3}$/.test(raw)) return raw
  const key = raw.toLowerCase()
  return ALIASES[key] ?? raw.toUpperCase().slice(0, 3)
}
