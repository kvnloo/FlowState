import * as Tone from 'tone';
import { AIAdvisor } from './aiAdvisor';

interface FrequencyResponse {
  baseFreq: number;
  beatFreq: number;
  timestamp: number;
  alphaResponse: number;
  thetaResponse: number;
  betaResponse: number;
  gammaResponse: number;
  userState: {
    timeOfDay: number;
    fatigue?: number;
    caffeineLevel?: number;
    lastSleep?: number;
  };
}

interface FrequencyRecommendation {
  baseFreq: number;
  beatFreq: number;
  confidence: number;
  reasoning: string;
}

export class AdaptiveAudioEngine {
  private leftOsc: Tone.Oscillator;
  private rightOsc: Tone.Oscillator;
  private gainNode: Tone.Gain;
  private advisor: AIAdvisor;
  private userResponses: FrequencyResponse[] = [];
  private currentSession: FrequencyResponse | null = null;
  private sessionStartTime: number = 0;

  // Frequency ranges for different brain states
  private readonly FREQUENCY_RANGES = {
    delta: { min: 0.5, max: 4 },
    theta: { min: 4, max: 8 },
    alpha: { min: 8, max: 13 },
    beta: { min: 13, max: 30 },
    gamma: { min: 30, max: 100 },
  };

  constructor(apiKey: string) {
    this.leftOsc = new Tone.Oscillator().toDestination();
    this.rightOsc = new Tone.Oscillator().toDestination();
    this.gainNode = new Tone.Gain(0.1).toDestination();
    this.advisor = new AIAdvisor(apiKey);
    
    this.leftOsc.connect(this.gainNode);
    this.rightOsc.connect(this.gainNode);

    // Load previous user responses from localStorage
    this.loadUserResponses();
  }

  private loadUserResponses() {
    const saved = localStorage.getItem('frequencyResponses');
    if (saved) {
      this.userResponses = JSON.parse(saved);
    }
  }

  private saveUserResponses() {
    localStorage.setItem('frequencyResponses', JSON.stringify(this.userResponses));
  }

  async start(targetState: 'focus' | 'relax' | 'meditate' | 'energize', userState?: {
    fatigue?: number;
    caffeineLevel?: number;
    lastSleep?: number;
  }) {
    const recommendation = await this.getOptimalFrequencies(targetState, userState);
    
    this.leftOsc.frequency.value = recommendation.baseFreq;
    this.rightOsc.frequency.value = recommendation.baseFreq + recommendation.beatFreq;
    
    this.sessionStartTime = Date.now();
    this.currentSession = {
      baseFreq: recommendation.baseFreq,
      beatFreq: recommendation.beatFreq,
      timestamp: this.sessionStartTime,
      alphaResponse: 0,
      thetaResponse: 0,
      betaResponse: 0,
      gammaResponse: 0,
      userState: {
        timeOfDay: new Date().getHours(),
        ...userState
      }
    };
    
    this.leftOsc.start();
    this.rightOsc.start();

    console.log('Starting session with frequencies:', {
      base: recommendation.baseFreq,
      beat: recommendation.beatFreq,
      reasoning: recommendation.reasoning
    });
  }

  stop() {
    this.leftOsc.stop();
    this.rightOsc.stop();
    
    if (this.currentSession) {
      this.userResponses.push(this.currentSession);
      this.saveUserResponses();
      this.currentSession = null;
    }
  }

  setVolume(volume: number) {
    this.gainNode.gain.value = volume;
  }

  // Update the current session with brainwave responses
  updateBrainwaveResponse(data: {
    alpha: number;
    theta: number;
    beta: number;
    gamma: number;
  }) {
    if (this.currentSession) {
      this.currentSession.alphaResponse = Math.max(this.currentSession.alphaResponse, data.alpha);
      this.currentSession.thetaResponse = Math.max(this.currentSession.thetaResponse, data.theta);
      this.currentSession.betaResponse = Math.max(this.currentSession.betaResponse, data.beta);
      this.currentSession.gammaResponse = Math.max(this.currentSession.gammaResponse, data.gamma);
    }
  }

  private async getOptimalFrequencies(
    targetState: 'focus' | 'relax' | 'meditate' | 'energize',
    userState?: { fatigue?: number; caffeineLevel?: number; lastSleep?: number; }
  ): Promise<FrequencyRecommendation> {
    const prompt = `
      Analyze the user's frequency response history and current state to recommend optimal binaural beat frequencies.
      
      Target State: ${targetState}
      Time of Day: ${new Date().getHours()}
      User State:
      - Fatigue Level (0-1): ${userState?.fatigue || 'unknown'}
      - Caffeine Level (0-1): ${userState?.caffeineLevel || 'unknown'}
      - Hours Since Last Sleep: ${userState?.lastSleep || 'unknown'}
      
      Previous Response History:
      ${JSON.stringify(this.userResponses.slice(-5), null, 2)}
      
      Consider:
      1. Historical effectiveness of frequencies for this user
      2. Time of day and user's current state
      3. Latest neuroscience research on binaural beats
      4. Optimal frequency ranges for target state
      
      Provide recommendation in JSON format:
      {
        "baseFreq": number (carrier frequency),
        "beatFreq": number (difference frequency),
        "confidence": number (0-1),
        "reasoning": string (explanation)
      }
    `;

    try {
      const response = await this.advisor.getFrequencyRecommendation(prompt);
      return response;
    } catch (error) {
      console.error('Error getting frequency recommendation:', error);
      
      // Fallback to default frequencies based on target state
      const defaults = {
        focus: { base: 200, beat: 10 },      // Alpha
        relax: { base: 200, beat: 6 },       // Theta
        meditate: { base: 200, beat: 4 },    // Delta/Theta
        energize: { base: 200, beat: 20 },   // Beta
      };

      return {
        baseFreq: defaults[targetState].base,
        beatFreq: defaults[targetState].beat,
        confidence: 0.5,
        reasoning: 'Using default frequencies due to AI service unavailability'
      };
    }
  }

  // Adjust frequencies in real-time based on brainwave feedback
  async adjustFrequencies(currentMetrics: {
    alphaQuality: number;
    thetaBalance: number;
    betaSuppression: number;
    flowScore: number;
  }) {
    if (!this.currentSession) return;

    const prompt = `
      Analyze current brainwave metrics and suggest frequency adjustments:
      
      Current Frequencies:
      - Base: ${this.currentSession.baseFreq}
      - Beat: ${this.currentSession.beatFreq}
      
      Current Metrics:
      ${JSON.stringify(currentMetrics, null, 2)}
      
      Suggest small adjustments to optimize entrainment.
      Response format:
      {
        "adjustBaseFreq": number (adjustment in Hz),
        "adjustBeatFreq": number (adjustment in Hz),
        "confidence": number (0-1),
        "reasoning": string
      }
    `;

    try {
      const adjustment = await this.advisor.getFrequencyAdjustment(prompt);
      
      if (adjustment.confidence > 0.7) {
        this.leftOsc.frequency.value += adjustment.adjustBaseFreq;
        this.rightOsc.frequency.value = this.leftOsc.frequency.value + 
          (this.currentSession.beatFreq + adjustment.adjustBeatFreq);
        
        console.log('Adjusted frequencies:', {
          newBase: this.leftOsc.frequency.value,
          newBeat: this.rightOsc.frequency.value - this.leftOsc.frequency.value,
          reasoning: adjustment.reasoning
        });
      }
    } catch (error) {
      console.error('Error adjusting frequencies:', error);
    }
  }
}
