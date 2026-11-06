import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useLang } from '../i18n'

export function useAsync(fn, deps) {
  const [state, setState] = useState({ loading: true, data: null, error: null })
  const [tick, setTick] = useState(0)
  useEffect(() => {
    let live = true
    setState((s) => ({ ...s, loading: true, error: null }))
    fn().then(
      (data) => live && setState({ loading: false, data, error: null }),
      (error) => live && setState({ loading: false, data: null, error }),
    )
    return () => { live = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick])
  return { ...state, reload: () => setTick((n) => n + 1) }
}

export function Loading() {
  const { t } = useLang()
  return <p role="status" className="p-4 opacity-70">{t('loading')}</p>
}

export function ErrorBox({ error, onRetry }) {
  const { t } = useLang()
  return (
    <div role="alert" className="border-2 border-dashed border-brand p-4">
      <p className="font-semibold">{t('error')}</p>
      {error?.message && <p className="text-sm opacity-80">{error.message}</p>}
      {onRetry && <button className="btn-secondary mt-2" onClick={onRetry}>{t('retry')}</button>}
    </div>
  )
}

export function AsyncView({ state, children }) {
  if (state.loading && !state.data) return <Loading />
  if (state.error) return <ErrorBox error={state.error} onRetry={state.reload} />
  return children(state.data)
}

/** Verification state shown with border/fill/pattern, never extra colours. */
export function StatusBadge({ status, label }) {
  const { t } = useLang()
  const styles = {
    verified: 'bg-brand text-paper border-brand',
    review_required: 'bg-paper text-brand border-brand border-dashed',
    unverified: 'pattern-hatch text-brand border-brand',
    missing: 'bg-paper text-brand border-brand/40 opacity-70',
    catalog: 'bg-brand/10 text-brand border-brand/40',
  }
  const mark = { verified: '✓ ', review_required: '? ', unverified: '△ ', missing: '– ', catalog: '' }[status] ?? ''
  return (
    <span className={`inline-block border px-2 py-0.5 text-xs font-semibold ${styles[status] || styles.unverified}`}
      data-status={status}>
      {mark}{label || t(`status_${status}`)}
    </span>
  )
}

export function Pagination({ page, pageSize, total, onChange }) {
  const { t } = useLang()
  const pages = Math.max(1, Math.ceil(total / pageSize))
  if (pages <= 1) return null
  return (
    <nav aria-label="pagination" className="mt-4 flex items-center gap-3">
      <button className="btn-secondary" disabled={page <= 1} onClick={() => onChange(page - 1)}>{t('prev')}</button>
      <span>{t('page')} {page} / {pages}</span>
      <button className="btn-secondary" disabled={page >= pages} onClick={() => onChange(page + 1)}>{t('next')}</button>
    </nav>
  )
}

export function Field({ label, htmlFor, children }) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={htmlFor} className="text-sm font-semibold">{label}</label>
      {children}
    </div>
  )
}

export function DistrictSelect({ id = 'district', districts, value, onChange }) {
  const { t, name } = useLang()
  return (
    <Field label={t('district')} htmlFor={id}>
      <select id={id} className="input" value={value || ''} onChange={(e) => onChange(e.target.value)}>
        <option value="">{t('any_district')}</option>
        {(districts || []).map((d) => <option key={d.id} value={d.id}>{name(d)}</option>)}
      </select>
    </Field>
  )
}

export function MonthSelect({ id = 'month', value, onChange }) {
  const { t, months } = useLang()
  return (
    <Field label={t('month')} htmlFor={id}>
      <select id={id} className="input" value={value || ''} onChange={(e) => onChange(e.target.value)}>
        <option value="">{t('any_month')}</option>
        {months.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
      </select>
    </Field>
  )
}

export function CropCard({ crop, to, children }) {
  const { name, altName, t } = useLang()
  return (
    <Link to={to} className="block border-2 border-brand bg-paper p-4 hover:bg-brand/5">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="text-lg font-bold">{name(crop)}</h3>
          <p className="text-sm opacity-80">{altName(crop)}</p>
        </div>
        <StatusBadge status={crop.verification_status} />
      </div>
      {crop.scientific_name && <p className="mt-1 text-xs italic">{crop.scientific_name}</p>}
      <p className="mt-1 text-xs opacity-70">{name(crop.category)} · {t(`type_${crop.crop_type}`)}</p>
      {children}
    </Link>
  )
}

let districtCache = null
export function useDistricts() {
  const [list, setList] = useState(districtCache || [])
  useEffect(() => {
    if (districtCache) return
    api.districts().then((d) => { districtCache = d; setList(d) }).catch(() => {})
  }, [])
  return list
}
export const resetDistrictCache = () => { districtCache = null }
