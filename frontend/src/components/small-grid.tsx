import Wavelet from "./wavelet"

// Define different brain state patterns
const STATES = {
  THETA_DOMINANT: {
    delta: () => 0.8 + Math.random() * 0.4,
    theta: () => 0.9 + Math.random() * 1.1,
    lowAlpha: () => 0.3 + Math.random() * 0.4,
    highAlpha: () => 0.2 + Math.random() * 0.3,
    lowBeta: () => 0.1 + Math.random() * 0.2,
    highBeta: () => 0.1 + Math.random() * 0.2,
    lowGamma: () => 0.1 + Math.random() * 0.1,
    highGamma: () => 0.1 + Math.random() * 0.1
  },
  BETA_DOMINANT: {
    delta: () => 0.1 + Math.random() * 0.2,
    theta: () => 0.1 + Math.random() * 0.2,
    lowAlpha: () => 0.2 + Math.random() * 0.3,
    highAlpha: () => 0.3 + Math.random() * 0.4,
    lowBeta: () => 0.8 + Math.random() * 1.2,
    highBeta: () => 0.9 + Math.random() * 1.1,
    lowGamma: () => 0.4 + Math.random() * 0.6,
    highGamma: () => 0.3 + Math.random() * 0.4
  },
  ALPHA_DOMINANT: {
    delta: () => 0.2 + Math.random() * 0.3,
    theta: () => 0.3 + Math.random() * 0.4,
    lowAlpha: () => 0.8 + Math.random() * 1.2,
    highAlpha: () => 0.9 + Math.random() * 1.1,
    lowBeta: () => 0.3 + Math.random() * 0.4,
    highBeta: () => 0.2 + Math.random() * 0.3,
    lowGamma: () => 0.1 + Math.random() * 0.2,
    highGamma: () => 0.1 + Math.random() * 0.2
  }
}

const generateWaveletData = (x: number, y: number, gridSize: number) => {
  // Create zones of different brain states based on position
  const centerX = gridSize / 2
  const centerY = gridSize / 2
  const distance = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2))
  
  // Choose state based on position
  let state
  if (distance < gridSize / 3) {
    state = STATES.BETA_DOMINANT
  } else if (y < gridSize / 2) {
    state = STATES.THETA_DOMINANT
  } else {
    state = STATES.ALPHA_DOMINANT
  }

  return {
    delta: state.delta(),
    theta: state.theta(),
    lowAlpha: state.lowAlpha(),
    highAlpha: state.highAlpha(),
    lowBeta: state.lowBeta(),
    highBeta: state.highBeta(),
    lowGamma: state.lowGamma(),
    highGamma: state.highGamma()
  }
}

export default function SmallGrid() {
  const gridSize = 8 // Increased from 5x5 to 8x8 for more density
  const wavelets = Array.from({ length: gridSize * gridSize }, (_, i) => {
    const x = i % gridSize
    const y = Math.floor(i / gridSize)
    return generateWaveletData(x, y, gridSize)
  })

  return (
    <div className="w-full max-w-4xl mx-auto p-4">
      <div 
        className="relative grid"
        style={{ 
          gridTemplateColumns: `repeat(${gridSize}, 1fr)`,
          gap: '0',
          mixBlendMode: 'screen',
          background: '#000',
          padding: '3rem',
          overflow: 'hidden'
        }}
      >
        {wavelets.map((data, index) => {
          const x = index % gridSize
          const y = Math.floor(index / gridSize)
          const centerDistance = Math.sqrt(
            Math.pow(x - gridSize/2, 2) + 
            Math.pow(y - gridSize/2, 2)
          )
          
          // Calculate size based on position and dominant frequencies
          const maxIntensity = Math.max(...Object.values(data))
          const baseSize = 40 + (maxIntensity * 160)
          const sizeVariation = 1 + (Math.random() * 0.5)
          const finalSize = baseSize * sizeVariation
          
          // Calculate opacity based on size and position
          const opacity = Math.max(0.3, 1 - (centerDistance / gridSize) - (finalSize / 400))

          return (
            <div 
              key={index} 
              className="relative"
              style={{
                width: '100%',
                paddingBottom: '100%',
                transform: `translate(${Math.random() * 20 - 10}%, ${Math.random() * 20 - 10}%)`
              }}
            >
              <div 
                className="absolute inset-0 flex items-center justify-center"
                style={{
                  transform: `scale(${1 + (maxIntensity * 0.5)})`,
                }}
              >
                <Wavelet 
                  data={data} 
                  size={finalSize} 
                  interactive={false} 
                  opacity={opacity}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

