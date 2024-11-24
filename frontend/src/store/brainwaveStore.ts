import { create } from 'zustand';
import { prisma } from '../lib/db';

interface BrainwaveState {
  currentSession: string | null;
  alpha: number;
  beta: number;
  theta: number;
  gamma: number;
  delta: number;
  attention: number;
  meditation: number;
  flowScore: number;
  isRecording: boolean;
  actions: {
    startSession: (userId: string, targetState: 'focus' | 'flow' | 'meditate') => Promise<void>;
    endSession: () => Promise<void>;
    updateBrainwaves: (data: {
      alpha: number;
      beta: number;
      theta: number;
      gamma: number;
      delta?: number;
      attention?: number;
      meditation?: number;
      flowScore?: number;
    }) => Promise<void>;
  };
}

export const useBrainwaveStore = create<BrainwaveState>((set, get) => ({
  currentSession: null,
  alpha: 0,
  beta: 0,
  theta: 0,
  gamma: 0,
  delta: 0,
  attention: 0,
  meditation: 0,
  flowScore: 0,
  isRecording: false,

  actions: {
    startSession: async (userId: string, targetState: 'focus' | 'flow' | 'meditate') => {
      try {
        // Create new session in database
        const session = await prisma.session.create({
          data: {
            userId,
            targetState,
            baseFreq: 200, // Default values, will be updated by audio engine
            beatFreq: 10,
            userState: {
              create: {
                timeOfDay: new Date().getHours(),
              },
            },
          },
        });

        set({
          currentSession: session.id,
          isRecording: true,
          alpha: 0,
          beta: 0,
          theta: 0,
          gamma: 0,
          delta: 0,
          attention: 0,
          meditation: 0,
          flowScore: 0,
        });

      } catch (error) {
        console.error('Failed to start session:', error);
        throw error;
      }
    },

    endSession: async () => {
      const { currentSession } = get();
      if (!currentSession) return;

      try {
        // Update session end time
        await prisma.session.update({
          where: { id: currentSession },
          data: { endTime: new Date() },
        });

        set({
          currentSession: null,
          isRecording: false,
        });

      } catch (error) {
        console.error('Failed to end session:', error);
        throw error;
      }
    },

    updateBrainwaves: async (data) => {
      const { currentSession } = get();
      if (!currentSession) return;

      try {
        // Store brainwave data in database
        await prisma.brainwave.create({
          data: {
            sessionId: currentSession,
            ...data,
          },
        });

        // Update local state
        set({
          alpha: data.alpha,
          beta: data.beta,
          theta: data.theta,
          gamma: data.gamma,
          delta: data.delta || 0,
          attention: data.attention || 0,
          meditation: data.meditation || 0,
          flowScore: data.flowScore || 0,
        });

      } catch (error) {
        console.error('Failed to update brainwaves:', error);
        throw error;
      }
    },
  },
}));