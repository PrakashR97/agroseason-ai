import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useLang } from '../i18n'
import SearchBox from '../components/SearchBox'
import { AsyncView, CropCard, DistrictSelect, MonthSelect, StatusBadge, useAsync, useDistricts } from '../components/ui'

export default function Home() {
  const { t, name, months } = useLang()
  const nav = useNavigate()
  const districts = useDistricts()
  const [q, setQ] = useState('')
  const [district, setDistrict] = useState('')
  const [month, setMonth] = useState('')

  const goCrop = (crop) => {
    const p = new URLSearchParams()
    if (district) p.set('district', district)
    if (month) p.set('month', month)
    nav(`/crops/${crop.id}${p.toString() ? `?${p}` : ''}`)
  }
  const submit = (e) => {
    e?.preventDefault()
    const p = new URLSearchParams()
    if (q.trim()) p.set('q', q.trim())
    if (district) p.set('district', district)
    if (month) p.set('month', month)
    nav(`/crops?${p}`)
  }

  const cats = useAsync(() => api.categories(), [])
  const seasonal = useAsync(
    () => (district && month ? api.districtCrops(district, { month, page_size: 12 }) : Promise.resolve(null)),
    [district, month])

  return (
    <div className="space-y-10">
      <section className="border-2 border-brand p-6">
        <h1 className="text-3xl font-extrabold md:text-4xl">{t('appName')}</h1>
        <p className="mt-2 max-w-2xl">{t('tagline')}</p>
        <form onSubmit={submit} className="mt-6 grid gap-4 md:grid-cols-[2fr_1fr_1fr_auto] md:items-end" role="search">
          <SearchBox value={q} onChange={setQ} onPick={goCrop} onSubmit={submit} districtId={district} month={month} />
          <DistrictSelect districts={districts} value={district} onChange={setDistrict} />
          <MonthSelect value={month} onChange={setMonth} />
          <button type="submit" className="btn-primary">{t('search')}</button>
        </form>
      </section>

      <section aria-labelledby="cats-h">
        <h2 id="cats-h" className="mb-3 text-2xl font-bold">{t('categories')}</h2>
        <AsyncView state={cats}>{(list) => (
          <ul className="grid grid-cols-2 gap-3 md:grid-cols-4">
            {list.map((c) => (
              <li key={c.id}>
                <Link to={`/crops?category=${c.slug}`} className="block border-2 border-brand p-3 font-semibold hover:bg-brand hover:text-paper">
                  {name(c)}
                </Link>
              </li>))}
          </ul>)}
        </AsyncView>
      </section>

      <section aria-labelledby="seasonal-h">
        <h2 id="seasonal-h" className="text-2xl font-bold">{t('seasonal')}</h2>
        <p className="mb-3 text-sm opacity-80">{t('seasonal_hint')}</p>
        {!district || !month ? <p className="border-2 border-dashed border-brand p-4">{t('pick_district_month')}</p> : (
          <AsyncView state={seasonal}>{(res) => res && (res.items.length === 0
            ? <p className="border-2 border-dashed border-brand p-4">{t('insufficient')}</p>
            : <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {res.items.map((it) => (
                <li key={it.crop.id}>
                  <CropCard crop={it.crop} to={`/crops/${it.crop.id}?district=${district}&month=${month}`}>
                    <div className="mt-2 flex flex-wrap gap-2 text-xs">
                      <StatusBadge status={it.verification_status} />
                      <span className="border border-brand px-2 py-0.5">{t(`scope_${it.scope}`)}</span>
                      <span>{it.seasons.join(', ')} · {months[month - 1]}</span>
                    </div>
                  </CropCard>
                </li>))}
            </ul>)}
          </AsyncView>)}
      </section>
    </div>
  )
}
