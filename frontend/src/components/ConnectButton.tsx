import { Brain } from 'lucide-react';
import { useState } from 'react';
import { MuseClient } from '../lib/museClient';

interface ConnectButtonProps {
  onConnect: (client: MuseClient) => void;
}

export function ConnectButton({ onConnect }: ConnectButtonProps) {
  const [connecting, setConnecting] = useState(false);

  const handleConnect = async () => {
    setConnecting(true);
    const client = new MuseClient();
    const success = await client.connect();
    
    if (success) {
      onConnect(client);
    }
    setConnecting(false);
  };

  return (
    <button
      onClick={handleConnect}
      disabled={connecting}
      className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
    >
      <Brain className="w-5 h-5" />
      {connecting ? 'Connecting...' : 'Connect Muse'}
    </button>
  );
}