import { useEffect, useState } from 'react';
import { MuseClient } from '../lib/museClient';
import { EEGClient } from '../lib/eegClient';
import { BinauralBeatsEngine } from '../lib/audioEngine';
import { ConnectButton } from '../components/ConnectButton';
import { WaveChart } from '../components/WaveChart';
import { BrainwaveBanner } from '../components/BrainwaveBanner';
import { FlowStateIndicator } from '../components/FlowStateIndicator';
import { useBrainwaveStore } from '../store/brainwaveStore';
import { Activity, Brain, Waves, Volume2, VolumeX, Play, Pause } from 'lucide-react';

type EntrainmentState = 'focus' | 'flow' | 'meditate';

export function Dashboard() {
  const [museClient, setMuseClient] = useState<MuseClient | null>(null);
  const [eegClient, setEegClient] = useState<EEGClient | null>(null);
  const [audioEngine] = useState(() => new BinauralBeatsEngine());
  const [alphaTheta, setAlphaTheta] = useState(0);
  const [signalQuality, setSignalQuality] = useState<{[key: string]: number}>({});
  const [volume, setVolume] = useState(0.1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentState, setCurrentState] = useState<EntrainmentState>('focus');
  const { delta, theta, alpha, beta, gamma, updateWaves } = useBrainwaveStore();

  const handleMuseConnect = async (client: MuseClient) => {
    setMuseClient(client);
    await client.startMonitoring((data) => {
      updateWaves({
        delta: Math.abs(data[0]),
        theta: Math.abs(data[1]),
        alpha: Math.abs(data[2]),
        beta: Math.abs(data[3]),
        gamma: Math.abs(data[4]),
      });
    });
  };

  const handleBackendConnect = async () => {
    const client = new EEGClient();
    const success = await client.connect();
    
    if (success) {
      setEegClient(client);
      client.onData((data) => {
        updateWaves(data.band_powers);
        setAlphaTheta(data.alpha_theta_ratio);
        setSignalQuality(data.signal_quality);
      });
    }
  };

  const handleStateChange = async (state: EntrainmentState) => {
    if (isPlaying) {
      await audioEngine.stop();
    }
    setCurrentState(state);
    if (isPlaying) {
      await startEntrainment(state);
    }
  };

  const startEntrainment = async (state: EntrainmentState) => {
    try {
      const userState = {
        fatigue: 0.5, // TODO: Calculate from EEG data
        time_of_day: new Date().getHours(),
      };
      await audioEngine.start(state, userState);
      setIsPlaying(true);
    } catch (error) {
      console.error('Failed to start entrainment:', error);
    }
  };

  const stopEntrainment = async () => {
    try {
      await audioEngine.stop();
      setIsPlaying(false);
    } catch (error) {
      console.error('Failed to stop entrainment:', error);
    }
  };

  const handleVolumeChange = async (newVolume: number) => {
    try {
      await audioEngine.setVolume(newVolume);
      setVolume(newVolume);
    } catch (error) {
      console.error('Failed to update volume:', error);
    }
  };

  useEffect(() => {
    handleBackendConnect();
    return () => {
      museClient?.disconnect();
      eegClient?.disconnect();
      audioEngine.stop();
    };
  }, []);

  const bannerData = Array.from({ length: 10 }, (_, i) => ({
    delta: delta[delta.length - 1 - i] || 0,
    theta: theta[theta.length - 1 - i] || 0,
    alpha: alpha[alpha.length - 1 - i] || 0,
    beta: beta[beta.length - 1 - i] || 0,
    gamma: gamma[gamma.length - 1 - i] || 0,
  })).reverse();

  return (
    <div className="space-y-8">
      <header className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Neurofeedback Dashboard</h1>
        <p className="text-gray-600 mb-8">Monitor your brainwave activity in real-time</p>
        {!museClient && !eegClient && (
          <div className="space-y-4">
            <ConnectButton onConnect={handleMuseConnect} />
            <button
              onClick={handleBackendConnect}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              Connect to Backend
            </button>
          </div>
        )}
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <BrainwaveBanner data={bannerData} />
        <FlowStateIndicator 
          alphaTheta={alphaTheta}
          signalQuality={signalQuality}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2" />
            Real-time Brainwaves
          </h2>
          <WaveChart data={bannerData} />
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Waves className="w-5 h-5 mr-2" />
            Neural Entrainment
          </h2>
          
          <div className="space-y-6">
            <div className="flex gap-4">
              {(['focus', 'flow', 'meditate'] as EntrainmentState[]).map((state) => (
                <button
                  key={state}
                  onClick={() => handleStateChange(state)}
                  className={`flex-1 px-4 py-2 rounded-lg capitalize transition-colors ${
                    currentState === state
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {state}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-4">
              <button
                onClick={isPlaying ? stopEntrainment : () => startEntrainment(currentState)}
                className="p-2 rounded-full bg-purple-600 text-white hover:bg-purple-700 transition-colors"
              >
                {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
              </button>

              <div className="flex-1 flex items-center gap-4">
                <VolumeX className="w-5 h-5 text-gray-500" />
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={volume}
                  onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                  className="flex-1"
                />
                <Volume2 className="w-5 h-5 text-gray-500" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}