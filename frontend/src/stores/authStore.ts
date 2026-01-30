import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api } from '@/lib/api';
import { User, LoginCredentials, RegisterData } from '@/types/user';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  _hasHydrated: boolean;
  _lastLoadTime: number;  // Track when we last loaded user
  _loadPromise: Promise<void> | null;  // Prevent duplicate requests

  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  loadUser: () => Promise<void>;
  clearError: () => void;
  setHasHydrated: (state: boolean) => void;
}

// Minimum time between loadUser API calls (5 minutes)
const LOAD_USER_THROTTLE_MS = 5 * 60 * 1000;

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: true,
      error: null,
      _hasHydrated: false,
      _lastLoadTime: 0,
      _loadPromise: null,

  login: async (credentials) => {
    console.log('Store: Starting login...');
    set({ isLoading: true, error: null });
    try {
      const data = await api.login(credentials);
      console.log('Store: Login successful, user:', data.user);
      set({
        user: data.user,
        token: data.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
      console.log('Store: Auth state updated');
    } catch (error: any) {
      console.error('Store: Login error:', error);
      const errorMsg = error.response?.data?.detail || 'Login failed';
      set({
        error: errorMsg,
        isLoading: false,
      });
      throw error;
    }
  },

  register: async (data) => {
    set({ isLoading: true, error: null });
    try {
      await api.register(data);
      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Registration failed',
        isLoading: false,
      });
      throw error;
    }
  },

  logout: async () => {
    try {
      await api.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      set({
        user: null,
        token: null,
        isAuthenticated: false,
      });
    }
  },

  loadUser: async () => {
    const state = get();

    // If already authenticated and recently loaded, skip API call
    if (state.isAuthenticated && state.user && (Date.now() - state._lastLoadTime < LOAD_USER_THROTTLE_MS)) {
      set({ isLoading: false });
      return;
    }

    // If there's already a pending request, wait for it
    if (state._loadPromise) {
      return state._loadPromise;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isAuthenticated: false, isLoading: false });
      return;
    }

    // If we have user data from persistence and it's recent, use it
    if (state.isAuthenticated && state.user && state._hasHydrated) {
      set({ isLoading: false, _lastLoadTime: Date.now() });
      return;
    }

    set({ isLoading: true });

    const loadPromise = (async () => {
      try {
        const user = await api.getCurrentUser();
        set({
          user,
          token,
          isAuthenticated: true,
          isLoading: false,
          _lastLoadTime: Date.now(),
          _loadPromise: null,
        });
      } catch (error) {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
          _loadPromise: null,
        });
      }
    })();

    set({ _loadPromise: loadPromise });
    return loadPromise;
  },

  clearError: () => set({ error: null }),

  setHasHydrated: (state) => set({ _hasHydrated: state }),
}),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);
