import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../api'
import { useLang } from '../i18n'
import { AsyncView, CropCard, Pagination, useAsync } from '../components/ui'

export default function Catalog() {
  const { t, name } = useLang()
  const [params, setParams] = useSearchParams()
  const q = params.get('q') || ''
  const category = params.get('category') || ''
  const page = Number(params.get('page') || 1)
  const district = params.get('district') || ''
  const month = params.get('month') || ''
  const [text, setText] = useState(q)
  useEffect(() => setText(q), [q])

  const set = (patch) => {
    const p = new URLSearchParams(params)
    Object.entries(patch).forEach(([k, v]) => (v ? p.set(k, v) : p.delete(k)))
    if (!('page' in patch)) p.delete('page')
    setParams(p)
  }
  const cats = useAsync(() => api.categories(), [])
  const list = useAsync(() => api.crops({ q, category, page, page_size: 24 }), [q, category, page])

  return (
    <div>
      <h1 className="mb-4 text-3xl font-bold">{t('catalog')}</h1>
      <form className="mb-4 flex gap-2" role="search" onSubmit={(e) => { e.preventDefault(); set({ q: text.trim() }) }}>
        <label htmlFor="catalog-q" className="sr-only">{t('search')}</label>
        <input id="catalog-q" className="input" type="search" value={text} placeholder={t('search_placeholder')}
          onChange={(e) => setText(e.target.value)} />
        <button className="btn-primary" type="submit">{t('search')}</button>
      </form>
      <div className="mb-4 flex flex-wrap gap-2" role="group" aria-label={t('categories')}>
        <button className={category ? 'btn-secondary' : 'btn-primary'} aria-pressed={!category} onClick={() => set({ category: '' })}>{t('filter_all')}</button>
        {cats.data?.map((c) => (
          <button key={c.id} aria-pressed={category === c.slug} className={category === c.slug ? 'btn-primary' : 'btn-secondary'}
            onClick={() => set({ category: c.slug })}>{name(c)}</button>))}
      </div>
      <AsyncView state={list}>{(res) => (
        <>
          <p className="mb-2 text-sm" aria-live="polite">{res.total}</p>
          {res.items.length === 0 ? <p className="border-2 border-dashed border-brand p-4">{t('no_results')}</p> : (
            <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {res.items.map((c) => (
                <li key={c.id}><CropCard crop={c} to={`/crops/${c.id}${district || month ? `?${new URLSearchParams({ ...(district && { district }), ...(month && { month }) })}` : ''}`} /></li>))}
            </ul>)}
          <Pagination page={res.page} pageSize={res.page_size} total={res.total} onChange={(p) => set({ page: String(p) })} />
        </>)}
      </AsyncView>
    </div>
  )
}
