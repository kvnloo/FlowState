import React from 'react';

interface WaveletProps {
  data: {
    delta: number;
    theta: number;
    lowAlpha: number;
    highAlpha: number;
    lowBeta: number;
    highBeta: number;
    lowGamma: number;
    highGamma: number;
  };
  size?: number;
  interactive?: boolean;
}

const Wavelet: React.FC<WaveletProps> = ({ data, size = 60, interactive = false }) => {
  const waves = [
    { name: 'delta', color: '#dd0a0a' },
    { name: 'theta', color: '#ff8500' },
    { name: 'lowAlpha', color: '#fcea01' },
    { name: 'highAlpha', color: '#58ed14' },
    { name: 'lowBeta', color: '#16caf4' },
    { name: 'highBeta', color: '#022aba' },
    { name: 'lowGamma', color: '#6f5ba3' },
    { name: 'highGamma', color: '#e50cbc' },
  ];

  return (
    <div 
      className={`relative ${interactive ? 'cursor-pointer hover:scale-110 transition-transform' : ''}`}
      style={{ width: size, height: size }}
    >
      {waves.map((wave, index) => (
        <div
          key={wave.name}
          className="absolute rounded-full"
          style={{
            backgroundColor: wave.color,
            width: `${(data[wave.name as keyof typeof data] * size) / 100}px`,
            height: `${(data[wave.name as keyof typeof data] * size) / 100}px`,
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: waves.length - index,
          }}
        />
      ))}
    </div>
  );
};

export default Wavelet;

