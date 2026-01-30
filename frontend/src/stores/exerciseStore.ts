import { create } from 'zustand';
import { api } from '@/lib/api';
import { Exercise, ExerciseResult, UserProgress } from '@/types/exercise';

// Polling configuration
const MAX_POLL_ATTEMPTS = 10;
const INITIAL_POLL_INTERVAL = 1000;
const MAX_POLL_INTERVAL = 8000;

interface ExerciseState {
  currentExercise: (Exercise & { user_progress: UserProgress }) | null;
  editorCode: string;
  submissionStatus: 'idle' | 'submitting' | 'grading' | 'completed';
  results: ExerciseResult | null;
  isLoading: boolean;
  error: string | null;
  pollAttempts: number;
  lastSubmissionTime: number;

  loadExercise: (exerciseId: string) => Promise<void>;
  setEditorCode: (code: string) => void;
  submitCode: (exerciseId: string, code: string, language: string) => Promise<void>;
  checkResult: (exerciseId: string, submissionId: string, attempt?: number) => Promise<void>;
  requestHint: (exerciseId: string, hintNumber: number) => Promise<string>;
  reset: () => void;
  clearError: () => void;
}

export const useExerciseStore = create<ExerciseState>((set, get) => ({
  currentExercise: null,
  editorCode: '',
  submissionStatus: 'idle',
  results: null,
  isLoading: false,
  error: null,
  pollAttempts: 0,
  lastSubmissionTime: 0,

  loadExercise: async (exerciseId) => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.getExercise(exerciseId);
      set({
        currentExercise: data.exercise,
        editorCode: data.exercise.starter_code,
        isLoading: false,
        submissionStatus: 'idle',
        results: null,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to load exercise',
        isLoading: false,
      });
    }
  },

  setEditorCode: (code) => set({ editorCode: code }),

  submitCode: async (exerciseId, code, language) => {
    const now = Date.now();
    const lastSubmission = get().lastSubmissionTime;

    // Debounce: prevent rapid submissions (min 2 seconds between)
    if (now - lastSubmission < 2000) {
      console.log('⚠️ Submission throttled - please wait');
      return;
    }

    set({ submissionStatus: 'submitting', error: null, pollAttempts: 0, lastSubmissionTime: now });
    try {
      const data = await api.submitExercise(exerciseId, code, language);

      // AI assessment is instant - check results immediately
      if (data.status === 'completed') {
        const result = await api.getExerciseResult(exerciseId, data.submission_id);
        set({ results: result, submissionStatus: 'completed' });
      } else {
        // Fallback: poll with limits (should rarely happen with AI assessment)
        set({ submissionStatus: 'grading' });
        setTimeout(() => {
          get().checkResult(exerciseId, data.submission_id, 1);
        }, INITIAL_POLL_INTERVAL);
      }
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to submit exercise',
        submissionStatus: 'idle',
      });
    }
  },

  checkResult: async (exerciseId, submissionId, attempt = 1) => {
    // Stop polling after max attempts
    if (attempt > MAX_POLL_ATTEMPTS) {
      console.log('⚠️ Max poll attempts reached, stopping');
      set({
        error: 'Grading is taking longer than expected. Please refresh to check results.',
        submissionStatus: 'idle',
      });
      return;
    }

    try {
      const result = await api.getExerciseResult(exerciseId, submissionId);
      if (result.status === 'completed') {
        set({ results: result, submissionStatus: 'completed', pollAttempts: 0 });
      } else {
        // Exponential backoff: 1s, 2s, 4s, 8s (capped)
        const nextInterval = Math.min(INITIAL_POLL_INTERVAL * Math.pow(2, attempt - 1), MAX_POLL_INTERVAL);
        set({ pollAttempts: attempt });

        console.log(`📊 Poll attempt ${attempt}/${MAX_POLL_ATTEMPTS}, next in ${nextInterval}ms`);

        setTimeout(() => {
          get().checkResult(exerciseId, submissionId, attempt + 1);
        }, nextInterval);
      }
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to get results',
        submissionStatus: 'idle',
        pollAttempts: 0,
      });
    }
  },

  requestHint: async (exerciseId, hintNumber) => {
    try {
      const data = await api.getHint(exerciseId, hintNumber);
      return data.hint;
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to get hint',
      });
      throw error;
    }
  },

  reset: () =>
    set({
      currentExercise: null,
      editorCode: '',
      submissionStatus: 'idle',
      results: null,
      error: null,
      pollAttempts: 0,
    }),

  clearError: () => set({ error: null }),
}));
