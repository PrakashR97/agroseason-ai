import { useLang } from '../i18n'

const PHASES = ['nursery', 'sowing', 'transplanting', 'growth', 'harvest']

function cellClass(cell, phase) {
  if (!cell.phases.includes(phase)) return 'bg-paper'
  if (phase === 'growth') return cell.all_verified ? 'bg-brand/30' : 'pattern-dots'
  return cell.all_verified ? 'bg-brand' : 'pattern-hatch'
}

export default function CalendarGrid({ data, selectedMonth, onSelectMonth }) {
  const { t, months } = useLang()
  if (!data) return null
  const short = months.map((m) => m.slice(0, 3))
  return (
    <div>
      {data.message && <p className="mb-3 border-2 border-dashed border-brand p-3 font-semibold">{t('insufficient')}</p>}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[640px] border-collapse border-2 border-brand text-center text-sm"
          aria-label={t('calendar_title')}>
          <thead>
            <tr>
              <th scope="col" className="border border-brand p-2 text-left">&nbsp;</th>
              {data.months.map((c, i) => (
                <th key={c.month} scope="col" className={`border border-brand p-0 ${selectedMonth === c.month ? 'bg-brand text-paper' : ''}`}>
                  <button type="button" className="w-full p-2 font-semibold" aria-pressed={selectedMonth === c.month}
                    aria-label={months[i]} onClick={() => onSelectMonth?.(c.month)}>{short[i]}</button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {PHASES.map((p) => (
              <tr key={p}>
                <th scope="row" className="border border-brand p-2 text-left font-semibold">{t(`phase_${p}`)}</th>
                {data.months.map((c) => (
                  <td key={c.month} className={`h-9 border border-brand ${cellClass(c, p)}`}
                    data-testid={`cell-${p}-${c.month}`} data-active={c.phases.includes(p)}>
                    {c.phases.includes(p) && <span className="sr-only">{t(`phase_${p}`)}</span>}
                  </td>
                ))}
              </tr>
            ))}
            <tr>
              <th scope="row" className="border border-brand p-2 text-left font-semibold">{t('row_suitability')}</th>
              {data.months.map((c) => (
                <td key={c.month} className="border border-brand p-1 text-xs font-semibold"
                  data-testid={`suit-${c.month}`} data-suitability={c.suitability}>
                  {t(`suit_short_${c.suitability}`)}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-4 text-sm" aria-label={t('legend')}>
        <span className="font-semibold">{t('legend')}:</span>
        <span className="flex items-center gap-1"><i className="inline-block h-4 w-6 border border-brand bg-brand" />{t('legend_solid')}</span>
        <span className="flex items-center gap-1"><i className="pattern-hatch inline-block h-4 w-6 border border-brand" />{t('legend_hatch')}</span>
        <span className="flex items-center gap-1"><i className="inline-block h-4 w-6 border border-brand bg-paper" />{t('legend_empty')}</span>
      </div>
      <p className="mt-2 text-sm opacity-80">{t('calendar_disclaimer')}</p>
      {data.seasons?.some((s) => s.harvest_estimated) && <p className="text-sm">△ {t('harvest_estimated')}</p>}
    </div>
  )
}
