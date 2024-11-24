import React from 'react';

interface BrainwaveIconProps {
  data: {
    delta: number;
    theta: number;
    alpha: number;
    beta: number;
    gamma: number;
  };
  size?: number;
}

export function BrainwaveIcon({ data, size = 60 }: BrainwaveIconProps) {
  const circles = [
    { name: 'delta', color: '#dc2626', value: data.delta },
    { name: 'theta', color: '#ea580c', value: data.theta },
    { name: 'alpha', color: '#9333ea', value: data.alpha },
    { name: 'beta', color: '#2563eb', value: data.beta },
    { name: 'gamma', color: '#16a34a', value: data.gamma },
  ];

  return (
    <svg width={size} height={size} viewBox="0 0 60 60">
      <defs>
        <radialGradient id="circleGradient" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="white" stopOpacity="0.15" />
          <stop offset="100%" stopColor="white" stopOpacity="0" />
        </radialGradient>
      </defs>
      {circles.map((circle, index) => {
        const radius = (index + 1) * 4;
        const intensity = Math.min(Math.max(circle.value, 0.2), 1);
        
        return (
          <g key={circle.name}>
            <circle
              cx="30"
              cy="30"
              r={radius}
              fill={`url(#circleGradient)`}
              style={{ mixBlendMode: 'screen' }}
              opacity={intensity * 0.3}
            />
            <circle
              cx="30"
              cy="30"
              r={radius}
              fill="none"
              stroke={circle.color}
              strokeWidth="0.5"
              opacity={intensity * 0.6}
            />
          </g>
        );
      })}
    </svg>
  );
}