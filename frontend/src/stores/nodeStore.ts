import { create } from 'zustand';
import { api } from '@/lib/api';
import { Node, NodeDetail } from '@/types/node';

interface NodeState {
  nodes: Node[];
  currentNode: NodeDetail | null;
  isLoading: boolean;
  error: string | null;
  _nodesCache: Record<string, NodeDetail>;  // Cache fetched nodes
  _pendingRequests: Record<string, Promise<void>>;  // Prevent duplicate requests

  loadNodes: (params?: { category?: string; difficulty?: string }) => Promise<void>;
  selectNode: (nodeId: string) => Promise<void>;
  startNode: (nodeId: string) => Promise<void>;
  clearError: () => void;
}

export const useNodeStore = create<NodeState>((set, get) => ({
  nodes: [],
  currentNode: null,
  isLoading: false,
  error: null,
  _nodesCache: {},
  _pendingRequests: {},

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
    const state = get();

    // If already selected and cached, use cached version (instant!)
    if (state.currentNode?.node_id === nodeId) {
      return;
    }

    // Check cache first
    if (state._nodesCache[nodeId]) {
      set({ currentNode: state._nodesCache[nodeId], isLoading: false });
      return;
    }

    // If there's already a pending request for this node, wait for it
    if (nodeId in state._pendingRequests && state._pendingRequests[nodeId] !== undefined) {
      return state._pendingRequests[nodeId];
    }

    set({ isLoading: true, error: null });

    const request = (async () => {
      try {
        const data = await api.getNode(nodeId);
        const nodeDetail = { ...data.node, ...data.progress };

        set((state) => ({
          currentNode: nodeDetail,
          isLoading: false,
          _nodesCache: { ...state._nodesCache, [nodeId]: nodeDetail },
          _pendingRequests: { ...state._pendingRequests, [nodeId]: undefined as any },
        }));
      } catch (error: any) {
        set((state) => ({
          error: error.response?.data?.detail || 'Failed to load node',
          isLoading: false,
          _pendingRequests: { ...state._pendingRequests, [nodeId]: undefined as any },
        }));
      }
    })();

    set((state) => ({
      _pendingRequests: { ...state._pendingRequests, [nodeId]: request },
    }));

    return request;
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
