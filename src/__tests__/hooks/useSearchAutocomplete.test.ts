import { renderHook, act, waitFor } from '@testing-library/react';
import { useSearchAutocomplete } from '../../hooks/useSearchAutocomplete';
import { searchIssues } from '../../services/issueApi';

jest.mock('../../services/issueApi');
jest.useFakeTimers();

const mockSearchIssues = searchIssues as jest.MockedFunction<typeof searchIssues>;

const MOCK_RESULTS = [
  { id: '1', title: 'Fix login bug', labels: ['bug', 'auth'] },
  { id: '2', title: 'Fix logout flow', labels: ['bug'] },
];

describe('useSearchAutocomplete', () => {
  beforeEach(() => {
    mockSearchIssues.mockReset();
  });

  afterEach(() => {
    jest.clearAllTimers();
  });

  it('returns empty results initially', () => {
    const { result } = renderHook(() => useSearchAutocomplete());
    expect(result.current.results).toEqual([]);
    expect(result.current.query).toBe('');
    expect(result.current.isLoading).toBe(false);
    expect(result.current.isOpen).toBe(false);
  });

  it('does not search for queries shorter than min length', () => {
    const { result } = renderHook(() => useSearchAutocomplete({ minQueryLength: 2 }));

    act(() => { result.current.setQuery('a'); });
    act(() => { jest.advanceTimersByTime(300); });

    expect(mockSearchIssues).not.toHaveBeenCalled();
    expect(result.current.results).toEqual([]);
  });

  it('searches after debounce delay', async () => {
    mockSearchIssues.mockResolvedValue(MOCK_RESULTS);
    const { result } = renderHook(() => useSearchAutocomplete({ debounceMs: 300 }));

    act(() => { result.current.setQuery('Fix'); });
    expect(mockSearchIssues).not.toHaveBeenCalled();

    await act(async () => { jest.advanceTimersByTime(300); });

    await waitFor(() => {
      expect(mockSearchIssues).toHaveBeenCalledWith('Fix');
      expect(result.current.results).toEqual(MOCK_RESULTS);
      expect(result.current.isOpen).toBe(true);
    });
  });

  it('sets loading state during fetch', async () => {
    let resolve: (v: typeof MOCK_RESULTS) => void;
    mockSearchIssues.mockImplementation(
      () => new Promise(r => { resolve = r; })
    );

    const { result } = renderHook(() => useSearchAutocomplete({ debounceMs: 100 }));

    act(() => { result.current.setQuery('Fix'); });
    await act(async () => { jest.advanceTimersByTime(100); });

    expect(result.current.isLoading).toBe(true);

    await act(async () => { resolve!(MOCK_RESULTS); });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
  });

  it('handles API errors gracefully', async () => {
    mockSearchIssues.mockRejectedValue(new Error('Network error'));
    const { result } = renderHook(() => useSearchAutocomplete({ debounceMs: 100 }));

    act(() => { result.current.setQuery('Fix'); });
    await act(async () => { jest.advanceTimersByTime(100); });

    await waitFor(() => {
      expect(result.current.error).toBe('검색 중 오류가 발생했습니다');
      expect(result.current.isLoading).toBe(false);
      expect(result.current.results).toEqual([]);
    });
  });

  it('clears results when query is emptied', async () => {
    mockSearchIssues.mockResolvedValue(MOCK_RESULTS);
    const { result } = renderHook(() => useSearchAutocomplete({ debounceMs: 100 }));

    act(() => { result.current.setQuery('Fix'); });
    await act(async () => { jest.advanceTimersByTime(100); });
    await waitFor(() => { expect(result.current.results).toHaveLength(2); });

    act(() => { result.current.setQuery(''); });
    await act(async () => { jest.advanceTimersByTime(100); });

    expect(result.current.results).toEqual([]);
    expect(result.current.isOpen).toBe(false);
  });

  it('closes dropdown on close()', async () => {
    mockSearchIssues.mockResolvedValue(MOCK_RESULTS);
    const { result } = renderHook(() => useSearchAutocomplete({ debounceMs: 100 }));

    act(() => { result.current.setQuery('Fix'); });
    await act(async () => { jest.advanceTimersByTime(100); });
    await waitFor(() => { expect(result.current.isOpen).toBe(true); });

    act(() => { result.current.close(); });
    expect(result.current.isOpen).toBe(false);
  });

  it('cancels stale requests', async () => {
    let callCount = 0;
    mockSearchIssues.mockImplementation(async (q) => {
      callCount++;
      if (callCount === 1) {
        return [{ id: '99', title: 'Stale', labels: [] }];
      }
      return MOCK_RESULTS;
    });

    const { result } = renderHook(() => useSearchAutocomplete({ debounceMs: 100 }));

    act(() => { result.current.setQuery('Fi'); });
    await act(async () => { jest.advanceTimersByTime(50); });
    act(() => { result.current.setQuery('Fix'); });
    await act(async () => { jest.advanceTimersByTime(100); });

    await waitFor(() => {
      expect(result.current.results).toEqual(MOCK_RESULTS);
    });
  });
});
