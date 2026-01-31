import axios, { type AxiosInstance } from 'axios';

// Always use /api prefix - Next.js rewrites proxy this to the backend
// This avoids CORS issues completely
const baseURL = '/api';

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem('auth-storage');
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    return parsed?.state?.token ?? null;
  } catch {
    return null;
  }
}

const client: AxiosInstance = axios.create({
  baseURL: `${baseURL}/v1`,
  headers: { 'Content-Type': 'application/json' },
});

client.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const api = {
  // Auth
  login: (credentials: { email: string; password: string }) =>
    client.post('/auth/login', credentials).then((r) => r.data),

  register: (data: { email: string; password: string; full_name: string }) =>
    client.post('/auth/register', data).then((r) => r.data),

  logout: () => client.post('/auth/logout').then((r) => r.data),

  getCurrentUser: () => client.get('/auth/me').then((r) => r.data),

  updateProfile: (data: { full_name: string }) =>
    client.put('/auth/profile', data).then((r) => r.data),

  updateSettings: (settings: Record<string, unknown>) =>
    client.put('/auth/settings', { settings }).then((r) => r.data),

  // Nodes
  getNodes: (params?: { category?: string; difficulty?: string }) =>
    client.get('/nodes', { params }).then((r) => r.data),

  getNode: (nodeId: string) =>
    client.get(`/nodes/${nodeId}`).then((r) => r.data),

  startNode: (nodeId: string) =>
    client.post(`/nodes/${nodeId}/start`).then((r) => r.data),

  // Exercises
  getExercise: (exerciseId: string) =>
    client.get(`/exercises/${exerciseId}`).then((r) => r.data),

  submitExercise: (exerciseId: string, code: string, language: string) =>
    client
      .post(`/exercises/${exerciseId}/submit`, { code, language })
      .then((r) => r.data),

  getExerciseResult: (exerciseId: string, submissionId: string) =>
    client
      .get(`/exercises/${exerciseId}/result/${submissionId}`)
      .then((r) => r.data),

  getHint: (
    exerciseId: string,
    hintLevelOrNumber: number,
    userCode?: string
  ) => {
    if (userCode !== undefined && userCode !== null) {
      return client
        .post('/chat/hint', {
          exercise_id: exerciseId,
          hint_level: hintLevelOrNumber,
          user_code: userCode,
        })
        .then((r) => r.data);
    }
    return client
      .post(`/exercises/${exerciseId}/hint`, null, {
        params: { hint_number: hintLevelOrNumber },
      })
      .then((r) => r.data);
  },

  // Chat
  sendChatMessage: (body: {
    message: string;
    context_type?: string;
    context_id?: string;
    user_code?: string;
  }) => client.post('/chat/message', body).then((r) => r.data),

  getChatHistory: (sessionId: string) =>
    client.get(`/chat/history/${sessionId}`).then((r) => r.data),

  // Learning session
  continueLearning: (sessionId: string, message: string) =>
    client
      .post('/learning-session/continue', { session_id: sessionId, message })
      .then((r) => r.data),

  startLearningSession: (nodeId: string) =>
    client.post(`/learning-session/start/${nodeId}`).then((r) => r.data),

  // Course content (instant learning)
  startLearningInstant: (nodeId: string) =>
    client.post(`/course-content/start/${nodeId}`).then((r) => r.data),

  getLearningStep: (nodeId: string, stepNumber: number) =>
    client
      .get(`/course-content/step/${nodeId}/${stepNumber}`)
      .then((r) => r.data),

  getAllSteps: (nodeId: string) =>
    client.get(`/course-content/all-steps/${nodeId}`).then((r) => r.data),

  // Learning paths (no trailing slash to avoid redirect losing auth header)
  getLearningPaths: () =>
    client.get('/learning-paths').then((r) => r.data),

  getLearningPathDetail: (pathId: string) =>
    client.get(`/learning-paths/${pathId}`).then((r) => r.data),

  // Progress
  getDashboardStats: () =>
    client.get('/progress/dashboard').then((r) => r.data),

  // Onboarding
  getOnboardingQuestions: () =>
    client.get('/onboarding/questions').then((r) => r.data),

  submitAssessment: (body: {
    answers: Array<{ question_index: number; answer: string }>;
    free_text_goals?: string | null;
  }) => client.post('/onboarding/assess', body).then((r) => r.data),
};
