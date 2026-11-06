import { useEffect, useState } from 'react'
import { api } from '../api'
import { useLang } from '../i18n'

function Placeholder({ label }) {
  return (
    <svg viewBox="0 0 200 200" role="img" aria-label={label} className="h-full w-full bg-paper">
      <g fill="none" stroke="#166534" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" opacity="0.6">
        <path d="M100 170V95" />
        <path d="M100 95c0-30 22-48 55-48 0 30-20 48-55 48z" />
        <path d="M100 125c0-24-18-38-45-38 0 24 14 38 45 38z" />
      </g>
    </svg>
  )
}

export default function SketchImage({ crop }) {
  const { t, name } = useLang()
  const [sk, setSk] = useState(null)

  useEffect(() => {
    let live = true
    let timer
    const load = async (generate) => {
      try {
        const s = await api.sketch(crop.id, { generate: generate ? 'true' : undefined })
        if (!live) return
        setSk(s)
        if (s.status !== 'generated' && s.job_id) {
          const poll = async () => {
            try {
              const j = await api.job(s.job_id)
              if (!live) return
              if (['queued', 'running'].includes(j.status)) timer = setTimeout(poll, 3000)
              else load(false)
            } catch { /* stop polling */ }
          }
          timer = setTimeout(poll, 3000)
        }
      } catch { if (live) setSk({ status: 'placeholder', reason: null }) }
    }
    load(true)
    return () => { live = false; clearTimeout(timer) }
  }, [crop.id])

  const generated = sk?.status === 'generated'
  return (
    <figure className="border-2 border-brand bg-paper">
      <div className="aspect-square w-full">
        {generated
          ? <img src={sk.image_url} alt={`${t('sketch')}: ${name(crop)}`} className="h-full w-full object-contain" />
          : <Placeholder label={t('sketch_placeholder')} />}
      </div>
      <figcaption className="border-t-2 border-brand p-2 text-xs">
        {generated ? (
          <>
            <p>{t('attribution')}: {sk.attribution}</p>
            {sk.license_name && <p>{t('license')}: {sk.license_url
              ? <a className="underline" href={sk.license_url} target="_blank" rel="noreferrer noopener">{sk.license_name}</a> : sk.license_name}</p>}
            {sk.source_page_url && <a className="underline" href={sk.source_page_url} target="_blank" rel="noreferrer noopener">Source</a>}
          </>
        ) : <p>{sk?.job_id ? t('sketch_pending') : t('sketch_placeholder')}</p>}
      </figcaption>
    </figure>
  )
}
