import { useEffect, useState } from 'react';
import { AdaptiveAudioEngine } from '../lib/adaptiveAudioEngine';
import { Brain, Play, Square, Volume2, Coffee, Moon, Zap } from 'lucide-react';
import { useBrainwaveStore } from '../store/brainwaveStore';

const audioEngine = new AdaptiveAudioEngine(process.env.VITE_OPENAI_API_KEY || '');

interface UserState {
  fatigue: number;
  caffeineLevel: number;
  lastSleep: number;
}

export function Training() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(0.1);
  const [targetState, setTargetState] = useState<'focus' | 'relax' | 'meditate' | 'energize'>('focus');
  const [userState, setUserState] = useState<UserState>({
    fatigue: 0.5,
    caffeineLevel: 0.5,
    lastSleep: 8,
  });
  const { delta, theta, alpha, beta, gamma } = useBrainwaveStore();

  useEffect(() => {
    if (isPlaying) {
      // Update brainwave response every 5 seconds
      const interval = setInterval(() => {
        audioEngine.updateBrainwaveResponse({
          alpha: alpha[alpha.length - 1] || 0,
          theta: theta[theta.length - 1] || 0,
          beta: beta[beta.length - 1] || 0,
          gamma: gamma[gamma.length - 1] || 0,
        });
      }, 5000);

      return () => clearInterval(interval);
    }
  }, [isPlaying, alpha, theta, beta, gamma]);

  const handlePlay = async () => {
    if (isPlaying) {
      audioEngine.stop();
    } else {
      await audioEngine.start(targetState, userState);
    }
    setIsPlaying(!isPlaying);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    audioEngine.setVolume(newVolume);
  };

  const handleStateChange = (newState: typeof targetState) => {
    setTargetState(newState);
    if (isPlaying) {
      audioEngine.stop();
      audioEngine.start(newState, userState);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <header className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Brain Training</h1>
        <p className="text-gray-600">Personalized neural entrainment session</p>
      </header>

      <div className="bg-white p-8 rounded-xl shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target State
              </label>
              <div className="grid grid-cols-2 gap-2">
                {(['focus', 'relax', 'meditate', 'energize'] as const).map((state) => (
                  <button
                    key={state}
                    onClick={() => handleStateChange(state)}
                    className={`px-4 py-2 rounded-lg capitalize ${
                      targetState === state
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {state}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <Moon className="w-4 h-4" />
                  Fatigue Level
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={userState.fatigue}
                  onChange={(e) =>
                    setUserState((prev) => ({
                      ...prev,
                      fatigue: parseFloat(e.target.value),
                    }))
                  }
                  className="w-full"
                />
                <div className="text-sm text-gray-600">
                  {(userState.fatigue * 100).toFixed(0)}%
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <Coffee className="w-4 h-4" />
                  Caffeine Level
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={userState.caffeineLevel}
                  onChange={(e) =>
                    setUserState((prev) => ({
                      ...prev,
                      caffeineLevel: parseFloat(e.target.value),
                    }))
                  }
                  className="w-full"
                />
                <div className="text-sm text-gray-600">
                  {(userState.caffeineLevel * 100).toFixed(0)}%
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  Hours Since Last Sleep
                </label>
                <input
                  type="range"
                  min="0"
                  max="24"
                  step="0.5"
                  value={userState.lastSleep}
                  onChange={(e) =>
                    setUserState((prev) => ({
                      ...prev,
                      lastSleep: parseFloat(e.target.value),
                    }))
                  }
                  className="w-full"
                />
                <div className="text-sm text-gray-600">{userState.lastSleep} hours</div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <Volume2 className="w-4 h-4" />
                  Volume
                </label>
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