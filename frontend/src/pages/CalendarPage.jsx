import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../api'
import { useLang } from '../i18n'
import CalendarGrid from '../components/CalendarGrid'
import { AsyncView, DistrictSelect, Field, StatusBadge, useAsync, useDistricts } from '../components/ui'

export default function CalendarPage() {
  const { t, name, months } = useLang()
  const [params, setParams] = useSearchParams()
  const cropId = params.get('crop') || ''
  const district = params.get('district') || ''
  const [month, setMonth] = useState(null)
  const [irrigation, setIrrigation] = useState('')
  const districts = useDistricts()
  const setP = (k, v) => { const p = new URLSearchParams(params); v ? p.set(k, v) : p.delete(k); setParams(p, { replace: true }) }

  const crops = useAsync(() => api.crops({ page_size: 100 }).then(async (first) => {
    let items = first.items
    for (let p = 2; items.length < first.total && p < 5; p++) items = items.concat((await api.crops({ page: p, page_size: 100 })).items)
    return items
  }), [])
  const cal = useAsync(() => (cropId ? api.calendar({ crop_id: cropId, district_id: district, month, irrigation }) : Promise.resolve(null)),
    [cropId, district, month, irrigation])
  useEffect(() => { setMonth(null) }, [cropId])

  return (
    <div>
      <h1 className="mb-4 text-3xl font-bold">{t('calendar_title')}</h1>
      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <Field label={t('crop')} htmlFor="cal-crop">
          <select id="cal-crop" className="input" value={cropId} onChange={(e) => setP('crop', e.target.value)}>
            <option value="">{t('choose_crop')}</option>
            {crops.data?.map((c) => <option key={c.id} value={c.id}>{name(c)}</option>)}
          </select>
        </Field>
        <DistrictSelect id="cal-district" districts={districts} value={district} onChange={(v) => setP('district', v)} />
        <Field label={t('irrigation')} htmlFor="cal-irr">
          <select id="cal-irr" className="input" value={irrigation} onChange={(e) => setIrrigation(e.target.value)}>
            <option value="">{t('irr_any')}</option>
            <option value="irrigated">{t('irr_irrigated')}</option>
            <option value="rainfed">{t('irr_rainfed')}</option>
          </select>
        </Field>
      </div>
      {!cropId ? <p className="border-2 border-dashed border-brand p-4">{t('choose_crop')}</p> : (
        <AsyncView state={cal}>{(d) => d && (
          <>
            <p className="mb-3 flex flex-wrap items-center gap-2 text-sm">
              <span className="border border-brand px-2 py-0.5">{t(`scope_${d.scope}`)}</span>
              {d.seasons.map((s) => <span key={s.id} className="flex items-center gap-1 border border-brand px-2 py-0.5">{s.season_name} <StatusBadge status={s.verification_status} /></span>)}
            </p>
            <CalendarGrid data={d} selectedMonth={month} onSelectMonth={setMonth} />
            {d.selected_month && <p className="mt-4 border-2 border-brand p-3" role="status">
              <strong>{months[month - 1]}:</strong> {t(`suit_${d.selected_month.suitability}`)}
              {d.selected_month.phases.length > 0 && ` — ${d.selected_month.phases.map((p) => t(`phase_${p}`)).join(', ')}`}
            </p>}
            {d.seasons.some((s) => s.notes) && <ul className="mt-3 list-disc pl-5 text-sm">{d.seasons.filter((s) => s.notes).map((s) => <li key={s.id}>{s.season_name}: {s.notes}</li>)}</ul>}
          </>)}
        </AsyncView>)}
    </div>
  )
}
