import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { HomePage } from './pages/HomePage'
import { StreamForecastPage } from './pages/StreamForecastPage'
import { CaseForecastPage } from './pages/CaseForecastPage'
import { DataStreamsPage } from './pages/DataStreamsPage'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/stream" element={<StreamForecastPage />} />
          <Route path="/case" element={<CaseForecastPage />} />
          <Route path="/data" element={<DataStreamsPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
