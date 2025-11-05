import { useMemo } from 'react';
import { EnhancedWavelet } from './EnhancedWavelet';
import { generateClusters, generateWaveletDataForPoint, ClusterConfig } from '../lib/clusteringAlgorithm';
import { generateIntensityBasedSize } from '../lib/sizeDistribution';
import {
  calculateWaveletCount,
  generatePosition,
  calculateEdgeOpacity,
  calculateZIndex,
  sortWaveletsByIntensity,
  WaveletPosition,
  CanvasConfig
} from '../lib/positioningEngine';

interface HeatMapGridV2Props {
  width?: number;
  height?: number;
  density?: number;        // Wavelets per 10,000 sq px (default: 25)
  numClusters?: number;
  clusterRadius?: number;
  noiseStrength?: number;
}

export function HeatMapGridV2({
  width = 1000,
  height = 1000,
  density = 25,              // Not used anymore, keeping for compatibility
  numClusters = 15,          // More clusters than before (was 8)
  clusterRadius = 10,        // Tighter radius (was 15)
  noiseStrength = 0.2
}: HeatMapGridV2Props) {
  // Generate wavelets with simple 5x5 grid positioning
  const { wavelets, canvasWidth, canvasHeight } = useMemo(() => {
    const gridSize = 5; // 5x5 = 25 wavelets total
    const generatedWavelets: WaveletPosition[] = [];

    // Generate clusters for color variation
    const clusters = generateClusters(100, numClusters);
    const clusterConfig: ClusterConfig = {
      gridSize: 100,
      numClusters,
      clusterRadius,
      noiseStrength
    };

    // Generate 5x5 grid of wavelets
    for (let row = 0; row < gridSize; row++) {
      for (let col = 0; col < gridSize; col++) {
        // Grid position - NO random offset yet
        const baseX = (col + 0.5) * (width / gridSize);
        const baseY = (row + 0.5) * (height / gridSize);
        const x = baseX;
        const y = baseY;

        // Generate brainwave data based on position
        const xNorm = (x / width) * 100;
        const yNorm = (y / height) * 100;
        const brainwaveData = generateWaveletDataForPoint(
          xNorm,
          yNorm,
          clusters,
          clusterConfig
        );

        // Calculate total intensity
        const totalIntensity = (
          brainwaveData.delta +
          brainwaveData.theta +
          brainwaveData.lowAlpha +
          brainwaveData.highAlpha +
          brainwaveData.lowBeta +
          brainwaveData.highBeta +
          brainwaveData.lowGamma +
          brainwaveData.highGamma
        ) / 8;

        // Step 2: Randomize size (300-400px for significant overlap)
        const size = 300 + Math.random() * 100;

        // Step 3: Reduce opacity (0.6-0.8 for transparency and color mixing)
        const opacity = 0.6 + Math.random() * 0.2;

        // Simple z-index based on intensity
        const zIndex = Math.floor(totalIntensity * 100);

        generatedWavelets.push({
          x,
          y,
          size,
          zIndex,
          opacity,
          intensity: totalIntensity,
          ...brainwaveData
        } as WaveletPosition & typeof brainwaveData);
      }
    }

    console.log('DEBUG: Total wavelets created:', generatedWavelets.length);
    console.log('DEBUG: First wavelet:', generatedWavelets[0]);

    // Sort by z-index for proper rendering order (back to front)
    const sortedWavelets = sortWaveletsByIntensity(generatedWavelets);

    return {
      wavelets: sortedWavelets,
      canvasWidth: width,
      canvasHeight: height
    };
  }, [width, height, numClusters, clusterRadius, noiseStrength]);

  return (
    <div className="relative w-full flex items-center justify-center p-8">
      {/* Main canvas */}
      <div
        className="relative overflow-hidden"
        style={{
          width: canvasWidth,
          height: canvasHeight,
          backgroundColor: '#000',
          // Radial gradient vignette for smooth edge fade
          background: 'radial-gradient(ellipse at center, #000 0%, #000 70%, transparent 100%)'
        }}
      >
        {/* Wavelets container */}
        <div
          className="absolute inset-0"
          style={{
            mixBlendMode: 'normal', // Parent uses normal, children use screen
          }}
        >
          {wavelets.map((wavelet: any, index) => (
            <EnhancedWavelet
              key={index}
              delta={wavelet.delta}
              theta={wavelet.theta}
              lowAlpha={wavelet.lowAlpha}
              highAlpha={wavelet.highAlpha}
              lowBeta={wavelet.lowBeta}
              highBeta={wavelet.highBeta}
              lowGamma={wavelet.lowGamma}
              highGamma={wavelet.highGamma}
              size={wavelet.size}
              x={wavelet.x}
              y={wavelet.y}
              zIndex={wavelet.zIndex}
              opacity={wavelet.opacity}
            />
          ))}
        </div>

        {/* Subtle edge vignette overlay for extra fade */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background: 'radial-gradient(ellipse at center, transparent 60%, rgba(0,0,0,0.5) 90%, rgba(0,0,0,0.9) 100%)',
            mixBlendMode: 'multiply'
          }}
        />
      </div>

      {/* Debug info (optional) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="absolute bottom-2 left-2 text-xs text-white bg-black bg-opacity-70 p-3 rounded font-mono">
          <div className="font-bold text-yellow-300 mb-2">DEBUG INFO:</div>
          <div>Wavelets: {wavelets.length}</div>
          <div>Canvas: {canvasWidth}x{canvasHeight}</div>
          <div>Grid cell: {canvasWidth / 5}x{canvasHeight / 5}px</div>
          {wavelets[0] && (
            <>
              <div className="mt-2 font-bold text-green-300">First wavelet:</div>
              <div>Position: ({Math.round(wavelets[0].x)}, {Math.round(wavelets[0].y)})</div>
              <div>Size: {wavelets[0].size}px</div>
              <div>Opacity: {wavelets[0].opacity}</div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
