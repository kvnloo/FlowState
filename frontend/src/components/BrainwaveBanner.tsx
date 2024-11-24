import React, { useState, useCallback } from 'react';
import { Maximize2, Minimize2, Code } from 'lucide-react';
import { BrainwaveIcon } from './BrainwaveIcon';
import { useBrainwaveStore } from '../store/brainwaveStore';

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
  const [devMode, setDevMode] = useState(false);
  const bannerRef = React.useRef<HTMLDivElement>(null);
  const loadSampleData = useBrainwaveStore(state => state.loadSampleData);

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
      className={`relative bg-black p-4 rounded-xl overflow-hidden ${
        isFullscreen ? 'fixed inset-0 z-50' : 'w-full'
      }`}
    >
      <div className="absolute top-4 right-4 flex gap-2 z-10">
        <button
          onClick={() => setDevMode(!devMode)}
          className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
        >
          <Code className="w-5 h-5 text-white" />
        </button>
        <button
          onClick={toggleFullscreen}
          className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
        >
          {isFullscreen ? (
            <Minimize2 className="w-5 h-5 text-white" />
          ) : (
            <Maximize2 className="w-5 h-5 text-white" />
          )}
        </button>
      </div>

      {devMode && (
        <button
          onClick={loadSampleData}
          className="absolute top-4 left-4 px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors text-white text-sm z-10"
        >
          Load Dummy Data
        </button>
      )}

      <div className="flex items-center h-[80px] gap-[2px] overflow-x-auto">
        {data.map((reading, index) => (
          <div
            key={index}
            className="flex-shrink-0"
            style={{ opacity: 0.9 }}
          >
            <BrainwaveIcon
              data={reading}
              size={isFullscreen ? 120 : 60}
            />
          </div>
        ))}
      </div>
    </div>
  );
}