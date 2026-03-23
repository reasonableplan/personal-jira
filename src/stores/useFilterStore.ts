import { create } from 'zustand';
import type { IssueStatus, IssuePriority, IssueType } from '../types/issue';

interface FilterState {
  statusFilter: IssueStatus[];
  priorityFilter: IssuePriority[];
  typeFilter: IssueType[];
  searchQuery: string;
  setStatusFilter: (values: IssueStatus[]) => void;
  toggleStatusFilter: (value: IssueStatus) => void;
  setPriorityFilter: (values: IssuePriority[]) => void;
  togglePriorityFilter: (value: IssuePriority) => void;
  setTypeFilter: (values: IssueType[]) => void;
  toggleTypeFilter: (value: IssueType) => void;
  setSearchQuery: (query: string) => void;
  clearFilters: () => void;
  hasActiveFilters: () => boolean;
  reset: () => void;
}

const INITIAL_STATE = {
  statusFilter: [] as IssueStatus[],
  priorityFilter: [] as IssuePriority[],
  typeFilter: [] as IssueType[],
  searchQuery: '',
};

const toggleItem = <T>(arr: T[], item: T): T[] =>
  arr.includes(item) ? arr.filter((v) => v !== item) : [...arr, item];

export const useFilterStore = create<FilterState>((set, get) => ({
  ...INITIAL_STATE,

  setStatusFilter: (values) => set({ statusFilter: values }),
  toggleStatusFilter: (value) =>
    set((s) => ({ statusFilter: toggleItem(s.statusFilter, value) })),

  setPriorityFilter: (values) => set({ priorityFilter: values }),
  togglePriorityFilter: (value) =>
    set((s) => ({ priorityFilter: toggleItem(s.priorityFilter, value) })),

  setTypeFilter: (values) => set({ typeFilter: values }),
  toggleTypeFilter: (value) =>
    set((s) => ({ typeFilter: toggleItem(s.typeFilter, value) })),

  setSearchQuery: (query) => set({ searchQuery: query }),

  clearFilters: () => set(INITIAL_STATE),

  hasActiveFilters: () => {
    const s = get();
    return (
      s.statusFilter.length > 0 ||
      s.priorityFilter.length > 0 ||
      s.typeFilter.length > 0 ||
      s.searchQuery !== ''
    );
  },

  reset: () => set(INITIAL_STATE),
}));
