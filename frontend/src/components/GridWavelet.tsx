import { memo } from 'react';

/**
 * Optimized Wavelet component for dense grid rendering
 * Uses CSS-only rendering and memoization for performance
 */

interface GridWaveletProps {
  delta: number;
  theta: number;
  lowAlpha: number;
  highAlpha: number;
  lowBeta: number;
  highBeta: number;
  lowGamma: number;
  highGamma: number;
  size: number;
  opacity?: number;
}

// Color constants matching the inspiration images exactly
const COLORS = {
  delta: '#dd0a0a',
  theta: '#ff8500',
  lowAlpha: '#fcea01',
  highAlpha: '#58ed14',
  lowBeta: '#16caf4',
  highBeta: '#022aba',
  lowGamma: '#6f5ba3',
  highGamma: '#e50cbc'
} as const;

function GridWaveletComponent({
  delta,
  theta,
  lowAlpha,
  highAlpha,
  lowBeta,
  highBeta,
  lowGamma,
  highGamma,
  size,
  opacity = 1
}: GridWaveletProps) {
  // Calculate circle sizes - outer to inner
  const getSize = (intensity: number, index: number) => {
    const baseSize = size * 0.95;
    const minSize = baseSize * 0.08;
    const maxSize = baseSize * (1 - index * 0.11);
    return minSize + intensity * (maxSize - minSize);
  };

  // Order from outer to inner for proper layering
  const layers = [
    { value: highGamma, color: COLORS.highGamma, index: 0 },
    { value: lowGamma, color: COLORS.lowGamma, index: 1 },
    { value: highBeta, color: COLORS.highBeta, index: 2 },
    { value: lowBeta, color: COLORS.lowBeta, index: 3 },
    { value: highAlpha, color: COLORS.highAlpha, index: 4 },
    { value: lowAlpha, color: COLORS.lowAlpha, index: 5 },
    { value: theta, color: COLORS.theta, index: 6 },
    { value: delta, color: COLORS.delta, index: 7 }
  ];

  return (
    <div
      className="absolute"
      style={{
        width: size,
        height: size,
        left: '50%',
        top: '50%',
        transform: 'translate(-50%, -50%)',
        pointerEvents: 'none'
      }}
    >
      {layers.map((layer, i) => {
        const layerSize = getSize(layer.value, layer.index);
        return (
          <div
            key={i}
            className="absolute rounded-full"
            style={{
              backgroundColor: layer.color,
              width: layerSize,
              height: layerSize,
              left: '50%',
              top: '50%',
              transform: 'translate(-50%, -50%)',
              opacity: opacity * (0.7 + layer.value * 0.3), // Vary opacity by intensity
              willChange: 'transform', // GPU acceleration hint
            }}
          />
        );
      })}
    </div>
  );
}

// Memoize to prevent unnecessary re-renders
export const GridWavelet = memo(GridWaveletComponent, (prev, next) => {
  // Only re-render if values actually changed
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
    prev.opacity === next.opacity
  );
});

GridWavelet.displayName = 'GridWavelet';
