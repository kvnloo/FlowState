/**
 * Absolute positioning engine for seamless wavelet placement
 * Removes grid constraints, allows unrestricted overlap
 */

import { ClusterPoint } from './clusteringAlgorithm';

export interface WaveletPosition {
  x: number;           // Absolute X coordinate (0-canvasWidth)
  y: number;           // Absolute Y coordinate (0-canvasHeight)
  size: number;        // Diameter in pixels
  zIndex: number;      // Layering priority (0-1000)
  opacity: number;     // Base opacity (0-1)
  intensity: number;   // Total intensity for this wavelet
}

export interface CanvasConfig {
  width: number;
  height: number;
  targetDensity: number;  // Wavelets per 10,000 sq px
  edgeFade: number;       // Percentage of edge to fade (0-0.3)
}

/**
 * Calculate total wavelets needed for target density
 */
export function calculateWaveletCount(config: CanvasConfig): number {
  const area = config.width * config.height;
  const baseCount = Math.floor((area / 10000) * config.targetDensity);

  // Add 20% for edge overflow area
  return Math.floor(baseCount * 1.2);
}

/**
 * Generate position with cluster influence
 * Denser placement near cluster centers
 */
export function generatePosition(
  canvasWidth: number,
  canvasHeight: number,
  clusters: ClusterPoint[],
  index: number,
  total: number
): { x: number; y: number; clusterInfluence: number } {
  // Use index-based seeding for reproducibility
  const seed = (index / total) * Math.PI * 2;

  // Start with random position (can extend beyond visible bounds by 10%)
  const margin = 0.1;
  let x = (Math.random() - margin) * canvasWidth * (1 + margin * 2);
  let y = (Math.random() - margin) * canvasHeight * (1 + margin * 2);

  // Pull toward nearest cluster with probability based on distance
  const nearestCluster = clusters.reduce((nearest, cluster) => {
    const dx = x - (cluster.x / 100) * canvasWidth;
    const dy = y - (cluster.y / 100) * canvasHeight;
    const distance = Math.sqrt(dx * dx + dy * dy);

    return distance < nearest.distance ? { cluster, distance } : nearest;
  }, { cluster: clusters[0], distance: Infinity });

  // Pull strength based on cluster intensity
  const pullStrength = nearestCluster.cluster.intensity * 0.4;

  if (Math.random() < pullStrength) {
    const clusterX = (nearestCluster.cluster.x / 100) * canvasWidth;
    const clusterY = (nearestCluster.cluster.y / 100) * canvasHeight;

    // Pull position toward cluster
    const pullFactor = 0.3 + Math.random() * 0.4; // 30-70% toward cluster
    x = x + (clusterX - x) * pullFactor;
    y = y + (clusterY - y) * pullFactor;
  }

  // Calculate final cluster influence for this position
  const clusterInfluence = clusters.reduce((sum, cluster) => {
    const clusterX = (cluster.x / 100) * canvasWidth;
    const clusterY = (cluster.y / 100) * canvasHeight;
    const dx = x - clusterX;
    const dy = y - clusterY;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const maxInfluenceDistance = Math.min(canvasWidth, canvasHeight) * 0.3;

    if (distance < maxInfluenceDistance) {
      const influence = (1 - distance / maxInfluenceDistance) * cluster.intensity;
      return sum + influence;
    }
    return sum;
  }, 0);

  return {
    x: Math.max(0, Math.min(canvasWidth, x)),
    y: Math.max(0, Math.min(canvasHeight, y)),
    clusterInfluence: Math.min(1, clusterInfluence)
  };
}

/**
 * Calculate edge vignette opacity
 * Smooth radial fade from center to edges
 */
export function calculateEdgeOpacity(
  x: number,
  y: number,
  canvasWidth: number,
  canvasHeight: number,
  fadeFactor: number = 0.15
): number {
  // Distance from center as percentage
  const centerX = canvasWidth / 2;
  const centerY = canvasHeight / 2;
  const dx = (x - centerX) / centerX;
  const dy = (y - centerY) / centerY;
  const distanceFromCenter = Math.sqrt(dx * dx + dy * dy);

  // No fade in center 70%, then smooth fade to 0% at edges
  const fadeStart = 1 - fadeFactor;
  if (distanceFromCenter <= fadeStart) {
    return 1;
  }

  // Smooth cosine fade
  const fadeProgress = (distanceFromCenter - fadeStart) / fadeFactor;
  const fade = Math.cos(fadeProgress * Math.PI / 2);

  return Math.max(0, fade);
}

/**
 * Calculate z-index based on total intensity
 * Brighter wavelets render on top
 */
export function calculateZIndex(intensity: number, maxZIndex: number = 1000): number {
  // Map intensity (0-1) to z-index (0-maxZIndex)
  // Add small random variation to prevent z-fighting
  const baseZ = Math.floor(intensity * maxZIndex);
  const variation = Math.floor(Math.random() * 10) - 5;

  return Math.max(0, Math.min(maxZIndex, baseZ + variation));
}

/**
 * Sort wavelets for optimal rendering order
 * Background to foreground (low intensity to high)
 */
export function sortWaveletsByIntensity(wavelets: WaveletPosition[]): WaveletPosition[] {
  return [...wavelets].sort((a, b) => a.zIndex - b.zIndex);
}

/**
 * Generate jitter for natural placement
 * Prevents wavelets from appearing too aligned
 */
export function addPositionJitter(x: number, y: number, maxJitter: number = 5): { x: number; y: number } {
  return {
    x: x + (Math.random() - 0.5) * maxJitter,
    y: y + (Math.random() - 0.5) * maxJitter
  };
}
