import { useEffect, useState } from 'react';
import { MuseClient } from '../lib/museClient';
import { ConnectButton } from '../components/ConnectButton';
import { WaveChart } from '../components/WaveChart';
import { BrainwaveBanner } from '../components/BrainwaveBanner';
import { useBrainwaveStore } from '../store/brainwaveStore';
import { Activity, Brain, Waves } from 'lucide-react';

export function Dashboard() {
  const [client, setClient] = useState<MuseClient | null>(null);
  const { delta, theta, alpha, beta, gamma, updateWaves } = useBrainwaveStore();

  const handleConnect = async (museClient: MuseClient) => {
    setClient(museClient);
    await museClient.startMonitoring((data) => {
      // Simple frequency band extraction (simplified for demo)
      updateWaves({
        delta: Math.abs(data[0]),
        theta: Math.abs(data[1]),
        alpha: Math.abs(data[2]),
        beta: Math.abs(data[3]),
        gamma: Math.abs(data[4]),
      });
    });
  };

  useEffect(() => {
    return () => {
      client?.disconnect();
    };
  }, [client]);

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
        {!client && <ConnectButton onConnect={handleConnect} />}
      </header>

      <BrainwaveBanner data={bannerData} />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-5 h-5 text-purple-600" />
            <h2 className="text-xl font-semibold">Alpha Waves</h2>
          </div>
          <WaveChart data={alpha} label="Alpha" color="#9333ea" />
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Waves className="w-5 h-5 text-blue-600" />
            <h2 className="text-xl font-semibold">Beta Waves</h2>
          </div>
          <WaveChart data={beta} label="Beta" color="#2563eb" />
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-green-600" />
            <h2 className="text-xl font-semibold">Gamma Waves</h2>
          </div>
          <WaveChart data={gamma} label="Gamma" color="#16a34a" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Waves className="w-5 h-5 text-orange-600" />
            <h2 className="text-xl font-semibold">Theta Waves</h2>
          </div>
          <WaveChart data={theta} label="Theta" color="#ea580c" />
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Waves className="w-5 h-5 text-red-600" />
            <h2 className="text-xl font-semibold">Delta Waves</h2>
          </div>
          <WaveChart data={delta} label="Delta" color="#dc2626" />
        </div>
      </div>
    </div>
  );
}