export interface BrainwaveData {
  delta: number    // 0-1 intensity values
  theta: number
  lowAlpha: number
  highAlpha: number
  lowBeta: number
  highBeta: number
  lowGamma: number
  highGamma: number
  timestamp: number
}

export interface WaveletProps {
  data: BrainwaveData
  size?: number
  interactive?: boolean
  className?: string
}

export const BRAINWAVE_COLORS = {
  delta: '#dd0a0a',
  theta: '#ff8500',
  lowAlpha: '#fcea01',
  highAlpha: '#58ed14',
  lowBeta: '#16caf4',
  highBeta: '#022aba',
  lowGamma: '#6f5ba3',
  highGamma: '#e50cbc'
} as const

export const BRAINWAVE_OPACITIES = {
  delta: 0.2,
  theta: 0.4,
  lowAlpha: 0.5,
  highAlpha: 0.5,
  lowBeta: 0.5,
  highBeta: 0.5,
  lowGamma: 0.5,
  highGamma: 0.5
} as const

