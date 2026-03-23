import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useBurndownData } from '../useBurndownData';
import type { BurndownData } from '../../types/burndown';

const MOCK_RESPONSE: BurndownData = {
  sprintName: 'Sprint 1',
  startDate: '2026-03-01',
  endDate: '2026-03-14',
  totalPoints: 40,
  points: [
    { date: '2026-03-01', ideal: 40, actual: 40 },
    { date: '2026-03-14', ideal: 0, actual: 5 },
  ],
};

describe('useBurndownData', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('returns loading state initially', () => {
    (fetch as ReturnType<typeof vi.fn>).mockReturnValue(new Promise(() => {}));
    const { result } = renderHook(() => useBurndownData('sprint-1'));
    expect(result.current.isLoading).toBe(true);
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('fetches and returns burndown data', async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_RESPONSE),
    });
    const { result } = renderHook(() => useBurndownData('sprint-1'));
    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.data).toEqual(MOCK_RESPONSE);
    expect(result.current.error).toBeNull();
  });

  it('calls correct API endpoint', async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_RESPONSE),
    });
    renderHook(() => useBurndownData('sprint-1'));
    expect(fetch).toHaveBeenCalledWith('/api/v1/sprints/sprint-1/burndown');
  });

  it('handles fetch error', async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found',
    });
    const { result } = renderHook(() => useBurndownData('sprint-1'));
    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBe('번다운 데이터 로드 실패: 404 Not Found');
  });

  it('handles network error', async () => {
    (fetch as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('Network error'));
    const { result } = renderHook(() => useBurndownData('sprint-1'));
    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBe('Network error');
  });

  it('does not fetch when sprintId is empty', () => {
    renderHook(() => useBurndownData(''));
    expect(fetch).not.toHaveBeenCalled();
  });

  it('refetches when sprintId changes', async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_RESPONSE),
    });
    const { rerender } = renderHook(
      ({ id }) => useBurndownData(id),
      { initialProps: { id: 'sprint-1' } },
    );
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    rerender({ id: 'sprint-2' });
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
    expect(fetch).toHaveBeenLastCalledWith('/api/v1/sprints/sprint-2/burndown');
  });
});
