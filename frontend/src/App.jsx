import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import CalendarPage from './pages/CalendarPage'
import Catalog from './pages/Catalog'
import CropDetail from './pages/CropDetail'
import { DistrictDetail, Districts } from './pages/Districts'
import Home from './pages/Home'
import ResearchStatus from './pages/ResearchStatus'
import Settings from './pages/Settings'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="crops" element={<Catalog />} />
        <Route path="crops/:id" element={<CropDetail />} />
        <Route path="districts" element={<Districts />} />
        <Route path="districts/:id" element={<DistrictDetail />} />
        <Route path="calendar" element={<CalendarPage />} />
        <Route path="research" element={<ResearchStatus />} />
        <Route path="settings" element={<Settings />} />
        <Route path="*" element={<p className="p-6 text-xl font-bold">404</p>} />
      </Route>
    </Routes>
  )
}
