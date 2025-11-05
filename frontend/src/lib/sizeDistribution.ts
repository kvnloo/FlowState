/**
 * Power-law size distribution for organic, realistic wavelet sizing
 * Matches the visual pattern from inspiration images:
 * - 70% tiny dots (3-8px)
 * - 20% medium blobs (15-40px)
 * - 8% large spheres (60-120px)
 * - 2% massive blobs (150-250px)
 */

export interface SizeCategory {
  weight: number;
  min: number;
  max: number;
  name: string;
}

export const SIZE_DISTRIBUTION: SizeCategory[] = [
  { name: 'tiny', weight: 0.70, min: 3, max: 8 },
  { name: 'medium', weight: 0.20, min: 15, max: 40 },
  { name: 'large', weight: 0.08, min: 60, max: 120 },
  { name: 'massive', weight: 0.02, min: 150, max: 250 }
];

/**
 * Generate a size based on power-law distribution
 */
export function generateWaveletSize(): number {
  const random = Math.random();
  let cumulativeWeight = 0;

  for (const category of SIZE_DISTRIBUTION) {
    cumulativeWeight += category.weight;
    if (random <= cumulativeWeight) {
      // Random size within this category's range
      const range = category.max - category.min;
      return category.min + Math.random() * range;
    }
  }

  // Fallback (should never reach here)
  return SIZE_DISTRIBUTION[0].min + Math.random() * (SIZE_DISTRIBUTION[0].max - SIZE_DISTRIBUTION[0].min);
}

/**
 * Generate size with intensity multiplier
 * Higher intensity = tendency toward larger sizes
 */
export function generateIntensityBasedSize(intensity: number): number {
  // Base size from power-law distribution
  const baseSize = generateWaveletSize();

  // Intensity multiplier: 0.7x to 1.3x
  const intensityMultiplier = 0.7 + (intensity * 0.6);

  return baseSize * intensityMultiplier;
}

/**
 * Get size category statistics for debugging
 */
export function getSizeDistributionStats(sizes: number[]): Record<string, number> {
  const stats: Record<string, number> = {
    tiny: 0,
    medium: 0,
    large: 0,
    massive: 0
  };

  sizes.forEach(size => {
    if (size < 8) stats.tiny++;
    else if (size < 40) stats.medium++;
    else if (size < 120) stats.large++;
    else stats.massive++;
  });

  return stats;
}

/**
 * Validate size distribution matches target weights
 * Returns percentage deviation from target
 */
export function validateDistribution(sizes: number[]): {
  actual: Record<string, number>;
  target: Record<string, number>;
  deviation: number;
} {
  const total = sizes.length;
  const stats = getSizeDistributionStats(sizes);

  const actual = {
    tiny: stats.tiny / total,
    medium: stats.medium / total,
    large: stats.large / total,
    massive: stats.massive / total
  };

  const target = {
    tiny: 0.70,
    medium: 0.20,
    large: 0.08,
    massive: 0.02
  };

  // Calculate total deviation
  const deviation = Object.keys(target).reduce((sum, key) => {
    return sum + Math.abs(actual[key as keyof typeof actual] - target[key as keyof typeof target]);
  }, 0) / 4;

  return { actual, target, deviation };
}
