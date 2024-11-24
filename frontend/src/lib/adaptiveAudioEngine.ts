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
  flowScore: number;
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
  strobeFreq: number;
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

  // Optimized frequency ranges for flow states
  private readonly FREQUENCY_RANGES = {
    flow: { 
      alpha: { min: 8, max: 12 },    // Upper alpha band
      theta: { min: 6, max: 8 },     // Upper theta band
      beta: { min: 12, max: 15 }     // Low beta band
    },
    carrier: { min: 100, max: 400 }, // Carrier frequency range
    strobe: { min: 4, max: 12 }      // Safe strobe frequency range
  };

  constructor(apiKey: string) {
    this.leftOsc = new Tone.Oscillator().toDestination();
    this.rightOsc = new Tone.Oscillator().toDestination();
    this.gainNode = new Tone.Gain(0.1).toDestination();
    this.advisor = new AIAdvisor(apiKey);
    
    this.leftOsc.connect(this.gainNode);
    this.rightOsc.connect(this.gainNode);

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

  private calculateFlowScore(data: {
    alpha: number;
    theta: number;
    beta: number;
  }): number {
    // Enhanced flow state detection algorithm
    const alphaPower = data.alpha;
    const thetaPower = data.theta;
    const betaPower = data.beta;

    // Calculate ratios important for flow state
    const alphaTheta = alphaPower / (thetaPower || 0.1);  // Alpha/Theta ratio
    const alphaBeta = alphaPower / (betaPower || 0.1);    // Alpha/Beta ratio

    // Ideal ranges for flow state
    const idealAlphaTheta = 1.5;  // Slightly more alpha than theta
    const idealAlphaBeta = 2.0;   // Alpha should be stronger than beta

    // Calculate how close we are to ideal ratios
    const alphaThetaScore = 1 - Math.min(Math.abs(alphaTheta - idealAlphaTheta) / idealAlphaTheta, 1);
    const alphaBetaScore = 1 - Math.min(Math.abs(alphaBeta - idealAlphaBeta) / idealAlphaBeta, 1);

    // Combine scores with weights
    return 0.6 * alphaThetaScore + 0.4 * alphaBetaScore;
  }

  async start(targetState: 'focus' | 'flow' | 'meditate', userState?: {
    fatigue?: number;
    caffeineLevel?: number;
    lastSleep?: number;
  }) {
    const recommendation = await this.getOptimalFrequencies(targetState, userState);
    
    // Set audio frequencies
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
      flowScore: 0,
      userState: {
        timeOfDay: new Date().getHours(),
        ...userState
      }
    };
    
    this.leftOsc.start();
    this.rightOsc.start();

    // Return strobe frequency for visual synchronization
    return recommendation.strobeFreq;
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
      // Update maximum band powers
      this.currentSession.alphaResponse = Math.max(this.currentSession.alphaResponse, data.alpha);
      this.currentSession.thetaResponse = Math.max(this.currentSession.thetaResponse, data.theta);
      this.currentSession.betaResponse = Math.max(this.currentSession.betaResponse, data.beta);
      this.currentSession.gammaResponse = Math.max(this.currentSession.gammaResponse, data.gamma);

      // Calculate and update flow score
      const flowScore = this.calculateFlowScore({
        alpha: data.alpha,
        theta: data.theta,
        beta: data.beta
      });
      this.currentSession.flowScore = Math.max(this.currentSession.flowScore, flowScore);

      // If flow score is high enough, save these frequencies as effective
      if (flowScore > 0.8) {
        this.userResponses.push({
          ...this.currentSession,
          timestamp: Date.now(),
          flowScore
        });
        this.saveUserResponses();
      }
    }
  }

  private async getOptimalFrequencies(
    targetState: 'focus' | 'flow' | 'meditate',
    userState?: { fatigue?: number; caffeineLevel?: number; lastSleep?: number; }
  ): Promise<FrequencyRecommendation> {
    // Filter for successful flow states in similar conditions
    const successfulSessions = this.userResponses.filter(session => 
      session.flowScore > 0.8 &&
      Math.abs(session.userState.timeOfDay - new Date().getHours()) <= 2
    );

    // If we have successful sessions, use them to inform our choice
    if (successfulSessions.length > 0) {
      const bestSession = successfulSessions.reduce((best, current) => 
        current.flowScore > best.flowScore ? current : best
      );

      return {
        baseFreq: bestSession.baseFreq,
        beatFreq: bestSession.beatFreq,
        strobeFreq: bestSession.beatFreq / 2, // Harmonically related to audio
        confidence: 0.9,
        reasoning: 'Using previously successful frequency combination'
      };
    }

    // Otherwise, use AI advisor with enhanced parameters
    const prompt = `
      Recommend optimal frequencies for neural entrainment targeting flow state.
      
      Current Context:
      - Target State: ${targetState}
      - Time: ${new Date().getHours()}:00
      - Fatigue: ${userState?.fatigue || 'unknown'}
      - Caffeine: ${userState?.caffeineLevel || 'unknown'}
      - Sleep: ${userState?.lastSleep || 'unknown'}h ago
      
      Requirements:
      1. Base frequency should be in carrier range (${this.FREQUENCY_RANGES.carrier.min}-${this.FREQUENCY_RANGES.carrier.max}Hz)
      2. Beat frequency should target upper alpha/lower beta (${this.FREQUENCY_RANGES.flow.alpha.min}-${this.FREQUENCY_RANGES.flow.beta.min}Hz)
      3. Strobe frequency should be harmonically related to beat frequency
      4. Consider circadian rhythms and user state
      
      Previous successful combinations:
      ${JSON.stringify(successfulSessions.slice(-3), null, 2)}
    `;

    try {
      const response = await this.advisor.getFrequencyRecommendation(prompt);
      return response;
    } catch (error) {
      console.error('Error getting frequency recommendation:', error);
      
      // Enhanced default frequencies based on target state
      const defaults = {
        focus: { base: 200, beat: 10, strobe: 5 },     // Upper alpha
        flow: { base: 200, beat: 8, strobe: 4 },       // Alpha-theta border
        meditate: { base: 200, beat: 6, strobe: 3 },   // Theta
      };

      return {
        ...defaults[targetState],
        confidence: 0.5,
        reasoning: 'Using research-based default frequencies'
      };
    }
  }
}
