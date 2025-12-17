import { create } from 'zustand';
import { api } from '@/lib/api';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatSession {
  id: string;
  context_type: string;
  context_id?: string;
  messages: ChatMessage[];
  isActive: boolean;
}

export interface AIAction {
  type: 'navigate' | 'display_content' | 'show_exercise';
  data: any;
}

interface ChatState {
  currentSession: ChatSession | null;
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  pendingActions: AIAction[];
  dynamicContentId: string | null;
  dynamicExerciseId: string | null;

  sendMessage: (
    message: string,
    contextType?: string,
    contextId?: string,
    userCode?: string
  ) => Promise<void>;
  getHint: (exerciseId: string, hintLevel: number, userCode?: string) => Promise<string>;
  loadHistory: (sessionId: string) => Promise<void>;
  continueLearningSession: (sessionId: string, message: string) => Promise<any>;
  handleAIResponse: (response: any) => void;
  clearPendingActions: () => void;
  clearChat: () => void;
  clearError: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  currentSession: null,
  messages: [],
  isLoading: false,
  error: null,
  pendingActions: [],
  dynamicContentId: null,
  dynamicExerciseId: null,

  sendMessage: async (message, contextType = 'general', contextId, userCode) => {
    set({ isLoading: true, error: null });

    // Check if this is a background request (should not show in chat)
    const isBackground = message.startsWith('[BACKGROUND]');

    // Debug logging
    console.log("chatStore.sendMessage called with:", {
      message: message.substring(0, 50),
      contextType,
      contextId,
      userCode,
      isBackground
    });

    // Only add user message to chat if NOT a background request
    if (!isBackground) {
      const userMessage: ChatMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
      };
      set((state) => ({
        messages: [...state.messages, userMessage],
      }));
    }

    try {
      console.log("🚀 Sending to /chat/message API:", {
        message: message.substring(0, 50),
        context_type: contextType,
        context_id: contextId,
        user_code: userCode
      });

      const response = await api.sendChatMessage({
        message,
        context_type: contextType,
        context_id: contextId,
        user_code: userCode,
      });

      // Add assistant response
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: response.timestamp,
      };

      set((state) => ({
        messages: [...state.messages, assistantMessage],
        isLoading: false,
      }));

      // Handle AI actions (including navigation)
      get().handleAIResponse(response);
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to send message',
        isLoading: false,
      });
      // Remove optimistic user message on error (only if it was added)
      if (!isBackground) {
        set((state) => ({
          messages: state.messages.slice(0, -1),
        }));
      }
      throw error;
    }
  },

  getHint: async (exerciseId, hintLevel, userCode = '') => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.getHint(exerciseId, hintLevel, userCode);

      // Add hint as assistant message
      const hintMessage: ChatMessage = {
        role: 'assistant',
        content: `💡 **Hint ${hintLevel}:**\n\n${response.hint}`,
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, hintMessage],
        isLoading: false,
      }));

      return response.hint;
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to get hint',
        isLoading: false,
      });
      throw error;
    }
  },

  loadHistory: async (sessionId) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.getChatHistory(sessionId);
      set({
        messages: response.messages,
        isLoading: false,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to load history',
        isLoading: false,
      });
      throw error;
    }
  },

  continueLearningSession: async (sessionId: string, message: string) => {
    set({ isLoading: true, error: null });

    console.log("🚀 Sending to /learning-session/continue API (bypasses context routing!):", {
      sessionId,
      message: message.substring(0, 50)
    });

    // Add user message
    const userMessage: ChatMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    set((state) => ({
      messages: [...state.messages, userMessage],
    }));

    try {
      const response = await api.continueLearning(sessionId, message);

      // Add AI response
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, assistantMessage],
        isLoading: false,
      }));

      // Handle AI actions
      get().handleAIResponse(response);

      return response;
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to continue learning',
        isLoading: false,
      });
      // Remove optimistic message
      set((state) => ({
        messages: state.messages.slice(0, -1),
      }));
      throw error;
    }
  },

  handleAIResponse: (response: any) => {
    const actions: AIAction[] = [];

    // Handle content_id
    if (response.content_id) {
      set({ dynamicContentId: response.content_id });
      actions.push({
        type: 'display_content',
        data: { content_id: response.content_id },
      });
    }

    // Handle exercise_id
    if (response.exercise_id) {
      set({ dynamicExerciseId: response.exercise_id });
      actions.push({
        type: 'show_exercise',
        data: { exercise_id: response.exercise_id },
      });
    }

    // Handle explicit actions
    if (response.actions && Array.isArray(response.actions)) {
      actions.push(...response.actions);
    }

    // Extract actions from tool results (for navigate_to_next_step tool)
    if (response.tool_results && Array.isArray(response.tool_results)) {
      response.tool_results.forEach((result: any) => {
        if (result.action) {
          console.log('📦 Extracted action from tool result:', result.action);
          actions.push(result.action);
        }
      });
    }

    // Store actions
    if (actions.length > 0) {
      console.log('💾 Storing pending actions:', actions);
      set({ pendingActions: actions });
    }
  },

  clearPendingActions: () => {
    set({ pendingActions: [] });
  },

  clearChat: () => {
    set({
      messages: [],
      currentSession: null,
      error: null,
      pendingActions: [],
      dynamicContentId: null,
      dynamicExerciseId: null,
    });
  },

  clearError: () => set({ error: null }),
}));
