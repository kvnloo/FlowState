interface StrobePattern {
  frequency: number;
  intensity: number;
  duration: number;
}

export class StrobeService {
  private ws: WebSocket | null = null;
  private readonly wsUrl: string;

  constructor() {
    this.wsUrl = 'ws://localhost:8000/ws/eeg';
  }

  connect(onPattern: (pattern: StrobePattern) => void) {
    if (this.ws) {
      this.ws.close();
    }

    this.ws = new WebSocket(this.wsUrl);

    this.ws.onopen = () => {
      console.log('Connected to strobe control service');
    };

    this.ws.onmessage = (event) => {
      const pattern: StrobePattern = JSON.parse(event.data);
      onPattern(pattern);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('Disconnected from strobe control service');
    };
  }

  sendBrainwaveData(data: {
    delta: number;
    theta: number;
    alpha: number;
    beta: number;
    gamma: number;
  }) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
