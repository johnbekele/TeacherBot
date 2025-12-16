import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default config
export const api = axios.create({
  baseURL: `${API_URL}/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API methods
export default {
  // Auth
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  register: (email: string, password: string, name: string) =>
    api.post('/auth/register', { email, password, name }),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),

  // Nodes
  getNodes: () => api.get('/nodes'),
  getNode: (nodeId: string) => api.get(`/nodes/${nodeId}`),
  createNode: (data: any) => api.post('/nodes', data),

  // Exercises
  getExercise: (exerciseId: string) => api.get(`/exercises/${exerciseId}`),
  submitExercise: (exerciseId: string, code: string) =>
    api.post(`/exercises/${exerciseId}/submit`, { code }),
  getHint: (exerciseId: string, hintLevel: number, userCode: string) =>
    api.post(`/exercises/${exerciseId}/hint`, { hint_level: hintLevel, user_code: userCode }),

  // Chat
  sendChatMessage: (data: {
    message: string;
    context_type?: string;
    context_id?: string;
    user_code?: string;
  }) => api.post('/chat/message', data),
  getChatHistory: (sessionId: string) => api.get(`/chat/history/${sessionId}`),
  continueLearning: (sessionId: string, message: string) =>
    api.post('/learning-session/continue', { session_id: sessionId, message }),

  // Progress
  getProgress: () => api.get('/progress'),
  updateProgress: (nodeId: string, status: string) =>
    api.post('/progress', { node_id: nodeId, status }),

  // Onboarding
  submitOnboarding: (data: any) => api.post('/onboarding', data),
};
