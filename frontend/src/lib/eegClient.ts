/**
 * Client for connecting to the FlowState EEG backend service.
 * Handles WebSocket connection and data processing.
 */

type EEGData = {
  timestamp: number;
  alpha_theta_ratio: number;
  band_powers: {
    delta: number;
    theta: number;
    alpha: number;
    beta: number;
    gamma: number;
  };
  signal_quality: {
    [channel: string]: number;
  };
};

type EEGCallback = (data: EEGData) => void;

export class EEGClient {
  private ws: WebSocket | null = null;
  private callbacks: EEGCallback[] = [];
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second delay

  constructor(private url: string = 'ws://localhost:8000/ws/eeg') {}

  async connect(): Promise<boolean> {
    try {
      return new Promise((resolve, reject) => {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('Connected to EEG backend');
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1000;
          resolve(true);
        };

        this.ws.onmessage = (event) => {
          try {
            const data: EEGData = JSON.parse(event.data);
            this.callbacks.forEach(callback => callback(data));
          } catch (error) {
            console.error('Error parsing EEG data:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket connection closed');
          this.handleDisconnect();
        };
      });
    } catch (error) {
      console.error('Connection failed:', error);
      return false;
    }
  }

  private handleDisconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        console.log(`Attempting to reconnect (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})...`);
        this.connect();
        this.reconnectAttempts++;
        this.reconnectDelay *= 2; // Exponential backoff
      }, this.reconnectDelay);
    }
  }

  onData(callback: EEGCallback) {
    this.callbacks.push(callback);
    return () => {
      this.callbacks = this.callbacks.filter(cb => cb !== callback);
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.callbacks = [];
  }

  async getDevices(): Promise<any[]> {
    try {
      const response = await fetch('http://localhost:8000/api/devices');
      const data = await response.json();
      return data.devices;
    } catch (error) {
      console.error('Error fetching devices:', error);
      return [];
    }
  }

  async connectDevice(address: string): Promise<boolean> {
    try {
      const response = await fetch(`http://localhost:8000/api/connect/${address}`, {
        method: 'POST'
      });
      const data = await response.json();
      return data.success;
    } catch (error) {
      console.error('Error connecting to device:', error);
      return false;
    }
  }
}
