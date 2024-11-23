import { AIAdvisor } from './aiAdvisor';

export interface FlowTrigger {
  id: string;
  name: string;
  category: 'psychological' | 'environmental' | 'social' | 'creative';
  description: string;
  intensity: number; // 0-1
  duration: number; // minutes
  prerequisites?: string[];
}

export interface FlowActivity {
  id: string;
  name: string;
  description: string;
  triggers: string[]; // Flow trigger IDs
  difficulty: number; // 0-1
  duration: number; // minutes
  skillRequired: number; // 0-1
  energyRequired: number; // 0-1
}

export interface UserFlowProfile {
  skillLevels: Record<string, number>;
  preferredTriggers: string[];
  challengeThreshold: number;
  optimalTimeOfDay: number[];
  successfulSessions: {
    date: string;
    duration: number;
    triggers: string[];
    flowScore: number;
  }[];
}

export class FlowTriggerSystem {
  private advisor: AIAdvisor;
  private userProfile: UserFlowProfile;

  // Core flow triggers based on Flow Research Collective research
  private readonly FLOW_TRIGGERS: FlowTrigger[] = [
    {
      id: 'clear_goals',
      name: 'Clear Goals',
      category: 'psychological',
      description: 'Well-defined objectives for the session',
      intensity: 0.7,
      duration: 5,
    },
    {
      id: 'immediate_feedback',
      name: 'Immediate Feedback',
      category: 'psychological',
      description: 'Real-time feedback on performance and progress',
      intensity: 0.8,
      duration: 30,
    },
    {
      id: 'challenge_balance',
      name: 'Challenge-Skill Balance',
      category: 'psychological',
      description: 'Optimal balance between challenge and ability',
      intensity: 0.9,
      duration: 30,
    },
    {
      id: 'deep_focus',
      name: 'Deep Focus Environment',
      category: 'environmental',
      description: 'Distraction-free environment for concentration',
      intensity: 0.8,
      duration: 45,
    },
    {
      id: 'autonomy',
      name: 'Autonomy',
      category: 'psychological',
      description: 'Control over session parameters and progression',
      intensity: 0.6,
      duration: 30,
    },
    {
      id: 'novelty',
      name: 'Novelty',
      category: 'creative',
      description: 'New and engaging elements or challenges',
      intensity: 0.7,
      duration: 15,
    },
    {
      id: 'social_flow',
      name: 'Social Flow',
      category: 'social',
      description: 'Collaborative or competitive elements',
      intensity: 0.8,
      duration: 30,
      prerequisites: ['clear_goals'],
    },
    {
      id: 'risk_taking',
      name: 'Calculated Risk',
      category: 'psychological',
      description: 'Safe environment for pushing boundaries',
      intensity: 0.9,
      duration: 20,
      prerequisites: ['challenge_balance'],
    },
  ];

  private readonly FLOW_ACTIVITIES: FlowActivity[] = [
    {
      id: 'focused_work',
      name: 'Deep Work Session',
      description: 'Focused work session with clear objectives',
      triggers: ['clear_goals', 'deep_focus', 'immediate_feedback'],
      difficulty: 0.7,
      duration: 45,
      skillRequired: 0.6,
      energyRequired: 0.8,
    },
    {
      id: 'creative_exploration',
      name: 'Creative Exploration',
      description: 'Open-ended creative session with novel challenges',
      triggers: ['novelty', 'autonomy', 'deep_focus'],
      difficulty: 0.6,
      duration: 30,
      skillRequired: 0.5,
      energyRequired: 0.7,
    },
    {
      id: 'skill_development',
      name: 'Skill Development',
      description: 'Structured practice with progressive challenges',
      triggers: ['challenge_balance', 'immediate_feedback', 'clear_goals'],
      difficulty: 0.8,
      duration: 60,
      skillRequired: 0.7,
      energyRequired: 0.9,
    },
  ];

  constructor(apiKey: string) {
    this.advisor = new AIAdvisor(apiKey);
    this.userProfile = this.loadUserProfile();
  }

  private loadUserProfile(): UserFlowProfile {
    const saved = localStorage.getItem('userFlowProfile');
    if (saved) {
      return JSON.parse(saved);
    }
    
    return {
      skillLevels: {},
      preferredTriggers: [],
      challengeThreshold: 0.7,
      optimalTimeOfDay: [9, 10, 11, 14, 15, 16], // Default productive hours
      successfulSessions: [],
    };
  }

  private saveUserProfile() {
    localStorage.setItem('userFlowProfile', JSON.stringify(this.userProfile));
  }

  async recommendFlowTriggers(
    currentState: {
      energy: number;
      skill: number;
      timeOfDay: number;
      previousSuccess?: string[];
    },
    targetActivity: string
  ) {
    const prompt = `
      Analyze the user's current state and recommend optimal flow triggers.
      
      Current State:
      - Energy Level: ${currentState.energy}
      - Skill Level: ${currentState.skill}
      - Time of Day: ${currentState.timeOfDay}
      - Previous Successful Triggers: ${currentState.previousSuccess?.join(', ') || 'None'}
      
      Target Activity: ${targetActivity}
      
      User Profile:
      ${JSON.stringify(this.userProfile, null, 2)}
      
      Available Flow Triggers:
      ${JSON.stringify(this.FLOW_TRIGGERS, null, 2)}
      
      Consider:
      1. Challenge-Skill Balance
      2. Energy Requirements
      3. Time of Day Effects
      4. Previous Success Patterns
      5. Progressive Challenge
      
      Recommend:
      1. Primary flow triggers to activate
      2. Sequence and timing
      3. Environmental adjustments
      4. Specific challenges to maintain engagement
      
      Provide recommendations in JSON format:
      {
        "triggers": [string],
        "sequence": [{
          "trigger": string,
          "timing": number,
          "intensity": number
        }],
        "environment": {
          "lighting": string,
          "sound": string,
          "space": string
        },
        "challenges": [{
          "description": string,
          "difficulty": number,
          "duration": number
        }]
      }
    `;

    try {
      const recommendation = await this.advisor.getFlowTriggerRecommendation(prompt);
      return recommendation;
    } catch (error) {
      console.error('Error getting flow trigger recommendations:', error);
      return this.getDefaultRecommendation(targetActivity);
    }
  }

  private getDefaultRecommendation(targetActivity: string): any {
    const activity = this.FLOW_ACTIVITIES.find(a => a.id === targetActivity);
    if (!activity) return null;

    return {
      triggers: activity.triggers,
      sequence: activity.triggers.map((trigger, index) => ({
        trigger,
        timing: index * 15,
        intensity: 0.7
      })),
      environment: {
        lighting: 'moderate',
        sound: 'ambient',
        space: 'organized'
      },
      challenges: [{
        description: 'Progressive challenge based on activity',
        difficulty: activity.difficulty,
        duration: activity.duration
      }]
    };
  }

  updateUserProfile(sessionData: {
    triggers: string[];
    duration: number;
    flowScore: number;
    skillProgress: Record<string, number>;
  }) {
    // Update skill levels
    Object.entries(sessionData.skillProgress).forEach(([skill, progress]) => {
      this.userProfile.skillLevels[skill] = (this.userProfile.skillLevels[skill] || 0) + progress;
    });

    // Update successful sessions
    this.userProfile.successfulSessions.push({
      date: new Date().toISOString(),
      duration: sessionData.duration,
      triggers: sessionData.triggers,
      flowScore: sessionData.flowScore
    });

    // Update preferred triggers based on success patterns
    this.updatePreferredTriggers();

    // Adjust challenge threshold based on success rate
    this.updateChallengeThreshold();

    // Save updated profile
    this.saveUserProfile();
  }

  private updatePreferredTriggers() {
    // Analyze recent successful sessions to identify effective triggers
    const recentSessions = this.userProfile.successfulSessions
      .slice(-10)
      .filter(session => session.flowScore > 0.7);

    const triggerCounts = new Map<string, number>();
    recentSessions.forEach(session => {
      session.triggers.forEach(trigger => {
        triggerCounts.set(trigger, (triggerCounts.get(trigger) || 0) + 1);
      });
    });

    // Update preferred triggers based on frequency of success
    this.userProfile.preferredTriggers = Array.from(triggerCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([trigger]) => trigger);
  }

  private updateChallengeThreshold() {
    // Calculate success rate from recent sessions
    const recentSessions = this.userProfile.successfulSessions.slice(-10);
    const successRate = recentSessions.filter(s => s.flowScore > 0.7).length / recentSessions.length;

    // Adjust challenge threshold based on success rate
    if (successRate > 0.8) {
      this.userProfile.challengeThreshold = Math.min(0.9, this.userProfile.challengeThreshold + 0.05);
    } else if (successRate < 0.6) {
      this.userProfile.challengeThreshold = Math.max(0.5, this.userProfile.challengeThreshold - 0.05);
    }
  }

  getAvailableActivities(): FlowActivity[] {
    return this.FLOW_ACTIVITIES;
  }

  getFlowTriggers(): FlowTrigger[] {
    return this.FLOW_TRIGGERS;
  }

  getUserProfile(): UserFlowProfile {
    return this.userProfile;
  }
}
