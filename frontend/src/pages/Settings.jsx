import { useLang } from '../i18n'

export default function Settings() {
  const { t, lang, setLang } = useLang()
  return (
    <div>
      <h1 className="mb-2 text-3xl font-bold">{t('language')}</h1>
      <p className="mb-4">{t('language_hint')}</p>
      <fieldset className="flex gap-3">
        <legend className="sr-only">{t('language')}</legend>
        {['en', 'ta'].map((l) => (
          <label key={l} className={`flex cursor-pointer items-center gap-2 border-2 border-brand px-4 py-3 ${lang === l ? 'bg-brand text-paper' : ''}`}>
            <input type="radio" name="lang" checked={lang === l} onChange={() => setLang(l)} className="accent-brand" />
            {l === 'en' ? t('english') : t('tamil')}
          </label>))}
      </fieldset>
    </div>
  )
}
