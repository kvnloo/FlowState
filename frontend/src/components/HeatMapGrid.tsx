import { useMemo } from 'react';
import { GridWavelet } from './GridWavelet';
import {
  generateClusters,
  generateWaveletDataForPoint,
  ClusterConfig
} from '../lib/clusteringAlgorithm';

interface HeatMapGridProps {
  gridSize?: number;
  numClusters?: number;
  clusterRadius?: number;
  noiseStrength?: number;
  animate?: boolean;
}

export function HeatMapGrid({
  gridSize = 40, // Default 40x40 for desktop heat map
  numClusters = 8,
  clusterRadius = 15,
  noiseStrength = 0.2,
  animate = false
}: HeatMapGridProps) {
  // Generate clusters and wavelet data
  const { clusters, wavelets } = useMemo(() => {
    const generatedClusters = generateClusters(gridSize, numClusters);

    const config: ClusterConfig = {
      gridSize,
      numClusters,
      clusterRadius,
      noiseStrength
    };

    const generatedWavelets = [];

    // Generate wavelet for each grid cell
    for (let y = 0; y < gridSize; y++) {
      for (let x = 0; x < gridSize; x++) {
        const data = generateWaveletDataForPoint(x, y, generatedClusters, config);
        generatedWavelets.push({
          x,
          y,
          ...data
        });
      }
    }

    return {
      clusters: generatedClusters,
      wavelets: generatedWavelets
    };
  }, [gridSize, numClusters, clusterRadius, noiseStrength]);

  // Calculate cell size based on grid size and container
  const cellSize = useMemo(() => {
    // Target container width ~800px, adjust cell size accordingly
    const targetWidth = 800;
    return Math.max(12, Math.min(30, targetWidth / gridSize));
  }, [gridSize]);

  return (
    <div className="relative w-full flex items-center justify-center p-8">
      <div
        className="relative"
        style={{
          width: gridSize * cellSize,
          height: gridSize * cellSize,
          backgroundColor: '#000',
          mixBlendMode: 'normal'
        }}
      >
        {/* Grid container with screen blend mode */}
        <div
          className="absolute inset-0"
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${gridSize}, ${cellSize}px)`,
            gridTemplateRows: `repeat(${gridSize}, ${cellSize}px)`,
            gap: 0,
            mixBlendMode: 'screen'
          }}
        >
          {wavelets.map((wavelet, index) => {
            const {
              x,
              y,
              delta,
              theta,
              lowAlpha,
              highAlpha,
              lowBeta,
              highBeta,
              lowGamma,
              highGamma,
              size
            } = wavelet;

            // Calculate opacity based on distance from center
            const centerX = gridSize / 2;
            const centerY = gridSize / 2;
            const dx = x - centerX;
            const dy = y - centerY;
            const distanceFromCenter = Math.sqrt(dx * dx + dy * dy);
            const maxDistance = Math.sqrt(centerX * centerX + centerY * centerY);

            // Vignette effect - brighter in center
            const vignetteOpacity = 0.4 + (1 - distanceFromCenter / maxDistance) * 0.6;

            // Total intensity for this wavelet
            const totalIntensity = (delta + theta + lowAlpha + highAlpha +
                                   lowBeta + highBeta + lowGamma + highGamma) / 8;

            // Final opacity combines vignette and intensity
            const finalOpacity = vignetteOpacity * (0.5 + totalIntensity * 0.5);

            return (
              <div
                key={index}
                className="relative"
                style={{
                  width: cellSize,
                  height: cellSize,
                  overflow: 'visible'
                }}
              >
                <GridWavelet
                  delta={delta}
                  theta={theta}
                  lowAlpha={lowAlpha}
                  highAlpha={highAlpha}
                  lowBeta={lowBeta}
                  highBeta={highBeta}
                  lowGamma={lowGamma}
                  highGamma={highGamma}
                  size={Math.min(size, cellSize * 2.5)} // Limit max size to prevent overflow
                  opacity={finalOpacity}
                />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
