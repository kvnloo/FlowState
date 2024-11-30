import { useEffect, useState } from 'react';
import { MuseClient } from '../lib/museClient';
import { EEGClient } from '../lib/eegClient';
import { ConnectButton } from '../components/ConnectButton';
import { WaveChart } from '../components/WaveChart';
import { BrainwaveBanner } from '../components/BrainwaveBanner';
import { FlowStateIndicator } from '../components/FlowStateIndicator';
import { useBrainwaveStore } from '../store/brainwaveStore';
import { Activity, Brain, Waves } from 'lucide-react';

export function Dashboard() {
  const [museClient, setMuseClient] = useState<MuseClient | null>(null);
  const [eegClient, setEegClient] = useState<EEGClient | null>(null);
  const [alphaTheta, setAlphaTheta] = useState(0);
  const [signalQuality, setSignalQuality] = useState<{[key: string]: number}>({});
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

  useEffect(() => {
    // Try to connect to backend on component mount
    handleBackendConnect();
    
    return () => {
      museClient?.disconnect();
      eegClient?.disconnect();
    };
  }, []);

  // Create an array of the last 10 readings for the banner
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
            <Brain className="w-5 h-5 mr-2" />
            Flow State Analysis
          </h2>
          <div className="space-y-4">
            <p className="text-gray-600">
              The Alpha/Theta ratio is a key indicator of your cognitive state:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-600">
              <li>Below 0.8: Mind wandering or unfocused</li>
              <li>0.8 - 1.6: Focused attention</li>
              <li>Above 1.6: Optimal flow state</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}