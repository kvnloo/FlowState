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

export function BrainwaveIcon({ data, size = 100 }: BrainwaveIconProps) {
  const circles = [
    { name: 'delta', color: '#dc2626', value: data.delta },
    { name: 'theta', color: '#ea580c', value: data.theta },
    { name: 'alpha', color: '#9333ea', value: data.alpha },
    { name: 'beta', color: '#2563eb', value: data.beta },
    { name: 'gamma', color: '#16a34a', value: data.gamma },
  ];

  return (
    <svg width={size} height={size} viewBox="0 0 100 100">
      {circles.map((circle, index) => {
        const radius = (index + 1) * 10;
        const intensity = Math.min(Math.max(circle.value, 0.2), 1);
        
        return (
          <g key={circle.name}>
            <circle
              cx="50"
              cy="50"
              r={radius}
              fill={circle.color}
              opacity={intensity * 0.3}
            />
            <circle
              cx="50"
              cy="50"
              r={radius - 2}
              fill="none"
              stroke={circle.color}
              strokeWidth="0.5"
              opacity={intensity}
            />
          </g>
        );
      })}
    </svg>
  );
}