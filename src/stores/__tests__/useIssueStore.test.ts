import { act } from '@testing-library/react';
import { useIssueStore } from '../useIssueStore';
import type { Issue } from '../../types/issue';

const MOCK_ISSUE: Issue = {
  id: '550e8400-e29b-41d4-a716-446655440000',
  title: 'Test issue',
  description: 'Test description',
  status: 'backlog',
  priority: 'medium',
  issue_type: 'task',
  parent_id: null,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

const MOCK_ISSUE_2: Issue = {
  id: '550e8400-e29b-41d4-a716-446655440001',
  title: 'Second issue',
  description: '',
  status: 'ready',
  priority: 'high',
  issue_type: 'bug',
  parent_id: null,
  created_at: '2026-01-02T00:00:00Z',
  updated_at: '2026-01-02T00:00:00Z',
};

beforeEach(() => {
  act(() => useIssueStore.getState().reset());
});

describe('useIssueStore', () => {
  describe('initial state', () => {
    it('starts with empty issues', () => {
      const state = useIssueStore.getState();
      expect(state.issues).toEqual([]);
      expect(state.selectedIssueId).toBeNull();
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  describe('setIssues', () => {
    it('replaces all issues', () => {
      act(() => useIssueStore.getState().setIssues([MOCK_ISSUE, MOCK_ISSUE_2]));
      expect(useIssueStore.getState().issues).toHaveLength(2);
    });
  });

  describe('addIssue', () => {
    it('appends a new issue', () => {
      act(() => useIssueStore.getState().addIssue(MOCK_ISSUE));
      expect(useIssueStore.getState().issues).toEqual([MOCK_ISSUE]);
    });

    it('does not duplicate by id', () => {
      act(() => {
        useIssueStore.getState().addIssue(MOCK_ISSUE);
        useIssueStore.getState().addIssue(MOCK_ISSUE);
      });
      expect(useIssueStore.getState().issues).toHaveLength(1);
    });
  });

  describe('updateIssue', () => {
    it('merges partial fields into existing issue', () => {
      act(() => useIssueStore.getState().setIssues([MOCK_ISSUE]));
      act(() => useIssueStore.getState().updateIssue(MOCK_ISSUE.id, { title: 'Updated' }));
      expect(useIssueStore.getState().issues[0].title).toBe('Updated');
      expect(useIssueStore.getState().issues[0].description).toBe('Test description');
    });

    it('no-ops for unknown id', () => {
      act(() => useIssueStore.getState().setIssues([MOCK_ISSUE]));
      act(() => useIssueStore.getState().updateIssue('unknown-id', { title: 'X' }));
      expect(useIssueStore.getState().issues[0].title).toBe('Test issue');
    });
  });

  describe('removeIssue', () => {
    it('removes by id', () => {
      act(() => useIssueStore.getState().setIssues([MOCK_ISSUE, MOCK_ISSUE_2]));
      act(() => useIssueStore.getState().removeIssue(MOCK_ISSUE.id));
      expect(useIssueStore.getState().issues).toHaveLength(1);
      expect(useIssueStore.getState().issues[0].id).toBe(MOCK_ISSUE_2.id);
    });

    it('clears selectedIssueId if removed issue was selected', () => {
      act(() => {
        useIssueStore.getState().setIssues([MOCK_ISSUE]);
        useIssueStore.getState().selectIssue(MOCK_ISSUE.id);
      });
      act(() => useIssueStore.getState().removeIssue(MOCK_ISSUE.id));
      expect(useIssueStore.getState().selectedIssueId).toBeNull();
    });
  });

  describe('selectIssue', () => {
    it('sets selectedIssueId', () => {
      act(() => useIssueStore.getState().selectIssue(MOCK_ISSUE.id));
      expect(useIssueStore.getState().selectedIssueId).toBe(MOCK_ISSUE.id);
    });

    it('clears selection with null', () => {
      act(() => useIssueStore.getState().selectIssue(MOCK_ISSUE.id));
      act(() => useIssueStore.getState().selectIssue(null));
      expect(useIssueStore.getState().selectedIssueId).toBeNull();
    });
  });

  describe('setLoading / setError', () => {
    it('sets loading state', () => {
      act(() => useIssueStore.getState().setLoading(true));
      expect(useIssueStore.getState().loading).toBe(true);
    });

    it('sets error and clears loading', () => {
      act(() => useIssueStore.getState().setLoading(true));
      act(() => useIssueStore.getState().setError('Network error'));
      expect(useIssueStore.getState().error).toBe('Network error');
      expect(useIssueStore.getState().loading).toBe(false);
    });
  });
});
