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
  // Find dominant frequency
  const frequencies = [
    { value: delta, color: COLORS_ENHANCED.delta },
    { value: theta, color: COLORS_ENHANCED.theta },
    { value: lowAlpha, color: COLORS_ENHANCED.lowAlpha },
    { value: highAlpha, color: COLORS_ENHANCED.highAlpha },
    { value: lowBeta, color: COLORS_ENHANCED.lowBeta },
    { value: highBeta, color: COLORS_ENHANCED.highBeta },
    { value: lowGamma, color: COLORS_ENHANCED.lowGamma },
    { value: highGamma, color: COLORS_ENHANCED.highGamma },
  ];

  const dominant = frequencies.reduce((max, f) => f.value > max.value ? f : max);

  // DEBUG: Log what we're actually rendering
  console.log('EnhancedWavelet rendering:', { size, x, y, opacity, color: dominant.color });

  const containerStyle: CSSProperties = {
    position: 'absolute',
    left: `${x}px`, // Explicit px units
    top: `${y}px`,
    width: `${size}px`, // Explicit px units
    height: `${size}px`,
    transform: 'translate(-50%, -50%)',
    pointerEvents: 'none',
    zIndex,
    // Step 4: Add screen blend mode for bright additive color mixing
    mixBlendMode: 'screen',
  };

  return (
    <div style={containerStyle}>
      <div
        style={{
          backgroundColor: dominant.color,
          width: `${size}px`, // Explicit px units
          height: `${size}px`,
          borderRadius: '50%',
          opacity: opacity,
        }}
      />
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
