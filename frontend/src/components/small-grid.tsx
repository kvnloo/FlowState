/**
 * Small grid component - now uses the improved HeatMapGrid
 * This is kept for backward compatibility but delegates to HeatMapGrid
 */

import { HeatMapGrid } from './HeatMapGrid';

export default function SmallGrid() {
  return (
    <div className="w-full max-w-4xl mx-auto p-4">
      <HeatMapGrid
        gridSize={12}
        numClusters={5}
        clusterRadius={8}
        noiseStrength={0.25}
      />
    </div>
  );
}

