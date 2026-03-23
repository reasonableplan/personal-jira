import { renderHook, act } from '@testing-library/react';
import { useDebounce } from '../../hooks/useDebounce';

jest.useFakeTimers();

describe('useDebounce', () => {
  afterEach(() => {
    jest.clearAllTimers();
  });

  it('returns initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('hello', 300));
    expect(result.current).toBe('hello');
  });

  it('does not update value before delay', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'hello', delay: 300 } }
    );

    rerender({ value: 'world', delay: 300 });
    act(() => { jest.advanceTimersByTime(200); });
    expect(result.current).toBe('hello');
  });

  it('updates value after delay', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'hello', delay: 300 } }
    );

    rerender({ value: 'world', delay: 300 });
    act(() => { jest.advanceTimersByTime(300); });
    expect(result.current).toBe('world');
  });

  it('resets timer on rapid changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'a', delay: 300 } }
    );

    rerender({ value: 'ab', delay: 300 });
    act(() => { jest.advanceTimersByTime(100); });
    rerender({ value: 'abc', delay: 300 });
    act(() => { jest.advanceTimersByTime(200); });
    expect(result.current).toBe('a');

    act(() => { jest.advanceTimersByTime(100); });
    expect(result.current).toBe('abc');
  });

  it('cleans up timer on unmount', () => {
    const { unmount } = renderHook(() => useDebounce('test', 300));
    const clearTimeoutSpy = jest.spyOn(global, 'clearTimeout');
    unmount();
    expect(clearTimeoutSpy).toHaveBeenCalled();
    clearTimeoutSpy.mockRestore();
  });
});
