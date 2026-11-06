import { Link, useParams, useSearchParams } from 'react-router-dom'
import { api } from '../api'
import { useLang } from '../i18n'
import CalendarGrid from '../components/CalendarGrid'
import ResearchPanel from '../components/ResearchPanel'
import SketchImage from '../components/SketchImage'
import { AsyncView, DistrictSelect, MonthSelect, StatusBadge, useAsync, useDistricts } from '../components/ui'

function GuideSection({ s }) {
  const { t, lang } = useLang()
  const label = lang === 'ta' ? s.label_ta : s.label_en
  const missing = s.status === 'missing'
  if (missing) {
    return (
      <div className="flex flex-wrap items-center justify-between gap-2 border-2 border-dashed border-brand p-3">
        <div><span className="font-semibold">{label}</span><br /><span className="text-sm">{t('insufficient')}</span></div>
        <StatusBadge status="missing" />
      </div>
    )
  }
  return (
    <details className="border-2 border-brand" open={s.status !== 'catalog'}>
      <summary className="flex cursor-pointer flex-wrap items-center justify-between gap-2 p-3 font-semibold">
        <span>{label}</span><StatusBadge status={s.status} />
      </summary>
      <div className="border-t-2 border-brand p-3">
        <p className="whitespace-pre-line">{s.value}</p>
        {s.note && <p className="mt-1 text-sm font-semibold">{s.note}</p>}
        {s.sources?.length > 0 && (
          <ul className="mt-2 list-disc pl-5 text-sm">
            {s.sources.map((x) => <li key={x.id}><a className="underline" href={x.url} target="_blank" rel="noreferrer noopener">{x.title}</a></li>)}
          </ul>)}
      </div>
    </details>
  )
}

export default function CropDetail() {
  const { id } = useParams()
  const [params, setParams] = useSearchParams()
  const district = params.get('district') || ''
  const month = params.get('month') || ''
  const { t, name, altName, months } = useLang()
  const districts = useDistricts()
  const setP = (k, v) => { const p = new URLSearchParams(params); v ? p.set(k, v) : p.delete(k); setParams(p, { replace: true }) }

  const crop = useAsync(() => api.crop(id), [id])
  const guide = useAsync(() => api.guide({ crop_id: id, district_id: district }), [id, district])
  const cal = useAsync(() => api.calendar({ crop_id: id, district_id: district, month }), [id, district, month])
  const dlist = useAsync(() => api.cropDistricts(id), [id])
  const refs = new Map()
  guide.data?.sections.forEach((s) => s.sources?.forEach((x) => refs.set(x.id, x)))

  return (
    <AsyncView state={crop}>{(c) => (
      <div className="space-y-8">
        <header className="grid gap-6 md:grid-cols-[1fr_280px]">
          <div>
            <p className="text-sm"><Link className="underline" to={`/crops?category=${c.category.slug}`}>{name(c.category)}</Link></p>
            <h1 className="text-4xl font-extrabold">{name(c)}</h1>
            <p className="text-xl">{altName(c)}</p>
            <p className="mt-1 italic">{c.scientific_name}</p>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <StatusBadge status={c.verification_status} />
              <span className="border border-brand px-2 py-0.5 text-xs">{t('crop_type')}: {t(`type_${c.crop_type}`)}</span>
            </div>
            {c.aliases.length > 0 && <p className="mt-3 text-sm"><span className="font-semibold">{t('aliases')}:</span> {c.aliases.join(', ')}</p>}
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <DistrictSelect id="cd-district" districts={districts} value={district} onChange={(v) => setP('district', v)} />
              <MonthSelect id="cd-month" value={month} onChange={(v) => setP('month', v)} />
            </div>
          </div>
          <SketchImage crop={c} />
        </header>

        {month && cal.data?.selected_month && (
          <p role="status" data-testid="month-banner"
            className={`border-2 border-brand p-4 text-lg font-semibold ${cal.data.selected_month.suitability === 'not_documented' ? 'border-dashed' : 'bg-brand text-paper'}`}>
            {months[month - 1]}{' '}
            {cal.data.selected_month.suitability === 'not_documented' ? t('month_not_documented') : t('month_recommended')}
            {cal.data.selected_month.suitability === 'documented_unverified' && ` (${t('status_unverified')})`}
            {cal.data.selected_month.suitability === 'not_documented' && <span className="block text-base font-normal">{t('insufficient')}</span>}
          </p>)}

        <section aria-labelledby="cal-h">
          <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
            <h2 id="cal-h" className="text-2xl font-bold">{t('calendar_title')}</h2>
            <Link className="underline" to={`/calendar?crop=${c.id}${district ? `&district=${district}` : ''}`}>{t('view_calendar')}</Link>
          </div>
          <p className="mb-2 text-sm"><span className="border border-brand px-2 py-0.5">{t(`scope_${cal.data?.scope || 'none'}`)}</span></p>
          <AsyncView state={cal}>{(d) => <CalendarGrid data={d} selectedMonth={Number(month) || null} onSelectMonth={(m) => setP('month', String(m))} />}</AsyncView>
        </section>

        <section aria-labelledby="var-h">
          <h2 id="var-h" className="text-2xl font-bold">{t('varieties')}</h2>
          <p className="mb-2 text-sm opacity-80">{t('varieties_note')}</p>
          {c.varieties.length === 0 ? <p>{t('insufficient')}</p> : (
            <ul className="flex flex-wrap gap-2">{c.varieties.map((v) => (
              <li key={v.id} className="flex items-center gap-2 border-2 border-brand px-3 py-1">{v.name}<StatusBadge status={v.verification_status} /></li>))}</ul>)}
        </section>

        <section aria-labelledby="guide-h">
          <h2 id="guide-h" className="text-2xl font-bold">{t('guide')}</h2>
          <p className="mb-3 text-sm opacity-80">{t('guide_note')}</p>
          <AsyncView state={guide}>{(g) => (
            <div className="space-y-2">
              <p className="text-sm" data-testid="guide-count">{g.documented_sections} / {g.total_sections}</p>
              {g.sections.map((s) => <GuideSection key={s.key} s={s} />)}
            </div>)}
          </AsyncView>
        </section>

        <section aria-labelledby="dist-h">
          <h2 id="dist-h" className="text-2xl font-bold">{t('suitable_districts')}</h2>
          <AsyncView state={dlist}>{(list) => list.length === 0 ? <p>{t('no_districts')}</p> : (
            <ul className="flex flex-wrap gap-2">{list.map((x) => (
              <li key={x.district.id}><Link className="flex items-center gap-2 border-2 border-brand px-3 py-1" to={`/districts/${x.district.id}`}>
                {name(x.district)}<StatusBadge status={x.verification_status} /></Link></li>))}</ul>)}
          </AsyncView>
        </section>

        <section aria-labelledby="src-h">
          <h2 id="src-h" className="text-2xl font-bold">{t('sources')}</h2>
          {refs.size === 0 ? <p>{t('no_sources')}</p> : (
            <ul className="list-disc pl-5">{[...refs.values()].map((x) => (
              <li key={x.id}><a className="underline" href={x.url} target="_blank" rel="noreferrer noopener">{x.title}</a>
                <span className="ml-2 text-xs">{t('retrieved')}: {x.retrieved_at.slice(0, 10)}</span></li>))}</ul>)}
        </section>

        <ResearchPanel crop={c} districtId={district} districts={districts} month={month} />
      </div>)}
    </AsyncView>
  )
}
