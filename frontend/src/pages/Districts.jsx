import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'
import { useLang } from '../i18n'
import { AsyncView, CropCard, MonthSelect, Pagination, StatusBadge, useAsync, useDistricts } from '../components/ui'

export function Districts() {
  const { t, name, altName } = useLang()
  const districts = useDistricts()
  const regions = [...new Set(districts.map((d) => d.region))]
  return (
    <div>
      <h1 className="mb-4 text-3xl font-bold">{t('districts_title')}</h1>
      {districts.length === 0 && <p role="status">{t('loading')}</p>}
      {regions.map((r) => (
        <section key={r} className="mb-6" aria-label={r}>
          <h2 className="mb-2 border-b-2 border-brand text-lg font-bold">{r}</h2>
          <ul className="grid grid-cols-2 gap-2 md:grid-cols-4">
            {districts.filter((d) => d.region === r).map((d) => (
              <li key={d.id}><Link to={`/districts/${d.id}`} className="block border-2 border-brand p-3 hover:bg-brand hover:text-paper">
                <span className="font-semibold">{name(d)}</span><br /><span className="text-sm opacity-80">{altName(d)}</span></Link></li>))}
          </ul>
        </section>))}
    </div>
  )
}

export function DistrictDetail() {
  const { id } = useParams()
  const { t, name, altName, months } = useLang()
  const districts = useDistricts()
  const [month, setMonth] = useState('')
  const [page, setPage] = useState(1)
  const d = districts.find((x) => String(x.id) === id)
  const list = useAsync(() => api.districtCrops(id, { month, page, page_size: 24 }), [id, month, page])
  return (
    <div>
      <p><Link className="underline" to="/districts">← {t('districts_title')}</Link></p>
      <h1 className="text-3xl font-bold">{d ? name(d) : ''} <span className="text-xl font-normal">{d ? altName(d) : ''}</span></h1>
      <h2 className="mt-4 text-xl font-bold">{t('district_crops')}</h2>
      <p className="mb-3 text-sm opacity-80">{t('district_crops_hint')}</p>
      <div className="mb-4 max-w-xs"><MonthSelect id="dd-month" value={month} onChange={(v) => { setMonth(v); setPage(1) }} /></div>
      <AsyncView state={list}>{(res) => res.items.length === 0
        ? <p className="border-2 border-dashed border-brand p-4">{t('insufficient')}</p>
        : <>
          <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {res.items.map((it) => (
              <li key={it.crop.id}>
                <CropCard crop={it.crop} to={`/crops/${it.crop.id}?district=${id}${month ? `&month=${month}` : ''}`}>
                  <div className="mt-2 flex flex-wrap gap-2 text-xs">
                    <StatusBadge status={it.verification_status} />
                    <span className="border border-brand px-2 py-0.5">{t(`scope_${it.scope}`)}</span>
                    {it.seasons.join(', ')}{month && ` · ${months[month - 1]}`}
                  </div>
                </CropCard>
              </li>))}
          </ul>
          <Pagination page={res.page} pageSize={res.page_size} total={res.total} onChange={setPage} />
        </>}
      </AsyncView>
    </div>
  )
}
