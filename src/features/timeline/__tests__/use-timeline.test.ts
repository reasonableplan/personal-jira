import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useTimeline } from '../use-timeline';
import type { TimelineIssue } from '../types';

const MOCK_ISSUES: TimelineIssue[] = [
  { id: '1', title: 'Auth API', epicId: 'e1', epicTitle: 'Auth Epic', status: 'IN_PROGRESS', priority: 'HIGH', startDate: '2026-03-01', dueDate: '2026-03-10' },
  { id: '2', title: 'Login UI', epicId: 'e1', epicTitle: 'Auth Epic', status: 'TODO', priority: 'MEDIUM', startDate: '2026-03-05', dueDate: '2026-03-15' },
  { id: '3', title: 'Dashboard', epicId: 'e2', epicTitle: 'UI Epic', status: 'DONE', priority: 'LOW', startDate: '2026-03-03', dueDate: '2026-03-08' },
];

const mockFetch = vi.fn();
global.fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
});

describe('useTimeline', () => {
  it('fetches and returns grouped timeline data', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => MOCK_ISSUES,
    });

    const { result } = renderHook(() => useTimeline());

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.epicGroups).toHaveLength(2);
    expect(result.current.epicGroups[0].epicTitle).toBe('Auth Epic');
    expect(result.current.epicGroups[0].issues).toHaveLength(2);
    expect(result.current.error).toBeNull();
  });

  it('handles fetch error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
    });

    const { result } = renderHook(() => useTimeline());

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.error).toBe('Failed to fetch timeline: 500 Internal Server Error');
    expect(result.current.epicGroups).toEqual([]);
  });

  it('handles network error', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useTimeline());

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.error).toBe('Network error');
    expect(result.current.epicGroups).toEqual([]);
  });

  it('computes timeline range from all issues', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => MOCK_ISSUES,
    });

    const { result } = renderHook(() => useTimeline());

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.timelineStart).toBe('2026-03-01');
    expect(result.current.totalDays).toBeGreaterThanOrEqual(14);
  });
});
