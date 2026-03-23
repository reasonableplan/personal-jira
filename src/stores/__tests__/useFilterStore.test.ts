import { act } from '@testing-library/react';
import { useFilterStore } from '../useFilterStore';

beforeEach(() => {
  act(() => useFilterStore.getState().reset());
});

describe('useFilterStore', () => {
  describe('initial state', () => {
    it('starts with no filters applied', () => {
      const state = useFilterStore.getState();
      expect(state.statusFilter).toEqual([]);
      expect(state.priorityFilter).toEqual([]);
      expect(state.typeFilter).toEqual([]);
      expect(state.searchQuery).toBe('');
    });
  });

  describe('setStatusFilter', () => {
    it('sets status filter values', () => {
      act(() => useFilterStore.getState().setStatusFilter(['backlog', 'ready']));
      expect(useFilterStore.getState().statusFilter).toEqual(['backlog', 'ready']);
    });

    it('replaces previous filter', () => {
      act(() => useFilterStore.getState().setStatusFilter(['backlog']));
      act(() => useFilterStore.getState().setStatusFilter(['done']));
      expect(useFilterStore.getState().statusFilter).toEqual(['done']);
    });
  });

  describe('toggleStatusFilter', () => {
    it('adds status if not present', () => {
      act(() => useFilterStore.getState().toggleStatusFilter('backlog'));
      expect(useFilterStore.getState().statusFilter).toContain('backlog');
    });

    it('removes status if already present', () => {
      act(() => useFilterStore.getState().setStatusFilter(['backlog', 'ready']));
      act(() => useFilterStore.getState().toggleStatusFilter('backlog'));
      expect(useFilterStore.getState().statusFilter).toEqual(['ready']);
    });
  });

  describe('setPriorityFilter', () => {
    it('sets priority filter values', () => {
      act(() => useFilterStore.getState().setPriorityFilter(['high', 'critical']));
      expect(useFilterStore.getState().priorityFilter).toEqual(['high', 'critical']);
    });
  });

  describe('togglePriorityFilter', () => {
    it('toggles priority value', () => {
      act(() => useFilterStore.getState().togglePriorityFilter('high'));
      expect(useFilterStore.getState().priorityFilter).toEqual(['high']);
      act(() => useFilterStore.getState().togglePriorityFilter('high'));
      expect(useFilterStore.getState().priorityFilter).toEqual([]);
    });
  });

  describe('setTypeFilter', () => {
    it('sets type filter values', () => {
      act(() => useFilterStore.getState().setTypeFilter(['bug']));
      expect(useFilterStore.getState().typeFilter).toEqual(['bug']);
    });
  });

  describe('toggleTypeFilter', () => {
    it('toggles type value', () => {
      act(() => useFilterStore.getState().toggleTypeFilter('task'));
      expect(useFilterStore.getState().typeFilter).toEqual(['task']);
      act(() => useFilterStore.getState().toggleTypeFilter('task'));
      expect(useFilterStore.getState().typeFilter).toEqual([]);
    });
  });

  describe('setSearchQuery', () => {
    it('sets search query string', () => {
      act(() => useFilterStore.getState().setSearchQuery('login bug'));
      expect(useFilterStore.getState().searchQuery).toBe('login bug');
    });
  });

  describe('clearFilters', () => {
    it('resets all filters to defaults', () => {
      act(() => {
        useFilterStore.getState().setStatusFilter(['done']);
        useFilterStore.getState().setPriorityFilter(['high']);
        useFilterStore.getState().setTypeFilter(['bug']);
        useFilterStore.getState().setSearchQuery('test');
      });
      act(() => useFilterStore.getState().clearFilters());
      const state = useFilterStore.getState();
      expect(state.statusFilter).toEqual([]);
      expect(state.priorityFilter).toEqual([]);
      expect(state.typeFilter).toEqual([]);
      expect(state.searchQuery).toBe('');
    });
  });

  describe('hasActiveFilters', () => {
    it('returns false when no filters', () => {
      expect(useFilterStore.getState().hasActiveFilters()).toBe(false);
    });

    it('returns true when any filter is set', () => {
      act(() => useFilterStore.getState().setSearchQuery('x'));
      expect(useFilterStore.getState().hasActiveFilters()).toBe(true);
    });
  });
});
