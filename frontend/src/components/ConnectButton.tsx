import { Brain } from 'lucide-react';
import { useState } from 'react';
import { MuseClient } from '../lib/museClient';

interface ConnectButtonProps {
  onConnect: (client: MuseClient) => void;
}

interface MuseDevice {
  name: string;
  address: string;
  rssi: number;
}

export function ConnectButton({ onConnect }: ConnectButtonProps) {
  const [connecting, setConnecting] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [devices, setDevices] = useState<MuseDevice[]>([]);
  const [client] = useState(() => new MuseClient());

  const handleScan = async () => {
    try {
      setError(null);
      setScanning(true);
      const foundDevices = await client.getDevices();
      setDevices(foundDevices);
      
      if (foundDevices.length === 0) {
        setError('No Muse devices found. Make sure your device is turned on and in pairing mode.');
      }
    } catch (err) {
      console.error('Scan error:', err);
      setError(err instanceof Error ? err.message : 'Failed to scan for devices');
    } finally {
      setScanning(false);
    }
  };

  const handleConnect = async (address: string) => {
    try {
      setError(null);
      setConnecting(true);
      const success = await client.connect(address);
      
      if (success) {
        onConnect(client);
      }
    } catch (err) {
      console.error('Connection error:', err);
      setError(err instanceof Error ? err.message : 'Failed to connect to device');
    } finally {
      setConnecting(false);
    }
  };

  return (
    <div className="space-y-4">
      <button
        onClick={handleScan}
        disabled={scanning}
        className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
      >
        <Brain className="w-5 h-5" />
        {scanning ? 'Scanning...' : 'Scan for Devices'}
      </button>
      
      {devices.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-medium text-gray-900">Available Devices</h3>
          <div className="space-y-2">
            {devices.map((device) => (
              <button
                key={device.address}
                onClick={() => handleConnect(device.address)}
                disabled={connecting}
                className="w-full flex items-center justify-between px-4 py-2 text-left border rounded-lg hover:bg-gray-50"
              >
                <span className="flex items-center gap-2">
                  <Brain className="w-4 h-4 text-gray-500" />
                  <span className="font-medium">{device.name}</span>
                </span>
                <span className="text-sm text-gray-500">
                  Signal: {device.rssi}dB
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
      
      {error && (
        <div className="text-red-600 text-sm bg-red-50 p-4 rounded-lg">
          {error}
        </div>
      )}
      
      <div className="text-sm text-gray-600">
        <p>Before scanning:</p>
        <ol className="list-decimal list-inside space-y-1 mt-2">
          <li>Ensure your Muse headband is turned on (check the light)</li>
          <li>Put the device in pairing mode (hold the button until light flashes)</li>
          <li>Make sure the device is not connected to any other device</li>
        </ol>
      </div>
    </div>
  );
}