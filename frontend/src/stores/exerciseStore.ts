import { create } from 'zustand';
import { api } from '@/lib/api';
import { Exercise, ExerciseResult, UserProgress } from '@/types/exercise';

interface ExerciseState {
  currentExercise: (Exercise & { user_progress: UserProgress }) | null;
  editorCode: string;
  submissionStatus: 'idle' | 'submitting' | 'grading' | 'completed';
  results: ExerciseResult | null;
  isLoading: boolean;
  error: string | null;

  loadExercise: (exerciseId: string) => Promise<void>;
  setEditorCode: (code: string) => void;
  submitCode: (exerciseId: string, code: string, language: string) => Promise<void>;
  checkResult: (exerciseId: string, submissionId: string) => Promise<void>;
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
    set({ submissionStatus: 'submitting', error: null });
    try {
      const data = await api.submitExercise(exerciseId, code, language);

      // AI assessment is instant - check results immediately
      if (data.status === 'completed') {
        // Get results right away
        const result = await api.getExerciseResult(exerciseId, data.submission_id);
        set({ results: result, submissionStatus: 'completed' });
      } else {
        // Fallback: poll if needed (for old sandbox grading)
        set({ submissionStatus: 'grading' });
        setTimeout(() => {
          get().checkResult(exerciseId, data.submission_id);
        }, 1000);
      }
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to submit exercise',
        submissionStatus: 'idle',
      });
    }
  },

  checkResult: async (exerciseId, submissionId) => {
    try {
      const result = await api.getExerciseResult(exerciseId, submissionId);
      if (result.status === 'completed') {
        set({ results: result, submissionStatus: 'completed' });
      } else {
        // Keep polling (should rarely happen with AI assessment)
        setTimeout(() => {
          get().checkResult(exerciseId, submissionId);
        }, 2000);
      }
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to get results',
        submissionStatus: 'idle',
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
    }),

  clearError: () => set({ error: null }),
}));
