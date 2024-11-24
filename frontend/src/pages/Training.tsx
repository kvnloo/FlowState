import { useState } from 'react';
import { BinauralBeatsEngine } from '../lib/audioEngine';
import { Brain, Play, Square, Volume2 } from 'lucide-react';

const audioEngine = new BinauralBeatsEngine();

export function Training() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [baseFreq, setBaseFreq] = useState(200);
  const [beatFreq, setBeatFreq] = useState(10);
  const [volume, setVolume] = useState(0.1);

  const handlePlay = () => {
    if (isPlaying) {
      audioEngine.stop();
    } else {
      audioEngine.start(baseFreq, beatFreq);
    }
    setIsPlaying(!isPlaying);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    audioEngine.setVolume(newVolume);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <header className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Brain Training</h1>
        <p className="text-gray-600">Customize your neural entrainment session</p>
      </header>

      <div className="bg-white p-8 rounded-xl shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Base Frequency (Hz)
              </label>
              <input
                type="range"
                min="100"
                max="400"
                value={baseFreq}
                onChange={(e) => setBaseFreq(Number(e.target.value))}
                className="w-full"
              />
              <span className="text-sm text-gray-600">{baseFreq} Hz</span>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Beat Frequency (Hz)
              </label>
              <input
                type="range"
                min="1"
                max="40"
                value={beatFreq}
                onChange={(e) => setBeatFreq(Number(e.target.value))}
                className="w-full"
              />
              <span className="text-sm text-gray-600">{beatFreq} Hz</span>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Volume
              </label>
              <div className="flex items-center gap-2">
                <Volume2 className="w-4 h-4 text-gray-500" />
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={volume}
                  onChange={handleVolumeChange}
                  className="w-full"
                />
              </div>
            </div>
          </div>

          <div className="flex flex-col justify-center items-center space-y-6">
            <button
              onClick={handlePlay}
              className="flex items-center gap-2 px-8 py-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              {isPlaying ? (
                <>
                  <Square className="w-5 h-5" />
                  Stop
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Start Session
                </>
              )}
            </button>

            {isPlaying && (
              <div className="flex items-center gap-2 text-green-600">
                <Brain className="w-5 h-5 animate-pulse" />
                <span>Session in progress...</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="bg-white p-8 rounded-xl shadow-sm">
        <h2 className="text-xl font-semibold mb-4">Frequency Bands Guide</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h3 className="font-medium text-gray-900">Delta (0.5-4 Hz)</h3>
            <p className="text-gray-600">Deep sleep, healing, and regeneration</p>
          </div>
          <div>
            <h3 className="font-medium text-gray-900">Theta (4-8 Hz)</h3>
            <p className="text-gray-600">Meditation, creativity, and deep relaxation</p>
          </div>
          <div>
            <h3 className="font-medium text-gray-900">Alpha (8-13 Hz)</h3>
            <p className="text-gray-600">Relaxed focus, stress reduction, and learning</p>
          </div>
          <div>
            <h3 className="font-medium text-gray-900">Beta (13-30 Hz)</h3>
            <p className="text-gray-600">Active thinking, focus, and problem solving</p>
          </div>
        </div>
      </div>
    </div>
  );
}