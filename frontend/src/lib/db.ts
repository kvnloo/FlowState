import { PrismaClient } from '@prisma/client';

// Use environment variable to connect to the backend's Prisma instance
const BACKEND_URL = process.env.VITE_BACKEND_URL || 'http://localhost:8000';

// Instead of direct Prisma connection, we'll use API endpoints
export const db = {
  // Session operations
  sessions: {
    create: async (data: any) => {
      const response = await fetch(`${BACKEND_URL}/api/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      return response.json();
    },
    update: async (id: string, data: any) => {
      const response = await fetch(`${BACKEND_URL}/api/sessions/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      return response.json();
    },
  },
  
  // Brainwave data operations
  brainwaves: {
    create: async (data: any) => {
      const response = await fetch(`${BACKEND_URL}/api/brainwaves`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      return response.json();
    },
  },
  
  // User operations
  users: {
    findUnique: async (id: string) => {
      const response = await fetch(`${BACKEND_URL}/api/users/${id}`);
      return response.json();
    },
    update: async (id: string, data: any) => {
      const response = await fetch(`${BACKEND_URL}/api/users/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      return response.json();
    },
  },
};
