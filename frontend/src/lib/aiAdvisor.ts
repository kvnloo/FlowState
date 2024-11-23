import { Configuration, OpenAIApi } from 'openai';

interface BrainwaveData {
  delta: number[];
  theta: number[];
  alpha: number[];
  beta: number[];
  gamma: number[];
}

interface FlowState {
  score: number;
  alphaQuality: number;
  thetaBalance: number;
  betaSuppression: number;
  recommendations: string[];
}

interface FrequencyRecommendation {
  baseFreq: number;
  beatFreq: number;
  confidence: number;
  reasoning: string;
}

interface FrequencyAdjustment {
  adjustBaseFreq: number;
  adjustBeatFreq: number;
  confidence: number;
  reasoning: string;
}

interface FlowTriggerRecommendation {
  triggers: string[];
  sequence: {
    trigger: string;
    timing: number;
    intensity: number;
  }[];
  environment: {
    lighting: string;
    sound: string;
    space: string;
  };
  challenges: {
    description: string;
    difficulty: number;
    duration: number;
  }[];
}

export class AIAdvisor {
  private openai: OpenAIApi;
  private readonly FLOW_STATE_PROMPT = `
    As a neurofeedback expert, analyze the following brainwave data and provide insights about the user's flow state:
    - Alpha waves (8-13 Hz): Associated with relaxed focus and learning
    - Theta waves (4-8 Hz): Associated with creativity and deep relaxation
    - Beta waves (13-30 Hz): Associated with active thinking and problem-solving
    - Delta waves (0.5-4 Hz): Associated with deep sleep and healing
    - Gamma waves (30-100 Hz): Associated with peak performance and insight

    Consider:
    1. Alpha/Theta ratio for optimal flow state
    2. Beta suppression for reduced analytical thinking
    3. Gamma bursts for moments of insight
    4. Overall wave pattern stability

    Current research suggests optimal flow states show:
    - Elevated alpha activity
    - Moderate theta activity
    - Reduced beta activity
    - Occasional gamma bursts
    
    Provide specific recommendations for improving or maintaining the current state.
  `;

  constructor(apiKey: string) {
    const configuration = new Configuration({
      apiKey: apiKey
    });
    this.openai = new OpenAIApi(configuration);
  }

  private calculateMetrics(data: BrainwaveData): {
    alphaAvg: number;
    thetaAvg: number;
    betaAvg: number;
    alphaTheta: number;
    betaSuppress: number;
  } {
    const alphaAvg = data.alpha.reduce((a, b) => a + b) / data.alpha.length;
    const thetaAvg = data.theta.reduce((a, b) => a + b) / data.theta.length;
    const betaAvg = data.beta.reduce((a, b) => a + b) / data.beta.length;
    
    return {
      alphaAvg,
      thetaAvg,
      betaAvg,
      alphaTheta: alphaAvg / thetaAvg,
      betaSuppress: 1 - (betaAvg / (alphaAvg + thetaAvg))
    };
  }

  async analyzeFlowState(data: BrainwaveData): Promise<FlowState> {
    const metrics = this.calculateMetrics(data);
    
    // Prepare data for LLM analysis
    const prompt = `
      ${this.FLOW_STATE_PROMPT}
      
      Current Metrics:
      - Alpha/Theta Ratio: ${metrics.alphaTheta.toFixed(2)}
      - Beta Suppression: ${metrics.betaSuppress.toFixed(2)}
      - Average Alpha: ${metrics.alphaAvg.toFixed(2)}
      - Average Theta: ${metrics.thetaAvg.toFixed(2)}
      - Average Beta: ${metrics.betaAvg.toFixed(2)}
      
      Provide recommendations in JSON format:
      {
        "flowScore": number between 0-1,
        "alphaQuality": number between 0-1,
        "thetaBalance": number between 0-1,
        "betaSuppression": number between 0-1,
        "recommendations": [string array of specific suggestions]
      }
    `;

    try {
      const response = await this.openai.createChatCompletion({
        model: "gpt-4",
        messages: [{
          role: "system",
          content: "You are a neurofeedback expert specializing in flow states and peak performance."
        }, {
          role: "user",
          content: prompt
        }],
        temperature: 0.7,
        max_tokens: 500
      });

      const result = JSON.parse(response.data.choices[0].message?.content || "{}");
      
      return {
        score: result.flowScore || 0,
        alphaQuality: result.alphaQuality || 0,
        thetaBalance: result.thetaBalance || 0,
        betaSuppression: result.betaSuppression || 0,
        recommendations: result.recommendations || []
      };
    } catch (error) {
      console.error('Error analyzing flow state:', error);
      return {
        score: 0,
        alphaQuality: 0,
        thetaBalance: 0,
        betaSuppression: 0,
        recommendations: ['Unable to analyze flow state at this time.']
      };
    }
  }

  async getFrequencyRecommendation(prompt: string): Promise<FrequencyRecommendation> {
    try {
      const response = await this.openai.createChatCompletion({
        model: "gpt-4",
        messages: [{
          role: "system",
          content: `You are a neurofeedback expert specializing in binaural beats and brainwave entrainment.
            Your recommendations should be based on the latest research in neuroscience and brainwave entrainment.
            Consider the user's current state, time of day, and historical response patterns.
            Provide specific, evidence-based frequency recommendations.`
        }, {
          role: "user",
          content: prompt
        }],
        temperature: 0.7,
        max_tokens: 500
      });

      return JSON.parse(response.data.choices[0].message?.content || "{}");
    } catch (error) {
      console.error('Error getting frequency recommendation:', error);
      throw error;
    }
  }

  async getFrequencyAdjustment(prompt: string): Promise<FrequencyAdjustment> {
    try {
      const response = await this.openai.createChatCompletion({
        model: "gpt-4",
        messages: [{
          role: "system",
          content: `You are a neurofeedback expert specializing in real-time binaural beat optimization.
            Analyze brainwave metrics and suggest minor frequency adjustments to improve entrainment.
            Keep adjustments small and gradual to maintain stability.
            Consider the relationship between different frequency bands and their effects.`
        }, {
          role: "user",
          content: prompt
        }],
        temperature: 0.7,
        max_tokens: 500
      });

      return JSON.parse(response.data.choices[0].message?.content || "{}");
    } catch (error) {
      console.error('Error getting frequency adjustment:', error);
      throw error;
    }
  }

  async getFlowTriggerRecommendation(prompt: string): Promise<FlowTriggerRecommendation> {
    try {
      const response = await this.openai.createChatCompletion({
        model: "gpt-4",
        messages: [{
          role: "system",
          content: `You are a flow state expert from the Flow Research Collective.
            Your recommendations should be based on the latest flow research and neuroscience.
            Consider the user's current state, skill level, and environmental factors.
            Provide specific, actionable recommendations for achieving and maintaining flow state.`
        }, {
          role: "user",
          content: prompt
        }],
        temperature: 0.7,
        max_tokens: 500
      });

      return JSON.parse(response.data.choices[0].message?.content || "{}");
    } catch (error) {
      console.error('Error getting flow trigger recommendation:', error);
      throw error;
    }
  }
}
