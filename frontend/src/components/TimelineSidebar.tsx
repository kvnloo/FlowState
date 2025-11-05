/**
 * Timeline sidebar component matching the inspiration images
 * Shows brain state annotations with circular indicators
 */

interface TimelineEvent {
  time: string;
  title: string;
  description: string;
  state?: 'theta' | 'alpha' | 'beta' | 'gamma' | 'mixed';
}

interface TimelineSidebarProps {
  events?: TimelineEvent[];
  height?: number;
}

const defaultEvents: TimelineEvent[] = [
  {
    time: '00:00',
    title: 'Session Start',
    description: 'Initial baseline measurement. Subject in relaxed, alert state.',
    state: 'alpha'
  },
  {
    time: '02:30',
    title: 'Theta Emergence',
    description: 'Theta waves increasing. Light meditative state detected. Reduced cortical activity.',
    state: 'theta'
  },
  {
    time: '05:00',
    title: 'Alpha Dominant',
    description: 'Strong alpha rhythm. Wakeful relaxation with closed eyes.',
    state: 'alpha'
  },
  {
    time: '07:45',
    title: 'Beta Activation',
    description: 'Beta waves rising. Active thinking and problem solving detected.',
    state: 'beta'
  },
  {
    time: '10:20',
    title: 'Gamma Bursts',
    description: 'High-frequency gamma activity. Peak cognitive processing and attention.',
    state: 'gamma'
  },
  {
    time: '12:00',
    title: 'Mixed State',
    description: 'Transitional period. Multiple frequency bands active.',
    state: 'mixed'
  },
  {
    time: '15:00',
    title: 'Return to Baseline',
    description: 'Returning to balanced state. Session concluding.',
    state: 'alpha'
  }
];

export function TimelineSidebar({
  events = defaultEvents,
  height = 800
}: TimelineSidebarProps) {
  const stateColors = {
    theta: '#ff8500',
    alpha: '#58ed14',
    beta: '#16caf4',
    gamma: '#e50cbc',
    mixed: '#ffffff'
  };

  return (
    <div
      className="relative bg-white border-l border-gray-200"
      style={{ height, minWidth: 320, maxWidth: 400 }}
    >
      {/* Vertical timeline line */}
      <div className="absolute left-8 top-0 bottom-0 w-px bg-gray-300" />

      <div className="p-6 space-y-8 overflow-y-auto h-full">
        {events.map((event, index) => (
          <div key={index} className="relative pl-10">
            {/* Circle indicator */}
            <div
              className="absolute left-0 top-1 flex items-center justify-center"
              style={{ transform: 'translateX(-50%)' }}
            >
              <div className="relative">
                {/* Outer rings for emphasis */}
                {event.state && (
                  <>
                    <div
                      className="absolute inset-0 rounded-full opacity-30"
                      style={{
                        width: 40,
                        height: 40,
                        border: `2px solid ${stateColors[event.state]}`,
                        transform: 'translate(-50%, -50%) scale(1.5)',
                        left: '50%',
                        top: '50%'
                      }}
                    />
                    <div
                      className="absolute inset-0 rounded-full opacity-50"
                      style={{
                        width: 40,
                        height: 40,
                        border: `2px solid ${stateColors[event.state]}`,
                        transform: 'translate(-50%, -50%) scale(1.2)',
                        left: '50%',
                        top: '50%'
                      }}
                    />
                  </>
                )}

                {/* Main circle */}
                <div
                  className="rounded-full border-4 border-white shadow-md"
                  style={{
                    width: 40,
                    height: 40,
                    backgroundColor: event.state
                      ? stateColors[event.state]
                      : '#cccccc'
                  }}
                />

                {/* Inner dot */}
                <div
                  className="absolute rounded-full bg-white"
                  style={{
                    width: 8,
                    height: 8,
                    left: '50%',
                    top: '50%',
                    transform: 'translate(-50%, -50%)'
                  }}
                />
              </div>
            </div>

            {/* Event content */}
            <div className="space-y-1">
              <div className="text-xs text-gray-500 font-mono">{event.time}</div>
              <div className="text-sm font-semibold text-gray-900">
                {event.title}
              </div>
              <div className="text-sm text-gray-600 leading-relaxed">
                {event.description}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gray-50 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          Recording duration: {events[events.length - 1]?.time || '00:00'}
        </div>
      </div>
    </div>
  );
}
