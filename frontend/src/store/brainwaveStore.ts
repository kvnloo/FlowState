import { create } from 'zustand';

interface BrainwaveState {
  delta: number[];
  theta: number[];
  alpha: number[];
  beta: number[];
  gamma: number[];
  updateWaves: (data: {
    delta: number;
    theta: number;
    alpha: number;
    beta: number;
    gamma: number;
  }) => void;
  loadSampleData: () => void;
}

export const useBrainwaveStore = create<BrainwaveState>((set) => ({
  delta: [],
  theta: [],
  alpha: [],
  beta: [],
  gamma: [],
  updateWaves: (data) =>
    set((state) => ({
      delta: [...state.delta.slice(-50), data.delta],
      theta: [...state.theta.slice(-50), data.theta],
      alpha: [...state.alpha.slice(-50), data.alpha],
      beta: [...state.beta.slice(-50), data.beta],
      gamma: [...state.gamma.slice(-50), data.gamma],
    })),
  loadSampleData: () => {
    const sampleData = Array.from({ length: 50 }, (_, i) => ({
      delta: Math.sin(i * 0.1) * 0.4 + 0.6,
      theta: Math.sin(i * 0.15 + 1) * 0.4 + 0.6,
      alpha: Math.sin(i * 0.2 + 2) * 0.4 + 0.6,
      beta: Math.sin(i * 0.25 + 3) * 0.4 + 0.6,
      gamma: Math.sin(i * 0.3 + 4) * 0.4 + 0.6,
    }));

    set({
      delta: sampleData.map(d => d.delta),
      theta: sampleData.map(d => d.theta),
      alpha: sampleData.map(d => d.alpha),
      beta: sampleData.map(d => d.beta),
      gamma: sampleData.map(d => d.gamma),
    });
  },
}));