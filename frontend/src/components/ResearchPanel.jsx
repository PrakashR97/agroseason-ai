import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import { useLang } from '../i18n'
import { StatusBadge } from './ui'

export function JobCard({ job }) {
  const { t } = useLang()
  const r = job.result || {}
  return (
    <div className="border-2 border-brand p-3" data-testid="job-card">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="font-semibold">{t('job_status')}: <span data-testid="job-status">{t(`job_${job.status}`)}</span></span>
        <span className="text-xs opacity-70">{job.id.slice(0, 8)}</span>
      </div>
      {job.error && <p className="mt-1 text-sm">{job.error}</p>}
      {r.message && <p className="mt-1 font-semibold">{t('insufficient')}</p>}
      {r.sources?.length > 0 && (
        <div className="mt-2"><p className="text-sm font-semibold">{t('sources_used')}</p>
          <ul className="list-disc pl-5 text-sm">
            {r.sources.map((s) => <li key={s.id}><a className="underline" href={s.url} target="_blank" rel="noreferrer noopener">{s.title}</a>{' '}
              <StatusBadge status={s.trusted ? 'verified' : 'review_required'} /></li>)}
          </ul></div>
      )}
      {r.missing_sections?.length > 0 && (
        <p className="mt-2 text-sm"><span className="font-semibold">{t('missing_info')}:</span> {r.missing_sections.length}</p>
      )}
    </div>
  )
}

/** Requests research for a crop (+district/month) and polls the background job. */
export default function ResearchPanel({ crop, districtId, districts, month }) {
  const { t } = useLang()
  const [state, setState] = useState(null)
  const [job, setJob] = useState(null)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)
  const timer = useRef()
  useEffect(() => () => clearTimeout(timer.current), [])

  const poll = (id) => {
    api.job(id).then((j) => {
      setJob(j)
      if (['queued', 'running'].includes(j.status)) timer.current = setTimeout(() => poll(id), 2500)
    }).catch((e) => setError(e))
  }

  const start = async () => {
    setBusy(true); setError(null)
    try {
      const dName = districts?.find((d) => String(d.id) === String(districtId))?.name_en
      const res = await api.research({ crop: crop.name_en, district: dName || undefined, month: month ? Number(month) : undefined })
      setState(res.state)
      if (res.job) { setJob(res.job); poll(res.job.id) }
    } catch (e) { setError(e) } finally { setBusy(false) }
  }

  return (
    <section aria-labelledby="research-h" className="border-2 border-brand p-4">
      <h2 id="research-h" className="text-xl font-bold">{t('research_title')}</h2>
      <p className="mt-1 text-sm opacity-80">{t('research_hint')}</p>
      <button className="btn-primary mt-3" onClick={start} disabled={busy}>{t('request_research')}</button>
      {error && <p role="alert" className="mt-2 font-semibold">{error.message}</p>}
      {state && !job && <p className="mt-2" role="status">{t({ cached: 'state_cached', budget_exhausted: 'state_budget' }[state] || 'state_queued')}</p>}
      {state === 'existing_job' && <p className="mt-2">{t('state_existing')}</p>}
      {job && <div className="mt-3" aria-live="polite"><JobCard job={job} /></div>}
    </section>
  )
}
