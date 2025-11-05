import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { Dashboard } from './pages/Dashboard';
import { Training } from './pages/Training';
import { History } from './pages/History';
import { HeatMapDemo } from './pages/HeatMapDemo';
import { WaveletDemoPage } from './pages/WaveletDemoPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/training" element={<Training />} />
            <Route path="/history" element={<History />} />
            <Route path="/heatmap" element={<HeatMapDemo />} />
            <Route path="/wavelet-demo" element={<WaveletDemoPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;