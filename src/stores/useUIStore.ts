import { create } from 'zustand';

export const VIEW_MODE = {
  BOARD: 'board',
  LIST: 'list',
  TIMELINE: 'timeline',
} as const;

export type ViewMode = (typeof VIEW_MODE)[keyof typeof VIEW_MODE];

export type SidePanelContentType = 'issue-detail' | 'create-issue' | null;

interface SidePanelState {
  isOpen: boolean;
  contentType: SidePanelContentType;
}

interface UIState {
  sidePanel: SidePanelState;
  viewMode: ViewMode;
  openSidePanel: (contentType: NonNullable<SidePanelContentType>) => void;
  closeSidePanel: () => void;
  toggleSidePanel: (contentType: NonNullable<SidePanelContentType>) => void;
  setViewMode: (mode: ViewMode) => void;
  reset: () => void;
}

const INITIAL_STATE = {
  sidePanel: { isOpen: false, contentType: null as SidePanelContentType },
  viewMode: VIEW_MODE.BOARD as ViewMode,
};

export const useUIStore = create<UIState>((set) => ({
  ...INITIAL_STATE,

  openSidePanel: (contentType) =>
    set({ sidePanel: { isOpen: true, contentType } }),

  closeSidePanel: () =>
    set({ sidePanel: { isOpen: false, contentType: null } }),

  toggleSidePanel: (contentType) =>
    set((state) => {
      if (state.sidePanel.isOpen && state.sidePanel.contentType === contentType) {
        return { sidePanel: { isOpen: false, contentType: null } };
      }
      return { sidePanel: { isOpen: true, contentType } };
    }),

  setViewMode: (mode) => set({ viewMode: mode }),

  reset: () => set(INITIAL_STATE),
}));
