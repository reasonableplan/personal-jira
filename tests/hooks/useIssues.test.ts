import { renderHook, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, type Mock } from 'vitest';
import { useIssues } from '../../src/hooks/useIssues';
import { fetchIssues } from '../../src/api/issues';
import { IssueStatus, IssuePriority, IssueType, PaginatedResponse, Issue } from '../../src/types/issue';

vi.mock('../../src/api/issues');

const mockFetchIssues = fetchIssues as Mock;

const mockResponse: PaginatedResponse<Issue> = {
  items: [
    {
      id: '1',
      title: 'Test',
      description: null,
      issue_type: IssueType.TASK,
      status: IssueStatus.TODO,
      priority: IssuePriority.MEDIUM,
      assignee: null,
      labels: [],
      required_skills: [],
      parent_id: null,
      context_bundle: null,
      created_at: '2026-03-20T10:00:00Z',
      updated_at: '2026-03-20T10:00:00Z',
    },
  ],
  total: 1,
  page: 1,
  page_size: 20,
  total_pages: 1,
};

describe('useIssues', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetchIssues.mockResolvedValue(mockResponse);
  });

  it('fetches issues on mount', async () => {
    const { result } = renderHook(() => useIssues());

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockResponse);
    expect(mockFetchIssues).toHaveBeenCalledWith(1, 20, {}, undefined, undefined);
  });

  it('uses initial options', async () => {
    const { result } = renderHook(() =>
      useIssues({
        initialPage: 2,
        initialPageSize: 50,
        initialFilters: { status: IssueStatus.TODO },
        initialSortField: 'title',
        initialSortOrder: 'asc',
      })
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(mockFetchIssues).toHaveBeenCalledWith(
      2, 50, { status: IssueStatus.TODO }, 'title', 'asc'
    );
  });

  it('sets error on fetch failure', async () => {
    mockFetchIssues.mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useIssues());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.data).toBeNull();
  });

  it('resets page to 1 when filters change', async () => {
    const { result } = renderHook(() => useIssues({ initialPage: 3 }));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    act(() => {
      result.current.setFilters({ status: IssueStatus.DONE });
    });

    expect(result.current.page).toBe(1);
  });

  it('resets page to 1 when page size changes', async () => {
    const { result } = renderHook(() => useIssues({ initialPage: 3 }));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    act(() => {
      result.current.setPageSize(50);
    });

    expect(result.current.page).toBe(1);
  });

  it('resets page to 1 when sorting changes', async () => {
    const { result } = renderHook(() => useIssues({ initialPage: 3 }));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    act(() => {
      result.current.setSorting('priority', 'desc');
    });

    expect(result.current.page).toBe(1);
  });

  it('refetch reloads data', async () => {
    const { result } = renderHook(() => useIssues());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(mockFetchIssues).toHaveBeenCalledTimes(1);

    act(() => {
      result.current.refetch();
    });

    await waitFor(() => {
      expect(mockFetchIssues).toHaveBeenCalledTimes(2);
    });
  });
});
