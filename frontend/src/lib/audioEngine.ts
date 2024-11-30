/**
 * Client for the FlowState adaptive audio engine.
 * Communicates with the backend to control binaural beats generation.
 */

type UserState = {
  fatigue?: number;
  caffeine_level?: number;
  last_sleep?: number;
  time_of_day?: number;
};

type FrequencyRecommendation = {
  base_frequency: number;
  beat_frequency: number;
  strobe_frequency: number;
  confidence: number;
  reasoning: string;
};

type TargetState = 'focus' | 'flow' | 'meditate';

export class BinauralBeatsEngine {
  private isPlaying = false;
  private volume = 0.1;
  private baseUrl = 'http://localhost:8000/api';

  constructor() {
    // Initialize connection to backend
  }

  async start(targetState: TargetState, userState?: UserState) {
    try {
      const response = await fetch(`${this.baseUrl}/audio/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          target_state: targetState,
          user_state: userState,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to start audio');
      }

      const data = await response.json();
      this.isPlaying = true;
      return data.strobe_frequency;
    } catch (error) {
      console.error('Error starting audio:', error);
      throw error;
    }
  }

  async stop() {
    try {
      const response = await fetch(`${this.baseUrl}/audio/stop`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to stop audio');
      }

      this.isPlaying = false;
    } catch (error) {
      console.error('Error stopping audio:', error);
      throw error;
    }
  }

  async setVolume(volume: number) {
    try {
      const response = await fetch(`${this.baseUrl}/audio/volume`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ volume }),
      });

      if (!response.ok) {
        throw new Error('Failed to set volume');
      }

      this.volume = volume;
    } catch (error) {
      console.error('Error setting volume:', error);
      throw error;
    }
  }

  async getOptimalFrequencies(targetState: TargetState, userState?: UserState): Promise<FrequencyRecommendation> {
    try {
      const params = new URLSearchParams({
        target_state: targetState,
        ...(userState && { user_state: JSON.stringify(userState) }),
      });

      const response = await fetch(
        `${this.baseUrl}/audio/frequencies?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error('Failed to get frequency recommendations');
      }

      return response.json();
    } catch (error) {
      console.error('Error getting frequencies:', error);
      throw error;
    }
  }

  getIsPlaying() {
    return this.isPlaying;
  }

  getCurrentVolume() {
    return this.volume;
  }
}
