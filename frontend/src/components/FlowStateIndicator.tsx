import React from 'react';
import { Brain } from 'lucide-react';

interface FlowStateIndicatorProps {
  alphaTheta: number;
  signalQuality: { [channel: string]: number };
}

export function FlowStateIndicator({ alphaTheta, signalQuality }: FlowStateIndicatorProps) {
  // Flow state thresholds based on Alpha/Theta ratio
  const LOW_THRESHOLD = 0.8;  // Below this: not focused
  const HIGH_THRESHOLD = 1.6; // Above this: optimal flow state
  
  // Calculate average signal quality
  const avgQuality = Object.values(signalQuality).reduce((a, b) => a + b, 0) / Object.values(signalQuality).length;
  
  // Determine flow state
  const getFlowState = () => {
    if (avgQuality < 0.7) return 'poor-signal';
    if (alphaTheta < LOW_THRESHOLD) return 'unfocused';
    if (alphaTheta > HIGH_THRESHOLD) return 'flow';
    return 'focused';
  };
  
  const flowState = getFlowState();
  
  // Style configurations
  const stateConfigs = {
    'poor-signal': {
      color: 'text-gray-400',
      bgColor: 'bg-gray-100',
      label: 'Poor Signal',
      description: 'Check headband placement'
    },
    'unfocused': {
      color: 'text-blue-500',
      bgColor: 'bg-blue-100',
      label: 'Unfocused',
      description: 'Mind is wandering'
    },
    'focused': {
      color: 'text-purple-500',
      bgColor: 'bg-purple-100',
      label: 'Focused',
      description: 'Maintaining attention'
    },
    'flow': {
      color: 'text-green-500',
      bgColor: 'bg-green-100',
      label: 'Flow State',
      description: 'Optimal performance'
    }
  };
  
  const config = stateConfigs[flowState];
  
  return (
    <div className={`rounded-lg p-6 ${config.bgColor} transition-all duration-500`}>
      <div className="flex items-center space-x-4">
        <div className={`p-3 rounded-full ${config.bgColor}`}>
          <Brain className={`w-8 h-8 ${config.color}`} />
        </div>
        <div>
          <h3 className={`text-lg font-semibold ${config.color}`}>
            {config.label}
          </h3>
          <p className="text-sm text-gray-600">{config.description}</p>
        </div>
      </div>
      
      <div className="mt-4 space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Alpha/Theta Ratio</span>
          <span className={`font-semibold ${config.color}`}>
            {alphaTheta.toFixed(2)}
          </span>
        </div>
        
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className={`h-full ${config.color} transition-all duration-300`}
            style={{ 
              width: `${Math.min((alphaTheta / HIGH_THRESHOLD) * 100, 100)}%`,
              opacity: avgQuality
            }}
          />
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Signal Quality</span>
          <span className={`font-semibold ${avgQuality < 0.7 ? 'text-red-500' : 'text-green-500'}`}>
            {(avgQuality * 100).toFixed(0)}%
          </span>
        </div>
      </div>
    </div>
  );
}
