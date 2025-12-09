import { create } from 'zustand';

interface UIState {
  focusMode: boolean;
  modalOpen: boolean;
  currentModal: string | null;
  sidebarCollapsed: boolean;

  toggleFocusMode: () => void;
  openModal: (modalName: string) => void;
  closeModal: () => void;
  toggleSidebar: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  focusMode: false,
  modalOpen: false,
  currentModal: null,
  sidebarCollapsed: false,

  toggleFocusMode: () => set((state) => ({ focusMode: !state.focusMode })),

  openModal: (modalName) =>
    set({ modalOpen: true, currentModal: modalName }),

  closeModal: () => set({ modalOpen: false, currentModal: null }),

  toggleSidebar: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
}));
