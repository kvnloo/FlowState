import React, { useState, useCallback } from 'react';
import { Maximize2, Minimize2 } from 'lucide-react';
import { BrainwaveIcon } from './BrainwaveIcon';

interface BrainwaveBannerProps {
  data: Array<{
    delta: number;
    theta: number;
    alpha: number;
    beta: number;
    gamma: number;
  }>;
}

export function BrainwaveBanner({ data }: BrainwaveBannerProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const bannerRef = React.useRef<HTMLDivElement>(null);

  const toggleFullscreen = useCallback(async () => {
    if (!document.fullscreenElement) {
      await bannerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      await document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  return (
    <div
      ref={bannerRef}
      className={`relative bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 p-6 rounded-xl overflow-hidden ${
        isFullscreen ? 'fixed inset-0 z-50' : 'w-full'
      }`}
    >
      <button
        onClick={toggleFullscreen}
        className="absolute top-4 right-4 p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors z-10"
      >
        {isFullscreen ? (
          <Minimize2 className="w-5 h-5 text-white" />
        ) : (
          <Maximize2 className="w-5 h-5 text-white" />
        )}
      </button>

      <div className="flex gap-4 overflow-x-auto pb-4 snap-x">
        {data.map((reading, index) => (
          <div
            key={index}
            className="snap-start flex-shrink-0"
            style={{ opacity: 1 - index * 0.1 }}
          >
            <BrainwaveIcon
              data={reading}
              size={isFullscreen ? 200 : 100}
            />
          </div>
        ))}
      </div>

      <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />
    </div>
  );
}