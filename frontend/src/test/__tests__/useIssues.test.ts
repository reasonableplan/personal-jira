import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useIssues } from '@/hooks/useIssues';
import { issueApi } from '@/services/api';
import type { Issue } from '@/types/issue';

vi.mock('@/services/api', () => ({
  issueApi: {
    list: vi.fn(),
    transition: vi.fn(),
  },
}));

const MOCK_ISSUES: Issue[] = [
  {
    id: 'i-1',
    title: 'Task A',
    description: null,
    status: 'Backlog',
    priority: 'Medium',
    parent_id: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 'i-2',
    title: 'Task B',
    description: 'desc',
    status: 'InProgress',
    priority: 'High',
    parent_id: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
];

describe('useIssues', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads issues on mount', async () => {
    vi.mocked(issueApi.list).mockResolvedValue(MOCK_ISSUES);

    const { result } = renderHook(() => useIssues());

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.issues).toEqual(MOCK_ISSUES);
    expect(result.current.error).toBeNull();
  });

  it('sets error on fetch failure', async () => {
    vi.mocked(issueApi.list).mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useIssues());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.issues).toEqual([]);
  });

  it('moveIssue optimistically updates then confirms', async () => {
    vi.mocked(issueApi.list).mockResolvedValue(MOCK_ISSUES);
    const moved = { ...MOCK_ISSUES[0]!, status: 'Ready' as const };
    vi.mocked(issueApi.transition).mockResolvedValue(moved);

    const { result } = renderHook(() => useIssues());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.moveIssue('i-1', 'Ready');
    });

    expect(issueApi.transition).toHaveBeenCalledWith('i-1', 'Ready');
    const updated = result.current.issues.find((i) => i.id === 'i-1');
    expect(updated?.status).toBe('Ready');
  });

  it('moveIssue reverts on API failure', async () => {
    vi.mocked(issueApi.list).mockResolvedValue(MOCK_ISSUES);
    vi.mocked(issueApi.transition).mockRejectedValue(new Error('Invalid'));

    const { result } = renderHook(() => useIssues());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.moveIssue('i-1', 'Done');
    });

    expect(result.current.error).toBe('Invalid');
  });
});
