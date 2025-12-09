import { create } from 'zustand';
import { api } from '@/lib/api';
import { Node, NodeDetail } from '@/types/node';

interface NodeState {
  nodes: Node[];
  currentNode: NodeDetail | null;
  isLoading: boolean;
  error: string | null;

  loadNodes: (params?: { category?: string; difficulty?: string }) => Promise<void>;
  selectNode: (nodeId: string) => Promise<void>;
  startNode: (nodeId: string) => Promise<void>;
  clearError: () => void;
}

export const useNodeStore = create<NodeState>((set) => ({
  nodes: [],
  currentNode: null,
  isLoading: false,
  error: null,

  loadNodes: async (params) => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.getNodes(params);
      set({ nodes: data.nodes, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to load nodes',
        isLoading: false,
      });
    }
  },

  selectNode: async (nodeId) => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.getNode(nodeId);
      set({ currentNode: { ...data.node, ...data.progress }, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to load node',
        isLoading: false,
      });
    }
  },

  startNode: async (nodeId) => {
    set({ isLoading: true, error: null });
    try {
      await api.startNode(nodeId);
      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to start node',
        isLoading: false,
      });
    }
  },

  clearError: () => set({ error: null }),
}));
