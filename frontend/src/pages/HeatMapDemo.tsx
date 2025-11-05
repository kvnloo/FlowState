import { useState } from 'react';
import { HeatMapGridV2 } from '../components/HeatMapGridV2';
import { TimelineSidebar } from '../components/TimelineSidebar';
import { Sliders, ZoomIn, ZoomOut, RotateCcw, Download } from 'lucide-react';

export function HeatMapDemo() {
  const [canvasWidth, setCanvasWidth] = useState(1000);
  const [canvasHeight, setCanvasHeight] = useState(1000);
  const [density, setDensity] = useState(25);
  const [numClusters, setNumClusters] = useState(15);
  const [clusterRadius, setClusterRadius] = useState(10);
  const [noiseStrength, setNoiseStrength] = useState(0.2);
  const [showControls, setShowControls] = useState(false);

  const handleReset = () => {
    setCanvasWidth(1000);
    setCanvasHeight(1000);
    setDensity(25);
    setNumClusters(15);
    setClusterRadius(10);
    setNoiseStrength(0.2);
  };

  const handleExport = () => {
    // TODO: Implement screenshot/export functionality
    console.log('Export functionality coming soon');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Brain Activity Heat Map
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              High-density visualization of neural oscillations
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowControls(!showControls)}
              className={`p-2 rounded-lg transition-colors ${
                showControls
                  ? 'bg-purple-100 text-purple-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              title="Toggle controls"
            >
              <Sliders className="w-5 h-5" />
            </button>

            <button
              onClick={handleReset}
              className="p-2 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
              title="Reset to defaults"
            >
              <RotateCcw className="w-5 h-5" />
            </button>

            <button
              onClick={handleExport}
              className="p-2 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
              title="Export image"
            >
              <Download className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Controls Panel */}
        {showControls && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Density */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <ZoomIn className="w-4 h-4" />
                  Density: {density}
                </label>
                <input
                  type="range"
                  min="15"
                  max="40"
                  value={density}
                  onChange={(e) => setDensity(Number(e.target.value))}
                  className="w-full"
                />
                <div className="text-xs text-gray-500">
                  ~{Math.floor((canvasWidth * canvasHeight / 10000) * density)} wavelets
                </div>
              </div>

              {/* Number of Clusters */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  Clusters: {numClusters}
                </label>
                <input
                  type="range"
                  min="5"
                  max="25"
                  value={numClusters}
                  onChange={(e) => setNumClusters(Number(e.target.value))}
                  className="w-full"
                />
                <div className="text-xs text-gray-500">
                  Hot zone count
                </div>
              </div>

              {/* Cluster Radius */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  Spread: {clusterRadius}
                </label>
                <input
                  type="range"
                  min="5"
                  max="20"
                  value={clusterRadius}
                  onChange={(e) => setClusterRadius(Number(e.target.value))}
                  className="w-full"
                />
                <div className="text-xs text-gray-500">
                  Cluster tightness
                </div>
              </div>

              {/* Noise Strength */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  Variation: {(noiseStrength * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="0.5"
                  step="0.05"
                  value={noiseStrength}
                  onChange={(e) => setNoiseStrength(Number(e.target.value))}
                  className="w-full"
                />
                <div className="text-xs text-gray-500">
                  Organic noise level
                </div>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Heat Map */}
        <div className="flex-1 overflow-auto">
          <div className="min-h-full flex items-center justify-center p-8">
            <HeatMapGridV2
              width={canvasWidth}
              height={canvasHeight}
              density={density}
              numClusters={numClusters}
              clusterRadius={clusterRadius}
              noiseStrength={noiseStrength}
            />
          </div>
        </div>

        {/* Timeline Sidebar */}
        <TimelineSidebar height={800} />
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 px-6 py-3">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div>
            Brainwave Frequency Bands: Delta (0.5-4 Hz) • Theta (4-8 Hz) • Alpha (8-13 Hz) • Beta (13-30 Hz) • Gamma (30-100 Hz)
          </div>
          <div className="flex items-center gap-4">
            <span>
              FPS: ~60
            </span>
            <span>
              Resolution: {canvasWidth}x{canvasHeight}
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
