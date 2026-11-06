import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from '../App'
import CalendarGrid from '../components/CalendarGrid'
import { StatusBadge, resetDistrictCache } from '../components/ui'
import { LangProvider } from '../i18n'

const districts = [
  { id: 1, slug: 'salem', name_en: 'Salem', name_ta: 'சேலம்', region: 'Western' },
  { id: 2, slug: 'namakkal', name_en: 'Namakkal', name_ta: 'நாமக்கல்', region: 'Western' },
]
const cat = { id: 1, slug: 'vegetables', name_en: 'Vegetables', name_ta: 'காய்கறிகள்' }
const tomato = { id: 7, slug: 'tomato', name_en: 'Tomato', name_ta: 'தக்காளி', scientific_name: 'Solanum lycopersicum',
  crop_type: 'repeated_harvest', verification_status: 'unverified', category: cat }

function mockApi(routes) {
  globalThis.fetch = vi.fn(async (url, opts) => {
    const path = String(url)
    const key = Object.keys(routes).find((k) => path.startsWith(k))
    if (!key) return { ok: false, status: 404, json: async () => ({ detail: 'nf' }) }
    const body = typeof routes[key] === 'function' ? routes[key](path, opts) : routes[key]
    return { ok: true, status: 200, json: async () => body }
  })
}

const base = {
  '/api/districts/1/crops': { items: [{ crop: tomato, scope: 'district', verification_status: 'verified', seasons: ['Rabi'], month_suitability: 'recommended' }], total: 1, page: 1, page_size: 12 },
  '/api/districts': districts,
  '/api/categories': [cat],
  '/api/crops/search': [{ crop: tomato, score: 1, matched_alias: 'thakkali', month_suitability: null }],
  '/api/crops?': { items: [tomato], total: 1, page: 1, page_size: 24 },
}

const renderApp = (path = '/', lang = 'en') =>
  render(<MemoryRouter initialEntries={[path]}><LangProvider initial={lang}><App /></LangProvider></MemoryRouter>)

beforeEach(() => { resetDistrictCache(); localStorage.clear() })
afterEach(() => vi.restoreAllMocks())

describe('home', () => {
  it('renders branding, search and categories', async () => {
    mockApi(base)
    renderApp()
    expect(screen.getByRole('heading', { name: 'AgroSeason AI' })).toBeInTheDocument()
    expect(screen.getByRole('combobox', { name: 'Crop' })).toBeInTheDocument()
    expect(await screen.findByRole('link', { name: 'Vegetables' })).toBeInTheDocument()
  })

  it('shows suggestions for a Thanglish query', async () => {
    mockApi(base)
    renderApp()
    await userEvent.type(screen.getByRole('combobox', { name: 'Crop' }), 'thakkali')
    const opt = await screen.findByRole('option', { name: /Tomato/ })
    expect(opt).toHaveTextContent('தக்காளி')
    expect(fetch.mock.calls.some(([u]) => String(u).includes('q=thakkali'))).toBe(true)
  })

  it('switches language to Tamil', async () => {
    mockApi(base)
    renderApp()
    await userEvent.click(screen.getByRole('button', { name: 'தமிழ்' }))
    expect(await screen.findByRole('heading', { name: 'அக்ரோசீசன் AI' })).toBeInTheDocument()
    expect(localStorage.getItem('lang')).toBe('ta')
    expect(await screen.findByRole('link', { name: 'காய்கறிகள்' })).toBeInTheDocument()
  })

  it('seasonal discovery appears once district and month are picked', async () => {
    mockApi(base)
    renderApp()
    expect(screen.getByText(/Choose a district and month/)).toBeInTheDocument()
    await waitFor(() => expect(screen.getByRole('option', { name: 'Salem' })).toBeInTheDocument())
    await userEvent.selectOptions(screen.getByLabelText('District'), '1')
    await userEvent.selectOptions(screen.getByLabelText('Month'), '11')
    const link = await screen.findByRole('link', { name: /Tomato/ })
    expect(link).toHaveAttribute('href', '/crops/7?district=1&month=11')
  })
})

describe('components', () => {
  it('StatusBadge distinguishes states with text and pattern, not colour', () => {
    const { rerender } = render(<LangProvider initial="en"><StatusBadge status="verified" /></LangProvider>)
    expect(screen.getByText(/Verified/)).toHaveAttribute('data-status', 'verified')
    rerender(<LangProvider initial="en"><StatusBadge status="unverified" /></LangProvider>)
    expect(screen.getByText(/Unverified/).className).toContain('pattern-hatch')
    rerender(<LangProvider initial="en"><StatusBadge status="review_required" /></LangProvider>)
    expect(screen.getByText(/Review required/).className).toContain('border-dashed')
  })

  it('CalendarGrid renders 12 months, phases and the honest empty state', async () => {
    const months = Array.from({ length: 12 }, (_, i) => ({
      month: i + 1, phases: i === 10 ? ['sowing'] : i === 1 ? ['harvest'] : [], suitability: i === 10 ? 'recommended' : 'not_documented',
      all_verified: i === 10 || i === 1 ? true : null, seasons: [],
    }))
    const onSelect = vi.fn()
    render(<LangProvider initial="en"><CalendarGrid data={{ months, seasons: [], message: null }} selectedMonth={11} onSelectMonth={onSelect} /></LangProvider>)
    expect(screen.getAllByRole('columnheader')).toHaveLength(13)
    expect(screen.getByTestId('cell-sowing-11')).toHaveAttribute('data-active', 'true')
    expect(screen.getByTestId('cell-sowing-11').className).toContain('bg-brand')
    expect(screen.getByTestId('cell-sowing-3')).toHaveAttribute('data-active', 'false')
    expect(screen.getByTestId('suit-11')).toHaveTextContent('Verified')
    await userEvent.click(screen.getByRole('button', { name: 'March' }))
    expect(onSelect).toHaveBeenCalledWith(3)
  })

  it('CalendarGrid shows insufficient information message', () => {
    const months = Array.from({ length: 12 }, (_, i) => ({ month: i + 1, phases: [], suitability: 'not_documented', all_verified: null, seasons: [] }))
    render(<LangProvider initial="en"><CalendarGrid data={{ months, seasons: [], message: 'x' }} /></LangProvider>)
    expect(screen.getByText('Insufficient verified information.')).toBeInTheDocument()
  })
})

describe('crop detail', () => {
  const detail = {
    ...tomato, description_en: null, description_ta: null, aliases: ['thakkali'], season_records: 0, verified_season_records: 0,
    varieties: [{ id: 1, name: 'PKM 1', notes: null, verification_status: 'unverified' }],
  }
  const months = Array.from({ length: 12 }, (_, i) => ({ month: i + 1, phases: [], suitability: 'not_documented', all_verified: null, seasons: [] }))
  const routes = {
    ...base,
    '/api/crops/7/districts': [],
    '/api/crops/7': detail,
    '/api/calendar': { scope: 'none', months, seasons: [], message: 'Insufficient verified information.', selected_month: { month: 11, suitability: 'not_documented', phases: [] } },
    '/api/cultivation-guide': { documented_sections: 0, total_sections: 2, sections: [
      { key: 'soil', label_en: 'Soil requirements', label_ta: 'மண் தேவைகள்', status: 'missing', value: null, sources: [] },
      { key: 'scientific_name', label_en: 'Scientific name', label_ta: 'அறிவியல் பெயர்', status: 'catalog', value: 'Solanum lycopersicum', sources: [] }] },
    '/api/sketches/7': { status: 'placeholder', image_url: null, job_id: null, reason: 'x' },
  }

  it('never fabricates data: missing sections and no-window banner', async () => {
    mockApi(routes)
    renderApp('/crops/7?district=1&month=11')
    expect(await screen.findByRole('heading', { name: 'Tomato' })).toBeInTheDocument()
    const banner = await screen.findByTestId('month-banner')
    expect(banner).toHaveTextContent('November has no documented sowing window')
    expect(banner).toHaveTextContent('Insufficient verified information.')
    const soil = (await screen.findByText('Soil requirements')).closest('div')
    expect(within(soil).getByText('Insufficient verified information.')).toBeInTheDocument()
    expect(screen.getByText('PKM 1')).toBeInTheDocument()
    expect(screen.getByText('No references stored yet.')).toBeInTheDocument()
  })

  it('research request shows job status', async () => {
    const job = { id: 'abcdef12-0000', kind: 'research', status: 'queued', error: null, result: {} }
    mockApi({ ...routes,
      '/api/research/jobs/abcdef12-0000': { ...job, status: 'completed', result: { sources: [{ id: 1, url: 'https://tnau.ac.in/x', title: 'TNAU page', trusted: true }], missing_sections: ['a'] } },
      '/api/research': (_, o) => (o?.method === 'POST' ? { state: 'queued', job } : {}) })
    renderApp('/crops/7')
    await userEvent.click(await screen.findByRole('button', { name: 'Request research' }))
    expect(await screen.findByTestId('job-status')).toHaveTextContent(/Queued|Completed/)
    expect(await screen.findByText('TNAU page', {}, { timeout: 4000 })).toHaveAttribute('href', 'https://tnau.ac.in/x')
  })
})

describe('districts', () => {
  it('lists districts in Tamil and English', async () => {
    mockApi(base)
    renderApp('/districts', 'ta')
    expect(await screen.findByRole('link', { name: /சேலம்/ })).toHaveAttribute('href', '/districts/1')
  })
})
