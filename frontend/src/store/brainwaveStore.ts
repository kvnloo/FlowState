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
}));