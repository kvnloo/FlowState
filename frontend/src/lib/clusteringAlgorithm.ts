/**
 * Clustering algorithm for organic brain state visualization
 * Creates natural-looking patterns similar to the inspiration images
 */

export interface ClusterConfig {
  gridSize: number;
  numClusters: number;
  clusterRadius: number;
  noiseStrength: number;
}

export interface ClusterPoint {
  x: number;
  y: number;
  intensity: number;
  state: BrainState;
}

export type BrainState = 'theta_dominant' | 'alpha_dominant' | 'beta_dominant' | 'gamma_dominant' | 'mixed';

// Simple noise function for organic variation
function noise2D(x: number, y: number): number {
  const n = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453;
  return n - Math.floor(n);
}

// Smooth interpolation
function smoothstep(edge0: number, edge1: number, x: number): number {
  const t = Math.max(0, Math.min(1, (x - edge0) / (edge1 - edge0)));
  return t * t * (3 - 2 * t);
}

/**
 * Generate cluster centers across the grid
 * Enhanced for tighter, more intense hot zones
 */
export function generateClusters(gridSize: number, numClusters: number): ClusterPoint[] {
  const clusters: ClusterPoint[] = [];
  const states: BrainState[] = ['theta_dominant', 'alpha_dominant', 'beta_dominant', 'gamma_dominant', 'mixed'];

  for (let i = 0; i < numClusters; i++) {
    clusters.push({
      x: Math.random() * gridSize,
      y: Math.random() * gridSize,
      // Higher baseline intensity: 0.7 to 1.0 (was 0.5 to 1.0)
      intensity: 0.7 + Math.random() * 0.3,
      state: states[Math.floor(Math.random() * states.length)]
    });
  }

  return clusters;
}

/**
 * Calculate influence of clusters on a grid point
 */
export function getClusterInfluence(
  x: number,
  y: number,
  clusters: ClusterPoint[],
  radius: number
): { intensity: number; state: BrainState } {
  let totalInfluence = 0;
  let weightedStateScores: Record<BrainState, number> = {
    theta_dominant: 0,
    alpha_dominant: 0,
    beta_dominant: 0,
    gamma_dominant: 0,
    mixed: 0
  };

  // Calculate influence from each cluster
  clusters.forEach(cluster => {
    const dx = x - cluster.x;
    const dy = y - cluster.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance < radius) {
      // Smooth falloff based on distance
      const influence = smoothstep(radius, 0, distance) * cluster.intensity;
      totalInfluence += influence;
      weightedStateScores[cluster.state] += influence;
    }
  });

  // Determine dominant state
  let dominantState: BrainState = 'mixed';
  let maxScore = 0;

  (Object.keys(weightedStateScores) as BrainState[]).forEach(state => {
    if (weightedStateScores[state] > maxScore) {
      maxScore = weightedStateScores[state];
      dominantState = state;
    }
  });

  return {
    intensity: Math.min(1, totalInfluence),
    state: dominantState
  };
}

/**
 * Add organic noise variation
 */
export function addNoiseVariation(
  x: number,
  y: number,
  baseIntensity: number,
  strength: number
): number {
  const n = noise2D(x * 0.1, y * 0.1);
  const variation = (n - 0.5) * strength;
  return Math.max(0, Math.min(1, baseIntensity + variation));
}

/**
 * Generate complete wavelet data for a grid point
 */
export function generateWaveletDataForPoint(
  x: number,
  y: number,
  clusters: ClusterPoint[],
  config: ClusterConfig
): {
  delta: number;
  theta: number;
  lowAlpha: number;
  highAlpha: number;
  lowBeta: number;
  highBeta: number;
  lowGamma: number;
  highGamma: number;
} {
  // Get cluster influence
  const { intensity, state } = getClusterInfluence(x, y, clusters, config.clusterRadius);

  // Add noise
  const finalIntensity = addNoiseVariation(x, y, intensity, config.noiseStrength);

  // Generate brain wave values based on state
  const baseValues = getStateValues(state, finalIntensity);

  // Size is now controlled by the caller, not calculated here
  return {
    ...baseValues
  };
}

/**
 * Get brain wave values for a specific state
 */
function getStateValues(state: BrainState, intensity: number) {
  const profiles = {
    theta_dominant: {
      delta: () => (0.6 + Math.random() * 0.4) * intensity,
      theta: () => (0.8 + Math.random() * 0.2) * intensity,
      lowAlpha: () => (0.2 + Math.random() * 0.3) * intensity,
      highAlpha: () => (0.1 + Math.random() * 0.2) * intensity,
      lowBeta: () => (0.1 + Math.random() * 0.1) * intensity,
      highBeta: () => (0.05 + Math.random() * 0.1) * intensity,
      lowGamma: () => (0.05 + Math.random() * 0.1) * intensity,
      highGamma: () => (0.05 + Math.random() * 0.1) * intensity
    },
    alpha_dominant: {
      delta: () => (0.2 + Math.random() * 0.3) * intensity,
      theta: () => (0.3 + Math.random() * 0.3) * intensity,
      lowAlpha: () => (0.7 + Math.random() * 0.3) * intensity,
      highAlpha: () => (0.8 + Math.random() * 0.2) * intensity,
      lowBeta: () => (0.3 + Math.random() * 0.2) * intensity,
      highBeta: () => (0.2 + Math.random() * 0.2) * intensity,
      lowGamma: () => (0.1 + Math.random() * 0.1) * intensity,
      highGamma: () => (0.1 + Math.random() * 0.1) * intensity
    },
    beta_dominant: {
      delta: () => (0.1 + Math.random() * 0.2) * intensity,
      theta: () => (0.1 + Math.random() * 0.2) * intensity,
      lowAlpha: () => (0.2 + Math.random() * 0.3) * intensity,
      highAlpha: () => (0.3 + Math.random() * 0.3) * intensity,
      lowBeta: () => (0.7 + Math.random() * 0.3) * intensity,
      highBeta: () => (0.8 + Math.random() * 0.2) * intensity,
      lowGamma: () => (0.4 + Math.random() * 0.3) * intensity,
      highGamma: () => (0.3 + Math.random() * 0.2) * intensity
    },
    gamma_dominant: {
      delta: () => (0.05 + Math.random() * 0.1) * intensity,
      theta: () => (0.1 + Math.random() * 0.1) * intensity,
      lowAlpha: () => (0.2 + Math.random() * 0.2) * intensity,
      highAlpha: () => (0.3 + Math.random() * 0.2) * intensity,
      lowBeta: () => (0.4 + Math.random() * 0.3) * intensity,
      highBeta: () => (0.5 + Math.random() * 0.3) * intensity,
      lowGamma: () => (0.7 + Math.random() * 0.3) * intensity,
      highGamma: () => (0.8 + Math.random() * 0.2) * intensity
    },
    mixed: {
      delta: () => (0.3 + Math.random() * 0.4) * intensity,
      theta: () => (0.4 + Math.random() * 0.4) * intensity,
      lowAlpha: () => (0.4 + Math.random() * 0.4) * intensity,
      highAlpha: () => (0.4 + Math.random() * 0.4) * intensity,
      lowBeta: () => (0.4 + Math.random() * 0.4) * intensity,
      highBeta: () => (0.4 + Math.random() * 0.4) * intensity,
      lowGamma: () => (0.3 + Math.random() * 0.4) * intensity,
      highGamma: () => (0.3 + Math.random() * 0.4) * intensity
    }
  };

  const profile = profiles[state];

  return {
    delta: profile.delta(),
    theta: profile.theta(),
    lowAlpha: profile.lowAlpha(),
    highAlpha: profile.highAlpha(),
    lowBeta: profile.lowBeta(),
    highBeta: profile.highBeta(),
    lowGamma: profile.lowGamma(),
    highGamma: profile.highGamma()
  };
}
