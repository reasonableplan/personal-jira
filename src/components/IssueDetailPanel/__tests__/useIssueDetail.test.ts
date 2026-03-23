import { renderHook, waitFor, act } from '@testing-library/react';
import { useIssueDetail } from '../useIssueDetail';

const mockFetch = jest.fn();
global.fetch = mockFetch;

const ISSUE_ID = 'issue-001';

beforeEach(() => {
  mockFetch.mockClear();
});

describe('useIssueDetail', () => {
  it('fetches comments on mount', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: () => Promise.resolve([]) });
    const { result } = renderHook(() => useIssueDetail(ISSUE_ID));
    expect(result.current.commentsLoading).toBe(true);
    await waitFor(() => expect(result.current.commentsLoading).toBe(false));
    expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining(`/api/v1/issues/${ISSUE_ID}/comments`));
  });

  it('sets comments on success', async () => {
    const comments = [{ id: 'c1', content: 'test' }];
    mockFetch.mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(comments) });
    const { result } = renderHook(() => useIssueDetail(ISSUE_ID));
    await waitFor(() => expect(result.current.comments).toEqual(comments));
  });

  it('handles fetch error', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));
    const { result } = renderHook(() => useIssueDetail(ISSUE_ID));
    await waitFor(() => expect(result.current.commentsLoading).toBe(false));
    expect(result.current.error).toBe('Failed to load issue details');
  });

  it('does not fetch when issueId is null', () => {
    renderHook(() => useIssueDetail(null));
    expect(mockFetch).not.toHaveBeenCalled();
  });

  it('refetches when issueId changes', async () => {
    mockFetch.mockResolvedValue({ ok: true, json: () => Promise.resolve([]) });
    const { rerender } = renderHook(({ id }) => useIssueDetail(id), {
      initialProps: { id: 'issue-001' as string | null },
    });
    await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(1));
    rerender({ id: 'issue-002' });
    await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(2));
  });

  it('exposes activeTab and setActiveTab', () => {
    mockFetch.mockResolvedValue({ ok: true, json: () => Promise.resolve([]) });
    const { result } = renderHook(() => useIssueDetail(ISSUE_ID));
    expect(result.current.activeTab).toBe('detail');
    act(() => result.current.setActiveTab('comments'));
    expect(result.current.activeTab).toBe('comments');
  });
});
