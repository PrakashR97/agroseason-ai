import { useEffect } from 'react'
import { api } from '../api'
import { useLang } from '../i18n'
import { JobCard } from '../components/ResearchPanel'
import { AsyncView, StatusBadge, useAsync } from '../components/ui'

export default function ResearchStatus() {
  const { t } = useLang()
  const jobs = useAsync(() => api.jobs(), [])
  const usage = useAsync(() => api.usage(), [])
  useEffect(() => {
    const active = jobs.data?.some((j) => ['queued', 'running'].includes(j.status))
    if (!active) return
    const i = setInterval(jobs.reload, 4000)
    return () => clearInterval(i)
  }, [jobs.data])  // eslint-disable-line

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">{t('research_title')}</h1>
      <section aria-labelledby="usage-h">
        <h2 id="usage-h" className="mb-2 text-xl font-bold">{t('usage')}</h2>
        <AsyncView state={usage}>{(u) => (
          <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {[[t('usage_serper'), `${u.serper_today} / ${u.serper_daily_limit}`],
              [t('usage_openai'), `${u.openai_today} / ${u.openai_daily_limit}`],
              [t('usage_month'), `${u.month_spend_usd} / ${u.monthly_budget_usd}`]].map(([k, v]) => (
              <div key={k} className="border-2 border-brand p-3"><dt className="text-sm">{k}</dt><dd className="text-xl font-bold">{v}</dd></div>))}
            <div className="border-2 border-brand p-3"><dt className="text-sm">Serper / OpenAI</dt>
              <dd className="flex gap-2"><StatusBadge status={u.serper_configured ? 'verified' : 'missing'} label={u.serper_configured ? t('usage_configured') : t('usage_not_configured')} />
                <StatusBadge status={u.openai_configured ? 'verified' : 'missing'} label={u.openai_configured ? t('usage_configured') : t('usage_not_configured')} /></dd></div>
          </dl>)}
        </AsyncView>
      </section>
      <section aria-labelledby="jobs-h">
        <h2 id="jobs-h" className="mb-2 text-xl font-bold">{t('recent_jobs')}</h2>
        <AsyncView state={jobs}>{(list) => list.length === 0 ? <p>{t('no_jobs')}</p> : (
          <ul className="space-y-3">{list.map((j) => <li key={j.id}><JobCard job={j} /></li>)}</ul>)}
        </AsyncView>
      </section>
    </div>
  )
}
