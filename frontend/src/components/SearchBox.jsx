import { useEffect, useId, useRef, useState } from 'react'
import { api } from '../api'
import { useLang } from '../i18n'

/** Debounced multilingual crop search with keyboard-navigable suggestions. */
export default function SearchBox({ value, onChange, onPick, onSubmit, districtId, month }) {
  const { t, name, altName } = useLang()
  const [hits, setHits] = useState([])
  const [open, setOpen] = useState(false)
  const [active, setActive] = useState(-1)
  const listId = useId()
  const timer = useRef()

  useEffect(() => {
    clearTimeout(timer.current)
    if (!value || value.trim().length < 2) { setHits([]); return }
    timer.current = setTimeout(() => {
      api.search({ q: value.trim(), limit: 6, district_id: districtId, month })
        .then((r) => { setHits(r); setOpen(true); setActive(-1) })
        .catch(() => setHits([]))
    }, 200)
    return () => clearTimeout(timer.current)
  }, [value, districtId, month])

  const pick = (h) => { setOpen(false); onPick(h.crop) }
  const onKey = (e) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); setOpen(true); setActive((a) => Math.min(a + 1, hits.length - 1)) }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setActive((a) => Math.max(a - 1, 0)) }
    else if (e.key === 'Escape') setOpen(false)
    else if (e.key === 'Enter' && open && active >= 0) { e.preventDefault(); pick(hits[active]) }
  }

  return (
    <div className="relative flex flex-col gap-1">
      <label htmlFor="crop-search" className="text-sm font-semibold">{t('search_crop')}</label>
      <input id="crop-search" className="input" type="search" autoComplete="off" role="combobox"
        aria-expanded={open && hits.length > 0} aria-controls={listId} aria-autocomplete="list"
        aria-activedescendant={active >= 0 ? `${listId}-${active}` : undefined}
        placeholder={t('search_placeholder')} value={value}
        onChange={(e) => { onChange(e.target.value); setOpen(true) }} onKeyDown={onKey}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        onKeyUp={(e) => { if (e.key === 'Enter' && active < 0 && onSubmit) onSubmit() }} />
      {open && hits.length > 0 && (
        <ul id={listId} role="listbox" aria-label={t('suggestions')}
          className="absolute left-0 right-0 top-full z-10 border-2 border-brand bg-paper">
          {hits.map((h, i) => (
            <li key={h.crop.id} id={`${listId}-${i}`} role="option" aria-selected={i === active}
              className={`cursor-pointer px-3 py-2 ${i === active ? 'bg-brand text-paper' : 'hover:bg-brand/10'}`}
              onMouseDown={(e) => { e.preventDefault(); pick(h) }}>
              <span className="font-semibold">{name(h.crop)}</span>{' '}
              <span className="opacity-80">· {altName(h.crop)}</span>
              {h.matched_alias && <span className="ml-2 text-xs opacity-70">({h.matched_alias})</span>}
              {h.month_suitability && h.month_suitability !== 'not_documented' &&
                <span className="ml-2 text-xs font-semibold">{t(`suit_short_${h.month_suitability}`)}</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
