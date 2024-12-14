interface MuseDevice {
  name: string;
  address: string;
  rssi: number;
}

export class MuseClient {
  private baseUrl = 'http://localhost:8000/api';
  private isConnecting: boolean = false;
  private isConnected: boolean = false;
  private websocket: WebSocket | null = null;

  async getDevices(): Promise<MuseDevice[]> {
    try {
      const response = await fetch(`${this.baseUrl}/devices`);
      if (!response.ok) {
        throw new Error('Failed to get devices');
      }
      const data = await response.json();
      return data.devices;
    } catch (error) {
      console.error('Error getting devices:', error);
      throw error;
    }
  }

  async connect(address: string) {
    if (this.isConnecting) {
      throw new Error('Already attempting to connect');
    }

    try {
      this.isConnecting = true;
      console.log('Connecting to Muse device...');

      // Connect to the device through backend
      const response = await fetch(`${this.baseUrl}/connect/${address}`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error('Failed to connect to device');
      }

      const data = await response.json();
      if (!data.success) {
        throw new Error('Device connection failed');
      }

      this.isConnected = true;
      console.log('Successfully connected to Muse');
      return true;
    } catch (error) {
      console.error('Connection error:', error);
      this.cleanup();
      throw error;
    } finally {
      this.isConnecting = false;
    }
  }

  async startMonitoring(callback: (data: number[]) => void) {
    if (!this.isConnected) {
      throw new Error('Not connected to Muse device');
    }

    try {
      console.log('Starting EEG monitoring...');
      
      // Connect to WebSocket for real-time data
      this.websocket = new WebSocket('ws://localhost:8000/api/ws');
      
      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.band_powers) {
          callback(Object.values(data.band_powers));
        }
      };

      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.cleanup();
      };

      console.log('EEG monitoring started');
    } catch (error) {
      console.error('Error starting monitoring:', error);
      throw error;
    }
  }

  private cleanup() {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    this.isConnected = false;
  }

  async disconnect() {
    this.cleanup();
  }

  getIsConnected() {
    return this.isConnected;
  }
}