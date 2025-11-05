import { memo, CSSProperties } from 'react';

/**
 * Enhanced Wavelet component with glow effects and brighter colors
 * Optimized for visual accuracy matching inspiration images
 */

interface EnhancedWaveletProps {
  delta: number;
  theta: number;
  lowAlpha: number;
  highAlpha: number;
  lowBeta: number;
  highBeta: number;
  lowGamma: number;
  highGamma: number;
  size: number;
  x: number;
  y: number;
  zIndex: number;
  opacity?: number;
}

// Enhanced colors - 20% brighter than original for better screen blend effect
const COLORS_ENHANCED = {
  delta: '#ff0d0d',      // Was #dd0a0a
  theta: '#ff9520',      // Was #ff8500
  lowAlpha: '#ffef1a',   // Was #fcea01
  highAlpha: '#6fff2a',  // Was #58ed14
  lowBeta: '#33d5ff',    // Was #16caf4
  highBeta: '#1a3dcc',   // Was #022aba
  lowGamma: '#8670b8',   // Was #6f5ba3
  highGamma: '#ff1acc'   // Was #e50cbc
} as const;

function EnhancedWaveletComponent({
  delta,
  theta,
  lowAlpha,
  highAlpha,
  lowBeta,
  highBeta,
  lowGamma,
  highGamma,
  size,
  x,
  y,
  zIndex,
  opacity = 1
}: EnhancedWaveletProps) {
  // All 8 frequencies with metadata
  const frequencies = [
    { name: 'delta', value: delta, color: COLORS_ENHANCED.delta },
    { name: 'theta', value: theta, color: COLORS_ENHANCED.theta },
    { name: 'lowAlpha', value: lowAlpha, color: COLORS_ENHANCED.lowAlpha },
    { name: 'highAlpha', value: highAlpha, color: COLORS_ENHANCED.highAlpha },
    { name: 'lowBeta', value: lowBeta, color: COLORS_ENHANCED.lowBeta },
    { name: 'highBeta', value: highBeta, color: COLORS_ENHANCED.highBeta },
    { name: 'lowGamma', value: lowGamma, color: COLORS_ENHANCED.lowGamma },
    { name: 'highGamma', value: highGamma, color: COLORS_ENHANCED.highGamma },
  ];

  // Sort by intensity (largest first for back-to-front rendering)
  // Filter out very weak signals to avoid clutter
  const sortedFrequencies = frequencies
    .filter(f => f.value > 0.05)
    .sort((a, b) => b.value - a.value);

  // Calculate circle size based on intensity
  const calculateCircleSize = (intensity: number, baseSize: number): number => {
    // Minimum 20% visibility, scale up to 100% based on intensity
    const minScale = 0.2;
    const maxScale = 1.0;
    return baseSize * (minScale + (intensity * (maxScale - minScale)));
  };

  const containerStyle: CSSProperties = {
    position: 'absolute',
    left: `${x}px`,
    top: `${y}px`,
    transform: 'translate(-50%, -50%)',
    pointerEvents: 'none',
  };

  return (
    <div style={containerStyle}>
      {sortedFrequencies.map((freq, index) => {
        const circleSize = calculateCircleSize(freq.value, size);
        // Largest circles (index 0) get lowest z-index (back), smallest get highest (front)
        const layerZIndex = zIndex + (sortedFrequencies.length - index);

        return (
          <div
            key={freq.name}
            style={{
              position: 'absolute',
              left: '50%',
              top: '50%',
              transform: 'translate(-50%, -50%)',
              width: `${circleSize}px`,
              height: `${circleSize}px`,
              backgroundColor: freq.color,
              borderRadius: '50%',
              opacity: 0.6,
              zIndex: layerZIndex,
              filter: 'blur(20px)',
            }}
          />
        );
      })}
    </div>
  );
}

// Memoize to prevent unnecessary re-renders
export const EnhancedWavelet = memo(EnhancedWaveletComponent, (prev, next) => {
  return (
    prev.delta === next.delta &&
    prev.theta === next.theta &&
    prev.lowAlpha === next.lowAlpha &&
    prev.highAlpha === next.highAlpha &&
    prev.lowBeta === next.lowBeta &&
    prev.highBeta === next.highBeta &&
    prev.lowGamma === next.lowGamma &&
    prev.highGamma === next.highGamma &&
    prev.size === next.size &&
    prev.x === next.x &&
    prev.y === next.y &&
    prev.zIndex === next.zIndex &&
    prev.opacity === next.opacity
  );
});

EnhancedWavelet.displayName = 'EnhancedWavelet';
