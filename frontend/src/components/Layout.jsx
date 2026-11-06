import { NavLink, Outlet } from 'react-router-dom'
import { useLang } from '../i18n'

const links = [['/', 'nav_home'], ['/crops', 'nav_crops'], ['/districts', 'nav_districts'],
  ['/calendar', 'nav_calendar'], ['/research', 'nav_research'], ['/settings', 'nav_settings']]

export default function Layout() {
  const { t, lang, setLang } = useLang()
  return (
    <div className="flex min-h-screen flex-col bg-paper text-brand">
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:bg-paper focus:p-2">{t('skip')}</a>
      <header className="bg-brand text-paper">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-2 px-4 py-3">
          <NavLink to="/" className="text-xl font-bold">🌱 {t('appName')}</NavLink>
          <div className="flex items-center gap-1" role="group" aria-label={t('language')}>
            {['en', 'ta'].map((l) => (
              <button key={l} onClick={() => setLang(l)} aria-pressed={lang === l}
                className={`border-2 border-paper px-2 py-1 text-sm font-semibold ${lang === l ? 'bg-paper text-brand' : 'bg-brand text-paper'}`}>
                {l === 'en' ? 'EN' : 'தமிழ்'}
              </button>
            ))}
          </div>
        </div>
        <nav aria-label="Main" className="mx-auto max-w-6xl overflow-x-auto px-4">
          <ul className="flex gap-1 pb-2">
            {links.map(([to, key]) => (
              <li key={to}>
                <NavLink to={to} end={to === '/'}
                  className={({ isActive }) => `block whitespace-nowrap border-b-4 px-3 py-2 ${isActive ? 'border-paper font-bold' : 'border-transparent'}`}>
                  {t(key)}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      </header>
      <main id="main" className="mx-auto w-full max-w-6xl flex-1 px-4 py-6"><Outlet /></main>
      <footer className="border-t-2 border-brand px-4 py-4 text-center text-sm">{t('footer')}</footer>
    </div>
  )
}
