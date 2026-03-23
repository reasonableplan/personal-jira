import { create } from 'zustand';
import type { Issue } from '../types/issue';

interface IssueState {
  issues: Issue[];
  selectedIssueId: string | null;
  loading: boolean;
  error: string | null;
  setIssues: (issues: Issue[]) => void;
  addIssue: (issue: Issue) => void;
  updateIssue: (id: string, patch: Partial<Issue>) => void;
  removeIssue: (id: string) => void;
  selectIssue: (id: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const INITIAL_STATE = {
  issues: [] as Issue[],
  selectedIssueId: null as string | null,
  loading: false,
  error: null as string | null,
};

export const useIssueStore = create<IssueState>((set) => ({
  ...INITIAL_STATE,

  setIssues: (issues) => set({ issues }),

  addIssue: (issue) =>
    set((state) => {
      if (state.issues.some((i) => i.id === issue.id)) return state;
      return { issues: [...state.issues, issue] };
    }),

  updateIssue: (id, patch) =>
    set((state) => ({
      issues: state.issues.map((i) => (i.id === id ? { ...i, ...patch } : i)),
    })),

  removeIssue: (id) =>
    set((state) => ({
      issues: state.issues.filter((i) => i.id !== id),
      selectedIssueId: state.selectedIssueId === id ? null : state.selectedIssueId,
    })),

  selectIssue: (id) => set({ selectedIssueId: id }),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error, loading: false }),

  reset: () => set(INITIAL_STATE),
}));
